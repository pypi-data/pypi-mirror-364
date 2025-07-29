# Copyright The Lightning AI team.
# Licensed under the Apache License, Version 2.0 (the "License");
#     http://www.apache.org/licenses/LICENSE-2.0
#
import queue
from datetime import datetime
from multiprocessing import Queue
from threading import Event, Thread
from time import time

from google.protobuf import timestamp_pb2
from google.protobuf.json_format import MessageToDict
from lightning_sdk.lightning_cloud.openapi import (
    LoggermetricsIdBody,
    MetricsstreamIdBody,
    V1Metrics,
    V1MetricsTracker,
    V1MetricValue,
    V1PhaseType,
)
from lightning_sdk.lightning_cloud.openapi.rest import ApiException

from litlogger.client import LitRestClient
from litlogger.file_writer import BinaryFileWriter


class _ManagerThread(Thread):
    """The _ManagerThread is used to append metrics to the metrics stream."""

    def __init__(
        self,
        teamspace_id: str,
        stream_id: str,
        cloud_account: str,
        client: LitRestClient,
        metrics_queue: Queue,
        is_ready_event: Event,
        stop_event: Event,
        done_event: Event,
        log_dir: str,
        version: str,
        store_step: bool,
        store_created_at: bool,
        rate_limiting: int = 1,
    ) -> None:
        super().__init__(daemon=True)
        self.teamspace_id = teamspace_id
        self.stream_id = stream_id
        self.client = client
        self.metrics_queue = metrics_queue
        self.last_time = time()
        self.rate_limiting = rate_limiting
        self.is_ready_event = is_ready_event
        self.stop_event = stop_event
        self.done_event = done_event
        self.metrics: dict[str, V1Metrics] = {}
        self.exception = None

        self.store_step = store_step
        self.store_created_at = store_created_at

        self.file_store = BinaryFileWriter(
            log_dir=log_dir,
            version=version,
            store_step=store_step,
            store_created_at=store_created_at,
            teamspace_id=teamspace_id,
            stream_id=stream_id,
            cloud_account=cloud_account,
            client=client,
        )

        self.trackers: dict[str, V1MetricsTracker] = {}

    def run(self) -> None:
        self._run()
        self.done_event.set()

    def _run(self) -> None:
        try:
            self.is_ready_event.set()

            while not self.stop_event.is_set():
                self.step()

            while self.step():
                pass

            self.step()

            self.file_store.upload()

            self.inform_done()

            self.done_event.set()
        except Exception as e:
            print(e)
            self.done_event.set()
            self.exception = e

    def step(self) -> bool:
        not_empty = self._read()
        if not_empty:
            self._send()
        return not_empty

    def _read(self) -> bool:
        try:
            metrics = self.metrics_queue.get(timeout=0.1)
            for name, values in metrics.items():
                self._update_tracker(name, values)
                self.metrics[name] = values
        except queue.Empty:
            return False

        return True

    def _send(self) -> None:
        metrics = list(self.metrics.values())
        num_values = sum([len(m.values) for m in metrics])

        if num_values == 0:
            return

        try:
            self.file_store.store(self.metrics, self.trackers)
        except ApiException as ex:
            raise ex

        try:
            self._send_metrics(metrics, num_values)
        except ApiException as ex:
            if "not found" in str(ex):
                raise Exception("The metrics stream has been deleted.") from ex
            raise ex

        self.last_time = time()

        self.metrics = {}

    def _update_tracker(self, name: str, values: list[V1MetricValue]) -> None:
        tracker = None

        # Create the tracker
        if name not in self.trackers:
            tracker = V1MetricsTracker(name=name, num_rows=0)
            self.trackers[name] = tracker
        else:
            tracker = self.trackers[name]

        values.internal_start_step = tracker.num_rows

        # Increment the number of rows
        for value_obj in values.values:
            value = float(value_obj.value)

            if tracker.started_at is None and self.store_created_at:
                tracker.started_at = datetime.timestamp(
                    datetime.strptime(value_obj.created_at, "%Y-%m-%dT%H:%M:%S.%f%z")
                )

            if tracker.min_value is None or (tracker.min_value is not None and value < tracker.min_value):
                tracker.min_value = value
                tracker.min_index = tracker.num_rows

            if tracker.max_value is None or (tracker.max_value is not None and value > tracker.max_value):
                tracker.max_value = value
                tracker.max_index = tracker.num_rows

            tracker.last_index = tracker.num_rows
            tracker.last_value = value

            if self.store_created_at:
                tracker.updated_at = datetime.timestamp(
                    datetime.strptime(value_obj.created_at, "%Y-%m-%dT%H:%M:%S.%f%z")
                )

            tracker.num_rows += 1

    def _send_metrics(self, metrics: list[V1Metrics], num_values: int) -> None:
        if num_values <= 1000:
            self.client.lit_logger_service_append_logger_metrics(
                project_id=self.teamspace_id,
                id=self.stream_id,
                body=LoggermetricsIdBody(
                    metrics=metrics,
                ),
            )
        else:
            raise RuntimeError("This shouldn't happen")

    def inform_done(self) -> None:
        if self.store_created_at:
            for tracker in self.trackers.values():
                timestamp = timestamp_pb2.Timestamp()
                timestamp.FromDatetime(datetime.fromtimestamp(tracker.started_at))
                tracker.started_at = MessageToDict(timestamp)

                timestamp = timestamp_pb2.Timestamp()
                timestamp.FromDatetime(datetime.fromtimestamp(tracker.updated_at))
                tracker.updated_at = MessageToDict(timestamp)

        self.client.lit_logger_service_update_metrics_stream(
            project_id=self.teamspace_id,
            id=self.stream_id,
            body=MetricsstreamIdBody(
                persisted=True,
                phase=V1PhaseType.COMPLETED,
                trackers=self.trackers,
            ),
        )
