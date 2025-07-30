#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#

import socket

import pandas
import pyspark.sql.connect.proto.relations_pb2 as relation_proto

from snowflake import snowpark
from snowflake.snowpark_connect.column_name_handler import with_column_map
from snowflake.snowpark_connect.utils.telemetry import (
    SnowparkConnectNotImplementedError,
)

# Full data is used at the moment to store all the data that has been read
# from the socket. This is a temporary solution for demonstration purposes
# and not scalable.
# TODO: Use a stage in Snowflake to store the data.
full_data = b""


def map_read_socket(
    rel: relation_proto.Relation,
    session: snowpark.Session,
    options: dict[str, str],
) -> snowpark.DataFrame:
    if rel.read.is_streaming is True:
        global full_data
        host = options.get("host", None)
        port = options.get("port", None)
        if not host or not port:
            raise ValueError("Host and port must be provided in options.")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((host, int(port)))
                data = s.recv(1024)
                full_data += data
                while data:
                    s.settimeout(1.25)
                    try:
                        data = s.recv(1024)
                        full_data += data
                    except socket.timeout:
                        break
                s.settimeout(None)
                dataframe_data = full_data.decode("utf-8")
                snowpark_cname = "VALUE"
                df = session.create_dataframe(
                    pandas.DataFrame({snowpark_cname: dataframe_data.split("\n")})
                )
                spark_cname = "value"
                return with_column_map(df, [spark_cname], [snowpark_cname])
            except OSError as e:
                raise Exception(f"Error connecting to {host}:{port} - {e}")
    else:
        raise SnowparkConnectNotImplementedError(
            "Socket reads are only supported in streaming mode."
        )
