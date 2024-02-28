from html import escape

from pyrogram.filters import group, new_chat_members
from pyrogram.types import Message
from telegram.ext import Application, ExtBot

from services.database import Database
from services.reporter import Reporter
from shahla import Shahla, async_injector


@Shahla.on_message(new_chat_members & group)  # type: ignore
@async_injector
async def on_new_chat_member(
    _: Shahla,
    app: Application,
    message: Message,
    reporter: Reporter,
    database: Database,
):
    new_members = message.new_chat_members

    chat_id = message.chat.id
    bot: ExtBot = app.bot

    for user in new_members:
        await bot.send_message(
            chat_id,
            f"Hello {escape(user.first_name)}, Welcome to the <b>Tasky Event Group</b>.",
            parse_mode="html",
        )
