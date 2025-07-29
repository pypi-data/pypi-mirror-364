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
Interface to configuration interface of an LTC2000 DAC
"""
from cirque.packages.grpc import ltc2000_cfg_pb2, ltc2000_cfg_pb2_grpc, datatypes_pb2


def _grpc_index(pin_spec: str):
    """
    For a pin specification, return the grpc port message.

    The pin specification is legal if it is
    - either the string 'clk', 'ck' or 'clock'
    - 'a' or 'A' followed by an integer
    - 'b' or 'B' followed by an integer
    """
    if not pin_spec:
        raise ValueError(f"Pin specification '{pin_spec}' cannot be empty")
    pin_spec = pin_spec.lower()
    if pin_spec in {"ck", "clk", "clock"}:
        kind = ltc2000_cfg_pb2.Port.Kind.CLK
        value = 0
    else:
        if pin_spec[0] == "a" or pin_spec[0] == "A":
            kind = ltc2000_cfg_pb2.Port.Kind.A
        elif pin_spec[0] == "b" or pin_spec[0] == "B":
            kind = ltc2000_cfg_pb2.Port.Kind.B
        else:
            raise ValueError(
                "Pin specification must start with either 'A', 'B' or be 'CLK'"
            )
        try:
            value = int(pin_spec[1:])
        except ValueError as error:
            raise ValueError(
                f"Pin location {pin_spec[1:]} is not a valid integer"
            ) from error
    if value < 0:
        raise ValueError("Pin value cannot be less than zero")
    return ltc2000_cfg_pb2.Port(kind=kind, value=value)


class LTC2000Cfg:
    """
    Initializes the LTC2000.
    :param connection: A :class:`~cirque.FPGAConnection` object
    """

    def __init__(self, connection):
        self.connection = connection
        self._stub = ltc2000_cfg_pb2_grpc.LTC2000CfgServiceStub(
            self.connection.get_channel()
        )

    @property
    def status(self):
        """
        Returns status information about the connected LTC
        and the internal FPGA firmware.

        :return: The status information with the following contents:
            - :python:`vtc_enabled` whether Voltage and Temperature compensation (VTC) is enabled
            - :python:`calibration_done` whether calibration is done. Only relevant when VTC is enabled
        """
        return self._stub.GetStatus(datatypes_pb2.Empty())

    @property
    def sampling_frequency(self):
        """
        Returns the sampling frequency of the connected DAC in Hz
        """
        return self._stub.GetSampleRate(datatypes_pb2.Empty()).value

    def get_port_delay(self, port: str) -> float:
        """
        Returns the delay in seconds of the Port at a certain index.

        :param port: The port. This value is:
            - 'clk' for the clock port
            - 'A<digit>' for pins in port A
            - 'B<digit>' for pins in port B
            Capitalization is ignored. The clock port may also be spelled 'ck' or 'clock'
        """
        index = _grpc_index(port)
        return self._stub.GetPortDelay(index).value

    def set_port_delay(self, port: str, value: float) -> float:
        """
        Sets the delay at a certain ports and
        returns the delay in seconds of the Port at a certain index.

        :param port: The port. This value is:
            - 'clk' for the clock port
            - 'A<digit>' for pins in port A
            - 'B<digit>' for pins in port B
            Capitalization is ignored. The clock port may also be spelled 'ck' or 'clock'

        :param value: The new settings in seconds that the port should have
        """
        index = _grpc_index(port)
        return self._stub.SetPortDelay(
            ltc2000_cfg_pb2.PortDelaySetting(port=index, value=value)
        ).value
