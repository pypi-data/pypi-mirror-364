from pyspark.sql.connect.proto import expressions_pb2 as _expressions_pb2
from pyspark.sql.connect.proto import relations_pb2 as _relations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExpExtension(_message.Message):
    __slots__ = ["named_argument", "subquery_expression"]
    NAMED_ARGUMENT_FIELD_NUMBER: _ClassVar[int]
    SUBQUERY_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    named_argument: NamedArgumentExpression
    subquery_expression: SubqueryExpression
    def __init__(self, named_argument: _Optional[_Union[NamedArgumentExpression, _Mapping]] = ..., subquery_expression: _Optional[_Union[SubqueryExpression, _Mapping]] = ...) -> None: ...

class NamedArgumentExpression(_message.Message):
    __slots__ = ["key", "value"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: _expressions_pb2.Expression
    def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_expressions_pb2.Expression, _Mapping]] = ...) -> None: ...

class SubqueryExpression(_message.Message):
    __slots__ = ["in_subquery_values", "input", "subquery_type", "table_arg_options"]
    class SubqueryType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class TableArgOptions(_message.Message):
        __slots__ = ["order_spec", "partition_spec", "with_single_partition"]
        ORDER_SPEC_FIELD_NUMBER: _ClassVar[int]
        PARTITION_SPEC_FIELD_NUMBER: _ClassVar[int]
        WITH_SINGLE_PARTITION_FIELD_NUMBER: _ClassVar[int]
        order_spec: _containers.RepeatedCompositeFieldContainer[_expressions_pb2.Expression.SortOrder]
        partition_spec: _containers.RepeatedCompositeFieldContainer[_expressions_pb2.Expression]
        with_single_partition: bool
        def __init__(self, partition_spec: _Optional[_Iterable[_Union[_expressions_pb2.Expression, _Mapping]]] = ..., order_spec: _Optional[_Iterable[_Union[_expressions_pb2.Expression.SortOrder, _Mapping]]] = ..., with_single_partition: bool = ...) -> None: ...
    INPUT_FIELD_NUMBER: _ClassVar[int]
    IN_SUBQUERY_VALUES_FIELD_NUMBER: _ClassVar[int]
    SUBQUERY_TYPE_EXISTS: SubqueryExpression.SubqueryType
    SUBQUERY_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBQUERY_TYPE_IN: SubqueryExpression.SubqueryType
    SUBQUERY_TYPE_SCALAR: SubqueryExpression.SubqueryType
    SUBQUERY_TYPE_TABLE_ARG: SubqueryExpression.SubqueryType
    SUBQUERY_TYPE_UNKNOWN: SubqueryExpression.SubqueryType
    TABLE_ARG_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    in_subquery_values: _containers.RepeatedCompositeFieldContainer[_expressions_pb2.Expression]
    input: _relations_pb2.Relation
    subquery_type: SubqueryExpression.SubqueryType
    table_arg_options: SubqueryExpression.TableArgOptions
    def __init__(self, input: _Optional[_Union[_relations_pb2.Relation, _Mapping]] = ..., subquery_type: _Optional[_Union[SubqueryExpression.SubqueryType, str]] = ..., table_arg_options: _Optional[_Union[SubqueryExpression.TableArgOptions, _Mapping]] = ..., in_subquery_values: _Optional[_Iterable[_Union[_expressions_pb2.Expression, _Mapping]]] = ...) -> None: ...
