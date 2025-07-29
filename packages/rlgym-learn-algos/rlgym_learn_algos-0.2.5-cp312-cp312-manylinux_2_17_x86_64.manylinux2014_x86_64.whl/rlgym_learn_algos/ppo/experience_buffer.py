import os
import pickle
from dataclasses import dataclass
from typing import Any, Dict, Generic, Iterable, List, Optional, Tuple

import numpy as np
import torch
from pydantic import BaseModel, Field, model_validator
from rlgym.api import ActionType, AgentID, ObsType, RewardType

from rlgym_learn_algos.util.torch_functions import get_device
from rlgym_learn_algos.util.torch_pydantic import PydanticTorchDevice

from .trajectory import Trajectory
from .trajectory_processor import (
    DerivedTrajectoryProcessorConfig,
    TrajectoryProcessor,
    TrajectoryProcessorConfig,
    TrajectoryProcessorData,
)

EXPERIENCE_BUFFER_FILE = "experience_buffer.pkl"


class ExperienceBufferConfigModel(BaseModel, extra="forbid"):
    max_size: int = 100000
    device: PydanticTorchDevice = "auto"
    save_experience_buffer_in_checkpoint: bool = True
    trajectory_processor_config: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def set_trajectory_processor_config(cls, data):
        if isinstance(data, ExperienceBufferConfigModel):
            if isinstance(data.trajectory_processor_config, BaseModel):
                data.trajectory_processor_config = (
                    data.trajectory_processor_config.model_dump()
                )
        elif isinstance(data, dict):
            if "trajectory_processor_config" in data:
                if isinstance(data["trajectory_processor_config"], BaseModel):
                    data["trajectory_processor_config"] = data[
                        "trajectory_processor_config"
                    ].model_dump()
            if "device" not in data:
                data["device"] = "auto"
            data["device"] = get_device(data["device"])
        return data


@dataclass
class DerivedExperienceBufferConfig:
    experience_buffer_config: ExperienceBufferConfigModel
    agent_controller_name: str
    seed: int
    dtype: torch.dtype
    learner_device: torch.device
    checkpoint_load_folder: Optional[str] = None


class ExperienceBuffer(
    Generic[
        TrajectoryProcessorConfig,
        AgentID,
        ObsType,
        ActionType,
        RewardType,
        TrajectoryProcessorData,
    ]
):
    @staticmethod
    def _cat(t1, t2, size):
        t2_len = len(t2)
        if t2_len > size:
            # t2 alone is larger than we want; copy the end
            # This clone is needed to avoid nesting views
            t = t2[-size:].clone()

        elif t2_len == size:
            # t2 is a perfect match; just use it directly
            t = t2

        elif len(t1) + t2_len > size:
            # t1+t2 is larger than we want; use t2 wholly with the end of t1 before it
            t = torch.cat((t1[t2_len - size :], t2), 0)

        else:
            # t1+t2 does not exceed what we want; concatenate directly
            t = torch.cat((t1, t2), 0)

        del t1
        del t2
        return t

    @staticmethod
    def _cat_list(cur, new, size):
        new_len = len(new)
        if new_len > size:
            t = new[-size:]
        elif new_len == size:
            t = new
        elif len(cur) + new_len > size:
            t = cur[new_len - size :] + new
        else:
            t = cur + new
        return t

    def __init__(
        self,
        trajectory_processor: TrajectoryProcessor[
            TrajectoryProcessorConfig,
            AgentID,
            ObsType,
            ActionType,
            RewardType,
            TrajectoryProcessorData,
        ],
    ):
        self.trajectory_processor = trajectory_processor
        self.agent_ids: List[AgentID] = []
        self.observations: List[ObsType] = []
        self.actions: List[ActionType] = []

    def load(self, config: DerivedExperienceBufferConfig):
        self.config = config
        self.rng = np.random.RandomState(config.seed)
        trajectory_processor_config = self.trajectory_processor.validate_config(
            config.experience_buffer_config.trajectory_processor_config
        )
        self.trajectory_processor.load(
            DerivedTrajectoryProcessorConfig(
                trajectory_processor_config=trajectory_processor_config,
                agent_controller_name=config.agent_controller_name,
                dtype=config.dtype,
                device=config.learner_device,
            )
        )
        self.log_probs = torch.tensor([], dtype=config.dtype)
        self.values = torch.tensor([], dtype=config.dtype)
        self.advantages = torch.tensor([], dtype=config.dtype)
        if self.config.checkpoint_load_folder is not None:
            self._load_from_checkpoint()
        self.log_probs = self.log_probs.to(config.learner_device)
        self.values = self.values.to(config.learner_device)
        self.advantages = self.advantages.to(config.learner_device)

    def _load_from_checkpoint(self):
        # lazy way
        # TODO: don't use pickle for torch things, use torch.load because of map_location. Or maybe define a custom unpickler for this? Or maybe one already exists?
        try:
            with open(
                os.path.join(
                    self.config.checkpoint_load_folder, EXPERIENCE_BUFFER_FILE
                ),
                "rb",
            ) as f:
                state_dict = pickle.load(f)
            self.agent_ids = state_dict["agent_ids"]
            self.observations = state_dict["observations"]
            self.actions = state_dict["actions"]
            self.log_probs = state_dict["log_probs"]
            self.values = state_dict["values"]
            self.advantages = state_dict["advantages"]
        except FileNotFoundError:
            print(
                f"{self.config.agent_controller_name}: Tried to load experience buffer from checkpoint using the file at location {str(os.path.join(self.config.checkpoint_load_folder, EXPERIENCE_BUFFER_FILE))}, but there is no such file! A blank experience buffer will be used instead."
            )

    def save_checkpoint(self, folder_path):
        os.makedirs(folder_path, exist_ok=True)
        if self.config.experience_buffer_config.save_experience_buffer_in_checkpoint:
            with open(
                os.path.join(folder_path, EXPERIENCE_BUFFER_FILE),
                "wb",
            ) as f:
                pickle.dump(
                    {
                        "agent_ids": self.agent_ids,
                        "observations": self.observations,
                        "actions": self.actions,
                        "log_probs": self.log_probs,
                        "values": self.values,
                        "advantages": self.advantages,
                    },
                    f,
                )
        self.trajectory_processor.save_checkpoint(folder_path)

    # TODO: update docs
    def submit_experience(
        self, trajectories: List[Trajectory[AgentID, ActionType, ObsType, RewardType]]
    ) -> TrajectoryProcessorData:
        """
        Function to add experience to the buffer.

        :param observations: An ordered sequence of observations from the environment.
        :param actions: The corresponding actions that were taken at each state in the `states` sequence.
        :param log_probs: The log probability for each action in `actions`
        :param rewards: A list of rewards such that rewards[i] is the reward for taking action actions[i] from observation observations[i]
        :param terminateds: An ordered sequence of the terminated flags from the environment.
        :param truncateds: An ordered sequence of the truncated flag from the environment.
        :param values: The output of the value function estimator evaluated on the observations.
        :param advantages: The advantage of each action at each state in `states` and `actions`

        :return: TrajectoryProcessorData
        """

        _cat = ExperienceBuffer._cat
        _cat_list = ExperienceBuffer._cat_list
        exp_buffer_data, trajectory_processor_data = (
            self.trajectory_processor.process_trajectories(trajectories)
        )
        (agent_ids, observations, actions, log_probs, values, advantages) = (
            exp_buffer_data
        )

        self.agent_ids = _cat_list(
            self.agent_ids, agent_ids, self.config.experience_buffer_config.max_size
        )
        self.observations = _cat_list(
            self.observations,
            observations,
            self.config.experience_buffer_config.max_size,
        )
        self.actions = _cat_list(
            self.actions, actions, self.config.experience_buffer_config.max_size
        )
        self.log_probs = _cat(
            self.log_probs,
            log_probs,
            self.config.experience_buffer_config.max_size,
        )
        self.values = _cat(
            self.values,
            values,
            self.config.experience_buffer_config.max_size,
        )
        self.advantages = _cat(
            self.advantages,
            advantages,
            self.config.experience_buffer_config.max_size,
        )

        return trajectory_processor_data

    # TODO: tensordict?
    def _get_samples(self, indices) -> Tuple[
        Iterable[AgentID],
        Iterable[ObsType],
        Iterable[ActionType],
        torch.Tensor,
        torch.Tensor,
        torch.Tensor,
    ]:
        return (
            [self.agent_ids[index] for index in indices],
            [self.observations[index] for index in indices],
            [self.actions[index] for index in indices],
            self.log_probs[indices],
            self.values[indices],
            self.advantages[indices],
        )

    def get_all_batches_shuffled(self, batch_size):
        """
        Function to return the experience buffer in shuffled batches. Code taken from the stable-baeselines3 buffer:
        https://github.com/DLR-RM/stable-baselines3/blob/2ddf015cd9840a2a1675f5208be6eb2e86e4d045/stable_baselines3/common/buffers.py#L482
        :param batch_size: size of each batch yielded by the generator.
        :return:
        """
        if self.config.learner_device.type != "cpu":
            torch.cuda.current_stream().synchronize()
        total_samples = self.values.shape[0]
        indices = self.rng.permutation(total_samples)
        start_idx = 0
        while start_idx + batch_size <= total_samples:
            yield self._get_samples(indices[start_idx : start_idx + batch_size])
            start_idx += batch_size

    def clear(self):
        """
        Function to clear the experience buffer.
        :return: None.
        """
        del self.observations
        del self.actions
        del self.log_probs
        del self.values
        del self.advantages
        self.__init__(self.trajectory_processor)
