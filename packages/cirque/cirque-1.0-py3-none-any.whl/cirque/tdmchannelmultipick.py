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
The BidirectionalMixer Module is used to shift the center frequency of a wideband signal.
The mixer works bidirectional, shifting the spectrum up in TX direction and mix it down by
the same frequency in RX.
This allows for instance performing parallel resonator sweeps.
"""

from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import tdmchannelmultipick_pb2, tdmchannelmultipick_pb2_grpc

from . import servicehubcontrol
from .servicehubutils import servicehub_call


class TDMChannelMultipick:
    """
    The BidirectionalMixer class is responsible for the communication with its
    specific Plugin on the platform. Generate the interface to a new endpoint
    by passing the connection and the endpoint name.
    """

    def __init__(self, connection, endpoint):
        self.connection = connection
        self._stub = tdmchannelmultipick_pb2_grpc.TDMChannelMultipickServiceStub(
            connection.get_channel()
        )
        hubcontrol = servicehubcontrol.ServicehubControl(connection)
        self.index = hubcontrol.get_endpoint_index_of_plugin(
            "TDMChannelMultipickPlugin", endpoint
        )

    def get_index(self):
        """
        Returns the index of a specific endpoint
        """
        return self.index

    @servicehub_call(errormsg="failed", tries=1)
    def set_active_channels(self, channels):
        """
        This method selects the active channels.
        It configures the transfer of specific samples of TDM transfers

        Args:
            channels (int []): array containing the desired TDM channels
        """
        return self._stub.SetActiveChannels(
            tdmchannelmultipick_pb2.Configuration(
                index=datatypes_pb2.EndpointIndex(value=self.index), channels=channels
            )
        )
