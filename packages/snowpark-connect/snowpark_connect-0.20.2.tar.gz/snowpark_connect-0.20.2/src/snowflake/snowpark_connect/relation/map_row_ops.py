#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import pyspark.sql.connect.proto.expressions_pb2 as expressions_proto
import pyspark.sql.connect.proto.relations_pb2 as relation_proto
from pyspark.errors.exceptions.base import AnalysisException, IllegalArgumentException

import snowflake.snowpark_connect.relation.utils as utils
from snowflake import snowpark
from snowflake.snowpark.functions import col, expr as snowpark_expr
from snowflake.snowpark.types import (
    BooleanType,
    ByteType,
    DecimalType,
    DoubleType,
    FloatType,
    IntegerType,
    LongType,
    NullType,
    ShortType,
)
from snowflake.snowpark_connect.column_name_handler import (
    schema_getter,
    set_schema_getter,
    with_column_map,
)
from snowflake.snowpark_connect.config import global_config
from snowflake.snowpark_connect.expression.literal import get_literal_field_and_name
from snowflake.snowpark_connect.expression.map_expression import (
    map_single_column_expression,
)
from snowflake.snowpark_connect.expression.typer import ExpressionTyper
from snowflake.snowpark_connect.relation.map_relation import map_relation
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)


def map_deduplicate(
    rel: relation_proto.Relation,
) -> snowpark.DataFrame:
    """
    Deduplicate a DataFrame based on a Relation's deduplicate.

    The deduplicate is a list of columns that is applied to the DataFrame.
    """
    input_df: snowpark.DataFrame = map_relation(rel.deduplicate.input)

    if (
        rel.deduplicate.HasField("within_watermark")
        and rel.deduplicate.within_watermark
    ):
        raise AnalysisException(
            "dropDuplicatesWithinWatermark is not supported with batch DataFrames/DataSets"
        )

    if (
        rel.deduplicate.HasField("all_columns_as_keys")
        and rel.deduplicate.all_columns_as_keys
    ):
        result: snowpark.DataFrame = input_df.drop_duplicates()
    else:
        result: snowpark.DataFrame = input_df.drop_duplicates(
            *input_df._column_map.get_snowpark_column_names_from_spark_column_names(
                list(rel.deduplicate.column_names)
            )
        )
    result._column_map = input_df._column_map
    result._table_name = input_df._table_name
    set_schema_getter(result, lambda: input_df.schema)
    return result


def map_dropna(rel: relation_proto.Relation) -> snowpark.DataFrame:
    """
    Drop NA values from the input DataFrame.


    """
    input_df: snowpark.DataFrame = map_relation(rel.drop_na.input)
    if rel.drop_na.HasField("min_non_nulls"):
        thresh = rel.drop_na.min_non_nulls
        how = "all"
    else:
        thresh = None
        how = "any"
    if len(rel.drop_na.cols) > 0:
        columns: list[str] = [
            # Use the mapping to get the Snowpark internal column name
            # TODO: Verify the behavior of duplicate column names with dropna
            input_df._column_map.get_snowpark_column_name_from_spark_column_name(c)
            for c in rel.drop_na.cols
        ]
        result: snowpark.DataFrame = input_df.dropna(
            how=how, subset=columns, thresh=thresh
        )
    else:
        result: snowpark.DataFrame = input_df.dropna(how=how, thresh=thresh)
    result._column_map = input_df._column_map
    result._table_name = input_df._table_name
    set_schema_getter(result, lambda: input_df.schema)
    return result


def map_fillna(rel: relation_proto.Relation) -> snowpark.DataFrame:
    """
    Fill NA values in the DataFrame.

    The `fill_value` is a scalar value that will be used to replace NaN values.
    """
    input_df: snowpark.DataFrame = map_relation(rel.fill_na.input)
    if len(rel.fill_na.cols) > 0:
        columns: list[str] = [
            input_df._column_map.get_snowpark_column_name_from_spark_column_name(c)
            for c in rel.fill_na.cols
        ]
        values = [get_literal_field_and_name(v)[0] for v in rel.fill_na.values]
        if len(values) == 1:
            # This happens when the client uses the `subset` parameter.
            values = values * len(columns)
        assert len(columns) == len(
            values
        ), "FILLNA: number of columns and values must match"
        result = input_df.fillna(dict(zip(columns, values)), include_decimal=True)
    else:
        assert len(rel.fill_na.values) == 1
        proto_value: expressions_proto.Expression.Literal = rel.fill_na.values[0]
        fill_value = get_literal_field_and_name(proto_value)[0]
        # Spark will cast floats to integers if the column is an integer type.
        # Snowpark doesn't, so we have to help it.
        if isinstance(fill_value, float):
            fill_value: dict[str, float | int] = {
                field.name: (
                    fill_value
                    if not isinstance(
                        field.datatype,
                        (snowpark.types.IntegerType, snowpark.types.LongType),
                    )
                    else int(fill_value)
                )
                for field in input_df.schema.fields
            }
        result = input_df.fillna(fill_value, include_decimal=True)
    result._column_map = input_df._column_map
    result._table_name = input_df._table_name
    set_schema_getter(result, lambda: input_df.schema)
    return result


def map_union(rel: relation_proto.Relation) -> snowpark.DataFrame:
    """
    Union two DataFrames together.

    The two DataFrames must have the same schema.
    """
    left_df: snowpark.DataFrame = map_relation(rel.set_op.left_input)
    right_df: snowpark.DataFrame = map_relation(rel.set_op.right_input)

    # workaround for unstructured type vs structured type
    left_dtypes = [field.datatype for field in left_df.schema.fields]
    right_dtypes = [field.datatype for field in right_df.schema.fields]

    allow_missing_columns = bool(rel.set_op.allow_missing_columns)

    spark_sql_ansi_enabled = global_config.spark_sql_ansi_enabled
    if left_dtypes != right_dtypes and not rel.set_op.by_name:
        if len(left_dtypes) != len(right_dtypes):
            raise AnalysisException("UNION: the number of columns must match")
        target_left_dtypes, target_right_dtypes = [], []
        for left_type, right_type in zip(left_dtypes, right_dtypes):
            match (left_type, right_type):
                case (snowpark.types.ArrayType(), snowpark.types.ArrayType()):
                    # Up casting unstructured array to structured array
                    common_type = snowpark.types.ArrayType(
                        left_type.element_type or right_type.element_type
                    )
                    target_left_dtypes.append(common_type)
                    target_right_dtypes.append(common_type)
                case (snowpark.types.ArrayType(), snowpark.types.StringType()) | (
                    snowpark.types.StringType(),
                    snowpark.types.ArrayType(),
                ):
                    # workaround for Null array. The NULL in SQL has StringType as the default type.
                    # TODO: seems like for Map, we can't cast the StringType to MapType using snowpark_fn.cast
                    common_type = (
                        right_type
                        if isinstance(left_type, snowpark.types.StringType)
                        else left_type
                    )
                    target_left_dtypes.append(common_type)
                    target_right_dtypes.append(common_type)
                case (other_t, NullType()) | (NullType(), other_t):
                    # Union of any type with null type is of the other type
                    target_left_dtypes.append(other_t)
                    target_right_dtypes.append(other_t)
                case (snowpark.types.BooleanType(), _) | (
                    _,
                    snowpark.types.BooleanType(),
                ):
                    if left_type != right_type and (
                        not spark_sql_ansi_enabled
                        or snowpark.types.StringType() not in [left_type, right_type]
                    ):  # In ansi mode , string type union boolean type is acceptable
                        raise AnalysisException(
                            f"""[INCOMPATIBLE_COLUMN_TYPE] UNION can only be performed on tables with compatible column types. "{str(left_type)}" type which is not compatible with "{str(right_type)}". """
                        )
                    target_left_dtypes.append(left_type)
                    target_right_dtypes.append(right_type)
                case _:
                    target_left_dtypes.append(left_type)
                    target_right_dtypes.append(right_type)

        def cast_columns(
            df: snowpark.DataFrame,
            df_dtypes: list[snowpark.types.DataType],
            target_dtypes: list[snowpark.types.DataType],
        ):
            if df_dtypes == target_dtypes:
                return df
            df_schema = df.schema  # Get current schema
            new_columns = []

            for i, field in enumerate(df_schema.fields):
                col_name = field.name
                current_type = field.datatype
                target_type = target_dtypes[i]

                if current_type != target_type:
                    new_columns.append(df[col_name].cast(target_type).alias(col_name))
                else:
                    new_columns.append(df[col_name])

            new_df = df.select(new_columns)
            return with_column_map(
                new_df,
                df._column_map.get_spark_columns(),
                df._column_map.get_snowpark_columns(),
                target_dtypes,
                df._column_map.column_metadata,
                parent_column_name_map=df._column_map,
            )

        left_df = cast_columns(left_df, left_dtypes, target_left_dtypes)
        right_df = cast_columns(right_df, right_dtypes, target_right_dtypes)

    # Save the column names so that we can restore them after the union.
    left_df_columns = left_df.columns

    result: snowpark.DataFrame = None

    if rel.set_op.by_name:
        # To use unionByName, we need to have the same column names.
        # We rename the columns back to their originals using the map
        left_column_map = left_df._column_map
        left_table_name = left_df._table_name
        left_schema_getter = schema_getter(left_df)
        right_column_map = right_df._column_map

        columns_to_restore: dict[str, tuple[str, str]] = {}

        for column in right_df.columns:
            spark_name = (
                right_column_map.get_spark_column_name_from_snowpark_column_name(column)
            )

            right_df = right_df.withColumnRenamed(column, spark_name)
            columns_to_restore[spark_name.upper()] = (spark_name, column)

        for column in left_df.columns:
            spark_name = (
                left_column_map.get_spark_column_name_from_snowpark_column_name(column)
            )

            left_df = left_df.withColumnRenamed(column, spark_name)
            columns_to_restore[spark_name.upper()] = (spark_name, column)

        result = left_df.union_all_by_name(
            right_df, allow_missing_columns=allow_missing_columns
        )

        if allow_missing_columns:
            spark_columns = []
            snowpark_columns = []

            for col_ in result.columns:
                spark_col_to_restore, snowpark_col_to_restore = columns_to_restore[
                    col_.upper()
                ]
                result = result.withColumnRenamed(col_, snowpark_col_to_restore)

                spark_columns.append(spark_col_to_restore)
                snowpark_columns.append(snowpark_col_to_restore)

            left_df_col_metadata = left_column_map.column_metadata or {}
            right_df_col_metadata = right_column_map.column_metadata or {}
            merged_column_metadata = left_df_col_metadata | right_df_col_metadata

            return with_column_map(
                result,
                spark_columns,
                snowpark_columns,
                column_metadata=merged_column_metadata,
            )

        for i in range(len(left_df_columns)):
            result = result.withColumnRenamed(result.columns[i], left_df_columns[i])

        result._column_map = left_column_map
        result._table_name = left_table_name
        set_schema_getter(result, left_schema_getter)
    elif rel.set_op.is_all:
        result = left_df.unionAll(right_df)
        result._column_map = left_df._column_map
        result._table_name = left_df._table_name
        set_schema_getter(result, lambda: left_df.schema)
    else:
        result = left_df.union(right_df)
        result._column_map = left_df._column_map
        result._table_name = left_df._table_name
        set_schema_getter(result, lambda: left_df.schema)

    # union operation does not preserve column qualifiers
    return with_column_map(
        result,
        result._column_map.get_spark_columns(),
        result._column_map.get_snowpark_columns(),
        column_metadata=result._column_map.column_metadata,
        parent_column_name_map=result._column_map,
    )


def map_intersect(rel: relation_proto.Relation) -> snowpark.DataFrame:
    """
    Return a new DataFrame containing rows in both DataFrames:

    1. If set_op.is_all is True, this method is implementing ```intersectAll```
        while preserving duplicates.

    2. If set_op.is_all is False, this method is implementing ```intersect```
        while removing duplicates.

    Examples
    --------
    >>> df1 = spark.createDataFrame([("a", 1), ("a", 1), ("a", 1), ("a", 2), ("b",  3), ("c", 4)], ["C1", "C2"]))
    >>> df2 = spark.createDataFrame([("a", 1), ("a", 1), ("b", 3)], ["C1", "C2"])
    >>> df1.intersect(df2).show()

    +---+---+
    | C1| C2|
    +---+---+
    |  a|  1|
    |  b|  3|
    +---+---+

    >>> df1.intersectAll(df2).show()

    +---+---+
    | C1| C2|
    +---+---+
    |  a|  1|
    |  a|  1|
    |  b|  3|
    +---+---+
    """
    left_df: snowpark.DataFrame = map_relation(rel.set_op.left_input)
    right_df: snowpark.DataFrame = map_relation(rel.set_op.right_input)

    if rel.set_op.is_all:
        left_df_with_row_number = utils.get_df_with_partition_row_number(
            left_df, rel.set_op.left_input.common.plan_id, "left_row_number"
        )
        right_df_with_row_number = utils.get_df_with_partition_row_number(
            right_df, rel.set_op.right_input.common.plan_id, "right_row_number"
        )

        result: snowpark.DataFrame = left_df_with_row_number.intersect(
            right_df_with_row_number
        ).select(*left_df._column_map.get_snowpark_columns())
    else:
        result: snowpark.DataFrame = left_df.intersect(right_df)

    # the result df keeps the column map of the original left_df
    result = with_column_map(
        result,
        left_df._column_map.get_spark_columns(),
        left_df._column_map.get_snowpark_columns(),
        column_metadata=left_df._column_map.column_metadata,
    )
    result._table_name = left_df._table_name
    set_schema_getter(result, lambda: left_df.schema)
    return result


def map_except(rel: relation_proto.Relation) -> snowpark.DataFrame:
    """
    Return a new DataFrame containing rows in the left DataFrame but not in the right DataFrame.

    1. If set_op.is_all is True, this method is implementing ```exceptAll```
        while preserving duplicates.

    2. If set_op.is_all is False, this method is implementing ```subtract```
        while removing duplicates.

    Examples
    --------
    >>> df1 = spark.createDataFrame([("a", 1), ("a", 1), ("a", 1), ("a", 2), ("b",  3), ("c", 4)], ["C1", "C2"]))
    >>> df2 = spark.createDataFrame([("a", 1), ("a", 1), ("b", 3)], ["C1", "C2"])
    >>> df1.subtract(df2).show()

    +---+---+
    | C1| C2|
    +---+---+
    |  a|  2|
    |  c|  4|
    +---+---+

    >>> df1.exceptAll(df2).show()

    +---+---+
    | C1| C2|
    +---+---+
    |  a|  1|
    |  a|  1|
    |  a|  2|
    |  c|  4|
    +---+---+
    """
    left_df: snowpark.DataFrame = map_relation(rel.set_op.left_input)
    right_df: snowpark.DataFrame = map_relation(rel.set_op.right_input)

    if rel.set_op.is_all:
        # Snowflake except removes all duplicated rows. In order to handle the case,
        # we add a partition row number column to the df to make duplicated rows unique to
        # avoid the duplicated rows to be removed.
        # For example, with the following left_df and right_df
        # +---+---+                               +---+---+
        # | C1| C2|                               | C1| C2|
        # +---+---+                               +---+---+
        # |  a|  1|                               |  a|  1|
        # |  a|  1|                               |  a|  2|
        # |  a|  2|                               +---+---+
        # |  c|  4|
        # +---+---+
        # we will do
        # +---+---+------------+                    +---+---+------------+
        # | C1| C2| ROW_NUMBER |     EXCEPT         | C1| C2| ROW_NUMBER |
        # +---+---+------------+                    +---+---+------------+
        # |  a|  1|         0  |                    |  a|  1|         0  |
        # |  a|  1|         1  |                    |  a|  2|         0  |
        # |  a|  2|         0  |                    +---+---+------------+
        # |  c|  4|         0  |
        # +---+---+------------+
        # at the end we will do a select to exclude the row number column
        left_df_with_row_number = utils.get_df_with_partition_row_number(
            left_df, rel.set_op.left_input.common.plan_id, "left_row_number"
        )
        right_df_with_row_number = utils.get_df_with_partition_row_number(
            right_df, rel.set_op.right_input.common.plan_id, "right_row_number"
        )

        # Perform except use left_df_with_row_number and right_df_with_row_number,
        # and drop the row number column after except.
        result_df = left_df_with_row_number.except_(right_df_with_row_number).select(
            *left_df._column_map.get_snowpark_columns()
        )
    else:
        result_df = left_df.except_(right_df)

    # the result df keeps the column map of the original left_df
    # union operation does not preserve column qualifiers
    result_df = with_column_map(
        result_df,
        left_df._column_map.get_spark_columns(),
        left_df._column_map.get_snowpark_columns(),
        column_metadata=left_df._column_map.column_metadata,
    )
    result_df._table_name = left_df._table_name
    set_schema_getter(result_df, lambda: left_df.schema)
    return result_df


def map_filter(
    rel: relation_proto.Relation,
) -> snowpark.DataFrame:
    """
    Filter a DataFrame based on a Relation's filter.

    The filter is a SQL expression that is applied to the DataFrame.
    """
    input_df = map_relation(rel.filter.input)
    typer = ExpressionTyper(input_df)
    _, condition = map_single_column_expression(
        rel.filter.condition, input_df._column_map, typer
    )
    result = input_df.filter(condition.col)
    result._column_map = input_df._column_map
    result._alias = input_df._alias
    result._table_name = input_df._table_name
    set_schema_getter(result, lambda: input_df.schema)
    return result


def map_limit(
    rel: relation_proto.Relation,
) -> snowpark.DataFrame:
    """
    Limit a DataFrame based on a Relation's limit.

    The limit is an integer that is applied to the DataFrame.
    """
    input_df: snowpark.DataFrame = map_relation(rel.limit.input)
    result: snowpark.DataFrame = input_df.limit(rel.limit.limit)
    result._column_map = input_df._column_map
    result._table_name = input_df._table_name
    set_schema_getter(result, lambda: input_df.schema)
    return result


def map_offset(
    rel: relation_proto.Relation,
) -> snowpark.DataFrame:
    """
    Offset a DataFrame based on a Relation's offset.

    The offset is an integer that is applied to the DataFrame.
    """
    input_df: snowpark.DataFrame = map_relation(rel.offset.input)
    # TODO: This is a terrible way to have to do this, but Snowpark does not
    # support offset without limit.
    result: snowpark.DataFrame = input_df.limit(
        input_df.count(), offset=rel.offset.offset
    )
    result._column_map = input_df._column_map
    result._table_name = input_df._table_name
    set_schema_getter(result, lambda: input_df.schema)
    return result


def map_replace(rel: relation_proto.Relation) -> snowpark.DataFrame:
    """
    Replace values in the DataFrame.

    The `replace_map` is a dictionary of column names to a dictionary of
    values to replace. The values in the dictionary are the values to replace
    and the keys are the values to replace them with.
    """
    input_df: snowpark.DataFrame = map_relation(rel.replace.input)
    ordered_columns = input_df.columns
    column_map = input_df._column_map
    table_name = input_df._table_name
    # note that seems like spark connect always send number values as double in rel.replace.replacements.
    to_replace = [
        get_literal_field_and_name(i.old_value)[0] for i in rel.replace.replacements
    ]
    values = [
        get_literal_field_and_name(i.new_value)[0] for i in rel.replace.replacements
    ]

    # Snowpark doesn't support replacing floats with integers. We used column expressions instead of Snowpark function to achieve spark's compatibility.
    def replace_case_expr(col_name: str, old_vals: list, new_vals: list):
        """
        Generate a SQL CASE expression to replace values in a DataFrame column,
        matching PySpark's DataFrame.replace() behavior exactly.

        - Numeric columns:
            - Non-numeric replacement values are skipped.
            - Integer columns (IntegerType, LongType, ShortType, ByteType):
                - Replacement values are truncated to integers (e.g., 82.9 → 82).
            - Float/Double/Decimal columns:
                - Replacement values retain their original numeric precision.
            - Numeric comparisons are done using TO_DOUBLE() to allow matching
              integer and float equivalents (e.g., 80 matches 80.0).
        - Boolean columns:
            - Only boolean replacements are allowed; non-boolean replacements are skipped.
            - Boolean values are represented as TRUE/FALSE in SQL.
        - String columns:
            - Replacement values are enclosed in single quotes.
            - NULL values are represented as SQL NULL.
        - NULL values:
            - Represented explicitly as SQL NULL without quotes.
        """
        col_datatype = next(
            field.datatype for field in input_df.schema.fields if field.name == col_name
        )
        numeric_flag = isinstance(
            col_datatype,
            (
                IntegerType,
                LongType,
                FloatType,
                DoubleType,
                DecimalType,
                ShortType,
                ByteType,
            ),
        )
        bool_flag = isinstance(col_datatype, BooleanType)

        case_expr = "CASE"
        for ov, nv in zip(old_vals, new_vals):
            if numeric_flag:
                if isinstance(ov, bool) or isinstance(ov, str):
                    # skip boolean/string replacements on numeric columns
                    continue

                if isinstance(
                    col_datatype, (IntegerType, LongType, ShortType, ByteType)
                ):
                    # Integer column: truncate replacement value to integer
                    if nv is None:
                        nv_expr = "NULL"
                    else:
                        try:
                            nv_numeric = int(float(nv))
                            nv_expr = str(nv_numeric)
                        except Exception:
                            # Skip invalid numeric replacements
                            continue
                else:
                    if nv is None:
                        nv_expr = "NULL"
                    else:
                        nv_expr = f"'{nv}'"

                case_expr += f" WHEN TO_DOUBLE({col_name}) = {float(ov)} THEN {nv_expr}"

            elif bool_flag:
                if not isinstance(ov, bool):
                    continue
                case_expr += f" WHEN {col_name} IS NOT NULL AND {col_name} = {str(ov).upper()} THEN {str(nv).upper()}"

            else:
                # If the column is a string type but either ov or nv is numeric, skip replacement.
                if isinstance(ov, (int, float, complex)) or isinstance(
                    nv, (int, float, complex)
                ):
                    continue
                ov_expr = f"'{ov}'" if ov is not None else "NULL"
                nv_expr = f"'{nv}'" if nv is not None else "NULL"
                case_expr += f" WHEN {col_name} = {ov_expr} THEN {nv_expr}"
        if case_expr == "CASE":
            return col(col_name)
        else:
            case_expr += f" ELSE {col_name} END"
            return snowpark_expr(case_expr)

    if len(rel.replace.cols) > 0:
        columns: list[str] = [
            input_df._column_map.get_snowpark_column_name_from_spark_column_name(c)
            for c in rel.replace.cols
        ]
        for c in columns:
            input_df = input_df.with_column(c, replace_case_expr(c, to_replace, values))
    else:
        for c in input_df.columns:
            input_df = input_df.with_column(c, replace_case_expr(c, to_replace, values))

    result = input_df.select(*[col(c) for c in ordered_columns])
    result._column_map = column_map
    result._table_name = table_name
    return result


def map_sample(
    rel: relation_proto.Relation,
) -> snowpark.DataFrame:
    """
    Sample a DataFrame based on a Relation's sample.
    """
    input_df: snowpark.DataFrame = map_relation(rel.sample.input)
    frac = rel.sample.upper_bound - rel.sample.lower_bound
    if frac < 0 or frac > 1:
        raise IllegalArgumentException("Sample fraction must be between 0 and 1")
    # The seed argument is not supported here. There are a number of reasons that implementing
    # this will be complicated in Snowflake. Here is a list of complications:
    #
    # 1. Spark Connect always provides a seed, even if the user has not provided one. This seed
    #    is a randomly generated number, so we cannot detect if the user has provided a seed or not.
    # 2. Snowflake only supports seed on tables, not on views.
    # 3. Snowpark almost always creates a new view in the form of nested queries for every query.
    #
    # Given these three issues, users would be required to write their own temporary tables prior
    # to sampling, which is not a good user experience and has significant performance implications.
    # For these reasons, we choose to ignore the seed argument until we have a plan for how to solve
    # these issues.
    if rel.sample.with_replacement:
        # TODO: Use a random number generator with ROW_NUMBER and SELECT.
        raise SnowparkConnectNotImplementedError(
            "Sample with replacement is not supported"
        )
    else:
        result: snowpark.DataFrame = input_df.sample(frac=frac)
        result._column_map = input_df._column_map
        result._table_name = input_df._table_name
        set_schema_getter(result, lambda: input_df.schema)
        return result


def map_tail(
    rel: relation_proto.Relation,
) -> snowpark.DataFrame:
    """
    Tail a DataFrame based on a Relation's tail.

    The tail is an integer that is applied to the DataFrame.
    """
    input_df: snowpark.DataFrame = map_relation(rel.tail.input)
    num_rows = input_df.count()
    result: snowpark.DataFrame = input_df.limit(
        num_rows, offset=max(0, num_rows - rel.tail.limit)
    )
    result._column_map = input_df._column_map
    result._table_name = input_df._table_name
    set_schema_getter(result, lambda: input_df.schema)
    return result
