#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import pyspark.sql.connect.proto.expressions_pb2 as expressions_proto
import pyspark.sql.connect.proto.relations_pb2 as relation_proto

from snowflake import snowpark
from snowflake.snowpark_connect.column_name_handler import set_schema_getter
from snowflake.snowpark_connect.expression.literal import get_literal_field_and_name
from snowflake.snowpark_connect.expression.map_expression import (
    map_single_column_expression,
)
from snowflake.snowpark_connect.expression.typer import ExpressionTyper
from snowflake.snowpark_connect.relation.map_relation import map_relation


def map_sample_by(rel: relation_proto.Relation) -> snowpark.DataFrame:
    """
    Sample by an expression on the input DataFrame.
    """
    input_df: snowpark.DataFrame = map_relation(rel.sample_by.input)
    exp: expressions_proto.Expression = rel.sample_by.col
    _, col_expr = map_single_column_expression(
        exp, input_df._column_map, ExpressionTyper(input_df)
    )
    fractions = {
        get_literal_field_and_name(frac.stratum)[0]: frac.fraction
        for frac in rel.sample_by.fractions
    }
    result: snowpark.DataFrame = input_df.sampleBy(col_expr.col, fractions)
    result._column_map = input_df._column_map
    result._table_name = input_df._table_name
    set_schema_getter(result, lambda: input_df.schema)
    return result
