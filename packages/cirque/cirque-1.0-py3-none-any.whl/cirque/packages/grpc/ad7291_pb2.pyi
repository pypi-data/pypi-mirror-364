import cirque.packages.grpc.datatypes_pb2 as _datatypes_pb2
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

class ChannelIdentifier(_message.Message):
    __slots__ = ("ep_index", "channel")
    EP_INDEX_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    ep_index: _datatypes_pb2.EndpointIndex
    channel: int
    def __init__(self, ep_index: _Optional[_Union[_datatypes_pb2.EndpointIndex, _Mapping]] = ..., channel: _Optional[int] = ...) -> None: ...
