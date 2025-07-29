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
Convenient wrapper for protobuf generated python code for BalUnAtten
"""
from cirque.packages.grpc import balunatten_pb2, balunatten_pb2_grpc

from .servicehubutils import servicehub_call


class BalUnAtten:
    """
    BalUnAtten is an RF frontend for the control and readout of cryogenic circuits via an SDR
    system, which can be controlled by an FPGA platform via GPIO. This plugin offers most commonly
    used functionality (as defined in the original python scripts) as well as a call for manually
    setting the GPIO pins for more advanced use-cases. So far readback is not supported.

    Further details can be found at 'Valentin Stümpert. "A frontend for direct RF-synthesis on
    the basis of a ZCU216 board". Master thesis. Karlsruher Institut für Technologie, Feb. 2023'
    """

    def __init__(self, connection):
        self.connection = connection
        self.stub = balunatten_pb2_grpc.BalUnAttenServiceStub(connection.get_channel())

    @servicehub_call(errormsg="failed", tries=1)
    def dac_set_attenuation(self, channel, val):
        """
        Sets the attenuation at given DAC-channel. Will be rounded to nearest .5 value.

        :param uint channel: 0..3 channel number
        :param float val: 0..31.5 attenuation in dB
        """
        self.stub.DACSetAttenuation(balunatten_pb2.Float(channel=channel, value=val))

    @servicehub_call(errormsg="failed", tries=1)
    def adc_set_attenuation(self, channel, val):
        """
        Sets the attenuation at given ADC-channel. Will be rounded to nearest .5 value.

        :param uint channel: 0..3 channel number
        :param float val: 0..31.5 attenuation in dB
        """
        self.stub.ADCSetAttenuation(balunatten_pb2.Float(channel=channel, value=val))

    @servicehub_call(errormsg="failed", tries=1)
    def dac_switch_off(self, channel):
        """
        Switch given DAC-channel off.

        :param uint channel: 0..3 channel number
        """
        self.stub.DACSwitchOff(balunatten_pb2.Channel(channel=channel))

    @servicehub_call(errormsg="failed", tries=1)
    def adc_switch_off(self, channel):
        """
        Switch given ADC-channel off.

        :param uint channel: 0..3 channel number
        """
        self.stub.ADCSwitchOff(balunatten_pb2.Channel(channel=channel))

    @servicehub_call(errormsg="failed", tries=1)
    def dac_switch_nyquist(self, channel, val):
        """
        Switch nyquist zone of given DAC channel. See documentation for corresponding frequency.

        :param uint channel: 0..3 channel number
        :param uint val: {1, 2} nyquist zone number
        """
        self.stub.DACSwitchNyquist(balunatten_pb2.Number(channel=channel, value=val))

    @servicehub_call(errormsg="failed", tries=1)
    def adc_switch_nyquist(self, channel, val):
        """
        Switch nyquist zone of given ADC channel. See documentation for corresponding frequency.

        :param uint channel: 0..3 channel number
        :param uint val: {1, 2, 5, 6} nyquist zone number
        """
        self.stub.ADCSwitchNyquist(balunatten_pb2.Number(channel=channel, value=val))

    @servicehub_call(errormsg="failed", tries=1)
    def dac_switch_dc(self, channel):
        """
        Sets given DAC channel to DC operation mode (can be understood as 0th nyquist zone).

        :param uint channel: 0..3 channel number
        """
        self.stub.DACSwitchDC(balunatten_pb2.Channel(channel=channel))

    @servicehub_call(errormsg="failed", tries=1)
    def set_gpio_pin(self, channel, pin, val):
        """
        Manually set pins for full control over the PCB.

        :param uint channel: 0..3 channel number
        :param uint pin: 0..39 pin offset from channel base number
        :param bool val: pin will be toggled either on or off
        """
        self.stub.SetGpioShifterPin(
            balunatten_pb2.PinVal(channel=channel, pin=pin, value=val)
        )
