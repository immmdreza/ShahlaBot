from enum import IntFlag
from .model_base import ModelBase, dataclass, field


class Permissions(IntFlag):
    Nothing = 0
    CanWarn = 1
    CanBan = 2
    CanMute = 4
    CanDelete = 8
    CanPin = 16
    CanSaveExtra = 32

    @staticmethod
    def all():
        perm = Permissions.Nothing
        for value in Permissions.iter_permissions():
            perm |= value
        return perm

    @staticmethod
    def iter_permissions():
        yield from Permissions.__members__.values()

    @staticmethod
    def to_string(permissions: "Permissions"):
        return {
            Permissions.Nothing: "None",
            Permissions.CanWarn: "Can Warn",
            Permissions.CanBan: "Can Ban",
            Permissions.CanMute: "Can Mute",
            Permissions.CanDelete: "Can Delete",
            Permissions.CanPin: "Can Pin",
            Permissions.CanSaveExtra: "Can Save Extra",
        }.get(permissions, str(permissions))


@dataclass
class GroupAdmin(ModelBase):
    user_chat_id: int
    permissions: Permissions = field(default=Permissions.Nothing)
