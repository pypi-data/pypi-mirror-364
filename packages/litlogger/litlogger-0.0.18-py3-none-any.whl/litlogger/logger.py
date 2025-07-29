# Copyright The Lightning AI team.
# Licensed under the Apache License, Version 2.0 (the "License");
#     http://www.apache.org/licenses/LICENSE-2.0
#
import logging
import os
import subprocess
import warnings
from argparse import Namespace
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

from google.protobuf import timestamp_pb2
from google.protobuf.json_format import MessageToDict
from lightning_utilities import module_available
from torch import Tensor
from torch.nn import Module
from typing_extensions import override

import litlogger
from litlogger.experiment import Experiment
from litlogger.generator import _create_name

if module_available("lightning"):
    from lightning.fabric.loggers.logger import Logger, rank_zero_experiment
    from lightning.fabric.utilities.cloud_io import get_filesystem
    from lightning.fabric.utilities.logger import _add_prefix
    from lightning.fabric.utilities.rank_zero import rank_zero_only
    from lightning.fabric.utilities.types import _PATH
    from lightning.pytorch.callbacks import ModelCheckpoint
    from lightning.pytorch.loggers.utilities import _scan_checkpoints
elif module_available("pytorch_lightning"):
    from lightning_fabric.loggers.logger import Logger, rank_zero_experiment
    from lightning_fabric.utilities.cloud_io import get_filesystem
    from lightning_fabric.utilities.logger import _add_prefix
    from lightning_fabric.utilities.rank_zero import rank_zero_only
    from lightning_fabric.utilities.types import _PATH
    from pytorch_lightning.callbacks import ModelCheckpoint
    from pytorch_lightning.loggers.utilities import _scan_checkpoints
else:
    raise ModuleNotFoundError("Either `lightning` or `pytorch_lightning` must be installed")

if module_available("litmodels"):
    from litmodels import upload_model

log = logging.getLogger(__name__)


class LightningLogger(Logger):
    LOGGER_JOIN_CHAR = "-"
    """The LightningLogger enables logging to the https://lightning.ai Platform"""

    def __init__(
        self,
        name: Optional[str] = None,
        experiment_project_name: Optional[str] = None,
        root_dir: Optional[_PATH] = None,
        teamspace: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
        store_step: Optional[bool] = False,
        store_created_at: Optional[bool] = False,
        log_model: bool = False,
        checkpoint_name: Optional[str] = None,
    ) -> None:
        """Constructor of the LightningLogger.

        Arguments:
            root_dir: The folder where the logs metadata are stored
            name: The name of your experiment
            experiment_project_name: The project name to which the experiment belongs. inferred if not given
            teamspace: The project on which you want to attach your charts.
            metadata: Extra metadata to associated to the experiment.
            store_step: Whether to store the provided step for each data point.
            store_created_at: Whether to keep the created at for each data point.
            log_model: Enable automatic logging of model checkpoints.
            checkpoint_name: Specify the name of the checkpoint to be logged.

        Example::

            from lightning_sdk.lightning_cloud.logger import Experiment
            from time import sleep
            import random

            experiment = Experiment("my-name")

            for i in range(1_000_000):
                experiment.log_metrics({"i": random.random()})
                sleep(1 / 100000)

            experiment.finalize()

        Example::

            from lightning.pytorch import Trainer
            from lightning.pytorch.demos.boring_classes import BoringModel, BoringDataModule
            from litlogger import LightningLogger

            class LoggingModel(BoringModel):
                def training_step(self, batch, batch_idx: int):
                    loss = self.step(batch)
                    # logging the computed loss
                    self.log("train_loss", loss)
                    return {"loss": loss}

            trainer = Trainer(
                max_epochs=10,
                enable_model_summary=False,
                logger=LightningLogger("./lightning_logs", name="boring_model")
            )
            model = BoringModel()
            data_module = BoringDataModule()
            trainer.fit(model, data_module)
            trainer.test(model, data_module)

        """
        self._root_dir = os.fspath(root_dir or "./lightning_logs")
        self._name = name or _create_name()
        self._experiment_project_name = experiment_project_name or self._get_experiment_name()
        self._version = None
        self._teamspace = teamspace
        self._experiment: Optional[Experiment] = None
        self._sub_dir = None
        self._prefix = ""
        self._fs = get_filesystem(root_dir)
        self._step = -1
        self._metadata = metadata or {}
        self._store_step = store_step
        self._store_created_at = store_created_at
        self._is_ready = False
        self._log_model = log_model
        self._checkpoint_callback: Optional[ModelCheckpoint] = None
        self._logged_model_time: dict[str, float] = {}
        self._checkpoint_name = checkpoint_name

    @property
    @override
    def name(self) -> str:
        """Gets the name of the experiment."""
        return self._name

    @property
    @override
    def version(self) -> str:
        """Get the experiment version - its time of creation."""
        return self._version

    @property
    @override
    def root_dir(self) -> str:
        """Gets the save directory where the TensorBoard experiments are saved."""
        return self._root_dir

    @property
    @override
    def log_dir(self) -> str:
        """The directory for this run's tensorboard checkpoint.

        By default, it is named ``'version_${self.version}'`` but it can be overridden by passing a string value for the
        constructor's version parameter instead of ``None`` or an int.

        """
        log_dir = os.path.join(self.root_dir, self.name)
        if isinstance(self.sub_dir, str):
            log_dir = os.path.join(log_dir, self.sub_dir)
        log_dir = os.path.expandvars(log_dir)
        return os.path.expanduser(log_dir)

    @property
    def save_dir(self) -> str:
        return self.log_dir

    @property
    def sub_dir(self) -> Optional[str]:
        """Gets the sub directory where the TensorBoard experiments are saved."""
        return self._sub_dir

    @property
    @rank_zero_experiment
    def experiment(self) -> Optional["Experiment"]:
        if not self._is_ready:
            return None

        if self._experiment is not None:
            return self._experiment

        assert rank_zero_only.rank == 0, "tried to init log dirs in non global_rank=0"
        if self.root_dir:
            self._fs.makedirs(self.root_dir, exist_ok=True)

        if self.version is None:
            version = timestamp_pb2.Timestamp()
            version.FromDatetime(datetime.utcnow())
            self._version = MessageToDict(version)

        self._experiment = Experiment(
            name=self._name,
            experiment_project_name=self._experiment_project_name,
            version=self.version,
            teamspace=self._teamspace,
            metadata={k: str(v) for k, v in self._metadata.items()},
            store_step=self._store_step,
            store_created_at=self._store_created_at,
            log_dir=self.log_dir,
        )
        return self._experiment

    @property
    @rank_zero_only
    def url(self) -> str:
        return self.experiment.url

    @override
    @rank_zero_only
    def log_metrics(self, metrics: Mapping[str, float], step: Optional[int] = None) -> None:
        assert rank_zero_only.rank == 0, "experiment tried to log from global_rank != 0"

        self._is_ready = True

        # FIXME: This should be handled by the tracker if this isn't defined by the user.
        self._step = self._step + 1 if step is None else step
        self._store_step = True

        metrics = _add_prefix(metrics, self._prefix, self.LOGGER_JOIN_CHAR)
        metrics = {k: v.item() if isinstance(v, Tensor) else v for k, v in metrics.items()}
        self.experiment.log_metrics(metrics, step=self._step)

    @override
    @rank_zero_only
    def log_hyperparams(  # type: ignore[override]
        self,
        params: Union[dict[str, Any], Namespace],
        metrics: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log hyperparams."""
        if isinstance(params, Namespace):
            params = params.__dict__
        params.update(self._metadata or {})
        self._metadata = params

    @rank_zero_only
    def log_metadata(  # type: ignore[override]
        self,
        params: Union[dict[str, Any], Namespace],
    ) -> None:
        """Log hyperparams."""
        if isinstance(params, Namespace):
            params = params.__dict__
        params.update(self._metadata or {})
        self._metadata = params

    @override
    @rank_zero_only
    def log_graph(self, model: Module, input_array: Optional[Tensor] = None) -> None:
        warnings.warn("LightningLogger does not support `log_graph`", UserWarning, stacklevel=2)

    @rank_zero_only
    def log_model(
        self,
        model_ckpt: Union[str, Path],
        name: str,
        version: Optional[str] = None,
        cloud_account: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log a model checkpoint as an artifact."""
        if not module_available("litmodels"):
            raise ModuleNotFoundError("litmodels is not installed. Please install it with `pip install litmodels`.")
        if "/" not in name:
            name = f"{self.experiment.owner_teamspace}/{name}"
        name += f":{version}" if version else ""
        if not metadata:
            metadata = {}
        metadata.update(
            {
                "litLogger": litlogger.__version__,
                "experiment.name": self.experiment.name,
                "experiment.owner_teamspace": self.experiment.owner_teamspace,
            }
        )
        upload_model(
            model=model_ckpt, name=name, progress_bar=True, cloud_account=cloud_account, metadata=metadata, verbose=1
        )

    @override
    @rank_zero_only
    def save(self) -> None:
        pass

    @override
    @rank_zero_only
    def finalize(self, status: Optional[str] = None) -> None:
        if self._experiment is not None:
            self._experiment.finalize(status)
        # log checkpoints as artifacts
        if self._checkpoint_callback and self._experiment is not None:
            self._scan_and_log_checkpoints(self._checkpoint_callback)

    def after_save_checkpoint(self, checkpoint_callback: ModelCheckpoint) -> None:
        # log checkpoints as artifacts
        if self._log_model is False:
            return
        if checkpoint_callback.save_top_k == -1:
            self._scan_and_log_checkpoints(checkpoint_callback)
        else:
            self._checkpoint_callback = checkpoint_callback

    def _scan_and_log_checkpoints(self, checkpoint_callback: ModelCheckpoint) -> None:
        # get checkpoints to be saved with associated score
        checkpoints = _scan_checkpoints(checkpoint_callback, self._logged_model_time)

        # log iteratively all new checkpoints
        for timestamp, path_ckpt, _score, tag in checkpoints:
            if not self._checkpoint_name:
                self._checkpoint_name = self.experiment.name
            # Ensure the version tag is unique by appending a timestamp. TODO: make it work with tag as before https://github.com/Lightning-AI/litLogger/pulls
            unique_tag = f"{tag}-{int(datetime.utcnow().timestamp())}"
            self.log_model(path_ckpt, name=self._checkpoint_name, version=unique_tag)
            # remember logged models - timestamp needed in case filename didn't change (last ckpt or custom name)
            self._logged_model_time[path_ckpt] = timestamp

    def _get_experiment_name(self) -> str:
        try:
            # try to get the git repo name
            git_root = (
                subprocess.check_output(["git", "rev-parse", "--show-toplevel"], stderr=subprocess.DEVNULL)
                .decode()
                .strip()
            )
            experiment_name = os.path.basename(git_root)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # if no git repo, use current directory name
            experiment_name = Path.cwd().name

        # default to 'project' if no meaningful name was found
        return experiment_name or "project"

    def log_config(self, path: str) -> None:
        """Log a configuration file (e.g., YAML, JSON) as an artifact to the Lightning platform.

        Args:
            path: Path to the config file to log.

        Example::
            logger = LightningLogger(...)
            logger.log_config('config.yaml')
        """
        self._is_ready = True
        self._store_step = True
        self.experiment.log_config(path)
