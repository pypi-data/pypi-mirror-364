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
Convenient wrapper for protobuf generated python code for RFPCB
"""
from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import rfpcbsuper_pb2, rfpcbsuper_pb2_grpc

from . import servicehubcontrol
from .servicehubutils import servicehub_call


class RFPCB:
    """
    The RFPCB can generate, mix and demodulate signals in the gigahertz range. Its intended
    purpose is for manipulating and reading out qubits, but it has also proven to be useful in
    other related high-frequency experiments.

    This super-plugin contains both functionality which is dependent on multiple plugins working
    together as well as functionalities of single plugins within the context of their specific
    configuration or use-case on the RFPCB. This ensures that the base plugins are being kept as
    generic as possible.

    Devices used are
     - 4x LMX2594 PLL (RFLO, IFLO, TXPL and RXPL)
     - LTC5586 demodulator
     - AD5672/AD5684 DAC (depending on RFPCB revision)
     - AD7291 ADC with temperature sensor

    Further details can be found at 'Robert Gartmann. “Digitally controllable integrated RF
    electronics for manipulation and readout of qubits”. Master thesis. Karlsruher Institut für
    Technologie, Dez. 2019'
    """

    def __init__(self, connection, endpoint, plugin_name="RFPCBSuperPlugin"):
        self.connection = connection
        self.stub = rfpcbsuper_pb2_grpc.RFPCBSuperServiceStub(connection.get_channel())
        self.index = servicehubcontrol.ServicehubControl(
            connection
        ).get_endpoint_index_of_plugin(plugin_name, endpoint)
        self.ep_index = datatypes_pb2.EndpointIndex(value=self.index)

    def get_index(self):
        """
        Get index of endpoint determined by servicehub control
        """
        return self.index

    @servicehub_call(errormsg="failed", tries=1)
    def reset(self, device_list):
        """
        Return listed LMX2594 or LTC5586 endpoints into their original state

        :param string[] device_list: possible names are "TXPL", "RXPL", "IFLO",
                            "RFLO" or "Demod"
        """
        arg = rfpcbsuper_pb2.EndpointList(index=self.ep_index, devices=[])
        for name in device_list:
            if name == "TXPL":
                arg.devices.append(rfpcbsuper_pb2.TXPL)
            elif name == "RXPL":
                arg.devices.append(rfpcbsuper_pb2.RXPL)
            elif name == "IFLO":
                arg.devices.append(rfpcbsuper_pb2.IFLO)
            elif name == "RFLO":
                arg.devices.append(rfpcbsuper_pb2.RFLO)
            elif name == "Demod":
                arg.devices.append(rfpcbsuper_pb2.DEMOD)
            else:
                raise ValueError(
                    "Unkown name '%s'. Must be 'TXPL', 'RXPL', 'IFLO', 'RFLO' or 'Demod'",
                    name,
                )
        self.stub.Reset(arg)

    @servicehub_call(errormsg="failed", tries=1)
    def startup(self, lmx_output_list=None, ltc_settings=(None, None, None)):
        """
        Set most of the parameters necessary for starting up or controlling LMX2594 and LTC5586
        endpoints in a single call.

        :param string[]/float[] lmx_output_list:
                            output power settings for LMX endpoints. string-entry: name of
                            endpoint (e.g. "TXPL"), first float-entry: -10..0 output A power in
                            dB, second float-entry: -10..0 output B power in dB. If a float is
                            replaced with a None, the respective output will be diabled. If both
                            outputs are disabled, the PLL will power down.
        :param uint/float ltc_settings:
                            demodulator gain in dB, gain_error in cdB and phase_error in 1°
                            respectively. Set a value to None to keep it unchanged.
        """
        # LTC message
        ltc_msg = rfpcbsuper_pb2.LTCStart()
        if not ltc_settings[0] is None:
            ltc_msg.gain = ltc_settings[0]
        if not ltc_settings[1] is None:
            ltc_msg.gain_error = ltc_settings[1]
        if not ltc_settings[2] is None:
            ltc_msg.phase_error = ltc_settings[2]
        # main message
        arg = rfpcbsuper_pb2.StartInfo(index=self.ep_index, ltc=ltc_msg, lmx_list=[])
        # LMX messages
        if lmx_output_list is None:
            lmx_output_list = []
        for lmx_settings in lmx_output_list:
            elm = rfpcbsuper_pb2.LMXStart()
            if lmx_settings[0] == "TXPL":
                elm.device = rfpcbsuper_pb2.TXPL
            elif lmx_settings[0] == "RXPL":
                elm.device = rfpcbsuper_pb2.RXPL
            elif lmx_settings[0] == "IFLO":
                elm.device = rfpcbsuper_pb2.IFLO
            elif lmx_settings[0] == "RFLO":
                elm.device = rfpcbsuper_pb2.RFLO
            else:
                raise ValueError(
                    "Unkown LMX endpoint name '%s'. Must be 'TXPL', 'RXPL', 'IFLO' or 'RFLO'",
                    lmx_settings[0],
                )
            if not lmx_settings[1] is None:
                elm.power_a = lmx_settings[1]
            if not lmx_settings[2] is None:
                elm.power_b = lmx_settings[2]
            arg.lmx_list.append(elm)
        # send
        self.stub.Startup(arg)

    @servicehub_call(errormsg="failed", tries=1)
    def sweep(self, freq, offset, method="mixsweep", atten=10.0):
        """
        Sets RFLO and IFLO for desired frequency & offset using one of the methods 'mixsweep'
        (default), 'ifsweep', 'ifsweep_extended', 'rfsweep' or 'rfsweep_extended'. Also sets
        initial output attenuation.

        :param double freq: target frequency in Hz
        :param double offset: target offset in Hz
        :param string method: mixing method to be used
        :param double atten: output attenuation in dB (relative to maximum)
        """
        if method == "mixsweep":
            method_internal = rfpcbsuper_pb2.SweepInput.Method.MIXSWEEP
        elif method == "ifsweep":
            method_internal = rfpcbsuper_pb2.SweepInput.Method.IFSWEEP
        elif method == "ifsweep_extended":
            method_internal = rfpcbsuper_pb2.SweepInput.Method.IFSWEEP_EXTENDED
        elif method == "rfsweep":
            method_internal = rfpcbsuper_pb2.SweepInput.Method.RFSWEEP
        elif method == "rfsweep_extended":
            method_internal = rfpcbsuper_pb2.SweepInput.Method.RFSWEEP_EXTENDED
        else:
            raise ValueError("Unkown method '%s'", method)
        self.stub.Sweep(
            rfpcbsuper_pb2.SweepInput(
                index=self.ep_index,
                frequency=freq,
                power=atten,
                offset=offset,
                method=method_internal,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_pcb_freq(self):
        """
        Calculates current target frequency from RFLO and IFLO. Only supports "mixsweep" so far.

        :return double: frequency in Hz
        """
        return self.stub.GetDeviceFreq(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_attenuation(self, val):
        """
        Sets the PCB's output attenuation by adjusting AD5672/AD5684 DAC voltage over HMC346ALC3B
        analog attenuator

        :param double val: 0..30 attenuation in dB
        """
        self.stub.SetAttenuation(
            datatypes_pb2.IndexedDouble(index=self.ep_index, value=val)
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_demod_temp(self):
        """
        Returns temperature of demodulator using AD7291 voltage over LTC5586 temperature diode.
        For average PCB temperature refer to AD7291 plugin instead.

        :return double: temperature in °C
        """
        return self.stub.GetDemodTemp(self.ep_index).value
