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
The SignalAmplifier Module is responsible for increasing the number of usable bits of digital signals.
This allows more precise measurements within DSP and other calculations.
"""

from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import signalamplifier_pb2_grpc

from . import servicehubcontrol
from .servicehubutils import servicehub_call


class SignalAmplifier:
    """
    The SignalAmplifier class is responsible for the communication with its
    specific Plugin on the platform. Generate the interface to a new endpoint
    by passing the connection and the endpoint name.
    """

    def __init__(self, connection, endpoint):
        self.connection = connection
        self._stub = signalamplifier_pb2_grpc.SignalAmplifierServiceStub(
            connection.getChannel()
        )
        hubcontrol = servicehubcontrol.ServicehubControl(connection)
        self.index = hubcontrol.get_endpoint_index_of_plugin(
            "SignalAmplifierPlugin", endpoint
        )

    def get_index(self):
        """
        Returns the index of a specific endpoint
        """
        return self.index

    @servicehub_call(errormsg="failed", tries=1)
    def get_overflow_counter(self):
        """
        This method reads the amount of samples, where an overflow occured
        """
        return self._stub.GetOverflowCounter(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def reset_overflow_counter(self):
        """
        This method resets the number of overflows
        """
        self._stub.ResetOverflowCounter(datatypes_pb2.EndpointIndex(value=self.index))

    @servicehub_call(errormsg="failed", tries=1)
    def set_factor(self, factor):
        """
        This method sets the amplification factor.

        Args:
            factor (int): Amplification factor
        """
        self._stub.SetFactor(
            datatypes_pb2.IndexedInt(
                index=datatypes_pb2.EndpointIndex(value=self.index), value=factor
            )
        )
