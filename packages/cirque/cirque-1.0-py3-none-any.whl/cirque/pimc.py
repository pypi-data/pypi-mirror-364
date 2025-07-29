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
The PIMC (Platform Information and Management Core) is a module used
for supervision and control of the platform.
It allows the users to get information about the current status of the platform and
enables several fault recovery mechanisms.
"""

from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import pimc_pb2_grpc

from .servicehubutils import servicehub_call


class PIMC:
    """
    The PIMC class is responsible for the communication with its
    specific Plugin on the platform. Generate the interface to a new endpoint
    by passing the connection and the endpoint name.
    """

    def __init__(self, connection):
        self.connection = connection
        self._stub = pimc_pb2_grpc.PIMCServiceStub(connection.get_channel())

    @servicehub_call(errormsg="failed", tries=1)
    def get_platform_ready(self):
        """
        get_platform_ready returns information,
        whether the platform has correctly been initialized.
        The readyness of the platform depends on several factors, that all have to be fulfilled.
        The requrirements for a platform to be ready are:

        - All clocks connected to the PIMC have to be in the valid range.
          Status of the clocks can be monitored by calling
          :func:`~firmware_modules.pimc.PIMC.GetClockInfo`
        - The state of the status inputs needs to be equal as stated in the ready_state
        - The busy signal of the platform needs to be zero.
          State of the busy signal can be monitored by calling
          :func:`~firmware_modules.pimc.PIMC.GetBusy`
        - The software-ready flag needs to be activated.
          See :func:`~firmware_modules.pimc.PIMC.SetSWReady`.
        - The platform has to be resetted at least once.
          See :func:`~firmware_modules.pimc.PIMC.GetResetDone`.

        Returns:
            Bool
        """
        return self._stub.GetReady(datatypes_pb2.Empty()).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_reset(self):
        """
        This reset is given to the IP cores within the FPGA side.
        The cores need to be connected to PIMC rst out.
        Some cores will go in an async state to its userspace/kernel driver
        if the reset is issued. Thus not working as expected.
        """
        self._stub.SetReset(datatypes_pb2.Empty())

    @servicehub_call(errormsg="failed", tries=1)
    def get_busy(self):
        """
        Returns whether the system is currently busy

        Returns:
            Bool
        """
        return self._stub.GetBusy(datatypes_pb2.Empty()).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_sw_ready(self):
        """
        Returns the software ready flag of the system.
        This flag is required for the system to change into ready state.
        """
        return self._stub.GetSWReady(datatypes_pb2.Empty()).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_sw_ready(self):
        """
        Sets the software ready flag of the system.
        This flag is required for the system to change into ready state.
        """
        self._stub.SetSWReady(datatypes_pb2.Empty())

    @servicehub_call(errormsg="failed", tries=1)
    def set_reset_done(self):
        """
        Sets the flag that a reset has been performed.
        This flag is requred for the system to change into ready state.
        """
        self._stub.SetResetDone(datatypes_pb2.Empty())

    @servicehub_call(errormsg="failed", tries=1)
    def get_reset_done(self):
        """
        Returns whether a reset has already been performed.

        Returns:
            Bool
        """
        return self._stub.GetResetDone(datatypes_pb2.Empty()).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_chip_version(self):
        """
        Returns the version of the current chip firmware.
        The version is iterated on major changes.
        Take the chip version into account for checking compatibility.

        Returns:
            Int
        """
        return self._stub.GetChipVersion(datatypes_pb2.Empty()).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_module_chip_version(self):
        """
        Returns the version of the pimc core module within the programmable logic.

        Returns:
            Int
        """
        return self._stub.GetModuleChipVersion(datatypes_pb2.Empty()).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_info_string(self):
        """
        Dumps all information about the core as a string.
        The string contains the following information:

        - ID of the PIMC
        - Version of the PIMC
        - ID of the firmware project
        - ID of the hardware platform
        - BuildRevision
        - Timestamp of the build
        - Name of the project
        - Name of the platform
        - CommitID of the build

        Returns:
            String
        """
        return self._stub.GetInfoString(datatypes_pb2.Empty()).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_all_clocks_valid(self):
        """
        Returns true if all clocks are active and their frequency is in the valid range.
        This is a requirement for the platform to get ready.

        For more detailed information, check :func:`~firmware_modules.pimc.PIMC.GetClocksInfo`

        Returns:
            Bool
        """
        return self._stub.GetAllClocksValid(datatypes_pb2.Empty()).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_clocks_info(self):
        """
        Returns more detailed information about the clocks that are supervised by the pimc.
        Active clocks and valid frequencies are a requirement for the platform
        to change to ready state.
        For a more concise information see :func:`~firmware_modules.pimc.PIMC.GetAllClocksValid`

        Returns:
            String
        """
        return self._stub.GetClocksInfo(datatypes_pb2.Empty()).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_status_inputs(self):
        """
        The pimc is able to monitor several input bits, that need to have a certain value
        in order to allow the platform start operation.
        This call returns the current values of the connected signals.
        The required states of the signals can be checked via
        :func:`~firmware_modules.pimc.PIMC.GetReadyState`
        Individual signals can also be neglected by changing the ready mask.
        The mask can be observed via :func:`~firmware_modules.pimc.PIMC.GetReadyMask`

        Returns:
            String
        """
        return self._stub.GetStatusInputs(datatypes_pb2.Empty()).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_ready_mask(self):
        """
        In order to allow the platform to change into ready state,
        all status inputs need to be ready.
        By means of the ready mask, individual signal can be discarded,
        so that they are not considered anymore by the PIMC.
        This call returns the current mask.

        Returns:
            String
        """
        return self._stub.GetReadyMask(datatypes_pb2.Empty()).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_ready_state(self):
        """
        The ready state defines, which values the individual input values need to have
        in order to allow the platform to change into ready mode

        Returns:
            String
        """
        return self._stub.GetReadyState(datatypes_pb2.Empty()).value
