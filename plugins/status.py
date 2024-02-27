"""
Shows user status in group, including number of warnings and admin status.
"""

from pyrogram.filters import command, group
from pyrogram.types import Message

import services.database_helpers as db_helpers
from models.configuration import Configuration
from models.group_admin import Permissions
from services.database import Database
from shahla import Shahla, async_injector, shahla_command


@Shahla.on_message(shahla_command("status", description="Shows user status", notes=(,)) & group)  # type: ignore
@async_injector
async def on_status_requested(
    shahla: Shahla,
    message: Message,
    config: Configuration,
    database: Database,
):
    warnings = database.user_warnings

    if not message.from_user:
        return

    target_user = await shahla.resolve_target_user_from_command(message)
    if not target_user:
        target_user = message.from_user
    else:
        # Requester should be an admin to see other user's status
        admin = db_helpers.get_group_admin_with_permission(
            database, message.from_user.id, Permissions.Nothing
        )
        if not admin:
            target_user = message.from_user

    warns = warnings.find_one({"user_chat_id": target_user.id})
    admin = db_helpers.get_group_admin_with_permission(
        database, target_user.id, Permissions.Nothing
    )

    warns_count = 0
    if warns:
        warns_count = warns.warns_count

    if admin is not None:
        is_admin = True
        permission_level = admin.permissions
    else:
        permission_level = 0
        is_admin = False

    is_super_admin = target_user.id in config.super_admins

    await message.reply_text(
        f"⚠️ User {target_user.first_name} has {warns_count} warnings.\n"
        f"✨ Is admin: {is_admin}\n"
        f"🌡️ Permission level: {permission_level}\n"
        f"🧁 Is super admin: {is_super_admin}"
    )
