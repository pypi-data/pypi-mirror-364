# Copyright© 2023-2025 Quantum Interface (quantuminterface@ipe.kit.edu)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from typing import Literal

import numpy as np
from cirque.packages.grpc import memmap_pb2_grpc, memmap_pb2

from .servicehubutils import servicehub_call, FPGAConnection

dtype_t = Literal["i8", "u8", "i16", "u16", "i32", "u32", "i64", "u64"]

dtype_grpc_map = {
    "u8": memmap_pb2.UINT8,
    "i8": memmap_pb2.INT8,
    "u16": memmap_pb2.UINT16,
    "i16": memmap_pb2.INT16,
    "u32": memmap_pb2.UINT32,
    "i32": memmap_pb2.INT32,
    "u64": memmap_pb2.UINT64,
    "i64": memmap_pb2.INT64,
}


def _dtype(val: str) -> memmap_pb2.Type:
    if val not in dtype_grpc_map:
        raise KeyError(
            f'Illegal data type {val}, available types are {", ".join(map(str, dtype_grpc_map.keys()))}'
        )
    return dtype_grpc_map[val]


def _size_of(simple_type: dtype_t) -> int:
    """
    Returns the size of `simple_type` in bit
    """
    return int(simple_type[1:])


dtype_np_map = {
    "u8": ">u1",
    "i8": ">i1",
    "u16": ">u2",
    "i16": ">i2",
    "u32": ">u4",
    "i32": ">i4",
    "u64": "<u8",
    "i64": ">i8",
}


class DevMem:
    """
    The DevMem Plugin provides raw memory access to registers inside FPGA modules.
    Note that the DevMem Plugin needs to be activated on the FPGA side and a valid memory range must be given.
    """

    def __init__(self, connection):
        if isinstance(connection, str):
            connection = FPGAConnection(ip=connection)
        self.connection = connection
        self._stub = memmap_pb2_grpc.DevMemServiceStub(connection.get_channel())

    @servicehub_call(errormsg="failed", tries=1)
    def read(self, address: int, count: int, dtype: dtype_t = "u32") -> np.ndarray:
        """
        Reads multiple values from a contiguous place in memory
        """
        message = memmap_pb2.ReadRequest(adr=address, count=count, type=_dtype(dtype))
        resp = self._stub.Read(message)
        return np.array(resp.value, dtype=np.uint64).astype(dtype_np_map[dtype])

    @servicehub_call(errormsg="failed", tries=1)
    def read_single(
        self, address: int, lsb=0, width=None, dtype: dtype_t = "u32"
    ) -> np.ndarray:
        """
        Reads multiple values from a contiguous place in memory
        """

        _width = width if width is not None else _size_of(dtype)

        message = memmap_pb2.ReadSliceRequest(
            adr=address, type=_dtype(dtype), slice_lsb=lsb, slice_width=_width
        )
        resp = self._stub.ReadSlice(message)
        np_type = np.obj2sctype(dtype_np_map[dtype])
        return np_type(np.uint64(resp.value[0]))

    @servicehub_call(errormsg="failed", tries=1)
    def write(self, address: int, values, dtype: dtype_t = "u32") -> bool:
        """
        Write multiple values to a contiguous place in memory
        """
        _values = np.array(values).astype(np.int64).view(np.uint64)
        msg = memmap_pb2.WriteRequest(
            adr=address, value=_values.tolist(), type=_dtype(dtype)
        )
        ack = self._stub.Write(msg)
        return ack.success

    @servicehub_call(errormsg="failed", tries=1)
    def write_single(
        self, address: int, value: int, lsb=0, width=None, dtype: dtype_t = "u32"
    ) -> bool:
        """
        Read multiple values from a contiguous place in memory
        """
        _width = width if width is not None else _size_of(dtype)
        msg = memmap_pb2.WriteSliceRequest(
            adr=address,
            value=value,
            type=_dtype(dtype),
            slice_lsb=lsb,
            slice_width=_width,
        )
        ack = self._stub.WriteSlice(msg)
        return ack.success
