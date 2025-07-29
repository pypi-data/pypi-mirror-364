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
The Stimulation module is responsible for data generation.
It is based on a BRAM, that is read cyclically.
The content of the BRAM is user definable by the functionality of this API.
"""

from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import stimulation_pb2, stimulation_pb2_grpc

from . import servicehubcontrol
from .servicehubutils import servicehub_call


class Stimulation:
    """
    The Stimulation class is responsible for the communication with its
    specific Plugin on the platform. Generate the interface to a new endpoint
    by passing the connection and the endpoint name.
    """

    def __init__(self, connection, endpoint):
        self._stub = stimulation_pb2_grpc.StimulationServiceStub(
            connection.get_channel()
        )
        self.connection = connection
        hubcontrol = servicehubcontrol.ServicehubControl(connection)
        self.index = hubcontrol.get_endpoint_index_of_plugin(
            "StimulationPlugin", endpoint
        )

    def get_index(self):
        """
        This method returns the index of the endpoint
        """
        return self.index

    @servicehub_call(errormsg="failed", tries=1)
    def enable(self):
        """
        This method enables the stimulation module.
        The BRAM is read cyclically and data is generated
        """
        self._stub.Enable(datatypes_pb2.EndpointIndex(value=self.index))

    @servicehub_call(errormsg="failed", tries=1)
    def disable(self):
        """
        This method disables the module. No data is generated anymore
        """
        self._stub.Disable(datatypes_pb2.EndpointIndex(value=self.index))

    @servicehub_call(errormsg="failed", tries=1)
    def get_enable(self):
        """
        Returns whether the module is enabled or disabled
        """
        return self._stub.GetEnable(datatypes_pb2.EndpointIndex(value=self.index)).value

    @servicehub_call(errormsg="failed", tries=1)
    def reset(self):
        """
        This method resets the Stimulation module.
        The BRAM is cleared and the read and write pointers
        are set back to their initial position.
        """
        self._stub.Reset(datatypes_pb2.EndpointIndex(value=self.index))

    @servicehub_call(errormsg="failed", tries=1)
    def is_complex_samples(self):
        """
        Returns whether the module works with real or complex (I/Q) samples
        """
        return self._stub.IsComplexSamples(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_delta_frequency(self):
        """
        Since the BRAM is read out cyclically, it is important,
        that there is no jump from the last sample to the first sample.
        The BRAM has to contain an integer number of periods for all tones that are active.
        Due to a limited amount of BRAM slices, not all frequencies are allowed.
        This method returns the difference between two valid frequencies
        """
        return self._stub.GetDeltaFrequency(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_sample_rate(self):
        """
        get_sample_rate returns the rate with which the data is generated
        """
        return self._stub.GetSampleRate(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_sample_count(self):
        """
        get_sample_count returns the amount of samples stored within the BRAM
        """
        return self._stub.GetSampleCount(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_rf_center_frequency(self, frequency):
        """
        Updates the center frequency of the module in the rf domain
        """
        return self._stub.SetRFCenterFrequency(
            datatypes_pb2.IndexedDouble(
                index=datatypes_pb2.EndpointIndex(value=self.index), value=frequency
            )
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_rf_center_frequency(self):
        """
        get_rf_center_frequency returns the center frequency of the upmixed sinals
        at the output of the system
        """
        return self._stub.GetRFCenterFrequency(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def add_tone(self, frequency, amplitude, phase, phase_iqi=None, amplitude_iqi=None):
        """
        add_tone allows the user to generate a single tone with sinusoidal shape
        by defining its shape

        Note: Using this method does not clear the BRAM content,
        but adds the new tone to the existing samples.
        If the BRAM shall be cleared,
        call :func:`~firmware_modules.stimulation.Stimulation.ClearSamples`
        before using this function.

        Args:
            frequency (double): Frequency of the tone to be generated
            amplitude (double): Amplitude of the tone to be generated
            phase (double): Phase of the tone to be generated
            phase_iqi (double): Phase mismatch between the I and Q path (optional)
            amplitude_iqi (double): Aplitude mismatch between the I and Q path (optional)
        """
        if phase_iqi is None:
            phase_iqi = 0.0
        if amplitude_iqi is None:
            amplitude_iqi = 1.0

        tone_specs = stimulation_pb2.ToneSpecs(
            frequency=frequency,
            amplitude=amplitude,
            phase=phase,
            phaseIQI=phase_iqi,
            amplitudeIQI=amplitude_iqi,
        )
        return self._stub.AddTone(
            stimulation_pb2.IndexedToneSpecs(
                index=datatypes_pb2.EndpointIndex(value=self.index), specs=tone_specs
            )
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def add_tones(
        self, frequencies, amplitudes, phases, phases_iqi=None, amplitudes_iqi=None
    ):
        """
        add_tones allows the user to define multiple tones
        with sinusoidal shape with one signle call
        See :func:`~firmware_modules.stimulation.Stimulation.AddTone`

        Note: The amplitude of all tones must not exceed 1

        Todo:
            Check length of lists or set defaults

        Args:
            frequencies (double[]): Frequencies of the tones to be generated
            amplitudes (double[]): Amplitudes of the tones to be generated
            phases (double[]): Phases of the tones to be generated
            phases_iqi (double[]): Phase mismatch between the I and Q path (optional)
            amplitudes_iqi (double[]): Amplitude mismatch between the I and Q path (optional)
        """
        if phases_iqi is None:
            phases_iqi = [0.0 for _ in range(len(frequencies))]
        if amplitudes_iqi is None:
            amplitudes_iqi = [1.0 for _ in range(len(frequencies))]

        tone_specs_vector = []
        for idx, frequency in enumerate(frequencies):
            tone_specs_vector.append(
                stimulation_pb2.ToneSpecs(
                    frequency=frequency,
                    amplitude=amplitudes[idx],
                    phase=phases[idx],
                    phaseIQI=phases_iqi[idx],
                    amplitudeIQI=amplitudes_iqi[idx],
                )
            )
        return self._stub.AddTones(
            stimulation_pb2.IndexedToneSpecsVector(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                specs=tone_specs_vector,
            )
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_playback_interval(self, start, end):
        """
        The playback interval defines the area of the BRAM that is read cyclically.
        By default, the complete BRAM is read.
        In case a special frequency has to be generated that does not fit into the BRAM
        this method can be used to modify the interval
        See :func:`~firmware_modules.stimulation.Stimulation.GetDeltaFrequency`

        Args:
            start (int): first sample in the BRAM to be read
            end (int): last sample in the BRAM to be read
        """
        self._stub.SetPlaybackInterval(
            stimulation_pb2.Interval(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                start=start,
                end=end,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_playback_interval(self):
        """
        Returns the currently used interval within the BRAM
        See :func:`~firmware_modules.stimulation.Stimulation.SetPlaybackInterval`
        """
        interval = self._stub.GetPlaybackInterval(
            datatypes_pb2.EndpointIndex(value=self.index)
        )
        return interval.start, interval.end

    @servicehub_call(errormsg="failed", tries=1)
    def get_playback_interval_stepsize(self):
        """
        TODO: What is this used for?
        """
        return self._stub.GetPlaybackIntervalStepSize(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def write_raw_data(self, data, adjust_playback_interval=False):
        """
        In case an arbitrary waveform has to be generated that does not have a sinusoidal shape,
        this method can be used.
        It allows the user to create an array of values that are stored into the BRAM
        and read cyclically.

        Args:
            data (int[]): Array with data to be generated
            adjust_playback_interval (bool): Defines wheter the playback interval is adjusted
            to the amount of data provided by this method.
            See :func:`~firmware_modules.stimulation.Stimulation.SetPlaybackInterval`
        """
        self._stub.WriteRawData(
            stimulation_pb2.RawData(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                value=list(data),
                adjustPlaybackInterval=adjust_playback_interval,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def clear_samples(self):
        """
        This method clears the BRAM and allows the user to create new data
        """
        self._stub.ClearSamples(datatypes_pb2.EndpointIndex(value=self.index))

    @servicehub_call(errormsg="failed", tries=1)
    def set_modulation(self, frequency, amplitude, offset, phase=0):
        """
        This method allows the user to modulate another signal on the generated tones.
        It is needed for simulating a microwave SQUID multiplexer and emulating the SQUID signal.
        The signal defined here is amplitude modulated on the tones generated by
        :func:`~firmware_modules.stimulation.Stimulation.AddTone` or
        :func:`~firmware_modules.stimulation.Stimulation.AddTones`

        Args:
            frequency (double): Frequency of the modulated signal
            amplitude (double): Amplitude of the modulated signal
            offset (double): Offset of the modulated signal
            phase (double): Phase of the modulated signal
        """
        self._stub.SetModulation(
            stimulation_pb2.Modulation(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                frequency=frequency,
                amplitude=amplitude,
                offset=offset,
                phase=phase,
            )
        )
