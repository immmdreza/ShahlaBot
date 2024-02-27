from datetime import datetime, timedelta

from pyrogram.filters import command, group
from pyrogram.types import ChatPermissions, Message

import services.database_helpers as db_helpers
from models.configuration import Configuration
from models.group_admin import Permissions
from models.user_warnings import UserWarning
from services.database import Database
from services.reporter import Reporter
from shahla import Shahla, async_injector, shahla_command

WARN_MESSAGE_FMT = (
    "User {target_fn} has been warned "
    "By: {admin_fn}\n"
    "Reason: {reason}\n"
    "Warnings: {warns_count}"
)


@Shahla.on_message(shahla_command("warn", description="Warns a user.", notes=("Admins only",)) & group)  # type: ignore
@async_injector
async def on_warn_requested(
    shahla: Shahla,
    message: Message,
    config: Configuration,
    reporter: Reporter,
    database: Database,
):
    warnings = database.user_warnings
    admins = database.group_admins

    if not message.from_user:
        return

    target_user, others = (
        await shahla.resolve_target_user_and_others_from_command(message)
    )
    if not target_user:
        await message.reply_text(
            "Please reply to a user or use the command in the format `/warn @username`."
        )
        return

    if not any(others):
        await message.reply_text(
            "Please reply to a user or use the command in the format `/warn @username reason`."
        )
        return

    sender_id = message.from_user.id
    admin = db_helpers.get_group_admin_with_permission(
        database, sender_id, Permissions.CanWarn
    )

    if not admin:
        await message.reply_text("You are not allowed to warn users.")
        return

    # admin can warn users ...
    if target_user.id == sender_id:
        await message.reply_text("You can't warn yourself.")
        return

    if target_user in config.super_admins:
        await message.reply_text("You can't warn a super admin.")
        return

    # check if target is not an admin
    if admins.exists({"user_chat_id": target_user.id}):
        await message.reply_text("You can't warn an admin.")
        return

    # check if there's a reason in command
    reason = " ".join(others)

    # increase warning count
    warning = warnings.find_one({"user_chat_id": target_user.id})
    if warning is None:
        warning = UserWarning(user_chat_id=target_user.id, warns_count=1)
        warnings.insert_one(warning)

        text = WARN_MESSAGE_FMT.format(
            target_fn=target_user.first_name,
            admin_fn=message.from_user.first_name,
            reason=reason,
            warns_count=1,
        )
        await message.reply_text(text)
        await reporter.report_full_by_user(
            "Warning", text, message.from_user, target_user
        )
    else:
        warning.warns_count += 1
        if warning.warns_count + 1 > config.maximum_warnings:
            if Permissions.CanBan in admin.permissions:
                await message.chat.restrict_member(
                    target_user.id,
                    ChatPermissions(),
                    until_date=datetime.now() + timedelta(days=1),
                )
                warning.warns_count = 0
                warnings.update_model(warning)
                await message.reply_text(
                    "User {target_fn} has been banned for 1 day (maximum warns).".format(
                        target_fn=target_user.first_name
                    )
                )
                await reporter.report_full_by_user(
                    "Ban",
                    "User {target_fn} has been banned for 1 day (maximum warns).".format(
                        target_fn=target_user.first_name
                    ),
                    message.from_user,
                    target_user,
                )
                return
            else:
                await message.reply_text(
                    "You can't warn a user with maximum warns."
                )
                return

        warnings.update_model(warning)

        text = WARN_MESSAGE_FMT.format(
            target_fn=target_user.first_name,
            admin_fn=message.from_user.first_name,
            reason=reason,
            warns_count=warning.warns_count,
        )
        await message.reply_text(text)
        await reporter.report_full_by_user(
            "Warning", text, message.from_user, target_user
        )
