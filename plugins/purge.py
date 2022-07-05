from pyrogram.filters import command, group, reply
from pyrogram.types import Message
from models.group_admin import Permissions

import services.database_helpers as db_helpers
from services.database import Database
from services.reporter import Reporter
from shahla import Shahla, async_injector


@Shahla.on_message(command("purge") & group & reply)  # type: ignore
@async_injector
async def on_purge_requested(
    shahla: Shahla,
    message: Message,
    reporter: Reporter,
    database: Database,
):
    if not message.from_user:
        return

    if not message.reply_to_message:
        return

    replied_message_id = message.reply_to_message.id

    admin = db_helpers.get_group_admin_with_permission(
        database, message.from_user.id, Permissions.CanWarn
    )

    if not admin:
        await message.reply_text("You are not allowed to delete messages.")
        return

    # delete all messages from the replied message to this
    deleted = await shahla.delete_messages(
        message.chat.id, range(replied_message_id, message.id)
    )
    await message.reply_text(f"Deleted {deleted} messages.")
    await reporter.report(
        "Purge",
        f"Purged {deleted} messages. from message at date {message.reply_to_message.date.isoformat()} to {message.date.isoformat()}\nBy: {message.from_user.first_name}",
    )
