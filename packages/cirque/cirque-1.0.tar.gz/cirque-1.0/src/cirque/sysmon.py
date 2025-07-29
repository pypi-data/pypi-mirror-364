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
"""
Convenient wrapper for protobuf generated python code for Xilinx SysMon
"""
from cirque.packages.grpc import sysmon_pb2, sysmon_pb2_grpc

from .servicehubutils import servicehub_call


class SysMon:
    """
    SysMon is a tool to check various temperatures and internal voltages on a Xilinx FPGA platform.
    This serves as an expansion of functionality provided by PIMC.

    Further details can be found at https://docs.xilinx.com/v/u/en-US/ug580-ultrascale-sysmon
    """

    tempEnum = sysmon_pb2.TempSelect.TempID
    voltEnum = sysmon_pb2.VoltSelect.VoltID

    def __init__(self, connection):
        self.connection = connection
        self._stub = sysmon_pb2_grpc.SysMonServiceStub(connection.get_channel())

    @servicehub_call(errormsg="failed", tries=1)
    def get_temperature(self, channel_enum):
        """
        Get temperature reading at various places on the platform. Please refer to sysmon.proto for
        an overview of available enum parameter values and a short description according to Xilinx.
        For a detailed description refer to datasheets and user guides by Xilinx.

        :params enum channel_enum: 0..2 enum name or underlying value
        :return float: temperature in °C

        Example usage:
        ---- test.py ----
        my_sysmon = SysMon(*connection*)
        # following calls are equivalent to get ps_apu temperature
        # via cirque class parameter
        T = my_sysmon.get_temperature(SysMon.tempEnum.ps_apu)
        # via proto generated class (be careful with import paths)
        T = my_sysmon.get_temperature(sysmon_pb2.TempSelect.TempID.ps_apu)
        # via underlying integer referring to enum (ps_apu -> 1)
        T = my_sysmon.get_temperature(1)
        -----------------
        """
        return self._stub.GetTemperature(
            sysmon_pb2.TempSelect(select=channel_enum)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_voltage(self, channel_enum):
        """
        Get voltage reading at various places on the platform. Please refer to sysmon.proto for an
        overview of available enum parameter values and a short description according to Xilinx.
        For a detailed description refer to datasheets and user guides by Xilinx.

        :param enum channel_enum: 0..26 enum name or underlying value
        :return float: voltage in V

        Example usage:
        ---- test.py ----
        my_sysmon = SysMon(*connection*)
        # following calls are equivalent to get ps_adc voltage
        # via cirque class parameter
        T = my_sysmon.get_voltage(SysMon.voltEnum.ps_adc)
        # via proto generated class (be careful with import paths)
        T = my_sysmon.get_voltage(sysmon_pb2.VoltSelect.VoltID.ps_adc)
        # via underlying integer referring to enum (ps_adc -> 17)
        T = my_sysmon.get_voltage(17)
        -----------------
        """
        return self._stub.GetVoltage(sysmon_pb2.VoltSelect(select=channel_enum)).value
