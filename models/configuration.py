from .model_base import ModelBase, dataclass, field


@dataclass()
class Configuration(ModelBase):
    functional_chat: int
    bot_username: str
    self_username: str
    report_chat_id: int
    super_admins: list[int] = field(default_factory=list)
