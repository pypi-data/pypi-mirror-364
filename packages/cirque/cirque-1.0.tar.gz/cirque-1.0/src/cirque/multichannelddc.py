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
The MultiChannelDDC Module is used to individually mix the signals of multiple channels
within a TDM scheme. The internal NCO can be set to a user-defined frequency. After this downmixing,
a low-pass filter is implemented. Currently, the filter coefficients are defined to form a low-pass
with a cutoff frequency at 1.6 MHz.
Additionally, there is the (hardwired) option to perform a decimation by 2 for a reduction of the
sampling rate.
"""
from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import multichannelddc_pb2, multichannelddc_pb2_grpc

from . import servicehubcontrol
from .servicehubutils import servicehub_call


class MultiChannelDDC:
    """
    The MultiChannelDDC class is responsible for the communication with its
    specific Plugin on the platform. Generate the interface to a new endpoint
    by passing the connection and the endpoint name.
    """

    def __init__(self, connection, endpoint):
        self.connection = connection
        self._stub = multichannelddc_pb2_grpc.MultiChannelDDCServiceStub(
            connection.get_channel()
        )
        hubcontrol = servicehubcontrol.ServicehubControl(connection)
        self.index = hubcontrol.get_endpoint_index_of_plugin(
            "MultiChannelDDCPlugin", endpoint
        )

    def get_index(self):
        """
        Returns the index of this specific endpoint
        """
        return self.index

    @servicehub_call(errormsg="failed", tries=1)
    def get_enabled(self):
        """
        Returns, whether the DDC is enabled
        """
        return self._stub.GetEnable(datatypes_pb2.EndpointIndex(value=self.index)).value

    @servicehub_call(errormsg="failed", tries=1)
    def enable(self):
        """
        Enables the DDC with the configured NCO frequencies
        """
        self._stub.Enable(datatypes_pb2.EndpointIndex(value=self.index))

    @servicehub_call(errormsg="failed", tries=1)
    def disable(self):
        """
        Disables the DDC. No more valid data is sent at the output of the module
        """
        self._stub.Disable(datatypes_pb2.EndpointIndex(value=self.index))

    @servicehub_call(errormsg="failed", tries=1)
    def get_tdm_channels(self):
        """
        Returns the amount of channels within the TDM scheme
        """
        return self._stub.GetTDMChannels(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_clock_frequency(self):
        """
        Returns the clock frequency of the module
        """
        return self._stub.GetClockFrequency(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_nco(self, channel, frequency, phase=0.0):
        """
        Configures the NCO for a single channel

        Args:
            channel (int): Index of the channel to be configured
            frequency (float): Frequency of the NCO to down-mix the input signal
        """
        param = multichannelddc_pb2.NCOParam(frequency=str(frequency), phase=phase)
        self._stub.SetNCO(
            multichannelddc_pb2.SingleNCO(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                channel=channel,
                param=param,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_ncos(self, frequencies, phases):
        """
        Configures all NCO Channels in one go

        Args:
            frequencies (float[]): List of frequencies the nco should be set to
            phases (float[]): List of phases the nco should be set to
        """
        params = []
        for frequency, phase in zip(frequencies, phases):
            params.append(
                multichannelddc_pb2.NCOParam(frequency=str(frequency), phase=phase)
            )
        self._stub.SetNCOs(
            multichannelddc_pb2.MultiNCO(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                params=params,
            )
        )
