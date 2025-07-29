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
Module to generate FLuxramp signals mainly to be used with echo_dac_extension board
"""
from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import fluxramp_generator_pb2, fluxramp_generator_pb2_grpc

from . import servicehubcontrol
from .servicehubutils import servicehub_call


class FluxrampGenerator:
    """
    The FluxrampGenerator class is responsible for the communication with its
    specific Plugin on the platform. Generate the interface to a new endpoint
    by passing the connection and the endpoint name.
    """

    def __init__(self, connection, endpoint):
        self.connection = connection
        self._stub = fluxramp_generator_pb2_grpc.FluxrampGeneratorServiceStub(
            self.connection.get_channel()
        )
        hubcontrol = servicehubcontrol.ServicehubControl(connection)
        self.index = hubcontrol.get_endpoint_index_of_plugin(
            "FluxrampGeneratorPlugin", endpoint
        )
        self.endpoint_index = datatypes_pb2.EndpointIndex(
            value=self.index, name=endpoint
        )

    @servicehub_call(errormsg="failed", tries=1)
    def enable(self):
        """
        This method enables the module and starts data generation.
        """
        self._stub.Enable(self.endpoint_index)

    @servicehub_call(errormsg="failed", tries=1)
    def disable(self):
        """
        This method disable the module and stops data generation.
        """
        self._stub.Disable(self.endpoint_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_enable(self):
        """
        The get_enable method returns, whether the module is currently enabled or disabled.
        """
        return self._stub.GetEnable(self.endpoint_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def reset(self):
        """
        With the reset method, the module can be resetted to its original state.
        """
        self._stub.Reset(self.endpoint_index)

    @servicehub_call(errormsg="failed", tries=1)
    def set_fluxramp(self, frequency, amplitude, falltime):
        """
        With the set_fluxramp method, the module can be configured to generate a waveform with a sawtooth shape.
        The shape can be defined by several parameters.

        Args:
            frequency (double): Frequency of the signal
            amplitude (double): Amplitude of the signal
            falltime  (double): Duration of the decreasing slope
        """
        self._stub.SetFluxramp(
            fluxramp_generator_pb2.FluxrampRequest(
                index=self.endpoint_index,
                frequency=frequency,
                amplitude=amplitude,
                falltime=falltime,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def clear_config(self):
        """
        With the ClearConfig method, the currently configured signal shape is cleared.
        A new configuration can be defined.
        """
        self._stub.ClearConfig(self.endpoint_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_sample_rate(self):
        """
        Returns the samplerate of the hardware module
        """
        return self._stub.GetSampleRate(self.endpoint_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_frequency(self):
        """
        Returns the frequency of the configured signal
        """
        return self._stub.GetFrequency(self.endpoint_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_amplitude(self):
        """
        Returns the amplitude of the configured signal
        """
        return self._stub.GetAmplitude(self.endpoint_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_falltime(self):
        """
        Returns the galltime of the configured signal
        """
        return self._stub.GetFalltime(self.endpoint_index).value
