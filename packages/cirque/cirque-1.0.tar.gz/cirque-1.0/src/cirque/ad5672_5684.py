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
Convenient wrapper for protobuf generated python code for AD5672/AD5684
"""
from cirque.packages.grpc import ad5672_5684_pb2, ad5672_5684_pb2_grpc
from cirque.packages.grpc import datatypes_pb2

from . import servicehubcontrol
from .servicehubutils import servicehub_call


class AD5672:
    """
    This Plugin offers control of a set of mostly similar, simple DACs.
    These are Analog Devices' AD5672, AD5684 and possibly some others,
    which are all commonly integrated as chips on PCBs.

    Each Endpoint corresponds to one chip, which contains multiple channels
    (AD5672: 8, AD5684: 4). This plugin offers support for either setting a
    specific 12-bit register value [0...4095], which corresponds to an output
    voltage of [0..5V], or directly setting the desired voltage.

    Further details can be found on a chip's data-sheet
        AD5672: https://www.analog.com/media/en/technical-documentation/data-sheets/ad5672r_5676r.pdf
        AD5684: https://www.analog.com/media/en/technical-documentation/data-sheets/AD5686_5684.pdf
    """

    def __init__(self, connection, endpoint, plugin_name="AD5672_5684Plugin"):
        self.connection = connection
        self.stub = ad5672_5684_pb2_grpc.AD5672_5684ServiceStub(
            connection.get_channel()
        )
        self.index = servicehubcontrol.ServicehubControl(
            connection
        ).get_endpoint_index_of_plugin(plugin_name, endpoint)
        self.ep_index = datatypes_pb2.EndpointIndex(value=self.index)

    def get_index(self):
        """
        Get index of endpoint determined by servicehub control
        """
        return self.index

    @servicehub_call(errormsg="failed", tries=1)
    def set_voltage(self, channel, value, unit="V"):
        """
        TODO: Split into two methods
        Set DAC voltage at given channel to desired value.
        :param int channel: number of the to be set channel
        :param value EITHER (int) 0..4095 register value OR (float) 0..5 voltage
        :param unit (string) 'V' or '1'/'reg'
        """
        if unit == "V":
            self.stub.SetOutput(
                ad5672_5684_pb2.Write(
                    ep_index=self.ep_index, channel=channel, volt=value
                )
            )
        elif unit in ("1", "reg"):
            self.stub.SetOutput(
                ad5672_5684_pb2.Write(
                    ep_index=self.ep_index, channel=channel, reg=value
                )
            )
        else:
            raise ValueError("'unit' must be 'V' or '1'/'reg'")
