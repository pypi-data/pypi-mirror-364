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
Convenient wrapper for protobuf generated python code for LMX2594
"""
from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import lmx2594_pb2, lmx2594_pb2_grpc

from . import servicehubcontrol
from .servicehubutils import servicehub_call


class LMX2594:
    """
    The LMX2594 is a high-performance, wideband synthesizer that can generate any frequency from
    10 MHz to 15 GHz without using an internal doubler, thus eliminating the need for
    sub-harmonic filters. The high-performance PLL with figure of merit of -236 dBc/Hz and
    high-phase detector frequency can attain very low in-band noise and integrated jitter. The
    high-speed N-divider has no pre-divider, thus significantly reducing the amplitude and number
    of spurs. There is also a programmable input multiplier to mitigate integer boundary spurs.
    (From datasheet)

    Overwiew: (see datasheet for schematic)
    Simple multiplications/divisions allow manipulating the input reference clock before being
    passed to the phase detector.
    The phase detector controls a charge pump in order to adjust the VCO. A sigma-delta-modulator
    allows the resulting division factor for the fed-back frequency to be set in steps of 2^-32,
    thus allowing a seemingly continous range of possible output frequencies.
    Outputs "A" and "B" share the same channel divider but can be individually toggled to
    directly output the VCO frequency instead or be turned off.

    Frequencies within the PLL can be calculated with:
        - Input stage: Phase_detect_frequency = input_frequency * (2 || if in_double enabled) *
                                                input_multiplier / r_div_before / r_div_after
        - Loop stage: VCO_frequency = Phase_detect_frequency * (N_div + fNum/fDen)
        - Output stage: output_frequency = VCO_frequency / {1               || if vco enabled
                                                            channel_divider || if ch_div enabled}

    Input ~10^8 HZ; Phase detect up to 4*10^8 Hz; VCO 7.5..15*10^9 Hz; Output 10^7 Hz..15*10^9 Hz

    Further details can be found at https://www.ti.com/product/LMX2594#tech-docs

    Besides register access, this Plugin also provides higher-level functionality like an
    automated calculation of a valid configuration to output a given frequency and allows
    conversions of register value <-> dB value for the output power. Changes can either be applied
    automatically or be stored in the kernel-driver by setting self.auto_update_write = False and
    be applied alltogether at a later point by calling self.update_write().
    """

    def __init__(self, connection, endpoint, plugin_name="LMX2594Plugin"):
        self.connection = connection
        self.stub = lmx2594_pb2_grpc.LMX2594ServiceStub(connection.get_channel())
        self.index = servicehubcontrol.ServicehubControl(
            connection
        ).get_endpoint_index_of_plugin(plugin_name, endpoint)
        self.ep_index = datatypes_pb2.EndpointIndex(value=self.index)
        self.prev_frac_method = lmx2594_pb2.WriteFracGuess.Method.FAREY
        self.prev_frac_max_den = 0xFFFFFFFF
        self.auto_update_write = True

    def get_index(self):
        """
        Get index of endpoint determined by servicehub control
        """
        return self.index

    # Chip main power state
    @servicehub_call(errormsg="failed", tries=1)
    def power_up(self):
        """
        Power up the PLL (~1W increase in power consumption)
        """
        self.stub.PowerUp(self.ep_index)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def power_down(self):
        """
        Power down the PLL (~1W decrease in power consumption)
        """
        self.stub.PowerDown(self.ep_index)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_power_state(self):
        """
        Whether the PLL is turned on or off

        :return bool: True: PLL on, False: PLL off
        """
        return self.stub.IsPowerUp(self.ep_index).value

    # Main frequency calculation
    @servicehub_call(errormsg="failed", tries=1)
    def set_frequency(self, freq):
        """
        Calculate required parameter configurations to generate the desired frequency for the
        chip and apply them. Only try setting the frequency manually instead of using this call
        if you know all of the edge-cases and limitations provided by the datasheet!

        :param double freq: Output frequency in Hz
        """
        self.stub.SetFrequency(
            datatypes_pb2.IndexedDouble(index=self.ep_index, value=freq)
        )
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_frequency(self):
        """
        Calculate the currently output frequency by inserting register values into the formulas
        from the description

        :return double: Output frequency in Hz
        """
        return self.stub.GetFrequency(self.ep_index).value

    # Input frequency manipulation
    @servicehub_call(errormsg="failed", tries=1)
    def set_input_frequency(self, freq):
        """
        Changes input frequency value used for internal calculations. Actual input frequency must
        of course be adjusted outside of LMX2594 plugin/driver.

        :param uint64 freq: Frequency in Hz
        """
        self.stub.SetInputFrequency(
            datatypes_pb2.IndexedLUInt(index=self.ep_index, value=freq)
        )
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_input_frequency(self):
        """
        Readback the value of the input frequency used in internal calculations

        :return uint64: Frequency in Hz
        """
        return self.stub.GetInputFrequency(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def enable_input_doubler(self):
        """
        Double phase detect frequency at input stage (if not already enabled)
        """
        self.stub.EnableVcoDoubler(self.ep_index)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def disable_input_doubler(self):
        """
        Half phase detect frequency at input stage (if not already disabled)
        """
        self.stub.DisableVcoDoubler(self.ep_index)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_input_doubler_state(self):
        """
        Get current state of the frequency doubler at input stage

        :return bool: True: Additional factor x2 for input freq -> phase detect freq
        """
        return self.stub.IsVcoDoublerEnabled(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_r_divider_before(self, factor):
        """
        Set value of the first integer divider at input stage

        :param uint factor: 1..128
        """
        self.stub.SetRDividerBefore(
            datatypes_pb2.IndexedUInt(index=self.ep_index, value=factor)
        )
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_r_divider_before(self):
        """
        Readback value of the first integer divider at input stage

        :return uint: division factor
        """
        return self.stub.GetRDividerBefore(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_input_multiplier(self, factor):
        """
        Set value of the integer multiplier at input stage

        :param uint factor: 3..7
        """
        self.stub.SetInputMultiplier(
            datatypes_pb2.IndexedUInt(index=self.ep_index, value=factor)
        )
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_input_multiplier(self):
        """
        Readback value of the integer multiplier at input stage

        :return uint: multiplication factor
        """
        return self.stub.GetInputMultiplier(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_r_divider_after(self, factor):
        """
        Set value of the second integer divider at input stage

        :param uint factor: 1..255
        """
        self.stub.SetRDividerAfter(
            datatypes_pb2.IndexedUInt(index=self.ep_index, value=factor)
        )
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_r_divider_after(self):
        """
        Readback value of the second integer divider at input stage

        :return uint: division factor
        """
        return self.stub.GetRDividerAfter(self.ep_index).value

    # Feedback loop frequency control
    @servicehub_call(errormsg="failed", tries=1)
    def set_frac_guess(self, method=None, max_den=None):
        """
        Change the to be used algorithm for approximating a double as uint32/uint32 during
        frequency calculations and its accuracy. Omit either parameter or set to None to keep
        previous setting

        :param string method: Either 'farey', 'facsec' or 'instant'
        :param uint max_den: 1..(2^32-1) Upper limit for denominator
        """
        if method is None:
            method_internal = self.prev_frac_method
        elif method == "farey":
            method_internal = lmx2594_pb2.WriteFracGuess.Method.FAREY
        elif method == "facsec":
            method_internal = lmx2594_pb2.WriteFracGuess.Method.FACSEC
        elif method == "instant":
            method_internal = lmx2594_pb2.WriteFracGuess.Method.INSTANT
        else:
            raise ValueError(
                "'method' must be 'farey', 'facsec' or 'instant'. Set type None to keep previous value."
            )

        if max_den is None:
            max_den_internal = self.prev_frac_max_den
        else:
            max_den_internal = max_den

        self.stub.SetFracGuess(
            index=self.ep_index, method=method_internal, maxden=max_den_internal
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_frac_guess(self):
        """
        Readback last set to be used algorithm for approximating a double as uint32/uint32 during
        frequency calculations and its accuracy

        :return (tuple[protobuf_enum_value,uint]) as (method, max_den)
                see lmx2594.proto for details
        """
        return self.prev_frac_method, self.prev_frac_max_den

    @servicehub_call(errormsg="failed", tries=1)
    def set_fnum(self, val):
        """
        Set numerator of fractional PLL at loop stage

        :param uint32 val: 0..(2^32-1)
        """
        self.stub.SetFnum(datatypes_pb2.IndexedUInt(index=self.ep_index, value=val))
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_fnum(self):
        """
        Readback numerator of fractional PLL at loop stage

        :return uint32: Fractional PLL numerator
        """
        return self.stub.GetFnum(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_fden(self, val):
        """
        Set denominator of fractional PLL at loop stage

        :param uint32 val: 1..(2^32-1)
        """
        self.stub.SetFden(datatypes_pb2.IndexedUInt(index=self.ep_index, value=val))
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_fden(self):
        """
        Readback denominator of fractional PLL at loop stage

        :return uint32: Fractional PLL denominator
        """
        return self.stub.GetFden(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_n_divider(self, val):
        """
        Set base integer divider at loop stage

        :param uint val: 28..524287
        """
        self.stub.SetNDivider(datatypes_pb2.IndexedUInt(index=self.ep_index, value=val))
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_n_divider(self):
        """
        Readback base integer divider at loop stage

        :return uint: Loop stage integer divider
        """
        return self.stub.GetNDivider(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_pfd_dly(self, val):
        """
        Additional parameter for calibration that must be set according to table 2 in datasheet

        :param uint val: 1..6
        """
        self.stub.SetPfdDly(datatypes_pb2.IndexedUInt(index=self.ep_index, value=val))
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_pfd_dly(self):
        """
        Additional parameter for calibration that must be set according to table 2 in datasheet
        """
        return self.stub.GetPfdDly(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def enable_mash_seed(self):
        """
        Details on how mash seed can be used to manipulate phase shift can be found on the
        datasheet.
        """
        self.stub.EnableMashSeed(self.ep_index)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def disable_mash_seed(self):
        """
        Details on how mash seed can be used to manipulate phase shift can be found on the
        datasheet.
        """
        self.stub.DisableMashSeed(self.ep_index)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_mash_seed_state(self):
        """
        Details on how mash seed can be used to manipulate phase shift can be found on the
        datasheet.

        :return bool: True: mash seed used; False: mash seed ignored
        """
        return self.stub.IsMashSeedEnabled(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_mash_seed(self, val):
        """
        Details on how mash seed can be used to manipulate phase shift can be found on the
        datasheet.

        :params uint32 val: 0..(2^32-1)
        """
        self.stub.SetMashSeed(datatypes_pb2.IndexedUInt(index=self.ep_index, value=val))
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_mash_seed(self):
        """
        Details on how mash seed can be used to manipulate phase shift can be found on the
        datasheet.

        :return uint32: Mash seed
        """
        return self.stub.GetMashSeed(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_charge_pump_current(self, val):
        """
        Changing the charge pump current allows fine tuning the shape of the output signal. See
        datasheet for details

        :param uint val: {0, 3, 6, 9, 12, 15}
        """
        self.stub.SetChargePumpCurrent(
            datatypes_pb2.IndexedUInt(index=self.ep_index, value=val)
        )
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_charge_pump_current(self):
        """
        Changing the charge pump current allows fine tuning the shape of the output signal. See
        datasheet for details

        :return uint: Charge pump current
        """
        return self.stub.GetChargePumpCurrent(self.ep_index).value

    # Output frequency adjustment
    @servicehub_call(errormsg="failed", tries=1)
    def set_channel_divider(self, factor):
        """
        Set value of channel divider at output stage

        :param uint factor: {2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 72, 96, 128, 192, 256, 384, 512, 768}
        """
        self.stub.SetChannelDivider(
            datatypes_pb2.IndexedUInt(index=self.ep_index, value=factor)
        )
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_channel_divider(self):
        """
        Readback value of channel divider at output stage

        :return uint: Channel divider
        """
        return self.stub.GetChannelDivider(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def switch_to_vco(self, output="A"):
        """
        Make the corresponding output use the VCO frequency insted of channel divider

        :param string output: 'A' or 'B'
        """
        if output in ("A", "a"):
            self.stub.SwitchToVcoA(self.ep_index)
        elif output in ("B", "b"):
            self.stub.SwitchToVcoB(self.ep_index)
        else:
            raise ValueError("'output' must either be 'A' or 'B'")
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def switch_to_chdiv(self, output="A"):
        """
        Make the corresponding output use the channel divider frequency insted of VCO

        :param string output: 'A' or 'B'
        """
        if output in ("A", "a"):
            self.stub.SwitchToChdivA(self.ep_index)
        elif output in ("B", "b"):
            self.stub.SwitchToChdivB(self.ep_index)
        else:
            raise ValueError("'output' must either be 'A' or 'B'")
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_vco_state(self, output="A"):
        """
        Readback if the corresponding output uses channel divider or VCO

        :param string output: 'A' or 'B'
        :return bool: True: Direct VCO output; False: channel divider
        """
        if output in ("A", "a"):
            return self.stub.IsVcoAEnabled(self.ep_index).value
        elif output in ("B", "b"):
            return self.stub.IsVcoBEnabled(self.ep_index).value
        else:
            raise ValueError("'output' must either be 'A' or 'B'")

    # Output power control
    @servicehub_call(errormsg="failed", tries=1)
    def set_output_power(self, val, output="A", unit="dB"):
        """
        Set output power of selected output. Can either be given in dB (relative to maximum output
        power, which in itself is frequency and temperature dependent) or a non-descriptive
        register value roughly corresponding to 0 ~ -10dB, 31 = 0dB. See Fig.18 up to Fig.20 on
        datasheet. Internally the plugin uses a linear interpolation for conversion between both
        units.

        :param string output: 'A' or 'B'
        :param string unit: 'db' or '1'/'reg'
        :param double/int val: EITHER (double) -10..0 OR (uint) 0..31
        """
        if output in ("A", "a"):
            if unit == "dB":
                self.stub.SetOutputPowerAdB(
                    datatypes_pb2.IndexedDouble(index=self.ep_index, value=val)
                )
            elif unit in ("1", "reg"):
                self.stub.SetOutputPowerA(
                    datatypes_pb2.IndexedUInt(index=self.ep_index, value=val)
                )
            else:
                raise ValueError("'unit' must either be 'dB' or ('1'/'reg')")
        elif output in ("B", "b"):
            if unit == "dB":
                self.stub.SetOutputPowerBdB(
                    datatypes_pb2.IndexedDouble(index=self.ep_index, value=val)
                )
            elif unit in ("1", "reg"):
                self.stub.SetOutputPowerB(
                    datatypes_pb2.IndexedUInt(index=self.ep_index, value=val)
                )
            else:
                raise ValueError("'unit' must either be 'dB' or ('1'/'reg')")
        else:
            raise ValueError("'output' must either be 'A' or 'B'")
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_output_power(self, output="A", unit="dB"):
        """
        Readback output power of selected output. Can either be returned in dB (relative to
        maximum output power, which in itself is frequency and temperature dependent) or a
        non-descriptive register value roughly corresponding to 0 ~ -10dB, 31 = 0dB. See Fig.18 up
        to Fig.20 on datasheet. Internally the plugin uses a linear interpolation for conversion
        between both units.

        :param string output: 'A' or 'B'
        :param sting unit: 'db' or '1'/'reg'
        :return: double/int
        """
        if output in ("A", "a"):
            if unit == "dB":
                return self.stub.GetOutputPowerAdB(self.ep_index).value
            elif unit in ("1", "reg"):
                return self.stub.GetOutputPowerA(self.ep_index).value
            else:
                raise ValueError("'unit' must either be 'dB' or ('1'/'reg')")
        elif output in ("B", "b"):
            if unit == "dB":
                return self.stub.GetOutputPowerBdB(self.ep_index).value
            elif unit in ("1", "reg"):
                return self.stub.GetOutputPowerB(self.ep_index).value
            else:
                raise ValueError("'unit' must either be 'dB' or ('1'/'reg')")
        else:
            raise ValueError("'output' must either be 'A' or 'B'")

    @servicehub_call(errormsg="failed", tries=1)
    def enable_output(self, output="A"):
        """
        Enable signals to be seen at the given output.

        :param string output: 'A' or 'B'
        """
        if output in ("A", "a"):
            self.stub.EnableOutputA(self.ep_index)
        elif output in ("B", "b"):
            self.stub.EnableOutputB(self.ep_index)
        else:
            raise ValueError("'output' must either be 'A' or 'B'")
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def disable_output(self, output="A"):
        """
        Disable signals to be seen at the given output.

        :param string output: 'A' or 'B'
        """
        if output in ("A", "a"):
            self.stub.DisableOutputA(self.ep_index)
        elif output in ("B", "b"):
            self.stub.DisableOutputB(self.ep_index)
        else:
            raise ValueError("'output' must either be 'A' or 'B'")
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_output_state(self, output="A"):
        """
        Whether given output is enabled or disabled

        :param string output: 'A' or 'B'
        :return bool: True: Given output is enabled
        """
        if output in ("A", "a"):
            return self.stub.IsOutputAEnabled(self.ep_index).value
        elif output in ("B", "b"):
            return self.stub.IsOutputBEnabled(self.ep_index).value
        else:
            raise ValueError("'output' must either be 'A' or 'B'")

    @servicehub_call(errormsg="failed", tries=1)
    def set_out_current(self, val):
        """
        Setting to a lower value allows slightly higher output power at higher frequencies at the
        expense of higher current consumption. (datasheet)

        :param uint val: 0(max boost)..3(no boost)
        """
        self.stub.SetOutCurrent(
            datatypes_pb2.IndexedUInt(index=self.ep_index, value=val)
        )
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_out_current(self):
        """
        Setting to a lower value allows slightly higher output power at higher frequencies at the
        expense of higher current consumption. (datasheet)

        :return uint: 0(max boost)..3(no boost)
        """
        return self.stub.GetOutCurrent(self.ep_index).value

    # Chip control
    @servicehub_call(errormsg="failed", tries=1)
    def enable_muxout_readback(self):
        """
        MUXout pin mostly used internally for lock detect
        """
        self.stub.EnableMuxoutReadback(self.ep_index)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def disable_muxout_readback(self):
        """
        MUXout pin mostly used internally for lock detect
        """
        self.stub.DisableMuxoutReadback(self.ep_index)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_muxout_readback_state(self):
        """
        MUXout pin mostly used internally for lock detect
        """
        return self.stub.IsMuxoutReadbackEnabled(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def recalibrate(self):
        """
        Since the chip internally uses different VCOs for different frequency ranges, this call
        might be sometimes needed to avoid heavy interference of a previously used oszillator
        after changing the frequency.
        """
        self.stub.Recalibrate(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def init(self):
        """
        Reload the state of the chip at first startup.
        """
        self.stub.Initial(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def update_read(self):
        """
        Overwrite the currently stored state of registers in the kernel-driver with the values
        read back from the actual chip.
        """
        self.stub.UpdateRead(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def update_write(self):
        """
        Write the current state of registers in the kernel-diver to the chip.
        """
        self.stub.UpdateWrite(self.ep_index)
