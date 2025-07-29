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
    The ServicehubControl gives general information about the Servicehub and the instantiated plugins.
    On our MPSoC Platforms, the Servicehub is responsible for managing the communication between the users
    and the programmable logic.
    The individual modules are instantiated as endpoints into the servicehub and can be called via plugins.
"""

from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import servicehubcontrol_pb2, servicehubcontrol_pb2_grpc

from .servicehubutils import servicehub_call


class ServicehubControl:
    """
    The ServicehubControl class offers several calls to read the current status of the platform
    Generate the interface by passing the connection.
    """

    def __init__(self, connection):
        self.connection = connection
        self._stub = servicehubcontrol_pb2_grpc.ServicehubControlServiceStub(
            connection.get_channel()
        )

    @servicehub_call(errormsg="failed", tries=1)
    def load_new_config_file(self, config_name: str):
        """
        Shutdown and restart grpc server with new config file found under the given name.
        Will not shutdown or restart on failure to read and parse config file.
        """
        self._stub.LoadNewConfigFile(datatypes_pb2.String(value=config_name))

    @servicehub_call(errormsg="failed", tries=1)
    def load_new_config(self, config: str):
        """
        Shutdown and restart grpc server with new config passed as a string.
        Will not shutdown or restart on failure to parse config.
        """
        self._stub.LoadNewConfig(datatypes_pb2.String(value=config))

    @servicehub_call(errormsg="failed", tries=1)
    def reload(self):
        """
        Issues a restart of the servicehub.
        This could help of the platform is stuck in undefined behavior.
        """
        self._stub.Reload(datatypes_pb2.Empty())

    @servicehub_call(errormsg="failed", tries=1)
    def reboot(self):
        """
        Issues a soft reboot of the whole platform
        The servicehub is automatically restarted once the platform is booted
        """
        self._stub.Reboot(datatypes_pb2.Empty())

    @servicehub_call(errormsg="failed", tries=1)
    def is_alive(self):
        """
        IsAlive is a dummy call that tries communicating with the platform without exchanging data.
        In case no return message arrives, the platform is stuck and a reboot is necessary.
        """
        self._stub.IsAlive(datatypes_pb2.Empty())

    @servicehub_call(errormsg="failed", tries=1)
    def get_servicehub_version(self):
        """
        Returns the current version of the servicehub that is running on the platform.
        For reliable communication, make sure that the version of the servicehub fits to the version of the user client

        Returns:
            String
        """
        return self._stub.GetServiceHubVersion(datatypes_pb2.Empty()).servicehub_version

    @servicehub_call(errormsg="failed", tries=1)
    def get_plugin_list(self):
        """
        Returns a list of all plugins that are instantiated on the platform.
        The user is able to communicate with each of these plugins by using the API calls of the respective classes.

        Returns:
            String[]
        """
        return self._stub.GetPluginList(datatypes_pb2.Empty()).str

    @servicehub_call(errormsg="failed", tries=1)
    def get_plugin_version(self, plugin):
        """
        Returns the version of a specific plugin.
        The version of the plugin needs to be compatible with the proto version used by the client application

        Args:
            plugin(String): Defines the plugin, a version is required for

        Returns:
            String
        """
        return self._stub.GetPluginVersion(
            servicehubcontrol_pb2.String(str=plugin)
        ).proto_version

    @servicehub_call(errormsg="failed", tries=1)
    def get_endpoints_of_plugin(self, plugin):
        """
        GetEndpointsOfPlugin returns a list of all endpoint names of a specific plugin.
        The user is able to communicate with the individual endpoints by instantiating
        an object of the respective class and using the API calls.

        Args:
            plugin(String): The name of the module, for which the endpoints are required for

        Returns:
            String[]
        """
        return self._stub.GetEndpointsOfPlugin(
            servicehubcontrol_pb2.String(str=plugin)
        ).str

    @servicehub_call(errormsg="failed", tries=1)
    def get_endpoint_index_of_plugin(self, plugin, endpoint):
        """
        GetEndpointIndexOfPlugin returns the index of one specific endpoint within the plugin.
        The index is needed for instantiation of the endpoint.

        Args:
            plugin (String): Name of the plugin
            endpoint (String): Name of the endpoint
        """
        return self._stub.GetEndpointIndexOfPlugin(
            servicehubcontrol_pb2.EndpointIndexRequest(
                plugin_name=plugin, endpoint_name=endpoint
            )
        ).val

    @servicehub_call(errormsg="failed", tries=1)
    def dump_coverage_data(self):
        """
        Returns string containing coverage data
        """
        return self._stub.DumpCoverageData(datatypes_pb2.Empty()).str
