from dataclasses import dataclass

from models.model_base import ModelBase


@dataclass
class ActionRewardLog(ModelBase):
    user_id: int
    reward_worth: int
    # action_name: str
