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
Convenient wrapper for protobuf generated python code for ChipInfoPlugin
"""
import json

from cirque.packages.grpc import chip_info_pb2, chip_info_pb2_grpc

from .servicehubutils import servicehub_call


class ChipInfo:
    """
    This Plugin offers an information dump of all chips on the hardware that communicate with the FPGA via I2C or SPI.
    """

    def __init__(self, connection):
        self.connection = connection
        self.stub = chip_info_pb2_grpc.ChipInfoServiceStub(connection.get_channel())

    @servicehub_call(errormsg="failed", tries=1)
    def get_chips_info(self, protocol, drivers):
        """
        Returns a JSON-formatted dump of all exposed registers of SPI and I2C devices

        :param string protocol: i2c or spi
        :param string[] drivers: list of all devices on the communication bus
        :return string: json dump
        """
        entries = [
            chip_info_pb2.ProtocolDriversMap.ProtocolDriversEntry(
                protocol=protocol, drivers=drivers
            )
        ]
        request = chip_info_pb2.ProtocolDriversMap(entries=entries)
        json_obj = json.loads(self.stub.GetChipsInfo(request).value)
        return json.dumps(json_obj, indent=4)
