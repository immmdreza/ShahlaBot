from typing import Optional
from .model_base import ModelBase, dataclass


@dataclass
class GameInfo(ModelBase):
    chat_id: int
    players_count: int
    alive_players: int
    finished: bool
    shekar_user_id: Optional[int] = None
    ski_text: Optional[str] = None
