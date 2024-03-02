from dataclasses import dataclass

from models.model_base import ModelBase


@dataclass
class GameAction(ModelBase):
    done_by_role: str
    worth: int
    one_time: bool = True
