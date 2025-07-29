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
Convenient wrapper for protobuf generated python code for AD7291
"""
from cirque.packages.grpc import ad7291_pb2, ad7291_pb2_grpc
from cirque.packages.grpc import datatypes_pb2

from . import servicehubcontrol
from .servicehubutils import servicehub_call


class AD7291:
    """
    This Plugin offers control over AD7291, an ADC with integrated temperature sensor.

    Each Endpoint corresponds to one chip, which contains 8 voltage readout channels as
    well as an additional channel hardwired to its temperature diode.

    Further details can be found at https://www.analog.com/media/en/technical-documentation/data-sheets/AD7291.pdf
    """

    def __init__(self, connection, endpoint, plugin_name="AD7291Plugin"):
        self.connection = connection
        self.stub = ad7291_pb2_grpc.AD7291ServiceStub(connection.get_channel())
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
    def get_voltage(self, channel):
        """
        Reads out ADC value of given channel and calculates corresponding voltage.

        :param int channel: 0..7 index of to be read channel
        """
        return self.stub.GetVoltage(
            ad7291_pb2.ChannelIdentifier(ep_index=self.ep_index, channel=channel)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_temperature(self):
        """
        Reads out ADC value for the temperature diode and calculates corresponding temperature.

        :return float: temperature in °C
        """
        return self.stub.GetTemperature(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_temperature_mean(self):
        """
        The chip offers a time-averaged mean temperature by internally calculating
        new_temp = 7/8*prev_temp + 1/8*current_temp in regular intervals. Considering the chip's
        slow response to thermal shock (see datasheet) this functionality is relatively useless,
        but offered here anyways.

        :return float: average temperature in °C
        """
        return self.stub.GetTemperatureMean(self.ep_index).value
