#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import pandas
import pyspark.sql.connect.proto.relations_pb2 as relation_proto

from snowflake import snowpark
from snowflake.snowpark._internal.analyzer import analyzer_utils
from snowflake.snowpark_connect.relation.map_relation import map_relation


def map_show_string(rel: relation_proto.Relation) -> pandas.DataFrame:
    """
    Generate the string representation of the input dataframe.

    We return a pandas DataFrame object here because the `show_string` relation
    message creates a string. The client expects this string to be packed into an Arrow
    Buffer object as a single cell.
    """
    input_df: snowpark.DataFrame = map_relation(rel.show_string.input)
    show_string = input_df._show_string_spark(
        num_rows=rel.show_string.num_rows,
        truncate=rel.show_string.truncate,
        vertical=rel.show_string.vertical,
        _spark_column_names=input_df._column_map.get_spark_columns(),
    )
    return pandas.DataFrame({"show_string": [show_string]})


def map_repr_html(rel: relation_proto.Relation) -> pandas.DataFrame:
    """
    Generate the html string representation of the input dataframe.
    """
    input_df: snowpark.DataFrame = map_relation(rel.html_string.input)
    input_panda = input_df.toPandas()
    input_panda.rename(
        columns={
            analyzer_utils.unquote_if_quoted(
                input_df._column_map.get_snowpark_columns()[i]
            ): input_df._column_map.get_spark_columns()[i]
            for i in range(len(input_panda.columns))
        },
        inplace=True,
    )
    html_string = input_panda.to_html(
        index=False,
        max_rows=rel.html_string.num_rows,
    )
    return pandas.DataFrame({"html_string": [html_string]})
