from time import sleep
import concurrent.futures

from tqdm.notebook import tqdm, trange
import grpc
import numpy as np
from ipe_servicehub_protos import dma_pb2, dma_pb2_grpc


class DMA:
    """
    This module is deprecated. Please use the DMAController module
    """

    def __init__(self, connection):
        self.connection = connection
        self._stub = dma_pb2_grpc.DMAServiceStub(self.connection.getChannel())

    def snapshot_32(
        self,
        count=8000,
        channels=[],
        timeout_in_msecs=1000,
        return_package_loss_info=False,
    ):
        """
        Returns a numpy array (length=count, dtype=int32). The channels are interleaved.
        count : total sample count
        channels : list of channel indices
        sample_rate_khz: optional parameter for low sample rates to increase timeout
        return_package_loss_info : if True, the PackageLossInfo will also be returned
        """
        res = np.zeros(count, dtype=np.int32)
        stream = self._stub.Snapshot32(
            dma_pb2.StreamRequest(
                count=count, channels=channels, TimeoutInMSecs=timeout_in_msecs
            )
        )
        idx = 0
        for repeated_int32 in stream:
            for Int32 in repeated_int32.value:
                res[idx] = np.int32(Int32)
                idx += 1
        LossInfo = self._stub.GetPackageLossInfo(dma_pb2.Empty())
        self._check_data_loss(LossInfo)
        if return_package_loss_info:
            return res, LossInfo
        return res

    def snapshot_16(
        self,
        count=8000,
        channels=[],
        sample_rate_khz=None,
        timeout_in_msecs=1000,
        return_package_loss_info=False,
    ):
        """
        Returns a numpy array (length=count, dtype=int16). The channels are interleaved.
        count : total sample count
        channels : list of channel indices
        sample_rate_khz: optional parameter for low sample rates to increase timeout
        return_package_loss_info : if True, the PackageLossInfo will also be returned
        """
        res = np.zeros(count, dtype=np.int16)
        timeout = timeout_in_msecs

        if sample_rate_khz is not None and timeout_in_msecs == 1000:
            min_samples = max(
                count, 128000 / len(channels)
            )  # TODO: Use Buffer length of driver at least one buffer of size 256kB has to be written
            timeout = int(
                np.int(np.ceil(min_samples / len(channels) / sample_rate_khz) + 100)
            )  # for good measure
        stream = self._stub.Snapshot32(
            dma_pb2.StreamRequest(
                count=count // 2, channels=channels, TimeoutInMSecs=max(timeout, 1000)
            )
        )
        idx = 0
        for repeated_int32 in stream:
            for Int32 in repeated_int32.value:
                res[idx], res[idx + 1] = self.__conv_to_16(Int32)
                idx += 2
        LossInfo = self._stub.GetPackageLossInfo(dma_pb2.Empty())
        self._check_data_loss(LossInfo)
        if return_package_loss_info:
            return res, LossInfo
        return res

    def __conv_to_16(self, value):
        a = np.int16(int(value) & 0x0000FFFF)
        b = np.int16((int(value) & 0xFFFF0000) >> 16)
        return a, b

    def __conv_to_8(self, value):
        a = np.int8(int(value) & 0x000000FF)
        b = np.int8((int(value) & 0x0000FF00) >> 8)
        c = np.int8((int(value) & 0x00FF0000) >> 16)
        d = np.int8((int(value) & 0xFF000000) >> 24)
        return a, b, c, d

    def snapshot_8(
        self,
        count=8000,
        channels=[],
        timeout_in_msecs=1000,
        return_package_loss_info=False,
    ):
        """
        Returns a numpy array (dtype=int8). The channels are interleaved.
        count : total sample count
        channels : list of channel indices
        sample_rate_khz: optional parameter for low sample rates to increase timeout
        return_package_loss_info : if True, the PackageLossInfo will also be returned
        """
        res = np.zeros(count, dtype=np.int16)
        stream = self._stub.Snapshot32(
            dma_pb2.StreamRequest(
                count=count // 4,
                channels=channels,
                TimeoutInMSecs=max(1000, timeout_in_msecs),
            )
        )
        idx = 0
        for repeated_int32 in stream:
            for int32 in repeated_int32.value:
                res[idx], res[idx + 1], res[idx + 2], res[idx + 3] = self.__conv_to_8(
                    int32
                )
                idx += 4
        LossInfo = self._stub.GetPackageLossInfo(dma_pb2.Empty())
        if return_package_loss_info:
            return res, LossInfo
        return res

    def download(
        self,
        remote_file="testStreamFile32.txt",
        local_dir=".",
        subpath="",
        disk_type="SSD",
        file_size=None,
    ):
        req = dma_pb2.FileRequest(
            FileName=remote_file,
            SubPath=subpath,
            DiskType=dma_pb2.DiskType.Value(disk_type),
        )
        stream = self._stub.FileDownload(req)
        local_file = local_dir + "/" + remote_file
        with tqdm.wrapattr(
            open(local_file, "wb"), "write", total=file_size, desc=remote_file
        ) as f:
            try:
                for d in stream:
                    f.write(bytes(d.value))
                    f.flush()
            except grpc._channel._Rendezvous as err:
                print("Unknown gRPC error, file probably not found.")
                # print(err)
                f.close()

    def snapshot_to_file(self, bytesize, channels, file_path):
        """
        Data is directly transmitted via gRPC and saved to `file_path` on the host system

        With the DMA writing to the platform RAM, high write speeds can
        be acheived e.g. for raw data acquisition.
        """
        stream = self._stub.Snapshot32(
            dma_pb2.StreamRequest(
                count=bytesize // 4, channels=channels, TimeoutInMSecs=1000
            )
        )
        with tqdm.wrapattr(
            open(file_path, "wb"),
            "write",
            total=bytesize,
            desc=file_path.split("/")[-1],
        ) as f:
            for repeated_int32 in stream:
                for int32 in repeated_int32.value:
                    f.write(bytes(int32.to_bytes(4, "little")))
                    f.flush()
        return self._stub.GetPackageLossInfo(dma_pb2.Empty())

    def stream_continuous(self):
        res = []
        br = 0
        stream = self._stub.StreamContinuous(dma_pb2.Empty())
        try:
            for d in stream:
                res.append(d)
                br = br + 1
                print(br)
                if br == 10:
                    stream.cancel()
        except grpc._channel._Rendezvous as err:
            print(err)

    def file_snapshot_32(
        self,
        count=8000,
        channels=[],
        file_name="testStreamFile32.bin",
        sub_path="",
        disk_type="SSD",
        timeout_in_msecs=1000,
        mute_warnings=False,
    ):
        req = dma_pb2.FileWriteCommand(
            FileName=file_name,
            SubPath=sub_path,
            DiskType=dma_pb2.DiskType.Value(disk_type),
            streamInfo=dma_pb2.StreamRequest(
                count=count,
                channels=channels,
                TimeoutInMSecs=max(1000, timeout_in_msecs),
            ),
        )
        loss_info = self._stub.FileSnapshot32(req)
        if not mute_warnings:
            self._check_data_loss(loss_info)
        return loss_info

    def file_stream(
        self,
        samples,
        channels,
        file_name,
        sample_rate=None,
        sub_path="",
        disk_type="SSD",
        mute_warnings=False,
    ):
        """
        Writes data to a file on the platform.
        For each channel the given amount of samples will be saved.
        If a sample rate is given, a progress bar is shown.
        The given disk type must match the one specified in the servicehub config on the board.
        """
        timeout_in_msecs = (
            1.4e8 / len(channels) / sample_rate
        )  # 1.4e8 = 280[kB] / 2[B/sample] / sample_rate[Hz] / number of channels * 1000 [ms/s]
        # print("TimeoutInMSecs : %.0f" %TimeoutInMSecs)
        req = dma_pb2.FileWriteCommand(
            FileName=file_name,
            SubPath=sub_path,
            DiskType=dma_pb2.DiskType.Value(disk_type),
            streamInfo=dma_pb2.StreamRequest(
                count=samples * len(channels) // 2,
                channels=channels,
                TimeoutInMSecs=max(1000, int(timeout_in_msecs)),
            ),
        )
        if sample_rate is None:
            loss_info = self._stub.FileSnapshot32(req)
        else:
            # Execute gRPC call and progress bar parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                ProgressBarThread = executor.submit(
                    self.stream_progress_bar, samples, sample_rate
                )
                FileStreamThread = executor.submit(self._stub.FileSnapshot32, req)
                loss_info = FileStreamThread.result()
                ProgressBarThread.result()
        if not mute_warnings:
            self._check_data_loss(loss_info)
        return loss_info

    def file_snapshot_8(
        self,
        count=8000,
        channels=[],
        file_name="testStreamFile8.bin",
        sub_path="",
        disk_type="SSD",
        timeout_in_msecs=1000,
        mute_warnings=False,
    ):
        req = dma_pb2.FileWriteCommand(
            FileName=file_name,
            SubPath=sub_path,
            DiskType=dma_pb2.DiskType.Value(disk_type),
            streamInfo=dma_pb2.StreamRequest(
                count=count,
                channels=channels,
                TimeoutInMSecs=max(1000, timeout_in_msecs),
            ),
        )
        loss_info = self._stub.FileSnapshot(req)
        if not mute_warnings:
            self._check_data_loss(loss_info)
        return loss_info

    def _check_data_loss(self, loss_info):
        if 0 != loss_info.LostInHardware + loss_info.LostInSoftware:
            print(
                f"Warning: Package Loss, lost in hardware: {loss_info.LostInHardware}, lost in software {loss_info.LostInSoftware}"
            )

    def stream_progress_bar(self, samples, sample_rate, description=None):
        bins = 100
        bin_wait_time_s = samples / bins / sample_rate
        for _ in trange(bins, desc=description):
            sleep(bin_wait_time_s)
        return True
