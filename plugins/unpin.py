from pyrogram.filters import command, group
from pyrogram.types import Message

import services.database_helpers as db_helpers
from models.group_admin import Permissions
from services.database import Database
from services.reporter import Reporter
from shahla import Shahla, async_injector, shahla_command


@Shahla.on_message(shahla_command("unpin", , description="Unpin a message.", notes=("Admins only",)) & group)  # type: ignore
@async_injector
async def on_unpin_requested(
    _: Shahla,
    message: Message,
    reporter: Reporter,
    database: Database,
):
    sender_id = message.from_user.id
    admin = db_helpers.get_group_admin_with_permission(
        database, sender_id, Permissions.CanPin
    )

    if not admin:
        await message.reply_text("You are not allowed to unpin messages.")
        return

    if message.reply_to_message:
        await message.reply_to_message.unpin()
    else:
        await message.reply_text("please reply to a message")

    await reporter.report_full_by_user(
        "pin", f"\n{message.from_user.first_name}) pinned a message", message.from_user
    )
