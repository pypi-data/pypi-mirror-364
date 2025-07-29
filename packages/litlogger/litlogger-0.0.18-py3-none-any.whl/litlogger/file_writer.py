# Copyright The Lightning AI team.
# Licensed under the Apache License, Version 2.0 (the "License");
#     http://www.apache.org/licenses/LICENSE-2.0
#
import json
import os
import struct
import tarfile
from datetime import datetime
from typing import Optional

import numpy as np
from lightning_sdk.api.utils import _FileUploader
from lightning_sdk.lightning_cloud.openapi import (
    V1Metrics,
    V1MetricsTracker,
    V1MetricValue,
)

from litlogger.client import LitRestClient


class BinaryFileWriter:
    def __init__(
        self,
        log_dir: str,
        version: str,
        store_step: bool,
        store_created_at: bool,
        teamspace_id: str,
        stream_id: str,
        cloud_account: str,
        client: LitRestClient,
    ) -> None:
        self.log_dir = log_dir
        self.version = version
        self.store_step = store_step
        self.store_created_at = store_created_at

        self.teamspace_id = teamspace_id
        self.stream_id = stream_id
        self.cloud_account = cloud_account
        self.client = client
        self.files = {}

    def store(self, metrics: dict[str, V1Metrics], trackers: Optional[dict[str, V1MetricsTracker]] = None) -> None:
        for k, v in metrics.items():
            if k not in self.files:
                filepath = os.path.join(self.log_dir, f"{k}.litbin")
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                self.files[k] = open(filepath, "wb")  # type: ignore # noqa: SIM115

                header = {
                    "version": 1,
                    "store_created_at": self.store_created_at,
                    "store_step": self.store_step,
                    "created_at": v.values[0].created_at,
                }

                header_in_bytes = json.dumps(header).encode("utf-8")
                header_size_bytes = np.asarray(len(header_in_bytes), dtype=">u4").tobytes()
                self.files[k].write(header_size_bytes)
                self.files[k].write(header_in_bytes)
                self.files[k].flush()

            if not self.store_step and not self.store_created_at:
                self._write_only_values(k, [v.value for v in v.values])
            elif self.store_step and not self.store_created_at:
                self._write_values_steps(k, v.values)
            else:
                assert trackers
                self._write_all(k, v.values, trackers)

    def _write_only_values(self, k: str, values: list[float]) -> None:
        buf = b""
        for value in values:
            buf += struct.pack(">f", value)

        self.files[k].write(buf)
        self.files[k].flush()

    def _write_values_steps(self, k: str, values: list[V1MetricValue]) -> None:
        buf = b""
        for value in values:
            buf += struct.pack(">Q", value.step)  # big endian unsigned long long
            buf += struct.pack(">f", value.value)  # big endian float

        self.files[k].write(buf)
        self.files[k].flush()

    def _write_all(self, k: str, values: list[V1MetricValue], trackers: dict[str, V1MetricsTracker]) -> None:
        buf = b""
        for value in values:
            created_at = datetime.timestamp(datetime.strptime(value.created_at, "%Y-%m-%dT%H:%M:%S.%f%z"))
            started_at = trackers[k].started_at
            buf += struct.pack(">Q", value.step)  # big endian unsigned long long
            buf += struct.pack(">f", created_at - started_at)  # big endian unsigned integer
            buf += struct.pack(">f", value.value)  # big endian float

        self.files[k].write(buf)
        self.files[k].flush()

    def upload(self) -> None:
        # flush & close all files
        for f in self.files.values():
            f.flush()
            f.close()

        filenames = [fn for fn in os.listdir(self.log_dir) if fn.endswith(".litbin")]

        # create a tar ball for upload
        with tarfile.open(os.path.join(self.log_dir, f"{self.version}.tar.gz"), "w:gz") as tar:
            for filename in filenames:
                tar.add(
                    os.path.join(self.log_dir, filename), arcname=f"{self.teamspace_id}/{self.stream_id}/{filename}"
                )
                os.remove(os.path.join(self.log_dir, filename))

        self._upload_tar()

    def _upload_tar(self) -> None:
        """Does a single part upload."""
        file_path = os.path.join(self.log_dir, f"{self.version}.tar.gz")
        remote_path = f"/litlogger/{self.stream_id}.tar.gz"
        file_uploader = _FileUploader(
            client=self.client,
            teamspace_id=self.teamspace_id,
            cloud_account=self.cloud_account,
            file_path=file_path,
            remote_path=remote_path,
            progress_bar=False,
        )
        file_uploader()
