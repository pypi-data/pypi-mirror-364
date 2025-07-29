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
Convenient wrapper for protobuf generated python code for LMK04208
"""
from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import lmk04208_pb2_grpc

from . import servicehubcontrol
from .servicehubutils import servicehub_call


class LMK04208:
    """
    The LMK04208 is a high performance clock conditioner with superior clock jitter cleaning,
    generation, and distribution with advanced features to meet next generation system
    requirements. The dual loop PLLatinum™ architecture is capable of 111 fs, RMS jitter (12 kHz
    to 20 MHz) using a low-noise VCXO module or sub-200 fs rms jitter (12 kHz to 20 MHz) using a
    low cost external crystal and varactor diode. (From datasheet)

    While the IPE servicehub plugin does not contain detailled control of functionalities yet, it
    allows the user to load a new configuration without needing to reboot the platform and changing
    the device-tree or initialization scripts.

    Further details can be found at https://www.ti.com/lit/ds/symlink/lmk04208.pdf
    """

    def __init__(self, connection, endpoint: str, plugin_name="LMK04208Plugin"):
        self.connection = connection
        self._stub = lmk04208_pb2_grpc.LMK04208ServiceStub(connection.get_channel())
        self.index = servicehubcontrol.ServicehubControl(
            connection
        ).get_endpoint_index_of_plugin(plugin_name, endpoint)
        self._ep_index = datatypes_pb2.EndpointIndex(value=self.index)

    def get_index(self):
        """
        Get index of endpoint determined by servicehub control
        """
        return self.index

    @servicehub_call(errormsg="failed", tries=1)
    def init(self, path: str = None):
        """
        Initialize with a full configuration. See lmk04298.proto for required format.
        If path is None or an empty string instead, the original configuration either
        read from device-tree or kernel-driver header file will be reloaded instead.

        :param string path: Path to file containing init config on the platform.
        """
        if path in (None, ""):
            self._stub.InitFromDT(self._ep_index)
        else:
            self._stub.InitFromFile(
                datatypes_pb2.IndexedString(index=self._ep_index, value=path)
            )

    # Do *not* make register accessable here, but add functionalities (once implemented in SH)
