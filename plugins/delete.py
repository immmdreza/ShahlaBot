from pyrogram.types import Message
from pyrogram.filters import command, group

from models.group_admin import Permissions
import services.database_helpers as db_helpers
from shahla import Shahla, async_injector
from services.reporter import Reporter
from services.database import Database


@Shahla.on_message(command("d") & group)  # type: ignore
@async_injector
async def on_delete_requested(
    _: Shahla,
    message: Message,
    reporter: Reporter,
    database: Database,
):
    sender_id = message.from_user.id
    admin = db_helpers.get_group_admin_with_permission(
        database, sender_id, Permissions.CanDelete
    )

    if not admin:
        await message.reply_text("You are not allowed to delete messages.")
        return

    # admin can delete messages ...
    if message.reply_to_message:
        await message.reply_to_message.delete()
    else:
        await message.reply_text("please reply to a message")

    await reporter.report(
        "Delete", f"\n{message.from_user.first_name}) deleted a message"
    )
