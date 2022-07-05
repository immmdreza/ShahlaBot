from enum import IntFlag
from .model_base import ModelBase, dataclass, field


class Permissions(IntFlag):
    Nothing = 0
    CanWarn = 1
    """Warn users"""

    CanBan = 2
    """Can permanently ban users"""

    CanMute = 4
    """CAn permanently mute users"""

    CanDelete = 8
    """Can delete message"""

    CanPin = 16
    """Can pin message"""

    CanSaveExtra = 32
    """Can save extra data"""

    CanMiniMute = 64
    """Can mute users for a short time ( less than one hour )"""

    CanMiniBan = 128
    """Can ban users for a short time ( less than one hour )"""

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
