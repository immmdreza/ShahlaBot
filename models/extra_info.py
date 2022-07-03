from .model_base import ModelBase, dataclass


@dataclass
class ExtraInfo(ModelBase):
    extra_name: str
    extra_message_id: int
