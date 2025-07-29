import cirque.packages.grpc.datatypes_pb2 as _datatypes_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union
from cirque.packages.grpc.datatypes_pb2 import EndpointIndex as EndpointIndex
from cirque.packages.grpc.datatypes_pb2 import Empty as Empty
from cirque.packages.grpc.datatypes_pb2 import Bool as Bool
from cirque.packages.grpc.datatypes_pb2 import Int as Int
from cirque.packages.grpc.datatypes_pb2 import LInt as LInt
from cirque.packages.grpc.datatypes_pb2 import UInt as UInt
from cirque.packages.grpc.datatypes_pb2 import LUInt as LUInt
from cirque.packages.grpc.datatypes_pb2 import Float as Float
from cirque.packages.grpc.datatypes_pb2 import Double as Double
from cirque.packages.grpc.datatypes_pb2 import String as String
from cirque.packages.grpc.datatypes_pb2 import IndexedBool as IndexedBool
from cirque.packages.grpc.datatypes_pb2 import IndexedInt as IndexedInt
from cirque.packages.grpc.datatypes_pb2 import IndexedLInt as IndexedLInt
from cirque.packages.grpc.datatypes_pb2 import IndexedUInt as IndexedUInt
from cirque.packages.grpc.datatypes_pb2 import IndexedLUInt as IndexedLUInt
from cirque.packages.grpc.datatypes_pb2 import IndexedFloat as IndexedFloat
from cirque.packages.grpc.datatypes_pb2 import IndexedDouble as IndexedDouble
from cirque.packages.grpc.datatypes_pb2 import IndexedString as IndexedString

DESCRIPTOR: _descriptor.FileDescriptor

class WriteFracGuess(_message.Message):
    __slots__ = ("index", "method", "maxden")
    class Method(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FAREY: _ClassVar[WriteFracGuess.Method]
        FACSEC: _ClassVar[WriteFracGuess.Method]
        INSTANT: _ClassVar[WriteFracGuess.Method]
    FAREY: WriteFracGuess.Method
    FACSEC: WriteFracGuess.Method
    INSTANT: WriteFracGuess.Method
    INDEX_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    MAXDEN_FIELD_NUMBER: _ClassVar[int]
    index: _datatypes_pb2.EndpointIndex
    method: WriteFracGuess.Method
    maxden: int
    def __init__(self, index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., method: _Optional[_Union[WriteFracGuess.Method, str]] = ..., maxden: _Optional[int] = ...) -> None: ...
