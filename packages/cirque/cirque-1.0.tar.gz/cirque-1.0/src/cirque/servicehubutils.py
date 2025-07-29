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
The servicehubutils contain all the infrastructure needed for the communication
with the platform. It allows opening a grpc channel and control it.
"""

from functools import partial

import grpc
from wrapt import decorator


class FPGAConnection:
    """
    The FPGAConnection is the connection point between user frontend and platform
    It opens the connection for all the modules that offer a communication interface

    Args:
        ip(str): ip address of the platform
        port(int): port of the platform
    """

    def __init__(self, **kwargs):
        self.ip_address = kwargs.get("ip", None) or "0.0.0.0"
        self.port = kwargs.get("port", None) or 50058
        self.grpc_connection = f"{self.ip_address}:{self.port}"
        self._channel = None
        self._open = False
        self.open()

    def open(self):
        """
        Opens a grpc connection to the platform
        """
        if self._channel is not None:
            self.close()
        self._channel = grpc.insecure_channel(self.grpc_connection)
        print(
            "Opened GRPC connection to " + str(self.ip_address) + ":" + str(self.port)
        )
        self._open = True

    def close(self):
        """
        Closes the connection to the platform
        """
        self._channel.close()
        del self._channel
        self._channel = None  # type: grpc.Channel
        print(
            "Closed GRPC connection to " + str(self.ip_address) + ":" + str(self.port)
        )
        self._open = False

    def get_channel(self):
        """
        Returns the open channel to the platform.
        Raises an exception, when no connection is open.
        """
        if not self._open:
            raise ConnectionError("Connection not open")
        return self._channel

    def is_open(self):
        """
        Returns, whether a connection to a platform is open
        """
        return self._open


def servicehub_call(call=None, errormsg="Error executing command", tries=5):
    """
    Decorator for methods with grpc-commands. Checks, whether the connection operates successfully
    and informs the user about issues

    Args:
        errormsg(str): Message to be displayed in case of problems
        tries(int): Number of tries before the error message is shown
    """
    if call is None:
        return partial(servicehub_call, errormsg=errormsg, tries=tries)

    @decorator
    def call_wrapper(call, instance, args, kwargs):
        if instance is None:
            instance = args[0]
        if instance.connection.is_open() is not True:
            print("No open connection")
        else:
            for i in range(0, tries):
                try:
                    return call(*args, **kwargs)

                except grpc.RpcError as error:
                    if i == tries - 1:
                        raise ConnectionError(
                            f"{errormsg}. Error message: {error}"
                        ) from error

    return call_wrapper(call)
