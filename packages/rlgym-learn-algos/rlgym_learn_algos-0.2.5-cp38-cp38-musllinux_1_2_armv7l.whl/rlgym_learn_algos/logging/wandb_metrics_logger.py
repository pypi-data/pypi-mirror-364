import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Optional, TypeVar

import wandb
from pydantic import BaseModel, Field
from rlgym_learn.api import AgentControllerData

from .dict_metrics_logger import DictMetricsLogger
from .metrics_logger import DerivedMetricsLoggerConfig, MetricsLogger

InnerMetricsLoggerConfig = TypeVar("InnerMetricsLoggerConfig")
InnerMetricsLoggerAdditionalDerivedConfig = TypeVar(
    "InnerMetricsLoggerAdditionalDerivedConfig"
)


def convert_nested_dict(d):
    new = {}
    for k, v in d.items():
        if isinstance(v, dict):
            converted = convert_nested_dict(v)
            to_add = {f"{k}/{k1}": v1 for k1, v1 in converted.items()}
        else:
            to_add = {k: v}
        new = {**new, **to_add}
    return new


class WandbMetricsLoggerConfigModel(BaseModel, extra="forbid"):
    enable: bool = True
    project: str = "rlgym-learn"
    group: str = "unnamed-runs"
    run: str = "rlgym-learn-run"
    id: Optional[str] = None
    new_run_with_timestamp_suffix: bool = False
    additional_wandb_run_config: Dict[str, Any] = Field(default_factory=dict)
    settings_kwargs: Dict[str, Any] = Field(default_factory=dict)


@dataclass
class WandbAdditionalDerivedConfig(
    Generic[InnerMetricsLoggerConfig, InnerMetricsLoggerAdditionalDerivedConfig]
):
    derived_wandb_run_config: Dict[str, Any] = Field(default_factory=dict)
    timestamp_suffix: Optional[str] = None
    inner_metrics_logger_config: InnerMetricsLoggerConfig = None
    inner_metrics_logger_additional_derived_config: (
        InnerMetricsLoggerAdditionalDerivedConfig
    ) = None


class WandbMetricsLogger(
    MetricsLogger[
        WandbMetricsLoggerConfigModel,
        WandbAdditionalDerivedConfig[
            InnerMetricsLoggerConfig, InnerMetricsLoggerAdditionalDerivedConfig
        ],
        AgentControllerData,
    ],
    Generic[
        InnerMetricsLoggerConfig,
        InnerMetricsLoggerAdditionalDerivedConfig,
        AgentControllerData,
    ],
):
    def __init__(
        self,
        inner_metrics_logger: DictMetricsLogger[
            InnerMetricsLoggerConfig,
            InnerMetricsLoggerAdditionalDerivedConfig,
            AgentControllerData,
        ],
        checkpoint_file_name: str = "wandb_metrics_logger.json",
    ):
        self.inner_metrics_logger = inner_metrics_logger
        self.checkpoint_file_name = checkpoint_file_name
        self.run_id = None

    def collect_env_metrics(self, data: List[Dict[str, Any]]):
        self.inner_metrics_logger.collect_env_metrics(data)

    def collect_agent_metrics(self, data: AgentControllerData):
        self.inner_metrics_logger.collect_agent_metrics(data)

    def report_metrics(self):
        self.wandb_run.log(convert_nested_dict(self.inner_metrics_logger.get_metrics()))
        self.inner_metrics_logger.report_metrics()

    def validate_config(self, config_obj: Any):
        return WandbMetricsLoggerConfigModel.model_validate(config_obj)

    def load(self, config):
        self.config = config
        self.inner_metrics_logger.load(
            DerivedMetricsLoggerConfig(
                checkpoint_load_folder=config.checkpoint_load_folder,
                agent_controller_name=config.agent_controller_name,
                metrics_logger_config=config.additional_derived_config.inner_metrics_logger_config,
                additional_derived_config=config.additional_derived_config.inner_metrics_logger_additional_derived_config,
            )
        )
        if self.config.checkpoint_load_folder is not None:
            self._load_from_checkpoint()
        if not self.config.metrics_logger_config.enable:
            self.wandb_run = None
            self.run_id = None
            return

        if self.run_id is not None and self.config.metrics_logger_config.id is not None:
            print(
                f"{self.config.agent_controller_name}: Wandb run id from checkpoint ({self.run_id}) is being overridden by wandb run id from config: {self.config.metrics_logger_config.id}"
            )
            self.run_id = self.config.metrics_logger_config.id

        wandb_config = {
            **self.config.additional_derived_config.derived_wandb_run_config,
            **self.config.metrics_logger_config.additional_wandb_run_config,
        }

        run_name = self.config.metrics_logger_config.run
        if self.config.metrics_logger_config.new_run_with_timestamp_suffix:
            print(
                f"{self.config.agent_controller_name}: Due to config, a new wandb run is being created with timestamp suffix. This run will use the project and group specified in config, and will use the run name in config prepended to the timestamp suffix."
            )
            if (
                self.config.additional_derived_config.timestamp_suffix is not None
                and len(self.config.additional_derived_config.timestamp_suffix) > 0
            ):
                run_name += self.config.additional_derived_config.timestamp_suffix
            else:
                run_name += f"-{time.time_ns()}"

        self.wandb_run = wandb.init(
            project=self.config.metrics_logger_config.project,
            group=self.config.metrics_logger_config.group,
            config=wandb_config,
            name=run_name,
            id=self.run_id,
            resume="allow",
            reinit=True,
            settings=wandb.Settings(
                **self.config.metrics_logger_config.settings_kwargs
            ),
        )
        self.run_id = self.wandb_run.id
        print(f"{self.config.agent_controller_name}: Created wandb run! {self.run_id}")

    def _load_from_checkpoint(self):
        try:
            with open(
                os.path.join(
                    self.config.checkpoint_load_folder,
                    self.checkpoint_file_name,
                ),
                "rt",
            ) as f:
                state = json.load(f)
            if "run_id" in state:
                self.run_id = state["run_id"]
            else:
                self.run_id = None
        except FileNotFoundError:
            print(
                f"{self.config.agent_controller_name}: Tried to load wandb run from checkpoint using the file at location {str(os.path.join(self.config.checkpoint_load_folder, self.checkpoint_file_name))}, but there is no such file! A new run will be created based on the config values instead."
            )
            self.run_id = None

    def save_checkpoint(self, folder_path):
        os.makedirs(folder_path, exist_ok=True)
        state = {"run_id": self.run_id}
        with open(
            os.path.join(
                folder_path,
                self.checkpoint_file_name,
            ),
            "wt",
        ) as f:
            json.dump(state, f, indent=4)
