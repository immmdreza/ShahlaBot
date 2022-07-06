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

    extra_names = message.command[1:]
    bot: ExtBot = application.bot

    fwded_message = await bot.forward_message(
        config.extra_channel_id, message.chat.id, message.reply_to_message.id
    )

    for extra_name in extra_names:

        extra = extra_list.find_one({"extra_name": extra_name})
        if extra:
            try:
                await bot.delete_message(
                    config.extra_channel_id, extra.extra_message_id
                )
            except:
                pass

            extra.extra_message_id = fwded_message.message_id
            extra_list.update_model(extra)
        else:
            extra = ExtraInfo(
                extra_name=extra_name, extra_message_id=fwded_message.message_id
            )
            extra_list.insert_one(extra)

    await message.reply_text(
        f"Extra(s) `{', '.join(extra_names)}` has been saved. You can now use it with `{', '.join(f'#{x}' for x in extra_names)}`."
    )
    await reporter.report(
        "Extra saved", f"Extra `{', '.join(extra_names)}` has been saved."
    )


@Shahla.on_message(command("delextra"))  # type: ignore
@async_injector
async def del_extra_requested(
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

    if not message.command or len(message.command) < 2:
        await message.reply_text(
            "Please use the command in the format `/setextra hello`."
        )
        return

    extra_list = database.extra_infos

    extra_names = message.command[1:]
    bot: ExtBot = application.bot

    for extra_name in extra_names:

        extra = extra_list.find_one({"extra_name": extra_name})
        if extra:
            try:
                await bot.delete_message(
                    config.extra_channel_id, extra.extra_message_id
                )
            except:
                pass
            extra_list.delete_one({"extra_name": extra_name})

    await message.reply_text(f"Extra(s) `{', '.join(extra_names)}` has been deleted.")
    await reporter.report(
        "Extra deleted", f"Extra `{', '.join(extra_names)}` has been deleted."
    )


@Shahla.on_message(command("extralist"))  # type: ignore
@async_injector
async def list_extra_requested(
    _: Shahla,
    message: Message,
    database: Database,
):

    extra_list = database.extra_infos

    extras = list(extra_list.find())

    if not extras:
        await message.reply_text("No extras found.")
        return

    await message.reply_text(
        "**Extras found**:\n" + "\n".join(f"`#{x.extra_name}`" for x in extras)
    )


@Shahla.on_message(regex("^#.*$"))  # type: ignore
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

    if not extra_name:
        return

    if extra_name in ["ski", "اسکی"]:
        # only shekar
        game_info = database.game_infos.find_one({"chat_id": message.chat.id})
        if not game_info:
            return

        if game_info.finished:
            return

        if game_info.shekar_user_id != message.from_user.id:
            return

    extra = extra_list.find_one({"extra_name": extra_name})
    if extra:
        bot: ExtBot = application.bot
        await bot.copy_message(
            message.chat.id, config.extra_channel_id, extra.extra_message_id
        )
