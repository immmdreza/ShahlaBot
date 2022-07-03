from telegram.ext import Application, ExtBot
from pyrogram.types import Message
from pyrogram.filters import command, reply, regex
from models.extra_info import ExtraInfo
from models.group_admin import Permissions

import services.database_helpers as db_helpers
from models.configuration import Configuration
from services.database import Database
from services.reporter import Reporter
from shahla import Shahla, async_injector


@Shahla.on_message(command("setextra") & reply)  # type: ignore
@async_injector
async def set_extra_requested(
    _: Shahla,
    message: Message,
    database: Database,
    config: Configuration,
    reporter: Reporter,
    application: Application,
):
    if not message.from_user:
        return

    sender_id = message.from_user.id
    admin = db_helpers.get_group_admin_with_permission(
        database, sender_id, Permissions.CanSaveExtra
    )

    if not admin:
        await message.reply_text("You are not allowed to save extras.")
        return

    if not message.reply_to_message:
        await message.reply_text("Please reply to a message.")
        return

    if not message.command or len(message.command) < 2:
        await message.reply_text(
            "Please use the command in the format `/setextra hello`."
        )
        return

    extra_list = database.extra_infos

    extra_name = message.command[1]
    bot: ExtBot = application.bot

    extra = extra_list.find_one({"extra_name": extra_name})
    if extra:
        await bot.delete_message(config.extra_channel_id, extra.extra_message_id)

        fwded_message = await bot.forward_message(
            config.extra_channel_id, message.chat.id, message.reply_to_message.id
        )
        extra.extra_message_id = fwded_message.message_id
        extra_list.update_model(extra)
    else:
        fwded_message = await bot.forward_message(
            config.extra_channel_id, message.chat.id, message.reply_to_message.id
        )
        extra = ExtraInfo(
            extra_name=extra_name, extra_message_id=fwded_message.message_id
        )
        extra_list.insert_one(extra)

    await message.reply_text(
        f"Extra `{extra_name}` has been saved. You can now use it with `#{extra_name}`."
    )
    await reporter.report("Extra saved", f"Extra `{extra_name}` has been saved.")


@Shahla.on_message(regex("^#.*"))  # type: ignore
@async_injector
async def get_extra_requested(
    _: Shahla,
    message: Message,
    database: Database,
    config: Configuration,
    application: Application,
):
    if not message.from_user:
        return

    extra_list = database.extra_infos

    extra_name = message.text.split("#")[1]
    extra = extra_list.find_one({"extra_name": extra_name})
    if extra:
        bot: ExtBot = application.bot
        await bot.copy_message(
            message.chat.id, config.extra_channel_id, extra.extra_message_id
        )
    else:
        await message.reply_text(f"Extra `{extra_name}` has not been saved.")
