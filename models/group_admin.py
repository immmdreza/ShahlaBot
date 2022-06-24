from enum import IntFlag
from .model_base import ModelBase, dataclass, field


class Permissions(IntFlag):
    Null = 0
    CanWarn = 1
    CanBan = 2
    CanMute = 4
    CanDelete = 8

    All = CanWarn | CanBan | CanMute | CanDelete


@dataclass
class GroupAdmin(ModelBase):
    user_chat_id: int
    permissions: Permissions = field(default=Permissions.Null)
