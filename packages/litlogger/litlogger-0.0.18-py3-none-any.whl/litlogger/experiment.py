# Copyright The Lightning AI team.
# Licensed under the Apache License, Version 2.0 (the "License");
#     http://www.apache.org/licenses/LICENSE-2.0
#
import os
from collections.abc import Mapping
from datetime import datetime
from multiprocessing import JoinableQueue
from threading import Event
from time import sleep, time
from typing import Optional

from google.protobuf import timestamp_pb2
from google.protobuf.json_format import MessageToDict
from lightning_sdk.api.utils import _get_cloud_url
from lightning_sdk.lightning_cloud.env import LIGHTNING_CLOUD_PROJECT_ID
from lightning_sdk.lightning_cloud.login import Auth
from lightning_sdk.lightning_cloud.openapi import (
    MetricsstreamCreateBody,
    MetricsStreamIdLoggerartifactsBody,
    V1Membership,
    V1Metrics,
    V1MetricsTags,
    V1MetricValue,
    V1OwnerType,
    V1SystemInfo,
)
from lightning_sdk.teamspace import Teamspace

from litlogger.client import LitRestClient
from litlogger.colors import _create_colors
from litlogger.diagnostics import collect_system_info
from litlogger.manager import _ManagerThread

_PUSH_TO_QUEUE_SLEEP = 1
_MAX_LOG_METRICS_BETWEEN_PUSH = 1000
_MAX_METRICS_PER_REQUEST = 1000
_MAP_PLUGIN_ID_TO_APP = {"job_run_plugin": "jobs", "distributed_plugin": "mmt", "litdata": "litdata"}


class Experiment:
    def __init__(
        self,
        name: str,
        experiment_project_name: str,
        version: str,
        log_dir: str,
        teamspace: Optional[str] = None,
        light_color: Optional[str] = None,
        dark_color: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
        store_step: Optional[bool] = True,
        store_created_at: Optional[bool] = False,
    ) -> None:
        """The base class to enable logging to the https://lightning.ai Platform.

        Arguments:
            name: The name of your experiment
            experiment_project_name: The project name to which the experiment belongs
            version: The version of the experiment
            log_dir: The directory where the logs are going to be stored.
            teamspace: The Teamspace on which you want to attach your charts.
            light_color: The color of the curve in light mode.
            dark_color: The color of the curve in dark mode.
            metadata: The parameters associated with the experiment.
            store_step: Whether to store the provided step for each data point.
            store_created_at: Whether to keep the created at for each data point.

        Example::

            from lightning_sdk.lightning_cloud.logger import Experiment
            from time import sleep
            import random

            experiment = Experiment("my-name")

            for i in range(1_000_000):
                experiment.log_metrics({"i": random.random()})
                sleep(1 / 100000)

            experiment.finalize()
        """
        self.name = name
        self.experiment_project_name = experiment_project_name
        self.version = version
        self.teamspace = teamspace
        self.done_event = Event()
        self.store_step = store_step
        self.store_created_at = store_created_at

        auth = Auth()
        auth.authenticate()

        self.client = LitRestClient(max_retries=0)
        self.project = _get_project(self.client, teamspace=teamspace)

        if self.project.owner_type == V1OwnerType.USER:
            response = self.client.user_service_search_users(query=self.project.owner_id)
            users = [u for u in response.users if u.id == self.project.owner_id]
            if len(users) == 0:
                raise RuntimeError("The owner of the project couldn't be found.")
            self.owner_name = users[0].username
        else:
            self.owner_name = self.client.organizations_service_get_organization(id=self.project.owner_id).name

        random_light_color, random_dark_color = _create_colors()

        tags = []
        if metadata:
            tags = [V1MetricsTags(name=str(k), value=str(v), from_code=True, active=False) for k, v in metadata.items()]

        self.stream = self.client.lit_logger_service_create_metrics_stream(
            project_id=self.project.project_id,
            body=MetricsstreamCreateBody(
                name=self.name,
                experiment_project_name=self.experiment_project_name,
                version=self.version,
                cloudspace_id=os.getenv("LIGHTNING_CLOUD_SPACE_ID"),
                app_id=os.getenv("LIGHTNING_CLOUD_APP_ID"),
                work_id=os.getenv("LIGHTNING_CLOUD_WORK_ID"),
                light_color=light_color or random_light_color,
                dark_color=dark_color or random_dark_color,
                tags=tags,
                store_step=store_step,
                store_created_at=store_created_at,
                system_info=V1SystemInfo(**collect_system_info()),
            ),
        )

        cloud_url = _get_cloud_url()
        self._url = (
            f"{cloud_url}/{self.owner_name}/{self.project.name}/experiments/"
            f"{self.name}%20-%20v{self.stream.version_number}"
        )

        url = f"{cloud_url}/{self.owner_name}/{self.project.name}/"

        if self.stream.cloudspace_id == "":
            url += "experiments"
            print(f"Your experiment is accessible at {url} with name '{self.name}'")
        else:
            cloudspace = self.client.cloud_space_service_get_cloud_space(
                project_id=self.project.project_id, id=self.stream.cloudspace_id
            )
            if self.stream.work_id != "":
                if self.stream.plugin_id not in _MAP_PLUGIN_ID_TO_APP:
                    raise RuntimeError(
                        f"The stream plugin id {self.stream.plugin_id} wasn't found in {_MAP_PLUGIN_ID_TO_APP}"
                    )
                app_id = {"job_run_plugin": "jobs", "distributed_plugin": "mmt", "litdata": "litdata"}[
                    self.stream.plugin_id
                ]
                url += f"studios/{cloudspace.name}/app?app_id={app_id}&job_name={self.stream.job_name}"
            else:
                url += f"studios/{cloudspace.name}/lit-logger?app_id=031"
            print(f"Your metrics are accessible at {url}")
        print(f"The direct url to this experiment is {self._url}")

        self.metrics_queue = JoinableQueue()
        self.stop_event = Event()
        self.is_ready_event = Event()
        self.manager = _ManagerThread(
            self.stream.project_id,
            self.stream.id,
            self.stream.cluster_id,
            self.client,
            self.metrics_queue,
            self.is_ready_event,
            self.stop_event,
            self.done_event,
            log_dir=log_dir,
            version=version,
            store_step=store_step,
            store_created_at=store_created_at,
        )
        self.manager.start()
        self.metrics: list[dict[str, V1Metrics]] = [{}]
        self.last_time = None
        self.num_values = 0
        self._wait_ready = 1

        # wait for the thread to be started
        while not self.is_ready_event.is_set():
            sleep(0.1)

    @property
    def owner_teamspace(self) -> str:
        return f"{self.owner_name}/{self.project.name}"

    @property
    def url(self) -> str:
        """Get the URL of the experiment."""
        return self._url

    def log_metrics(self, metrics: Mapping[str, float], step: Optional[int] = None) -> None:
        if self.last_time is None:
            self.last_time = time()

        if self.manager.exception is None:
            for name, value in metrics.items():
                created_at = None
                if self.store_created_at:
                    timestamp = timestamp_pb2.Timestamp()
                    timestamp.FromDatetime(datetime.now())
                    created_at = MessageToDict(timestamp)

                if not self.store_step:
                    step = None

                value = V1MetricValue(value=float(value), created_at=created_at, step=step)
                if name not in self.metrics[-1]:
                    self.metrics[-1][name] = V1Metrics(name=name, values=[value])
                else:
                    self.metrics[-1][name].values.append(value)

                self.num_values += 1

            should_send = time() - self.last_time > _PUSH_TO_QUEUE_SLEEP or self.num_values >= _MAX_METRICS_PER_REQUEST
            if should_send:
                self.metrics.append({})
                self._send()
                self.num_values = 0
        else:
            raise self.manager.exception

    def finalize(self, status: Optional[str] = None) -> None:
        # Send the last events
        self._send(check_num_values=False)
        # Sleep to ensure it is getting picked up

        # Trigger stop event
        self.stop_event.set()

        # Wait for all the metrics to be uploaded
        while not self.done_event.is_set():
            if self.manager.exception is not None:
                raise self.manager.exception

            sleep(0.1)

    def _send(self, check_num_values: bool = True) -> None:
        if not self.metrics:
            return
        if not len(self.metrics[0]):
            return

        metrics = self.metrics.pop(0)

        if check_num_values:
            num_values = sum([len(m.values) for m in metrics.values()])
            if num_values > _MAX_LOG_METRICS_BETWEEN_PUSH:
                raise RuntimeError(
                    f"You are generating too much metrics. "
                    f" The limit is {_MAX_LOG_METRICS_BETWEEN_PUSH} values per second."
                    f" You have logged {num_values} values."
                )

        self.metrics_queue.put(metrics)
        self.last_time = time()

    def log_config(self, path: str) -> None:
        """Log a configuration file (e.g., YAML, JSON) as an artifact to the Lightning platform.

        Args:
            path: Path to the config file to log.

        Example::
            experiment = Experiment(...)
            experiment.log_config('config.yaml')
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        try:
            # Upload the file to the teamspace drive
            teamspace_cls = Teamspace(name=self.teamspace, org=self.owner_name)
            remote_path = f"experiments/{self.name}/{path}"
            teamspace_cls.upload_file(file_path=path, remote_path=remote_path, progress_bar=False)

            artifact_path = f"{self.project.name}/uploads/{remote_path}/drive?path={path}"

            self.client.lit_logger_service_create_logger_artifact(
                project_id=self.stream.project_id,
                metrics_stream_id=self.stream.id,
                body=MetricsStreamIdLoggerartifactsBody(path=artifact_path),
            )
            print(f"✓ Uploaded config to the drive of the teamspace {teamspace_cls.name}")
        except Exception as e:
            raise RuntimeError(f"Failed to log config file as artifact: {e}") from e


def _get_project(client: LitRestClient, teamspace: Optional[str] = None, verbose: bool = True) -> V1Membership:
    """Get a project membership for the user from the backend."""
    project_id = None

    if teamspace is None:
        project_id = LIGHTNING_CLOUD_PROJECT_ID

    if project_id is not None:
        return _get_project_from_id(client, project_id)

    projects = client.projects_service_list_memberships()
    if len(projects.memberships) == 0:
        raise ValueError("No valid projects found. Please reach out to lightning.ai team to create a project")
    for project in projects.memberships:
        if project.project_id == teamspace or project.name == teamspace or project.display_name == teamspace:
            return project
    if len(projects.memberships) > 1 and verbose:
        print(f"Defaulting to the project: {projects.memberships[0].name}")
    return projects.memberships[0]


def _get_project_from_id(client: LitRestClient, project_id: str) -> V1Membership:
    project = client.projects_service_get_project(project_id)
    if not project:
        raise ValueError(f"{project_id} is not a valid project id.")
    print(f"Defaulting to the project: {project.name}")
    return V1Membership(
        name=project.name,
        display_name=project.display_name,
        description=project.description,
        created_at=project.created_at,
        project_id=project.id,
        owner_id=project.owner_id,
        owner_type=project.owner_type,
        quotas=project.quotas,
        updated_at=project.updated_at,
    )
