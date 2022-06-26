from pyrogram.types import Message
from pyrogram.filters import command, group

from shahla import Shahla, async_injector
from services.reporter import Reporter
from services.database import Database
from models.user_warnings import UserWarning
from models.group_admin import GroupAdmin, Permissions


WARN_MESSAGE_FMT = (
    "{target_fn} has been warned "
    "By: {admin_fn}\n"
    "Reason: {reason}\n"
    "Warnings: {warns_count}"
)


@Shahla.on_message(filters=command("warn") & group)  # type: ignore
@async_injector
async def on_message(
    shahla: Shahla, message: Message, reporter: Reporter, database: Database
):
    warnings = database.user_warnings
    admins = database.group_admins

    if not message.from_user:
        return

    target_user = await shahla.resolve_target_user_from_command(message)
    if not target_user:
        await message.reply_text(
            "Please reply to a user or use the command in the format `/warn @username`."
        )
        return

    sender_id = message.from_user.id
    admin = admins.find_one(dict(user_chat_id=sender_id))
    if admin is None:
        await message.reply_text("You are not an admin of this group.")
        return

    if not admin.permissions.CanWarn:
        await message.reply_text("You are not allowed to warn users.")
        return

    # admin can warn users ...
    if target_user.id == sender_id:
        await message.reply_text("You can't warn yourself.")
        return

    # check if target is not an admin
    if admins.exists(dict(user_chat_id=target_user.id)):
        await message.reply_text("You can't warn an admin.")
        return

    # increase warning count
    warning = warnings.find_one(dict(user_chat_id=target_user.id))
    if warning is None:
        warning = UserWarning(user_chat_id=target_user.id, warns_count=1)
        warnings.insert_one(warning)

        await message.reply_text(
            f"{target_user.first_name} has been warned "
            f"By: {message.from_user.first_name}\n"
            f"Warnings: {warning.warns_count}"
        )
    else:
        warning.warns_count += 1

        # TODO: ban on maximum warns

        warnings.update_one(dict(_id=warning.id), warning)

        await message.reply_text(
            f"{target_user.first_name} has been warned "
            f"By: {message.from_user.first_name}\n"
            f"Warnings: {warning.warns_count}"
        )
