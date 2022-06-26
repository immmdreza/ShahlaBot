import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

import asyncio
import os
from typing import cast

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatMemberHandler, CommandHandler

from shahla import Shahla, LifeTime
from services.reporter import Reporter
from services.database import Database
from models.configuration import Configuration
from plugins.bot_handlers.reporters import chat_member_updated


load_dotenv()
api_id = int(cast(str, os.getenv("API_ID")))
api_hash = cast(str, os.getenv("API_HASH"))
bot_token = cast(str, os.getenv("BOT_TOKEN"))

shahla = Shahla(
    "ShahlaBot",
    api_id,
    api_hash,
    plugins={"root": "plugins", "exclude": ["bot_handlers"]},
)

application = ApplicationBuilder().token(bot_token).build()


async def main():
    shahla.register_type(Database, lambda _: Database("shahla"))
    shahla.register_type(Configuration, lambda s: s.request_instance(Database).set_up())
    shahla.register_type(
        Reporter,
        lambda s: Reporter(s, s.request_instance(Configuration).report_chat_id),
        LifeTime.Scoped,
    )

    await shahla.start()

    user_bot = await shahla.get_me()
    print(f"User bot is {user_bot.first_name}", user_bot.id)

    application.bot_data["shahla"] = shahla

    chat_member_handler = ChatMemberHandler(
        chat_member_updated, ChatMemberHandler.ANY_CHAT_MEMBER
    )
    application.add_handler(chat_member_handler)

    bot_info = await application.bot.get_me()
    print(f"User bot is {bot_info.first_name}", bot_info.id)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    application.run_polling(allowed_updates=[Update.MY_CHAT_MEMBER, Update.CHAT_MEMBER])
