from datetime import datetime, timedelta

from pyrogram.filters import command, group
from pyrogram.types import Message , ChatPermissions
from pyrogram.errors import BadRequest

import services.database_helpers as db_helpers
from models.configuration import Configuration
from models.group_admin import Permissions
from services.database import Database
from services.reporter import Reporter
from shahla import Shahla, async_injector
from helpers import parse_time


@Shahla.on_message(command("mute") & group)  # type: ignore
@async_injector
async def mute(
    shahla: Shahla,
    message: Message,
    database: Database,
    config: Configuration,
    reporter: Reporter,
):
    admins = database.group_admins

    if not message.from_user:
        return

    sender_id = message.from_user.id

    target_user, others = await shahla.resolve_target_user_and_others_from_command(
        message
    )

    if target_user is None or not any(others):
        await message.reply_text(
            "Please reply to a user or use the command in the format `/mute @username reason`."
        )
        return

    parsed_time = parse_time(others[0])
    if parsed_time is None or parsed_time == timedelta():
        parsed_time = timedelta.max
        duration_str = "Forever"
        reason = " ".join(others)
    else:
        reason = " ".join(others[1:])
        duration_str = str(parsed_time)

    required_permissions = Permissions.CanMiniMute
    if parsed_time > timedelta(hours=1):
        required_permissions = Permissions.CanMute

    admin = db_helpers.get_group_admin_with_permission(
        database, sender_id, required_permissions
    )

    if admin is None:
        await message.reply_text("You're missing permissions.")
        return

    # admin can mute users ...
    if target_user.id == sender_id:
        await message.reply_text("You can't mute yourself.")
        return

    if target_user in config.super_admins:
        await message.reply_text("You can't mute a super admin.")
        return

    # check if target is not an admin
    if admins.exists(dict(user_chat_id=target_user.id)):
        await message.reply_text("You can't mute an admin.")
        return

    try:
        await shahla.restrict_chat_member(
            message.chat.id,
            target_user.id,
            ChatPermissions(can_send_messages = False),
            until_date=datetime.utcnow() + parsed_time,
        )
        await message.reply_text(
            f"User {target_user.first_name} muted by {message.from_user.first_name}\nreason: {reason}\nduration: {duration_str}"
        )
        await reporter.report(
            "Ban",
            f"User {target_user.first_name} muted by {message.from_user.first_name}\nreason: {reason}\nduration: {duration_str}",
        )
    except BadRequest as e:
        await message.reply_text(f"Can't mute: {e.MESSAGE}")
