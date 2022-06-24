from pyrogram.client import Client
from pyrogram.types import Message
from pyrogram.filters import command, group

from shahla import Shahla, async_injector
from services.reporter import Reporter
from services.database import Database
from models.user_warnings import UserWarning
from models.group_admin import GroupAdmin, Permissions


@Client.on_message(filters=command("warn") & group)  # type: ignore
@async_injector
async def on_message(
    shahla: Shahla, message: Message, reporter: Reporter, database: Database
):
    warnings = database.user_warnings
    admins = database.group_admins

    if not message.from_user:
        return

    sender_id = message.from_user.id
    admin = admins.find_one(user_chat_id=sender_id)
    if admin is None:
        await message.reply_text("You are not an admin of this group.")
        return

    if not admin.permissions.CanWarn:
        await message.reply_text("You are not allowed to warn users.")
        return

    # admin can warn users ...
    ...
