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

from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import detector_emulator_pb2_grpc
from . import servicehubcontrol
from .servicehubutils import servicehub_call


class DetectorEmulator:
    def __init__(self, connection, endpoint):
        self._stub = detector_emulator_pb2_grpc.DetectorEmulatorServiceStub(
            connection.get_channel()
        )
        self.connection = connection
        hubcontrol = servicehubcontrol.ServicehubControl(connection)
        self.index = hubcontrol.get_endpoint_index_of_plugin(
            "DetectorEmulatorPlugin", endpoint
        )

    def get_index(self):
        return self.index

    @servicehub_call(errormsg="failed", tries=1)
    def set_count_rate(self, count_rate):
        # rate = (count_rate * 2^30 * 2e-9)/4 =  0.536870912*count_rate
        self._stub.SetCountRate(
            datatypes_pb2.IndexedDouble(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                value=count_rate,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_pulse_attenuation(self, attenuation):
        self._stub.SetPulseAttenuation(
            datatypes_pb2.IndexedInt(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                value=attenuation,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_tau_eff(self, tau_eff):
        self._stub.SetTauEff(
            datatypes_pb2.IndexedDouble(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                value=tau_eff,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_squid_frequency(self, squid_frequency):
        # (2**32 * (c_squid_frequency))/(1000000000);

        self._stub.SetSquidFrequency(
            datatypes_pb2.IndexedDouble(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                value=squid_frequency,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_stimulation_frequency(self, stimulation_frequency):
        # (2**32 * (c_squid_frequency))/(1000000000);

        self._stub.SetStimulationFrequency(
            datatypes_pb2.IndexedDouble(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                value=stimulation_frequency,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_enable_pulse(self, enable):
        self._stub.SetEnablePulse(
            datatypes_pb2.IndexedBool(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                value=enable,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_enable_pulse(self):
        return self._stub.GetEnablePulse(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_enable_random(self, enable):
        self._stub.SetEnableRandom(
            datatypes_pb2.IndexedBool(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                value=enable,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_enable_random(self):
        return self._stub.GetEnablePulse(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_enable_squid(self, enable):
        self._stub.SetEnableSquid(
            datatypes_pb2.IndexedBool(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                value=enable,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_enable_squid(self):
        return self._stub.GetEnablePulse(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_enable_stimulation(self, enable):
        self._stub.SetEnableStimulation(
            datatypes_pb2.IndexedBool(
                index=datatypes_pb2.EndpointIndex(value=self.index),
                value=enable,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_enable_stimulation(self):
        return self._stub.GetEnablePulse(
            datatypes_pb2.EndpointIndex(value=self.index)
        ).value
