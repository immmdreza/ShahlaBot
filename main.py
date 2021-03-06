# import logging

# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )

import asyncio
from urllib.parse import quote_plus

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, Application
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import helpers
import services.group_lock as lock_service
from shahla import Shahla, LifeTime
from services.reporter import Reporter
from services.database import Database
from models.configuration import Configuration
from plugins.bot_handlers.reporters import chat_member_updated_handler
from plugins.bot_handlers.permission_editor import (
    open_permission_editor_handler,
    edit_permissions_handler,
    close_editor_handler,
)


load_dotenv()
api_id = helpers.get_from_env("API_ID", int)
api_hash = helpers.get_from_env("API_HASH")
bot_token = helpers.get_from_env("BOT_TOKEN")
main_chat_id = helpers.get_from_env("MAIN_CHAT_ID", int)
report_channel_id = helpers.get_from_env("REPORT_CHANNEL_ID", int)
extra_channel_id = helpers.get_from_env("EXTRA_CHANNEL_ID", int)
bot_username = helpers.get_from_env("BOT_USERNAME")
self_username = helpers.get_from_env("SELF_USERNAME")
bot_admins = helpers.get_from_env("SUPER_ADMINS", helpers.deserialize_list)
mongo_username = helpers.get_from_env("MONGO_USERNAME")
mongo_password = helpers.get_from_env("MONGO_PASSWORD")
mongo_host = helpers.get_from_env("MONGO_HOST")
session_string = helpers.get_from_env("SESSION_STRING")

shahla = Shahla(
    ":memory:",
    api_id,
    api_hash,
    session_string=session_string,
    plugins={"root": "plugins", "exclude": ["bot_handlers"]},
)

application = ApplicationBuilder().token(bot_token).build()


async def main():
    if mongo_username and mongo_password and mongo_host:
        host_addr = "mongodb://%s:%s@%s" % (
            quote_plus(mongo_username),
            quote_plus(mongo_password),
            mongo_host,
        )
    else:
        host_addr = None

    shahla.register_type(Database, lambda _: Database("shahla", host_addr))
    config = Configuration(
        main_chat_id,
        bot_username,
        self_username,
        report_channel_id,
        extra_channel_id,
        5,
        bot_admins,
    )
    shahla.register_type(
        Configuration, lambda s: s.request_instance(Database).set_up(config)
    )
    shahla.register_type(
        Reporter,
        lambda s: Reporter(s, s.request_instance(Configuration).report_chat_id),
        LifeTime.Scoped,
    )
    shahla.register_type(Application, lambda _: application)

    await shahla.start()

    # ss = await shahla.export_session_string()
    # print(ss)

    user_bot = await shahla.get_me()
    print(f"User bot is {user_bot.first_name}", user_bot.id)

    application.bot_data["shahla"] = shahla

    application.add_handler(chat_member_updated_handler)
    application.add_handler(open_permission_editor_handler)
    application.add_handler(edit_permissions_handler)
    application.add_handler(close_editor_handler)

    bot_info = await application.bot.get_me()
    print(f"User bot is {bot_info.first_name}", bot_info.id)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    aps = AsyncIOScheduler()

    aps.add_job(
        lock_service.notify_before_lock,
        # Every day at 00:30 (Asia/Tehran), the group will be notified (30 min) before lock.
        CronTrigger(hour=1, minute=30, timezone="Asia/Tehran"),
        kwargs={"shahla": shahla},
    )
    aps.add_job(
        lock_service.group_locker,
        # Every day at 01:00 AM (Asia/Tehran), the group will be locked
        CronTrigger(hour=2, timezone="Asia/Tehran"),
        kwargs={"shahla": shahla},
    ),

    aps.start()
    loop.run_until_complete(main())
    application.run_polling(
        allowed_updates=[
            Update.MY_CHAT_MEMBER,
            Update.CHAT_MEMBER,
            Update.INLINE_QUERY,
            Update.CALLBACK_QUERY,
        ]
    )
