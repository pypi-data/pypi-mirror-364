#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import os
import shutil
from pathlib import Path

import pyspark.sql.connect.proto.base_pb2 as proto_base
import pyspark.sql.connect.proto.commands_pb2 as commands_proto
from pyspark.errors.exceptions.base import AnalysisException
from pyspark.sql.connect.types import StructType

from snowflake import snowpark
from snowflake.snowpark._internal.analyzer.analyzer_utils import (
    quote_name_without_upper_casing,
    unquote_if_quoted,
)
from snowflake.snowpark.functions import col, lit, object_construct
from snowflake.snowpark_connect.config import (
    auto_uppercase_ddl,
    global_config,
    sessions_config,
    str_to_bool,
)
from snowflake.snowpark_connect.relation.io_utils import (
    convert_file_prefix_path,
    is_cloud_path,
)
from snowflake.snowpark_connect.relation.map_relation import map_relation
from snowflake.snowpark_connect.relation.read.reader_config import CsvWriterConfig
from snowflake.snowpark_connect.relation.stage_locator import get_paths_from_stage
from snowflake.snowpark_connect.relation.utils import random_string
from snowflake.snowpark_connect.type_mapping import snowpark_to_iceberg_type
from snowflake.snowpark_connect.utils.attribute_handling import (
    split_fully_qualified_spark_name,
)
from snowflake.snowpark_connect.utils.context import get_session_id
from snowflake.snowpark_connect.utils.session import get_or_create_snowpark_session
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
    telemetry,
)


# TODO: We will revise/refactor this after changes for all formats are finalized.
def clean_params(params):
    """
    Clean params for write operation. This, for now, allows us to use the same parameter code that
    read operations use.
    """
    # INFER_SCHEMA does not apply to writes
    if "INFER_SCHEMA" in params["format_type_options"]:
        del params["format_type_options"]["INFER_SCHEMA"]


def get_param_from_options(params, options, source):
    match source:
        case "csv":
            config = CsvWriterConfig(options)
            snowpark_args = config.convert_to_snowpark_args()

            if "header" in options:
                params["header"] = str_to_bool(options["header"])
            params["single"] = False

            params["format_type_options"] = snowpark_args
            clean_params(params)
        case "json":
            params["format_type_options"]["FILE_EXTENSION"] = source
        case "parquet":
            params["header"] = True
        case "text":
            config = CsvWriterConfig(options)
            params["format_type_options"]["FILE_EXTENSION"] = "txt"
            params["format_type_options"]["ESCAPE_UNENCLOSED_FIELD"] = "NONE"
            if "lineSep" in options:
                params["format_type_options"]["RECORD_DELIMITER"] = config.get(
                    "linesep"
                )

    if (
        source in ("csv", "parquet", "json") and "nullValue" in options
    ):  # TODO: Null value handling if not specified
        params["format_type_options"]["NULL_IF"] = options["nullValue"]


def _spark_to_snowflake_single_id(name: str) -> str:
    name = quote_name_without_upper_casing(name)
    return name.upper() if auto_uppercase_ddl() else name


def _spark_to_snowflake(multipart_id: str) -> str:
    return ".".join(
        _spark_to_snowflake_single_id(part)
        for part in split_fully_qualified_spark_name(multipart_id)
    )


def map_write(request: proto_base.ExecutePlanRequest):
    write_op = request.plan.command.write_operation
    if write_op.options is not None:
        telemetry.report_io_write(write_op.source, dict(write_op.options))
    else:
        telemetry.report_io_write(write_op.source)

    write_mode = None
    match write_op.mode:
        case commands_proto.WriteOperation.SaveMode.SAVE_MODE_APPEND:
            write_mode = "append"
        case commands_proto.WriteOperation.SaveMode.SAVE_MODE_ERROR_IF_EXISTS:
            write_mode = "errorifexists"
        case commands_proto.WriteOperation.SaveMode.SAVE_MODE_OVERWRITE:
            write_mode = "overwrite"
        case commands_proto.WriteOperation.SaveMode.SAVE_MODE_IGNORE:
            write_mode = "ignore"

    input_df: snowpark.DataFrame = handle_column_names(
        map_relation(write_op.input), write_op.source
    )
    session: snowpark.Session = get_or_create_snowpark_session()

    # Snowflake saveAsTable doesn't support format
    if (
        write_op.HasField("table")
        and write_op.HasField("source")
        and write_op.source in ("csv", "parquet", "json", "text")
    ):
        write_op.source = ""

    should_write_to_single_file = str_to_bool(write_op.options.get("single", "false"))
    if should_write_to_single_file:
        # providing default size as 1GB
        max_file_size = int(
            write_op.options.get("snowflake_max_file_size", "1073741824")
        )
    match write_op.source:
        case "csv" | "parquet" | "json" | "text":
            write_path = get_paths_from_stage(
                [write_op.path],
                session=session,
            )[0]
            # we need a random prefix to support "append" mode
            # otherwise copy into with overwrite=False will fail if the file already exists
            if should_write_to_single_file:
                extention = write_op.source if write_op.source != "text" else "txt"
                temp_file_prefix_on_stage = (
                    f"{write_path}/{random_string(10, 'sas_file_')}.{extention}"
                )
            else:
                temp_file_prefix_on_stage = (
                    f"{write_path}/{random_string(10, 'sas_file_')}"
                )
            overwrite = (
                write_op.mode
                == commands_proto.WriteOperation.SaveMode.SAVE_MODE_OVERWRITE
            )
            parameters = {
                "location": temp_file_prefix_on_stage,
                "file_format_type": write_op.source
                if write_op.source != "text"
                else "csv",
                "format_type_options": {
                    "COMPRESSION": "NONE",
                },
                "overwrite": overwrite,
            }
            if should_write_to_single_file:
                parameters["single"] = True
                parameters["max_file_size"] = max_file_size
            rewritten_df: snowpark.DataFrame = rewrite_df(input_df, write_op.source)
            get_param_from_options(parameters, write_op.options, write_op.source)
            if write_op.partitioning_columns:
                if write_op.source != "parquet":
                    raise SnowparkConnectNotImplementedError(
                        "Partitioning is only supported for parquet format"
                    )
                partitioning_columns = [f'"{c}"' for c in write_op.partitioning_columns]
                if len(partitioning_columns) > 1:
                    raise SnowparkConnectNotImplementedError(
                        "Multiple partitioning columns are not yet supported"
                    )
                else:
                    parameters["partition_by"] = partitioning_columns[0]
            rewritten_df.write.copy_into_location(**parameters)
            if not is_cloud_path(write_op.path):
                store_files_locally(
                    temp_file_prefix_on_stage,
                    write_op.path,
                    overwrite,
                    session,
                )
        case "jdbc":
            from snowflake.snowpark_connect.relation.write.map_write_jdbc import (
                map_write_jdbc,
            )

            options = dict(write_op.options)
            if write_mode is None:
                write_mode = "errorifexists"
            map_write_jdbc(input_df, session, options, write_mode)
        case "iceberg":
            table_name = (
                write_op.path
                if write_op.path is not None and write_op.path != ""
                else write_op.table.table_name
            )
            snowpark_table_name = _spark_to_snowflake(table_name)

            if write_mode == "overwrite":
                if check_snowflake_table_existance(snowpark_table_name, session):
                    session.sql(f"DELETE FROM {snowpark_table_name}").collect()
                    write_mode = "append"

            if write_mode in (None, "", "overwrite"):
                create_iceberg_table(
                    snowpark_table_name=snowpark_table_name,
                    location=write_op.options.get("location", None),
                    schema=input_df.schema,
                    snowpark_session=session,
                )
                write_mode = "append"
            input_df.write.saveAsTable(table_name=snowpark_table_name, mode=write_mode)
        case _:
            snowpark_table_name = _spark_to_snowflake(write_op.table.table_name)

            if (
                write_op.table.save_method
                == commands_proto.WriteOperation.SaveTable.TableSaveMethod.TABLE_SAVE_METHOD_SAVE_AS_TABLE
            ):
                input_df.write.saveAsTable(
                    table_name=snowpark_table_name,
                    mode=write_mode,
                )
            elif (
                write_op.table.save_method
                == commands_proto.WriteOperation.SaveTable.TableSaveMethod.TABLE_SAVE_METHOD_INSERT_INTO
            ):
                input_df.write.saveAsTable(
                    table_name=snowpark_table_name,
                    mode=write_mode or "append",
                )
            else:
                raise SnowparkConnectNotImplementedError(
                    f"Save command not supported: {write_op.table.save_method}"
                )


def map_write_v2(request: proto_base.ExecutePlanRequest):
    write_op = request.plan.command.write_operation_v2
    match write_op.mode:
        case commands_proto.WriteOperationV2.MODE_APPEND:
            write_mode = "append"
        case commands_proto.WriteOperationV2.MODE_CREATE:
            write_mode = "errorifexists"
        case commands_proto.WriteOperationV2.MODE_OVERWRITE:
            write_mode = "overwrite"
        case commands_proto.WriteOperationV2.MODE_REPLACE:
            write_mode = "overwrite"
        case commands_proto.WriteOperationV2.MODE_CREATE_OR_REPLACE:
            write_mode = "overwrite"
        case _:
            raise SnowparkConnectNotImplementedError(
                f"Write operation {write_op.mode} not implemented."
            )

    snowpark_table_name = _spark_to_snowflake(write_op.table_name)

    input_df: snowpark.DataFrame = handle_column_names(
        map_relation(write_op.input), "table"
    )
    session: snowpark.Session = get_or_create_snowpark_session()

    if write_op.table_name is None or write_op.table_name == "":
        raise SnowparkConnectNotImplementedError(
            "Write operation V2 only support table writing now"
        )

    # For OVERWRITE and APPEND modes, check if table exists first - Spark requires table to exist for these operations
    if write_op.mode in (
        commands_proto.WriteOperationV2.MODE_OVERWRITE,
        commands_proto.WriteOperationV2.MODE_APPEND,
    ):
        if not check_snowflake_table_existance(snowpark_table_name, session):
            raise AnalysisException(
                f"[TABLE_OR_VIEW_NOT_FOUND] The table or view `{write_op.table_name}` cannot be found. "
                f"Verify the spelling and correctness of the schema and catalog.\n"
            )

    if write_op.provider.lower() == "iceberg":
        if write_mode == "overwrite" and check_snowflake_table_existance(
            snowpark_table_name, session
        ):
            session.sql(f"DELETE FROM {snowpark_table_name}").collect()
            write_mode = "append"

        if write_mode in (
            "errorifexists",
            "overwrite",
        ):
            create_iceberg_table(
                snowpark_table_name=snowpark_table_name,
                location=write_op.table_properties.get("location"),
                schema=input_df.schema,
                snowpark_session=session,
            )

        input_df.write.saveAsTable(
            table_name=snowpark_table_name,
            mode="append",
        )
    else:
        input_df.write.saveAsTable(
            table_name=snowpark_table_name,
            mode=write_mode,
        )


def create_iceberg_table(
    snowpark_table_name: str,
    location: str,
    schema: StructType,
    snowpark_session: snowpark.Session,
):
    table_schema = [
        f"{_spark_to_snowflake_single_id(field.name)} {snowpark_to_iceberg_type(field.datatype)}"
        for field in schema.fields
    ]

    location = (
        location
        if location is not None and location != ""
        else f"SNOWPARK_CONNECT_DEFAULT_LOCATION/{snowpark_table_name}"
    )
    base_location = f"BASE_LOCATION = '{location}'"

    config_external_volume = sessions_config.get(get_session_id(), {}).get(
        "snowpark.connect.iceberg.external_volume", None
    )
    external_volume = (
        ""
        if config_external_volume is None or config_external_volume == ""
        else f"EXTERNAL_VOLUME = '{config_external_volume}'"
    )

    sql = f"""
        CREATE ICEBERG TABLE {snowpark_table_name} ({",".join(table_schema)})
        CATALOG = 'SNOWFLAKE'
        {external_volume}
        {base_location};
        """
    snowpark_session.sql(sql).collect()


def rewrite_df(input_df: snowpark.DataFrame, source: str) -> snowpark.DataFrame:
    """
    Rewrite dataframe if needed.
        json: construct the dataframe to 1 column in json format
            1. Append columns which represents the column name
            2. Use object_construct to aggregate the dataframe into 1 column

    """
    if source != "json":
        return input_df
    rand_salt = random_string(10, "_")
    rewritten_df = input_df.with_columns(
        [co + rand_salt for co in input_df.columns],
        [lit(unquote_if_quoted(co)) for co in input_df.columns],
    )
    construct_key_values = []
    for co in input_df.columns:
        construct_key_values.append(col(co + rand_salt))
        construct_key_values.append(col(co))
    return rewritten_df.select(object_construct(*construct_key_values))


def handle_column_names(df: snowpark.DataFrame, source: str) -> snowpark.DataFrame:
    """
    Handle column names.

    Quote column name in these scenarios:
        0. Not write to table
        1. Customer enabled case sensitivity in config
    """
    if not hasattr(df, "_column_map") or source == "jdbc":
        # don't change column names for jdbc sources as we directly use spark column names for writing to the destination tables.
        return df
    column_map = df._column_map
    case_sensitive = global_config.spark_sql_caseSensitive
    for column in df.columns:
        spark_column_name = unquote_if_quoted(
            column_map.get_spark_column_name_from_snowpark_column_name(column)
        )
        if source in ("csv", "parquet", "json") or case_sensitive:
            spark_column_name = f'"{spark_column_name}"'
        df = df.withColumnRenamed(column, spark_column_name)
    return df


def store_files_locally(
    stage_path: str, target_path: str, overwrite: bool, session: snowpark.Session
) -> None:
    target_path = convert_file_prefix_path(target_path)
    real_path = (
        Path(target_path).expanduser()
        if target_path.startswith("~/")
        else Path(target_path)
    )
    if overwrite and os.path.isdir(target_path):
        _truncate_directory(real_path)
    snowpark.file_operation.FileOperation(session).get(stage_path, str(real_path))


def _truncate_directory(directory_path: Path) -> None:
    if not directory_path.exists():
        raise FileNotFoundError(
            f"The specified directory {directory_path} does not exist."
        )
    # Iterate over all the files and directories in the specified directory
    for file in directory_path.iterdir():
        # Check if it is a file or directory and remove it
        if file.is_file() or file.is_symlink():
            file.unlink()
        elif file.is_dir():
            shutil.rmtree(file)


def check_snowflake_table_existance(
    snowpark_table_name: str,
    snowpark_session: snowpark.Session,
):
    try:
        snowpark_session.sql(f"SELECT 1 FROM {snowpark_table_name} LIMIT 1").collect()
        return True
    except Exception:
        return False
