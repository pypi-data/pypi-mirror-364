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
PPChannelizer
"""

from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import pp_channelizer_pb2_grpc

from . import servicehubcontrol
from .servicehubutils import servicehub_call


class PPChannelizer:
    """
    The PPChannelizer class is responsible for the communication with its
    specific Plugin on the platform. Generate the interface to a new endpoint
    by passing the connection and the endpoint name.
    """

    def __init__(self, connection, endpoint):
        self.connection = connection
        self._stub = pp_channelizer_pb2_grpc.PPChannelizerServiceStub(
            connection.get_channel()
        )
        hubcontrol = servicehubcontrol.ServicehubControl(connection)
        try:
            self.index = hubcontrol.get_endpoint_index_of_plugin(
                "PPChannelizerPlugin", endpoint
            )
            self.endpoint_index = datatypes_pb2.EndpointIndex(
                value=self.index, name=endpoint
            )
        except Exception:
            print("Error: endpoint with name " + endpoint + " not found.")

        self.conf = self.get_channelizer_config()

    def get_index(self):
        """
        Returns the index of this specific endpoint
        """
        return self.index

    def get_decimation(self):
        """
        Decimation defines the channel sampling rate compared to the input sample rate
        """
        return self.conf.ppc_decimation

    def get_channel_bandwidth(self):
        """
        Channel bandwidth defines the frequency bandwidth of a single channel
        """
        return self.conf.channel_bandwidth

    def get_ppc_bandwidth(self):
        """
        PPC_Bandwidth defines the frequency bandwidth of the whole channelizer.
        This value is usually equal to the input sample rate
        """
        return self.conf.ppc_bandwidth

    def get_reverse_iq(self):
        """
        If true, the phase between I and Q signals is reversed
        """
        return self.conf.reverse_iq

    def get_shifted(self):
        """
        If true, a frequency shift of channel_sample_rate/2 is applied
        ToDo: Should not be a boolean, but a value to define the shift frequency
        """
        return self.conf.shifted

    def get_sample_rate(self):
        """
        Defines the input sample rate of the channelizer
        """
        return self.conf.sample_rate

    def get_center_frequency(self):
        """
        Defines the center frequency of the channelizer,
        which equals to the center frequency of channel 0
        """
        return self.conf.center_frequency

    def get_passband(self):
        """
        Returns the usable passband of the input spectrum
        Some channels at the edges may not be used if the passband is smaller than theppc_bandwidth
        """
        return self.conf.bb_passband

    @servicehub_call(errormsg="failed", tries=1)
    def get_channelizer_config(self):
        """
        Get the config pp_channelizer endpoint
        Returns a list of the variables:
            [ppc_decitmation, ppc_bandwidth, channel_bandwidth, reverse_iq,
            shifted, sample_rate, center_frequency, bb_passband]
        """

        conf = self._stub.GetChannelizerConfig(self.endpoint_index)
        return conf
