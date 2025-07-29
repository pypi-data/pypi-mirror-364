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
Convenient wrapper for protobuf generated python code for LTC5586
"""
from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import ltc5586_pb2, ltc5586_pb2_grpc

from . import servicehubcontrol
from .servicehubutils import servicehub_call


class LTC5586:
    """
    The LTC 5586 is a direct conversion quadrature demodulator optimized for high linearity
    zero-IF and low IF receiver applications in the 300MHz to 6GHz frequency range. The very wide
    IF bandwidth of more than 1GHz makes the LTC5586 particularly suited for demodulation of very
    wideband signals, especially in digital predistortion (DPD) applications. The outstanding
    dynamic range of the LTC5586 makes the device suitable for demanding infrastructure direct
    conversion applications. Proprietary technology inside the LTC5586 provides the capability to
    optimize OIP2 to 80dBm, and achieve image rejection better than 60dB. The DC offset control
    function allows nulling of the DC offset at the A/D converter input, thereby optimizing the
    dynamic range of true zero-IF receivers that use DC coupled IF signal paths. The wideband RF
    and LO input ports make it possible to cover all the major wireless infrastructure frequency
    bands using a single device. The IF outputs of the LTC5586 are designed to interface directly
    with most common A/D converter input interfaces. The high OIP3 and high conversion gain of the
    device eliminate the need for additional amplifiers in the IF signal path. (From datasheet)

    Further details can be found at https://www.analog.com/media/en/technical-documentation/data-sheets/LTC5586.pdf
    """

    def __init__(self, connection, endpoint, plugin_name="LTC5586Plugin"):
        self.connection = connection
        self.stub = ltc5586_pb2_grpc.LTC5586ServiceStub(connection.get_channel())
        self.index = servicehubcontrol.ServicehubControl(
            connection
        ).get_endpoint_index_of_plugin(plugin_name, endpoint)
        self.ep_index = datatypes_pb2.EndpointIndex(value=self.index)
        self.auto_update_write = True

    def get_index(self):
        """
        Get index of endpoint determined by servicehub control
        """
        return self.index

    # Power adjustment
    @servicehub_call(errormsg="failed", tries=1)
    def set_attenuation(self, val):
        """
        Controls the step attenuator.

        :param uint val: 0..31 attenuation in dB
        """
        self.stub.SetAttenuation(
            datatypes_pb2.IndexedUInt(index=self.ep_index, value=val)
        )
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_attenuation(self):
        """
        Readback the step attenuator value.

        :return uint: attenuation in dB
        """
        return self.stub.GetAttenuation(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_gain(self, val):
        """
        Adjusts the amplifier gain from 8dB to 15dB (with an offset of 8).

        :param uint val: 0..7 gain in dB
        """
        self.stub.SetGain(datatypes_pb2.IndexedUInt(index=self.ep_index, value=val))
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_gain(self):
        """
        Readback the amplifier gain from 8dB to 15dB (with an offset of 8).

        :return uint: gain in dB
        """
        return self.stub.GetGain(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_gain_error(self, val, unit="dB"):
        """
        Controls the IQ gain error. Internally the plugin uses the linear dependency from
        datasheet fig. 5586 G42 for conversions between units.

        :param string unit: 'dB' or '1'/''reg
        :param uint/float val: EITHER (uint) 0..63 register value OR (float) -0.5..0.5 gain error in dB
        """
        if unit == "dB":
            self.stub.SetGainErrordB(
                datatypes_pb2.IndexedDouble(index=self.ep_index, value=val)
            )
        elif unit in ("1", "reg"):
            self.stub.SetGainError(
                datatypes_pb2.IndexedUInt(index=self.ep_index, value=val)
            )
        else:
            raise ValueError("'unit' must be 'dB' or '1'/'reg'")
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_gain_error(self, unit="dB"):
        """
        Controls the IQ gain error. Internally the plugin uses the linear dependency from
        datasheet fig. 5586 G42 for conversions between units.

        :param sting unit: 'dB' or '1'/'reg'
        :return uint/float: EITHER (uint) register value OR (float) gain error in dB
        """
        if unit == "dB":
            return self.stub.GetGainErrordB(self.ep_index).value
        elif unit in ("1", "reg"):
            return self.stub.GetGainError(self.ep_index).value
        else:
            raise ValueError("'unit' must be 'dB' or '1'/'reg'")

    # Frequency adjustment
    @servicehub_call(errormsg="failed", tries=1)
    def switch_to_high_band(self):
        """
        Switch to high band in the LO matching network.
        """
        self.stub.SwitchToHighBand(self.ep_index)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def switch_to_low_band(self):
        """
        Switch to low band in the LO matching network.
        """
        self.stub.SwitchToLowBand(self.ep_index)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_band(self):
        """
        Return whether LO matching network uses high or low band.

        :return bool: True: high band, False: low band
        """
        return self.stub.GetBand(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_lo_bias(self, val):
        """
        Used to optimize mixer IP3

        :param uint val: 0..7 register value
        """
        self.stub.SetLoBias(datatypes_pb2.IndexedUInt(index=self.ep_index, value=val))
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_lo_bias(self):
        """
        Used to optimize mixer IP3

        return uint: register value
        """
        return self.stub.GetLoBias(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_lo_match_c1(self, val):
        """
        Controls the CF1 capacitor in the LO matching network.

        :param uint val: 0..31 register value
        """
        self.stub.SetLoMatchC1(
            datatypes_pb2.IndexedUInt(index=self.ep_index, value=val)
        )
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_lo_match_c1(self):
        """
        Controls the CF1 capacitor in the LO matching network.

        :return uint: register value
        """
        return self.stub.GetLoMatchC1(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_lo_match_c2(self, val):
        """
        Controls the CF2 capacitor in the LO matching network.

        :param uint val: 0..31 register value
        """
        self.stub.SetLoMatchC2(
            datatypes_pb2.IndexedUInt(index=self.ep_index, value=val)
        )
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_lo_match_c2(self):
        """
        Controls the CF2 capacitor in the LO matching network.

        :return uint: register value
        """
        return self.stub.GetLoMatchC2(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_lo_match_inductor(self, val):
        """
        Controls the LF1 inductor in the LO matching network.

        :param uint val: 0..3 register value
        """
        self.stub.SetLoMatchInductor(
            datatypes_pb2.IndexedUInt(index=self.ep_index, value=val)
        )
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_lo_match_inductor(self):
        """
        Controls the LF1 inductor in the LO matching network.

        :return uint: register value
        """
        return self.stub.GetLoMatchInductor(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_lo_match(self, val):
        """
        Uses table 3 from datasheet to find and set required settings for CF1, CF2, LF1 and band
        for the demodulator to be in a valid range for incoming signals

        :param uint val: 0..6000 frequency in MHz
        """
        self.stub.SetLoMatchMHz(
            datatypes_pb2.IndexedUInt(index=self.ep_index, value=val)
        )
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_lo_match(self):
        """
        Returns the lower boundary of the current frequency range CF1, CF2, LF1 and band are
        adjusted to according to table 3 from the datasheet.

        :return uint: frequency in MHz
        """
        return self.stub.GetLoMatchMHz(self.ep_index).value

    # Phase error
    @servicehub_call(errormsg="failed", tries=1)
    def set_phase_error(self, val, unit="deg"):
        """
        Controls the IQ phase error. Internally the plugin uses a cubic fit function with data
        from fig. 5586 G43 datasheet and a binary search for unit conversions

        :param string unit: 'deg' or '1'/'reg'
        :param float/uint val: EITHER (float) -4.14..1.94 in 1° OR (uint) 0..512 register value
        """
        if unit == "deg":
            self.stub.SetPhaseErrorDeg(
                datatypes_pb2.IndexedDouble(index=self.ep_index, value=val)
            )
        elif unit in ("1", "reg"):
            self.stub.SetPhaseError(
                datatypes_pb2.IndexedUInt(index=self.ep_index, value=val)
            )
        else:
            raise ValueError("'unit' must be 'deg' or '1'/'reg'")
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_phase_error(self, unit="deg"):
        """
        Controls the IQ phase error. Internally the plugin uses a cubic fit function with data
        from fig. 5586 G43 datasheet and a binary search for unit conversions

        :param string unit: 'deg' or '1'/'reg'
        :return float/uint: EITHER (float) in 1° OR (uint) register value
        """
        if unit == "deg":
            return self.stub.GetPhaseErrorDeg(self.ep_index).value
        elif unit in ("1", "reg"):
            return self.stub.GetPhaseError(self.ep_index).value
        else:
            raise ValueError("'unit' must be 'deg' or '1'/'reg'")

    # I/Q specific configurations
    @servicehub_call(errormsg="failed", tries=1)
    def set_dc_offset(self, val, comp, unit="mV"):
        """
        Controls the DC offset for a given I/Q component. DC offset depends notably on temperature
        and frequency, see datasheet fig. 5586 G44. Internally the plugin uses the linear
        dependency from datasheet fig. 5586 G47 for conversions between units.

        :param string comp: "I" or "Q"
        :param string unit: 'mV' or '1'/'reg'
        :param float/uint val: EITHER (float) -70.0..100.0 OR (uint) 0..255
        """
        if comp in ("I", "i"):
            if unit == "mV":
                self.stub.SetDcOffsetImV(
                    datatypes_pb2.IndexedDouble(index=self.ep_index, value=val)
                )
            elif unit in ("1", "reg"):
                self.stub.SetDcOffsetI(
                    datatypes_pb2.IndexedUInt(index=self.ep_index, value=val)
                )
            else:
                raise ValueError("'unit' must be 'mV' or '1'/'reg'")
        elif comp in ("Q", "q"):
            if unit == "mV":
                self.stub.SetDcOffsetQmV(
                    datatypes_pb2.IndexedDouble(index=self.ep_index, value=val)
                )
            elif unit in ("1", "reg"):
                self.stub.SetDcOffsetQ(
                    datatypes_pb2.IndexedUInt(index=self.ep_index, value=val)
                )
            else:
                raise ValueError("'unit' must be 'mV' or '1'/'reg'")
        else:
            raise ValueError("'comp' must be 'I' or 'Q'")
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_dc_offset(self, comp, unit="mV"):
        """
        Reads back the target DC offset for a given I/Q component. DC offset depends notably on
        temperature and frequency, see datasheet fig. 5586 G44. Internally the plugin uses the
        linear dependency from datasheet fig. 5586 G47 for conversions between units.

        :param string comp: "I" or "Q"
        :param string unit: 'mV' or '1'/'reg'
        :return float/uint: EITHER (float) in mV OR (uint) 0..255
        """
        if comp in ("I", "i"):
            if unit == "mV":
                return self.stub.GetDcOffsetImV(self.ep_index).value
            elif unit in ("1", "reg"):
                return self.stub.GetDcOffsetI(self.ep_index).value
            else:
                raise ValueError("'unit' must be 'mV' or '1'/'reg'")
        elif comp in ("Q", "q"):
            if unit == "mV":
                return self.stub.GetDcOffsetQmV(self.ep_index).value
            elif unit in ("1", "reg"):
                return self.stub.GetDcOffsetQ(self.ep_index).value
            else:
                raise ValueError("'unit' must be 'mV' or '1'/'reg'")
        else:
            raise ValueError("'comp' must be 'I' or 'Q'")

    @servicehub_call(errormsg="failed", tries=1)
    def set_vector_adjust(self, name, val_x=None, val_y=None):
        """
        Set vector adjust for given name. HD(I/Q)(2/3) and IM3(I/Q) use x- and y-component as
        expected. For IM2 (x, y) refer to (IM2I, IM2Q) instead. Note the lower boundaries for IM3
        and IP3. Setting x or y to None keeps the respective component unchanged

        :params string name: {'im3', 'ip3', 'im2', 'im3i', 'im3q', 'hd2i', 'hd2q', 'hd3i', 'hd3q'}
        :param uint x: EITHER (uint) 0..255 OR (None) ignore
        :param uint y: EITHER (uint) 0..255 OR (None) ignore
        """
        arg = ltc5586_pb2.WriteVector(index=self.ep_index, name=name)
        if not val_x is None:
            arg.x = val_x
        if not val_y is None:
            arg.y = val_y
        self.stub.SetVectorAdjust(arg)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_vector_adjust(self, name):
        """
        Reads back the vector adjust for given name. HD(I/Q)(2/3) and IM3(I/Q) use x- and
        y-component as expected. For IM2 (x, y) refer to (IM2I, IM2Q) instead.

        :param string name: {'im3', 'ip3', 'im2', 'im3i', 'im3q', 'hd2i', 'hd2q', 'hd3i', 'hd3q'}
        :return (uint, uint): (x, y) vector
        """
        ret = self.stub.GetVectorAdjust(
            ltc5586_pb2.VectorReg(index=self.ep_index, name=name)
        )
        return ret.x, ret.y

    # Chip control
    @servicehub_call(errormsg="failed", tries=1)
    def enable_rf_switch(self):
        """
        Controls the RF switch state with a logical AND of the RFSW pin.
        """
        self.stub.EnableRfSwitch(self.ep_index)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def disable_rf_switch(self):
        """
        Controls the RF switch state with a logical AND of the RFSW pin.
        """
        self.stub.DisableRfSwitch(self.ep_index)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_rf_switch_state(self):
        """
        Controls the RF switch state with a logical AND of the RFSW pin.

        :return bool: True: RF switch is enabled
        """
        return self.stub.GetRfSwitch(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def enable_sdo_readback(self):
        """
        Controls the SDO readback mode for less data loss at high spi frequencies.
        """
        self.stub.EnableSdoReadback(self.ep_index)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def disable_sdo_readback(self):
        """
        Controls the SDO readback mode for less data loss at high spi frequencies.
        """
        self.stub.DisableSdoReadback(self.ep_index)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def get_sdo_readback_state(self):
        """
        Controls the SDO readback mode for less data loss at high spi frequencies.

        :return bool: True: SDO readback is enabled
        """
        return self.stub.GetSdoReadback(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def reset(self):
        """
        Reload the state of the chip
        """
        self.stub.Reset(self.ep_index)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

    @servicehub_call(errormsg="failed", tries=1)
    def init(self):
        """
        Reload the state of the chip
        TODO: Difference to reset???
        """
        self.stub.Initial(self.ep_index)
        if self.auto_update_write:
            self.stub.UpdateWrite(self.ep_index)

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
