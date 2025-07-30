#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import pyspark.sql.connect.proto.relations_pb2 as relation_proto

from snowflake import snowpark
from snowflake.snowpark_connect.column_name_handler import with_column_map
from snowflake.snowpark_connect.relation.map_relation import map_relation


def map_alias(rel: relation_proto.Relation) -> snowpark.DataFrame:
    """
    Returns an aliased dataframe in which the columns can now be referenced to using col(<df alias>, <column name>).
    """
    alias: str = rel.subquery_alias.alias
    # we set reuse_parsed_plan=False because we need new expr_id for the attributes (output columns) in aliased snowpark dataframe
    # reuse_parsed_plan will lead to ambiguous column name for operations like joining two dataframes that are aliased from the same dataframe
    input_df: snowpark.DataFrame = map_relation(
        rel.subquery_alias.input, reuse_parsed_plan=False
    )
    input_df._alias = alias
    qualifiers = [[alias]] * len(input_df._column_map.columns)

    return with_column_map(
        input_df,
        input_df._column_map.get_spark_columns(),
        input_df._column_map.get_snowpark_columns(),
        column_metadata=input_df._column_map.column_metadata,
        column_qualifiers=qualifiers,
        parent_column_name_map=input_df._column_map.get_parent_column_name_map(),
    )
