from dataclasses import dataclass, field

from .model_base import ModelBase


@dataclass()
class Configuration(ModelBase):
    functional_chat: int
    bot_username: str
    self_username: str
    report_chat_id: int
    extra_channel_id: int
    maximum_warnings: int = field(default=5)
    super_admins: list[int] = field(default_factory=list)
