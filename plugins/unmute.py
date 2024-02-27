from pyrogram.filters import command, group
from pyrogram.types import ChatPermissions, Message

import services.database_helpers as db_helpers
from models.configuration import Configuration
from models.group_admin import Permissions
from services.database import Database
from services.reporter import Reporter
from shahla import Shahla, async_injector, shahla_command

UNMUTE_MESSAGE_FMT = (
    "User {target_fn} has been unmuted " "By: {admin_fn}\n" "Reason: {reason}\n"
)


@Shahla.on_message(shahla_command("unmute", description="Unmute someone.", notes=("Admins only",)) & group)  # type: ignore
@async_injector
async def on_unmute_requested(
    shahla: Shahla,
    message: Message,
    config: Configuration,
    reporter: Reporter,
    database: Database,
):
    admins = database.group_admins

    if not message.from_user:
        return

    target_user, others = (
        await shahla.resolve_target_user_and_others_from_command(message)
    )
    if not target_user:
        await message.reply_text(
            "Please reply to a user or use the command in the format `/unmute @username`."
        )
        return

    if not any(others):
        await message.reply_text(
            "Please reply to a user or use the command in the format `/unmute @username reason`."
        )
        return

    sender_id = message.from_user.id
    admin = db_helpers.get_group_admin_with_permission(
        database, sender_id, Permissions.CanMute
    )

    if not admin:
        await message.reply_text("You are not allowed to unmute users.")
        return

    # admin can unmute users ...
    if target_user.id == sender_id:
        await message.reply_text("You can't unmute yourself.")
        return

    if target_user in config.super_admins:
        await message.reply_text("You can't unmute a super admin.")
        return

    # check if target is not an admin
    if admins.exists(dict(user_chat_id=target_user.id)):
        await message.reply_text("You can't unmute an admin.")
        return

    # check if there's a reason in command
    reason = " ".join(others)

    text = UNMUTE_MESSAGE_FMT.format(
        target_fn=target_user.first_name,
        admin_fn=message.from_user.first_name,
        reason=reason,
    )
    await shahla.restrict_chat_member(
        message.chat.id,
        target_user.id,
        ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_send_polls=True,
            can_add_web_page_previews=True,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True,
        ),
    )
    await message.reply_text(text)
    await reporter.report_full_by_user(
        "Unmuted", text, message.from_user, target_user
    )
