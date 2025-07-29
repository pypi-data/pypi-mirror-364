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
The DMAController is our custom implementation for a direct memory access solution.
The DMA allows storing data direclty from the programmable logic into the DDR
without using the CPU.
This leads to faster and more performant read- and write operations.
While the write access is configured and done automatically,
the user is responsible for reading the data and transferring the streams to the backend.
This API offers several methods for transferring the data,
allowing the users to perform post processing.
"""


import signal
from concurrent.futures import ThreadPoolExecutor
from time import sleep

import grpc
import numpy as np
from tqdm.notebook import tqdm, trange
from cirque.packages.grpc import datatypes_pb2
from cirque.packages.grpc import dmacontroller_pb2, dmacontroller_pb2_grpc

from .servicehubutils import servicehub_call


class DMAController:
    """
    The DMAController class is responsible for the communication with its
    specific Plugin on the platform. Generate the interface to a new endpoint
    by passing the connection and the endpoint name.
    """

    def __init__(self, connection, endpoint_index=0, **kwargs):
        self.connection = connection
        self._stub = dmacontroller_pb2_grpc.DMAControllerServiceStub(
            connection.get_channel()
        )
        self.ep_index = datatypes_pb2.EndpointIndex(value=endpoint_index)
        self.endpoint_index = endpoint_index
        self.total_bytes_per_sample = self.get_bytes_per_sample()
        self.dtype = self.eval_dtype(**kwargs)
        self.chains = self.get_parallel_streams()
        print(f"[DMAController] number of parallel streams: {str(self.chains)}")
        print(f"[DMAController] set dtype to {self.dtype.name}")

    @servicehub_call(errormsg="failed", tries=1)
    def eval_dtype(self, data_type="i", byte_order=">"):
        """Define the numpy data type to interpret the incoming byte stream with.
        see https://numpy.org/doc/stable/reference/arrays.dtypes.html
        """
        self.bytes_per_sample = 2
        return np.dtype(f"{byte_order:.1}{data_type:.1}{self.bytes_per_sample:d}")

    def compute_samples_per_sample(self, data_type):
        """
        Returns information about the number of parallel samples within one data package.
        This value is computed by dividing the total amount of bits per package by the width
        of the selected data type.

        Args:
            data_type: {numpy data type} Specifies the desired data type and extracts bit width
        """
        return int(self.total_bytes_per_sample / (self.chains * data_type.nbytes))

    def convert_iq_to_complex(self, data):
        """
        Converts interleaved I and Q data to a complex64 numpy array
        Source: https://stackoverflow.com/a/19642735

        Args:
            data: interleaved I and Q data
        """
        cdata = np.empty(len(data) // 2, dtype=np.complex64)
        cdata.real = data[0::2]
        cdata.imag = data[1::2]
        return cdata

    def deinterleave(self, interleaved_data, channel_count):
        """
        returns deinterleaved data as numpy 2d-array of shape
        (channel_count, len(interleaved_data)//channel_count)
        """
        sample_count = len(interleaved_data)

        if sample_count % channel_count != 0:
            raise IndexError("sample count must be multiple of channel count")

        deinterleaved = np.zeros(
            (channel_count, sample_count // channel_count), dtype=self.dtype
        )

        for ch_idx in range(channel_count):
            deinterleaved[ch_idx] = interleaved_data[ch_idx::channel_count]

        return deinterleaved

    @servicehub_call(errormsg="failed", tries=1)
    def get_bytes_per_sample(self):
        """
        returns the number of bytes per sample
        """
        return self._stub.GetBytesPerSample(self.ep_index).value

    @servicehub_call(errormsg="failed", tries=1)
    def get_parallel_streams(self):
        """
        returns the amount of parallel streams stored by the DMA Controller
        """
        parallel_streams = self._stub.GetParallelStreams(
            datatypes_pb2.EndpointIndex(value=self.endpoint_index)
        ).value
        if parallel_streams == 0:
            parallel_streams = 1
        return parallel_streams

    @servicehub_call(errormsg="failed", tries=1)
    def snapshot(
        self,
        sample_count,
        channels=None,
        subchains=None,
        sample_rate=0,
        timeout=0,
        package_mode=0,
        deinterleave=False,
        dtype=None,
        is_iq=False,
    ):
        """
        requests a grpc stream of acquired data and converts it to a numpy array.

        Args:
            sample_count    : total sample count for all channels
            channels        : list of channel indices
            subchains       : list of sub chain indices
            sample_rate     : approximate data rate in samples per second
                              (used to adapt the timeout value for slow data rates)
            timeout         : timeout in seconds to wait for stochastic data
            package_mode    : {boolean} if true, event data will be forwarded
            deinterleave    : {boolean} if true, the data of the channels will be deinterleaved,
                              returning a numpy-2d-array with the data seperated for each channel.
            dtype           : {numpy.dtype} change the data type to interpret the data with.
                              If None the default data type specified in the constructor is used.
            is_iq           : {boolean} interpret data as IQ-values and return the complex value.
                              Note: the itemsize of the dtype needs to be divided by 2.
        """
        # preallocate memory
        if dtype is None:
            dtype = self.dtype

        if channels is None:
            channels = []

        if subchains is None:
            subchains = []

        # elif dtype.itemsize * (1 + 1 * int(is_iq)) > self.bytes_per_sample:
        #    print("Warning: bytesize of requested data type exceeds word size of data.")

        samples_per_sample = self.compute_samples_per_sample(dtype)
        if samples_per_sample == 0:
            raise Exception("Error, system calculated 0 samples per block!")
        data = np.zeros(sample_count * samples_per_sample * self.chains, dtype=dtype)

        stream_request = dmacontroller_pb2.StreamRequest(
            index=self.ep_index,
            count=sample_count,
            channels=channels,
            subChains=subchains,
            sampleRate=sample_rate,
            timeout=timeout,
            packageMode=package_mode,
        )

        stream = self._stub.Snapshot(stream_request)

        # a function is needed to issue a stream.cancel() with a keyboard interrupt
        def cancel_stream(unused_sig, unused_frame):
            stream.cancel()

        signal.signal(signal.SIGINT, cancel_stream)

        oi = (
            0  # current offset index needed since byte stream is transmitted block wise
        )
        try:
            for block in stream:
                n = len(block.value) // dtype.itemsize
                data[oi : oi + n] = np.frombuffer(block.value, dtype=dtype)
                oi += n
        except (IndexError, ValueError) as e:
            self._handle_exception(e)

        pkg_loss = self.check_package_loss(stream)

        if is_iq:
            data = self.convert_iq_to_complex(data)
        if deinterleave:
            data = self.deinterleave(data, len(channels))
        return data, pkg_loss

    @servicehub_call(errormsg="failed", tries=1)
    def file_snapshot(
        self,
        sample_count,
        channels=None,
        subchains=None,
        sample_rate=0,
        timeout=0,
        package_mode=0,
        file_name="FileSnapshot.bin",
        sub_path="",
        disk_type="SSD",
    ):
        """
        requests the dma controller to write the acquired data to a file on the
        remote platform.

        Args:
            sample_count    : total sample count for all channels
            channels        : list of channel indices
            subchains       : list of sub chain indices
            package_mode    : {boolean} if true, event data will be forwarded
            sample_rate     : approximate data rate in samples per second
                              (used to adapt the timeout value for slow data rates)
            timeout         : timeout in seconds to wait for stochastic data
            file_name       : target file name
            sub_path        : sub path of the target file on the platform
            disk_type       : target memory device ('SD', 'SSD', 'USB', 'RAMDISK')

        Note:
            There is no check if the selected device is mounted properly
        """

        if channels is None:
            channels = []

        if subchains is None:
            subchains = []

        stream_request = dmacontroller_pb2.StreamRequest(
            index=self.ep_index,
            count=sample_count,
            channels=channels,
            subChains=subchains,
            sampleRate=sample_rate,
            timeout=timeout,
            packageMode=package_mode,
        )

        disk = dmacontroller_pb2.DiskType.Value(disk_type)
        file_stream_request = dmacontroller_pb2.FileStreamRequest(
            streamrequest=stream_request,
            FileName=file_name,
            SubPath=sub_path,
            DiskType=disk,
        )

        if sample_rate > 0:
            with ThreadPoolExecutor(max_workers=2) as executor:
                progress_bar_thread = executor.submit(
                    self._pseudo_progress_bar, sample_count, sample_rate
                )
                file_stream_thread = executor.submit(
                    self._stub.FileSnapshot.with_call, file_stream_request
                )
                call = file_stream_thread.result()
                progress_bar_thread.result()

        ## the future instance of FileSnapshot seems to cancel the call too early
        else:
            call = self._stub.FileSnapshot.with_call(file_stream_request)

        # a function is needed to issue a stream.cancel() with a keyboard interrupt
        def cancel_call(unused_sig, unused_frame):
            print("cancelling")
            call.cancel()

        signal.signal(signal.SIGINT, cancel_call)
        return self.check_package_loss(call[1])

    @servicehub_call(errormsg="failed", tries=1)
    def continuous_file_stream(
        self,
        channels=None,
        subchains=None,
        sample_rate=0,
        timeout=0,
        package_mode=0,
        file_name="FileSnapshot.bin",
        sub_path="",
        disk_type="SSD",
    ):
        """
        requests the dma controller to write the acquired data to a file on the
        remote platform.

        Args:
            channels        : list of channel indices
            subchains       : list of sub chain indices
            sample_rate     : approximate data rate in samples per second
                              (used to adapt the timeout value for slow data rates)
            timeout         : timeout in seconds to wait for stochastic data
            file_name       : target file name
            sub_path        : sub path of the target file on the platform
            disk_type       : target memory device ('SD', 'SSD', 'USB', 'RAMDISK')

        Note:
            There is no check if the selected device is mounted properly
        """

        if channels is None:
            channels = []

        if subchains is None:
            subchains = []

        stream_request = dmacontroller_pb2.StreamRequest(
            index=self.ep_index,
            count=0,  # will be ignored
            channels=channels,
            subChains=subchains,
            sampleRate=sample_rate,
            timeout=timeout,
            packageMode=package_mode,
        )
        disk = dmacontroller_pb2.DiskType.Value(disk_type)
        file_stream_request = dmacontroller_pb2.FileStreamRequest(
            streamrequest=stream_request,
            FileName=file_name,
            SubPath=sub_path,
            DiskType=disk,
        )

        call = self._stub.ContinuousFileStream.with_call(file_stream_request)

        # a function is needed to issue a stream.cancel() with a keyboard interrupt
        def cancel_call(unused_sig, unused_frame):
            call.cancel()

        signal.signal(signal.SIGINT, cancel_call)

        try:
            self.check_package_loss(call[1])
        except Exception as e:
            self._handle_exception(e)

    def _pseudo_progress_bar(self, sample_count, sample_rate):
        """
        Returns True after waiting for the specific time needed to acquire
        1/100 of the total sample count

        Args:
            sample_count(int): Total amount of samples to be acquired
            sample_rate(float): Sampling frequency on the platform
        """
        bins = 100
        bin_wait_time_s = sample_count / bins / sample_rate
        for _ in trange(bins, desc=None):
            sleep(bin_wait_time_s)
        return True

    def _stream_to_file(self, stream, file_path, file_size=None):
        """
        Stores the data stream acquired via grpc in a file on the local machine

        Args:
            stream(): Data stream from the platform
            file_path(str): Path on the local machine, where the file is located
        """
        file_name = file_path.split("/")[-1]
        with tqdm.wrapattr(
            open(file_path, "wb+"), "write", total=file_size, desc=file_name
        ) as f:
            try:
                for d in stream:
                    f.write(bytes(d.value))
                    f.flush()
            except OSError as e:
                self._handle_exception(e)

    @servicehub_call(errormsg="failed", tries=1)
    def download(
        self, file_name, remote_subpath, target_path, disk_type="SSD", file_size=None
    ):
        """
        Downloads a file previously recorded with the FileSnapshot command

        Args:
            file_name(str): name of the file to be downloaded
            remote_subpath(str): path on the platform, where the file is located
            target_path(str): path on the local machine, where the file should be stored
        """
        file_request = dmacontroller_pb2.FileRequest(
            FileName=file_name,
            SubPath=remote_subpath,
            DiskType=dmacontroller_pb2.DiskType.Value(disk_type),
        )

        stream = self._stub.FileDownload(file_request)

        local_file_path = target_path + "/" + file_name

        self._stream_to_file(stream, local_file_path, file_size)

    @servicehub_call(errormsg="failed", tries=1)
    def continuous_grpc_stream_to_file(
        self,
        channels,
        subchains,
        file_name,
        target_path,
        sample_rate=0,
        timeout=0,
        package_mode=0,
    ):
        """
        Requests a grpc stream of acquired data and saves it to a local file

        Args:
            channels        : list of channel indices
            subchains       : list of sub chain indices
            sample_rate     : approximate data rate in samples per second
                              (used to adapt the timeout value for slow data rates)
            timeout         : timeout in seconds to wait for stochastic data
            file_name       : file name
            local_path      : path of target file directory
        """

        stream_request = dmacontroller_pb2.StreamRequest(
            index=self.ep_index,
            count=0,  # value will be ignored
            channels=channels,
            subChains=subchains,
            sampleRate=sample_rate,
            timeout=timeout,
            packageMode=package_mode,
        )

        stream = self._stub.ContinuousStream(stream_request)

        # a function is needed to issue a stream.cancel() with a keyboard interrupt
        def cancel_stream(unused_sig, unused_frame):
            stream.cancel()

        signal.signal(signal.SIGINT, cancel_stream)

        local_file_path = target_path + "/" + file_name

        self._stream_to_file(stream, local_file_path, None)

        return local_file_path

    def limited_stream_to_file(
        self,
        sample_count,
        channels,
        subchains,
        file_name,
        target_path,
        sample_rate=0,
        timeout=0,
        package_mode=0,
    ):
        """
        Requests a grpc stream of acquired data and saves it to a local file

        Args:
            sample_count    : total sample count for all channels
            channels        : list of channel indices
            subchains       : list of sub chain indices
            sample_rate     : approximate data rate in samples per second
                              (used to adapt the timeout value for slow data rates)
            timeout         : timeout in seconds to wait for stochastic data
            file_name       : file name
            local_path      : path of target file directory
        """
        stream_request = dmacontroller_pb2.StreamRequest(
            index=self.ep_index,
            count=sample_count,
            channels=channels,
            subChains=subchains,
            sampleRate=sample_rate,
            timeout=timeout,
            packageMode=package_mode,
        )

        stream = self._stub.Snapshot(stream_request)

        # a function is needed to issue a stream.cancel() with a keyboard interrupt
        def cancel_stream(unused_sig, unused_frame):
            stream.cancel()

        signal.signal(signal.SIGINT, cancel_stream)

        local_file_path = target_path + "/" + file_name
        self._stream_to_file(
            stream, local_file_path, sample_count * self._stub.GetBytesPerSample()
        )

        return self.check_package_loss(stream)

    def _handle_exception(self, e):
        """ """
        if str(type(e)) == "<class 'grpc._channel._MultiThreadedRendezvous'>":
            print("gRPC Exception: " + e.details())
        elif isinstance(e, grpc.FutureCancelledError):
            print("Acquisition to file sucessfully cancelled.")
        elif isinstance(e, IndexError):
            print("Error: Index exceeded range.")
        elif isinstance(e, KeyboardInterrupt):
            print("Cancelled by keyboard interrupt.")
        else:
            print(f"unexpected error type : {type(e)}")
            print(e)
            raise e

    def check_package_loss(self, container):
        """
        Checks metadata or return value for package loss.
        """
        hw_loss = -1
        if str(type(container)).endswith("Rendezvous'>"):
            trailing_md = dict(container.trailing_metadata())
            try:
                hw_loss = int(trailing_md["lost-in-hardware"])
            except KeyError:
                print("Package Loss not found in Metadata:")
                print(trailing_md)

        elif str(type(container)) == "<class 'dmacontroller_pb2.LostSamples'>":
            hw_loss = container.Hardware

        if hw_loss == -1:
            print(
                f"Warning: Could not find package loss info from type {str(type(container))}"
            )

        if hw_loss > 0:
            print(f"Warning: Samples lost in hardware : {hw_loss}")

        return hw_loss

    @servicehub_call(errormsg="failed", tries=1)
    def limited_stream_with_metadata(
        self,
        sample_count,
        channels=None,
        subchains=None,
        sample_rate=0,
        timeout=0,
        package_mode=0,
        deinterleave=False,
        dtype=None,
        is_iq=False,
    ):
        """
        Requests a grpc stream of acquired data and converts it to a numpy array.

        Args:
            sample_count    : total sample count for all channels
            channels        : list of channel indices
            subchains       : list of sub chain indices
            sample_rate     : approximate data rate in samples per second
                              (used to adapt the timeout value for slow data rates)
            timeout         : timeout in seconds to wait for stochastic data
            deinterleave    : {boolean} if true, the data of the channels will be deinterleaved,
                              returning a numpy-2d-array with the data seperated for each channel.
            dtype           : {numpy.dtype} change the data type to interpret the data with.
                              If None the default data type specified in the constructor is used.
            is_iq           : {boolean} interpret data as IQ-values and return the complex value.
                              Note: the itemsize of the dtype needs to be divided by 2.
        """

        if channels is None:
            channels = []

        if subchains is None:
            subchains = []

        # preallocate memory
        if dtype is None:
            dtype = self.dtype
        elif dtype.itemsize * (1 + 1 * is_iq) > self.bytes_per_sample:
            print("Warning: itemsize of requested data type exceeds word size of data.")

        samples_per_sample = self.compute_samples_per_sample(dtype)
        data = np.zeros(sample_count * samples_per_sample * self.chains, dtype=dtype)

        stream_request = dmacontroller_pb2.StreamRequest(
            index=self.ep_index,
            count=sample_count,
            subChains=subchains,
            channels=channels,
            sampleRate=sample_rate,
            timeout=timeout,
            packageMode=package_mode,
        )

        stream = self._stub.SnapshotWithMetadata(stream_request)

        # a function is needed to issue a stream.cancel() with a keyboard interrupt
        def cancel_stream(unused_sig, unused_frame):
            stream.cancel()

        signal.signal(signal.SIGINT, cancel_stream)

        oi = (
            0  # current offset index needed since byte stream is transmitted block wise
        )
        max_fill_level = 0
        sample_cnt_without_loss = 0
        try:
            for message in stream:
                fill_level = message.data_fifo_highwatermark

                n = len(message.value) // dtype.itemsize
                data[oi : oi + n] = np.frombuffer(message.value, dtype=dtype)

                oi += n
                max_fill_level = max(max_fill_level, fill_level)

                if message.lost_samples == 0:
                    sample_cnt_without_loss = oi
        except (IndexError, ValueError) as e:
            self._handle_exception(e)

        pkg_loss = self.check_package_loss(stream)

        print(f"Data Fifo High Watermark : {(max_fill_level * 100)} percent")
        print(f"No Samples lost until {sample_cnt_without_loss}")

        if is_iq:
            data = self.convert_iq_to_complex(data)
        if deinterleave:
            data = self.deinterleave(data, len(channels))
        return data, pkg_loss
