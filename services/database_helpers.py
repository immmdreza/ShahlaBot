from models.group_admin import Permissions
from services.database import Database


def get_group_admin_with_permission(
    database: Database, user_id: int, permission: Permissions
):
    group_admins = database.group_admins
    admin = group_admins.find_one(dict(user_chat_id=user_id))
    if admin is None:
        return None

    if permission in Permissions(admin.permissions):
        admin.permissions = Permissions(admin.permissions)
        return admin
    return None
