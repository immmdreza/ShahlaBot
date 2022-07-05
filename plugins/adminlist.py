from pyrogram.filters import command, group
from pyrogram.types import Message

from services.database import Database
from shahla import Shahla, async_injector


@Shahla.on_message(command("adminlist") & group)  # type: ignore
@async_injector
async def on_purge_requested(
    _: Shahla,
    message: Message,
    database: Database,
):
    if not message.from_user:
        return

    admins = database.group_admins

    all_admins = list(admins.find())

    if not all_admins:
        await message.reply_text("No admins found.")
        return

    admin_list = f"**Admins list of {message.chat.title}**:\n\n"
    for admin in all_admins:
        admin_list += f"`{admin.user_chat_id}` - prmlvl: `{admin.permissions}`\n"

    await message.reply_text(admin_list)
