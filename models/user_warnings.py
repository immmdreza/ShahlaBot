from dataclasses import dataclass

from .model_base import ModelBase


@dataclass
class UserWarning(ModelBase):
    user_chat_id: int
    warns_count: int = 0
    can_report: bool = True
