from pyrogram.filters import command, group
from pyrogram.types import Message

import services.database_helpers as db_helpers
from models.configuration import Configuration
from models.group_admin import Permissions
from services.database import Database
from services.reporter import Reporter
from shahla import Shahla, async_injector, shahla_command

UN_WARN_MESSAGE_FMT = (
    "User {target_fn} has been unwarned "
    "By: {admin_fn}\n"
    "Reason: {reason}\n"
    "Warnings: {warns_count}"
)


@Shahla.on_message(shahla_command("unwarn", , description="Removes someones's warning", notes=("Admins only",)) & group)  # type: ignore
@async_injector
async def on_un_warn_requested(
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

    target_user, others = await shahla.resolve_target_user_and_others_from_command(
        message
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
        await message.reply_text("You can't unwarn yourself.")
        return

    if target_user in config.super_admins:
        await message.reply_text("You can't unwarn a super admin.")
        return

    # check if target is not an admin
    if admins.exists(dict(user_chat_id=target_user.id)):
        await message.reply_text("You can't unwarn an admin.")
        return

    # check if there's a reason in command
    reason = " ".join(others)

    # increase warning count
    warning = warnings.find_one(dict(user_chat_id=target_user.id))
    if warning is None:
        await message.reply_text("User has no warnings yet!")
    else:
        if warning.warns_count == 0:
            await message.reply_text("User has no warnings anymore!")
        else:
            warning.warns_count -= 1
            warnings.update_model(warning)

            text = UN_WARN_MESSAGE_FMT.format(
                target_fn=target_user.first_name,
                admin_fn=message.from_user.first_name,
                reason=reason,
                warns_count=warning.warns_count,
            )
            await message.reply_text(text)
            await reporter.report_full_by_user(
                "Un_Warning", text, message.from_user, target_user
            )
