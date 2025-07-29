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
The fluxramp demodulation is part of the data processing chain.
After separation of the individual channel data, the fluxramp demodulation
is required to reconstruct the raw sensor signal.
The I and Q data streams are used to calculate the phase information of the signal,
which contains the information.
"""

import numpy as np
from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import fluxrampdemod_pb2, fluxrampdemod_pb2_grpc

from . import servicehubcontrol
from .servicehubutils import servicehub_call


class FluxrampDemod:
    """
    The FluxrampDemod class is responsible for the communication with its
    specific Plugin on the platform. Generate the interface to a new endpoint
    by passing the connection and the endpoint name.
    """

    def __init__(self, connection, endpoint):
        self.connection = connection
        self._stub = fluxrampdemod_pb2_grpc.FluxRampDemodServiceStub(
            connection.get_channel()
        )
        hubcontrol = servicehubcontrol.ServicehubControl(connection)
        self.index = hubcontrol.get_endpoint_index_of_plugin(
            "FluxRampDemodPlugin", endpoint
        )

    def get_index(self):
        """
        Returns the index of a specific endpoint
        """
        return self.index

    @servicehub_call(errormsg="failed", tries=1)
    def set_bypass_act(self, bypass=1):
        """
        With this call, the module can be enabled and disabled.
        When the bypass is activated, the raw data from the channelizer is stored within the DDR.
        This is needed for calibration of the fluxramp demodulation

        Args:
            bypass (bool): Defines, whether the module is bypassed or not
        """
        return self._stub.SetFluxRampDemodBypassAct(
            datatypes_pb2.IndexedBool(
                index=datatypes_pb2.EndpointIndex(value=self.index), value=bypass
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_add_sync_bypass(self, addsync=1):
        """
        Enables the synchronization bit in the data stream when the bypass mode is activated.
        For calibration, the data of exactly one fluxramp period has to be extracted.
        The sync bit is activated once at the reset of the ramp. It is the LSB of the data stream.

        Args:
            addsync (bool): Defines, whether the synchronization is enabled
        """
        return self._stub.SetFluxRampDemodAddSyncBypass(
            datatypes_pb2.IndexedBool(
                index=datatypes_pb2.EndpointIndex(value=self.index), value=addsync
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_fluxramp_length(self, length):
        """
        Set number of samples during one ramp

        The number of samples N during one ramp is given by N = f_clk / f_ramp / N_pipelines,
        where f_clk is the clock rate of the demodulation module, f_ramp the ramp frequency and N_pipelines
        is the number of pipelines used for demodulation (see :func:`Fluxrampdemod.get_tdm_pipeline:count`).
        So in each channel N samples can be used for demodulation.
        Note that non integer values for N result in a desynchronization of demodulation and ramp generation.

        Args:
            length (int): Defines the amount of samples per channel within one fluxramp period
        """
        return self._stub.SetFluxRampLength(
            datatypes_pb2.IndexedUInt(
                index=datatypes_pb2.EndpointIndex(value=self.index), value=length
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_fluxramp_length(self):
        """
        See :func:`~Fluxrampdemod.set_fluxramp_length`
        """
        return self._stub.GetFluxRampLength(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_resync(self):
        """
        Manually resynchronize the start of demodulation on the (delayed) sync flag.
        Note:
            Resync is executed by default during configuration of FluxRampLength, NCO and SyncDelay

        """
        return self._stub.SetResync(datatypes_pb2.EndpointIndex(value=self.index))

    @servicehub_call(errormsg="failed", tries=1)
    def set_nco_frequency(self, channel, frequency):
        """
        For each channel, the module contains an NCO that downconverts the SQUID signal to DC.
        Before activation, the frequency of the SQUID signal has to be calculated
        and the NCO has to be set accordingly.

        Args:
            channel (int): Index of the specific channel the NCO frequency is configured for.
            frequency (double): Frequency of the SQUID signal to which the NCO has to be set.
        """
        return self._stub.SetNCOFrequency(
            fluxrampdemod_pb2.ChannelDouble(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                channel=channel,
                value=frequency,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_nco_frequencies(self, frequencies):
        """
        With this method, the frequencies of the NCOs for all channels can be set at once.
        It takes an array of frequencies that are mapped to the channels.
        See "SetNCOFrequency"

        Args:
            frequencies (double[]): Array of all SQUID signal frequencies
        """
        return self._stub.SetNCOFrequencies(
            fluxrampdemod_pb2.DoubleArray(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                value=list(frequencies),
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_nco_frequencies(self):
        """
        Returns the defined frequencies of the individual NCOs
        """
        return self._stub.GetNCOFrequencies(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_nco_phase(self, channel, phase):
        """
        For each channel, the module contains an NCO that downconverts the SQUID signal to DC.
        The phase of the input signal can be set accordingly to to the phase of the input signal,
        so that the baseline of the result is moved to zero.

        Args:
            channel (int): Index of the specific channel the NCO frequency is configured for.
            phase (double): Phase of the SQUID signal to which the NCO has to be set
            in order to move the baseline to zero.
        """
        return self._stub.SetNCOPhase(
            fluxrampdemod_pb2.ChannelDouble(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                channel=channel,
                value=phase,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_nco_phases(self, phases):
        """
        With this method, the phases of the NCOs for all channels can be set at once.
        It takes an array of phases that are mapped to the channels.
        See "SetNCOPhase"

        Args:
            phases (double[]): Array of all SQUID signal phases
        """
        if not isinstance(phases, np.ndarray):
            phases = [phases] * self.get_channel_count()
        return self._stub.SetNCOPhases(
            fluxrampdemod_pb2.DoubleArray(
                index=datatypes_pb2.EndpointIndex(value=self.index), value=phases
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_nco_phases(self):
        """
        Returns the defined phases of the individual NCOs
        """
        return self._stub.GetNCOPhases(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_offset(self, channel, offset):
        """
        For each channel, the module contains an NCO that downconverts the SQUID signal to DC.
        The offset of the NCO can be set to compensate the offset of the SQUID signal.

        Todo:
            Rename to "SetNCOOffset"

        Args:
            channel (int): Index of the specific channel the NCO frequency is configured for.
            offset (int): Inverted offset of the SQUID signal to which the NCO has to be set.
        """
        return self._stub.SetOffset(
            fluxrampdemod_pb2.ChannelData(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                channel=channel,
                value=offset,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_offsets(self, offsets=None):
        """
        With this method, the offsets of the NCOs for all channels can be set at once.
        It takes an array of offsets that are mapped to the channels.
        See :func:`~firmware_modules.fluxrampdemod.FluxrampDemod.SetOffset`

        Todo:
            "Rename to "SetNCOOffsets"

        Args:
            offsets (int[]): Array of all inverted SQUID signal offsets
        """
        if offsets is None:
            offsets = []

        if not isinstance(offsets, np.ndarray):
            offsets = [offsets] * self.get_channel_count()
        return self._stub.SetOffsets(
            fluxrampdemod_pb2.Signed32Array(
                index=datatypes_pb2.EndpointIndex(value=self.index), value=offsets
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_offsets(self):
        """
        Returns the defined offsets of the individual NCOs

        Todo:
            Rename to "GetNCOOffsets"
        """
        return self._stub.GetOffsets(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_nco_data(self, frequencies, phases, offsets):
        """
        set_nco_data allows calibration of all NCOs with one single call.
        It takes the frequecies, phases and offsets of all channels
        and configures the individual NCOs.
        See: "SetNCOFrequencies", "SetNCOPhases", "SetOffsets"

        Args:
            frequencies (double[]): Array of all SQUID signal frequencies
            phases (double[]): Array of all SQUID signal phases
            offsets (double[]): Array of all inverted SQUID signal offsets
        """
        return self._stub.SetNCOData(
            fluxrampdemod_pb2.NCOData(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                frequencies=list(frequencies),
                phases=list(phases),
                offsets=list(offsets),
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_rampgen_data(self, rampperiodecycles, rampsamplerate):
        """
        Apply configuration of RampGenerator

        Pass the number of cycles for one ramp and the sample rate of the ramp generator in Hz.
        These values will be used to calculate the number of samples received during one ramp (FluxRampLength).

        Note:
            This is a relic from old times. Use SetFluxRampLength and calculate the ramp frequency thereof.
        """
        return self._stub.SetRampGenData(
            fluxrampdemod_pb2.RampGenData(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                rampperiodecycles=rampperiodecycles,
                rampsamplerate=rampsamplerate,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_accumulation_range(self, start=0, end=0):
        """
        For valid operation of the fluxramp demodulation module it is necessary,
        that an exact integer amount of SQUID signal periods are converted
        within one single fluxramp period.
        Since it is not guaranteed that the frequency of the SQUID matches perfectly
        to the fluxramp period, the first and last samples within one fluxramp can be discarded
        in order to extract an integer number of periods.

        Args:
            start (int): First sample within the ramp to be used by the demodulation algorithm.
            end (int): Last sample within the ramp to be used by the demodulation algorithm.
        """
        if end < 1:
            fluxramp_length = self._stub.GetFluxRampLength(
                datatypes_pb2.EndpointIndex(value=self.index)
            ).value
            end += fluxramp_length
        self._stub.SetAccumulationRange(
            fluxrampdemod_pb2.StartAndEnd(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                start=start,
                end=end,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_accumulation_range(self):
        """
        Returns the first and last sample within on fluxramp
        that are considered by the demodulation algorithm
        """
        return self._stub.GetAccumulationRange(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_sample_rate(self):
        """
        Returns the sample rate of the module.
        """
        return self._stub.GetSampleRate(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_channel_count(self):
        """
        Returns the amount of channels that are demodulated by this module.
        """
        return self._stub.GetChannelCount(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_tdm_pipeline_count(self):
        """
        Todo:
            What is this used for?
        """
        return self._stub.GetTDMPipelineCount(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_channel_sample_rate(self):
        """
        Returns the sample rate for the data of one individual channel.
        This value is equal to the total sample rate provided by "GetSampleRate"
        divided by the amount of channels.
        """
        return self._stub.GetChannelSampleRate(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_window_preload_value(self, value=0):
        """
        Set the starting value of the rampgen windowing module

        Set starting value of window if rampgen is implemented as windowing module

        Note:
            Debug function, the whole window config can be set by :func:`set_window`

        Args:
            value: {int} preload value
        """
        self._stub.SetWindowPreloadValue(
            datatypes_pb2.IndexedInt(
                index=datatypes_pb2.EndpointIndex(value=self.index), value=value
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_window_preload_cycles(self, cycles=1):
        """
        Set the amount of samples to hold the starting value

        Note:
            Debug function, the whole window config can be set by :func:`set_window`

        Args:
            cycles: {int} amount of cycles.
        """
        self._stub.SetWindowPreloadCycles(
            datatypes_pb2.IndexedUInt(
                index=datatypes_pb2.EndpointIndex(value=self.index), value=cycles
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_window_step_sizes(self, value):
        """
        Set the step size of the RampGen Windowing module

        Set step size of Window if RampGen is implemented as windowing module.

        Note:
            Debug function, the whole window config can be set by :func:`set_window`

        Args:
            value: {int} step size
        """
        self._stub.SetWindowStepSizes(
            datatypes_pb2.IndexedInt(
                index=datatypes_pb2.EndpointIndex(value=self.index), value=value
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_window_ramp_cycles(self, cycles=0):
        """
        Set the number of steps of the rampgen windowing module

        Both the step count for rising and falling edge

        Note:
            Debug function, the whole window config can be set by :func:`set_window`

        Args:
            cycles: {int} step count
        """
        self._stub.SetWindowRampCycles(
            datatypes_pb2.IndexedUInt(
                index=datatypes_pb2.EndpointIndex(value=self.index), value=cycles
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_window_hold_cycles(self, cycles=0):
        """
        Set the sample count to hold the ramp before descending again

        Set starting value of window if rampgen is implemented as windowing module

        Note:
            Debug function, the whole window config can be set by :func:`set_window`

        Args:
            cycles: {int} step count
        """
        self._stub.SetWindowHoldCycles(
            datatypes_pb2.IndexedUInt(
                index=datatypes_pb2.EndpointIndex(value=self.index), value=cycles
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_window_preload_value(self):
        """
        Returns the window preload value

        See :func:`FluxrampDemod.set_window_preload_value`
        """
        return self._stub.GetWindowPreloadValue(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_window_preload_cycles(self):
        """
        Returns the window preload cycles

        See :func:`FluxrampDemod.set_window_preload_cycles`
        """
        return self._stub.GetWindowPreloadCycles(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_window_step_sizes(self):
        """
        Returns the window step size

        See :func:`FluxrampDemod.set_window_step_size`
        """
        return self._stub.GetWindowStepSizes(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_window_ramp_cycles(self):
        """
        Returns the window ramp cycles

        See :func:`FluxrampDemod.set_windo_ramp_cycles`
        """
        return self._stub.GetWindowRampCycles(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_window_hold_cycles(self):
        """
        Returns the amount of hold cycles in a window.

        See :func:`FluxrampDemod.set_window_hold_cycles`
        """
        return self._stub.GetWindowHoldCycles(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_raw_window(self, values):
        """
        In order to minimize leakage and intermodulation products,
        a window can be applied onto the input samples in order to filter the data.
        SetRawWindow allows the user to generate an arbitrary shape that will be used
        onto the samples within each ramp.
        The amount of samples therefore has to match the number of samples within one ramp.
        The filter values are stored within a BRAM and are read cyclic on each ramp.

        Args:
            values (double[]): Array of samples that generate the arbitrary filter shape
        """
        self._stub.SetRawWindow(
            fluxrampdemod_pb2.Signed32Array(
                index=datatypes_pb2.EndpointIndex(value=self.index), value=values
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_raw_window(self):
        """
        Returns the raw window that is stored within the BRAM
        See :func:`~fluxrampdemod.FluxrampDemod.SetRawWindow`
        """
        return self._stub.GetRawWindow(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_window(self, name="rectangular", length=0, offset=0, param=0):
        """
        For more information on the windows,
        see :func:`~fluxrampdemod.FluxrampDemod.SetRawWindow`
        Additionally to a raw window, the driver allows using several predefined windows
        that can be applied onto the input data.

        Args:
            name (enum): Shape of the filter.
            Available shapes are: None, Rectangular, Triangle, BlackmanHarris, Hamming
            length (int): Amount of samples the filter consists of.
            Should match the number of samples within one fluxramp period
            offset (?): ?
            param (?): ?
        """
        properties = {"name": name, "length": length, "offset": offset, "param": param}
        self._stub.SetWindow(
            fluxrampdemod_pb2.WindowRequest(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                properties=properties,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_window(self):
        """
        Returns information about the currently applied window.
        See :func:`~fluxrampdemod.FluxrampDemod.SetWindow`
        """
        window_msg = self._stub.GetWindow(datatypes_pb2.EndpointIndex(value=self.index))
        window = {
            "name": window_msg.name,
            "length": window_msg.length,
            "offset": window_msg.offset,
            "param": window_msg.param,
        }
        return window

    @servicehub_call(errormsg="failed", tries=1)
    def get_bram_offsets(self):
        """
        Returns the offsets of the individual BRAM blocks within the module.
        """
        return self._stub.GetBRAMOffsets(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_sync_delay(self, value=0):
        """
        This method can be used to introduce a delay between the ramp reset signal
        at the input and the sync signal.

        Todo:
            What is this used for?

        Args:
            value (int): Amount of samples the sync signal is applied after the ramp reset signal
        """
        self._stub.SetSyncDelay(
            datatypes_pb2.IndexedUInt(
                index=datatypes_pb2.EndpointIndex(value=self.index), value=value
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_sync_delay(self):
        """
        Returns the delay of the sync signal.
        See :func:`~fluxrampdemod.FluxrampDemod.SetSyncDelay`
        """
        return self._stub.GetSyncDelay(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value
