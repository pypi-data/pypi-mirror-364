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
Supermodule for control of the full reaoudchain.
The chain consists of modules for channelization, DDC, fluxramp demodulation and event detection.
"""

from cirque.packages.grpc import capreadoutchain_pb2, capreadoutchain_pb2_grpc
from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import servicehubcontrol_pb2, servicehubcontrol_pb2_grpc

from .servicehubutils import servicehub_call


class CapReadoutChain:
    """
    The CapReadoutChain class is responsible for the communication with its
    specific Plugin on the platform. Generate the interface to a new endpoint
    by passing the connection and the endpoint name.
    """

    def __init__(self, connection, endpoint):
        self.connection = connection
        self._stub = capreadoutchain_pb2_grpc.CapReadoutChainServiceStub(
            self.connection.get_channel()
        )
        self.index = (
            servicehubcontrol_pb2_grpc.ServicehubControlServiceStub(
                self.connection.get_channel()
            )
            .GetEndpointIndexOfPlugin(
                servicehubcontrol_pb2.EndpointIndexRequest(
                    plugin_name="CapReadoutChainPlugin", endpoint_name=endpoint
                )
            )
            .val
        )

    @servicehub_call(errormsg="failed", tries=1)
    def calibrate_readoutchain(self, tones, fluxramp_frequency, modulation_factor):
        """
        Calibrates the complete readout chain according to given parameters
        Args:
            tones: stimulation tones as defined with func::~capreadoutchain::define_tones
            fluxramp_frequency: {float} specifying the frequency of the generated fluxramp
            modulation_factor: {float} Emulates squid signal onto the stimulation tones. Only for debugging
        """
        return self._stub.CalibrateReadoutchain(
            capreadoutchain_pb2.Configuration(
                tones=tones,
                fluxrampFrequency=fluxramp_frequency,
                modulationFactor=modulation_factor,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_resonator_channels(self):
        """
        Returns a list of the configured resonator channels
        """
        return self._stub.GetResonatorChannels(datatypes_pb2.Empty())

    @servicehub_call(errormsg="failed", tries=1)
    def activate_raw_readout(self):
        """
        Activates the bypass in the fluxramp demodulation and the event detection,
        so that the raw data stream before fluxramp demodulation is sampled by the DMA.
        """
        self._stub.ActivateRawReadout(datatypes_pb2.Empty())

    @servicehub_call(errormsg="failed", tries=1)
    def activate_demodulated_readout(self):
        """
        Disables bypass in the fluxramp demodulation, so that the demodulated
        data is sampled by the DMA
        """
        self._stub.ActivateDemodulatedReadout(datatypes_pb2.Empty())

    @servicehub_call(errormsg="failed", tries=1)
    def get_fluxramp_configuration(self):
        """
        Returns the full configuration file for the processing chain
        """
        return self._stub.GetFluxrampConfiguration(datatypes_pb2.Empty())

    def define_tones(self, frequencies, amplitudes, phases, phases_iqi, amplitudes_iqi):
        """
        Converts a list of tones into the appropriate format to be loaded into the platform.
        Args:
            frequencies: {float[]} containing the frequencies in Hz
            amplitudes: {float[]} containing the amplitudes of the tones
            phases: {float[]} containing the phases of the tones
            phases_iqi: {float[]} containing correction values to supress iq phase imbalance
            amplitudes_iqi: {float[]} containing correction values to supress iq amplitude imbalance
        """
        tones = []
        for index, frequency in enumerate(frequencies):
            tones.append(
                capreadoutchain_pb2.ToneSpecs(
                    frequency=frequency,
                    amplitude=amplitudes[index],
                    phase=phases[index],
                    phaseIQI=phases_iqi[index],
                    amplitudeIQI=amplitudes_iqi[index],
                )
            )
        return capreadoutchain_pb2.Frequencies(value=tones)
