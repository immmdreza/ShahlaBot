from html import escape

from pyrogram.filters import group, new_chat_members
from pyrogram.types import Message
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ExtBot

from services.database import Database
from services.reporter import Reporter
from shahla import Shahla, async_injector


@Shahla.on_message(new_chat_members & group)  # type: ignore
@async_injector
async def on_new_chat_member(
    _: Shahla,
    message: Message,
    app: Application,
    reporter: Reporter,
    database: Database,
):
    new_members = message.new_chat_members

    chat_id = message.chat.id
    bot: ExtBot = app.bot

    for user in new_members:
        await bot.send_message(
            chat_id,
            f"🔮 سلام <b>{escape(user.first_name)}</b>، به گروه رویداد های تسک خوش آمدی!\n\n"
            + "یادت نره حتما قوانین بازی در این رویداد رو کامل و با دقت بخونی که خدایی نکرده بن نشی :(",
            parse_mode="html",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "قوانین رویداد", url="https://t.me/TaskyEvents"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "راهنمای شرکت در رویداد",
                            url="https://t.me/TaskyEventsGuide",
                        )
                    ],
                ]
            ),
        )

        await reporter.report("NewMember", f"{user.first_name} [{user.id}] Joined.")
