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
This module is responsible for communicating with the RFdc IP core from AMD/Xilinx
The ip core can be implemented on RFSoC devices and controlles the ADC and DACs
"""
from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import rfdc_pb2, rfdc_pb2_grpc

from .servicehubutils import servicehub_call


class RFdc:
    """
    The RFdc IP core can be configured in various ways and offers a lot of commands
    for customization. Most of the important ones are implemented in this wrapper
    and allow the user to control the RFdc within this framework.

    Instantiation of the endpoint is performed by passing the connection
    """

    def __init__(self, connection, endpoint_index=0):
        self.connection = connection
        self._stub = rfdc_pb2_grpc.RFdcServiceStub(connection.get_channel())
        self.ep_index = endpoint_index

    @servicehub_call(errormsg="failed", tries=1)
    def get_block_status(self, tile, block, converter_type):
        block_status = self._stub.GetBlockStatus(
            rfdc_pb2.ConverterIndex(
                tile=tile, block=block, converter_type=converter_type
            )
        )
        print(f"Frequency: {block_status.frequency}")
        print(f"Digital: {block_status.digitalstatus}")
        print(f"Analog: {block_status.analogstatus}")
        print(f"Clock: {block_status.clockstatus}")
        print(f"FIFO Flags enabled: {block_status.fifoflagsenabled}")
        print(f"FIFO Flags asserted: {block_status.fifoflagsasserted}")

    @servicehub_call(errormsg="failed", tries=1)
    def get_mixer_frequency(self, tile, block, converter_type):
        return self._stub.GetMixerFrequency(
            rfdc_pb2.ConverterIndex(
                tile=tile, block=block, converter_type=converter_type
            )
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_mixer_frequency(self, tile, block, converter_type, frequency):
        return self._stub.SetMixerFrequency(
            rfdc_pb2.Phase(
                index=rfdc_pb2.ConverterIndex(
                    tile=tile, block=block, converter_type=converter_type
                ),
                value=frequency,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def set_threshold_sticky_clear(self, tile, block, converter_type, threshold):
        return self._stub.SetThresholdStickyClear(
            rfdc_pb2.ThresholdToUpdate(
                index=rfdc_pb2.ConverterIndex(
                    tile=tile, block=block, converter_type=converter_type
                ),
                threshold=threshold,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def startup_tile(self, tile, converter_type):
        return self._stub.StartUp(
            rfdc_pb2.TileIndex(tile=tile, converter_type=converter_type)
        )

    @servicehub_call(errormsg="failed", tries=1)
    def shutdown_tile(self, tile, converter_type):
        return self._stub.Shutdown(
            rfdc_pb2.TileIndex(tile=tile, converter_type=converter_type)
        )

    @servicehub_call(errormsg="failed", tries=1)
    def reset_tile(self, tile, converter_type):
        return self._stub.Reset(
            rfdc_pb2.TileIndex(tile=tile, converter_type=converter_type)
        )

    @servicehub_call(errormsg="failed", tries=1)
    def interrupt_clear(self, tile, block, converter_type, intrmask):
        return self._stub.InterruptClear(
            rfdc_pb2.InterruptSettings(
                index=rfdc_pb2.ConverterIndex(
                    tile=tile, block=block, converter_type=converter_type
                ),
                intrmask=intrmask,
            )
        )

    # ToDo: Request Message should be ConverterIndex I guess
    @servicehub_call(errormsg="failed", tries=1)
    def get_interrupt_status(self, tile, block, converter_type, intrmask):
        return self._stub.GetInterruptStatus(
            rfdc_pb2.InterruptSettings(
                index=rfdc_pb2.ConverterIndex(
                    tile=tile, block=block, converter_type=converter_type
                ),
                intrmask=intrmask,
            )
        ).intrmask

    @servicehub_call(errormsg="failed", tries=1)
    def get_phase(self, tile, block, converter_type):
        return self._stub.GetPhase(
            rfdc_pb2.ConverterIndex(
                tile=tile, block=block, converter_type=converter_type
            )
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_phase(self, tile, block, converter_type, phase):
        return self._stub.SetPhase(
            rfdc_pb2.Phase(
                index=rfdc_pb2.ConverterIndex(
                    tile=tile, block=block, converter_type=converter_type
                ),
                value=phase,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_nyquist_zone(self, tile, block, converter_type):
        return self._stub.GetNyquistZone(
            rfdc_pb2.ConverterIndex(
                tile=tile, block=block, converter_type=converter_type
            )
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_nyquist_zone(self, tile, block, converter_type, frequency):
        return self._stub.SetNyquistZone(
            rfdc_pb2.Frequency(
                index=rfdc_pb2.ConverterIndex(
                    tile=tile, block=block, converter_type=converter_type
                ),
                value=frequency,
            )
        )

    # ToDo: Rename to SetMixerMode, isn't ConverterIndex needed?
    @servicehub_call(errormsg="failed", tries=1)
    def set_mixer_settings(self, tile, block, converter_type, mode, frequency):
        return self._stub.SetMixerSettings(
            rfdc_pb2.MixerSettings(
                index=rfdc_pb2.ConverterIndex(
                    tile=tile, block=block, converter_type=converter_type
                ),
                mode=mode,
                frequency=frequency,
            )
        )

    # ToDo: Why not use enum MixerMode as return message
    @servicehub_call(errormsg="failed", tries=1)
    def get_mixer_mode(self, tile, block, converter_type):
        return self._stub.GetMixerMode(
            rfdc_pb2.ConverterIndex(
                tile=tile, block=block, converter_type=converter_type
            )
        ).mode

    # ToDo: Request and receive messages contain too many fields
    @servicehub_call(errormsg="failed", tries=1)
    def get_data_type(self, tile, block, converter_type):
        return self._stub.GetDataType(
            rfdc_pb2.ConverterIndex(
                tile=tile, block=block, converter_type=converter_type
            )
        ).type

    @servicehub_call(errormsg="failed", tries=1)
    def get_interpolation(self, tile, block, converter_type):
        return self._stub.GetInterpolation(
            rfdc_pb2.ConverterIndex(
                tile=tile, block=block, converter_type=converter_type
            )
        ).factor

    @servicehub_call(errormsg="failed", tries=1)
    def set_interpolation(self, tile, block, converter_type, factor):
        return self._stub.SetInterpolation(
            rfdc_pb2.Interpolation(
                index=rfdc_pb2.ConverterIndex(
                    tile=tile, block=block, converter_type=converter_type
                ),
                factor=factor,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_dac_output_current(self, tile, block, converter_type):
        return self._stub.GetOutputCurrent(
            rfdc_pb2.ConverterIndex(
                tile=tile, block=block, converter_type=converter_type
            )
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_dac_output_current(self, tile, block, converter_type, output_current):
        return self._stub.SetOutputCurrent(
            rfdc_pb2.IndexedDouble(
                index=rfdc_pb2.ConverterIndex(
                    tile=tile, block=block, converter_type=converter_type
                ),
                value=output_current,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def get_digital_attenuation(self, tile, block, converter_type):
        return self._stub.GetDigitalAttenuation(
            rfdc_pb2.ConverterIndex(
                tile=tile, block=block, converter_type=converter_type
            )
        ).value

    @servicehub_call(errormsg="failed", tries=1)
    def set_digital_attenuation(self, tile, block, converter_type, attenuation):
        return self._stub.SetDigitalAttenuation(
            rfdc_pb2.IndexedDouble(
                index=rfdc_pb2.ConverterIndex(
                    tile=tile, block=block, converter_type=converter_type
                ),
                value=attenuation,
            )
        )

    @servicehub_call(errormsg="failed", tries=1)
    def report_status(self):
        return self._stub.ReportStatus(datatypes_pb2.Empty()).report
