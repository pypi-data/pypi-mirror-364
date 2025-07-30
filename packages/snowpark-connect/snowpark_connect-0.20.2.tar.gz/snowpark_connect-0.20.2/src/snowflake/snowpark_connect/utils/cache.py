#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import threading
from collections.abc import Callable
from typing import Dict, Tuple

import pandas

from snowflake import snowpark
from snowflake.snowpark_connect.column_name_handler import set_schema_getter
from snowflake.snowpark_connect.utils.snowpark_connect_logging import logger

# global cache mapping  (sessionID, planID) -> cached snowpark df .
df_cache_map: Dict[Tuple[str, any], snowpark.DataFrame] = {}

# reentrant lock for thread safety
_cache_map_lock = threading.RLock()


def df_cache_map_get(key: Tuple[str, any]) -> snowpark.DataFrame | None:
    with _cache_map_lock:
        return df_cache_map.get(key)


def df_cache_map_put_if_absent(
    key: Tuple[str, any],
    compute_fn: Callable[[], snowpark.DataFrame | pandas.DataFrame],
    materialize: bool,
) -> snowpark.DataFrame | pandas.DataFrame:
    """
    Put a DataFrame into the cache map if the key is absent. Optionally, as side effect, materialize
    the DataFrame content in a temporary table.

    Args:
        key (Tuple[str, int]): The key to insert into the cache map (session_id, plan_id).
        compute_fn (Callable[[], DataFrame]): A function to compute the DataFrame if the key is absent.
        materialize (bool): Whether to materialize the DataFrame.

    Returns:
        snowpark.DataFrame | pandas.DataFrame: The cached or newly computed DataFrame.
    """

    def _object_to_cache(df: snowpark.DataFrame) -> snowpark.DataFrame:
        if materialize:
            cached_result = df.cache_result()
            # caching does not change the column name map
            cached_result._column_map = df._column_map
            cached_result._table_name = df._table_name
            set_schema_getter(cached_result, lambda: df.schema)
            return cached_result
        return df

    with _cache_map_lock:
        if key not in df_cache_map:
            df = compute_fn()

            # check cache again, since recursive call in compute_fn could've already cached the result.
            # we want return it, instead of saving it again. This is important if materialize = True
            # because materialization is expensive operation that we don't want to do twice.
            if key in df_cache_map:
                return df_cache_map[key]

            # only cache snowpark Dataframe, but not pandas result.
            # Pandas result is only returned when df.show() is called, where we convert
            # a dataframe to a string representation.
            # We don't expect map_relation would return pandas df here because that would
            # be equivalent to calling df.show().cache(), which is not allowed.
            if isinstance(df, snowpark.DataFrame):
                df_cache_map[key] = _object_to_cache(df)
            else:
                # This is not expected, but we will just log a warning
                logger.warning(
                    "Unexpected pandas dataframe returned for caching. Ignoring the cache call."
                )
                return df

        return df_cache_map[key]


def df_cache_map_pop(key: Tuple[str, any]) -> None:
    with _cache_map_lock:
        df_cache_map.pop(key, None)
