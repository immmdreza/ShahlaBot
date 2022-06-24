from .model_base import ModelBase, dataclass, field


@dataclass()
class Configuration(ModelBase):
    functional_chat: int | None = field(default=None)
    username: str | None = field(default=None)
    report_chat_id: int | None = field(default=None)
    super_admins: list[int] = field(default_factory=list)
