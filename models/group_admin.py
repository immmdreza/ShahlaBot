from enum import IntFlag
from .model_base import ModelBase, dataclass, field


class Permissions(IntFlag):
    Nothing = 0

    CanDelete = 1
    """Can delete message"""

    CanPin = 2
    """Can pin message"""

    CanWarn = 4
    """Warn users"""

    CanMiniMute = 8
    """Can mute users for a short time ( less than one hour )"""

    CanMiniBan = 16
    """Can ban users for a short time ( less than one hour )"""

    CanBan = 32
    """Can permanently ban users"""

    CanMute = 64
    """CAn permanently mute users"""

    CanSaveExtra = 128
    """Can save extra data"""

    NiniAdmin = CanDelete | CanPin | CanWarn | CanMiniMute | CanMiniBan
    """Can do everything except ban and mute"""

    Admin = NiniAdmin | CanBan | CanMute | CanSaveExtra
    """Can do everything"""

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
            Permissions.CanMiniMute: "Can Mini Mute",
            Permissions.CanMiniBan: "Can Mini Ban",
            Permissions.NiniAdmin: "Nini Admin",
            Permissions.Admin: "Admin",
        }.get(permissions, str(permissions))


@dataclass
class GroupAdmin(ModelBase):
    user_chat_id: int
    permissions: Permissions = field(default=Permissions.Nothing)
