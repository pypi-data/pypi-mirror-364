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
By means of the RampGen module, Sawtooth and triangular waveforms can be generated.
In comparison to the more generic stimulation module, the rampgen module is more
ressource efficient and allows signals of every frequency
"""

from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import rampgen_pb2, rampgen_pb2_grpc

from .servicehubutils import servicehub_call


class RampGen:
    """
    The RampGen class is responsible for the communication with its
    specific Plugin on the platform. Generate the interface to a new endpoint
    by passing the connection and the endpoint name.
    """

    def __init__(self, connection, endpoint_index):
        self.connection = connection
        self._stub = rampgen_pb2_grpc.RampGenServiceStub(self.connection.getChannel())
        self.index = endpoint_index

    @servicehub_call(errormsg="failed", tries=1)
    def enable(self):
        """
        This method enables the module and starts data generation.
        """
        self._stub.Enable(datatypes_pb2.EndpointIndex(value=self.index))

    @servicehub_call(errormsg="failed", tries=1)
    def disable(self):
        """
        This method disables the module and stops data generation.
        """
        self._stub.Disable(datatypes_pb2.EndpointIndex(value=self.index))

    @servicehub_call(errormsg="failed", tries=1)
    def get_enable(self):
        """
        The get_enable method returns, whether the module is currently enabled or disabled.
        """
        return self._stub.GetEnable(datatypes_pb2.EndpointIndex(value=self.index)).value

    @servicehub_call(errormsg="failed", tries=1)
    def reset(self):
        """
        With the reset method, the module can be resetted to its original state.
        """
        self._stub.Reset(datatypes_pb2.EndpointIndex(value=self.index))

    @servicehub_call(errormsg="failed", tries=1)
    def set_sawtooth_ramp(self, frequency, amplitude, fall_time):
        """
        With the set_sawtooth_ramp method, the module can be configured to generate a waveform with a sawtooth shape.
        The shape can be defined by several parameters.

        Args:
            frequency (double): Frequency of the signal
            amplitude (double): Amplitude of the signal
            fall_time (double): Duration of the decreasing slope
        """
        self._stub.SetSawToothRamp(
            rampgen_pb2.RampRequest(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                frequency=frequency,
                amplitude=amplitude,
                param=fall_time,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_triangular_ramp(self, frequency, amplitude):
        """
        With the set_triangular_ramp method, the module can be configured
        to generate a waveform with a symmetric triangular shape.
        The shape can be defined by several parameters.
        For unsymmetric shapes, see :func:`~firmware_modules.rampgen.RampGen.SetSawToothRamp`

        Args:
            frequency (double): Frequency of the signal
            amplitude (double): Amplitude of the signal
        """
        self._stub.SetTriangularRamp(
            rampgen_pb2.RampRequest(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                frequency=frequency,
                amplitude=amplitude,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def clear_config(self):
        """
        With the clear_config method, the currently configured signal shape is cleared.
        A new configuration can be defined.
        """
        self._stub.ClearConfig(datatypes_pb2.EndpointIndex(value=self.index))

    @servicehub_call(errormsg="failed", tries=1)
    def get_frequency(self):
        """
        Returns the frequency of the configured signal
        """
        return self._stub.GetFrequency(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value
