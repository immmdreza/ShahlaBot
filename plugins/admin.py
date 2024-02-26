from html import escape

from pyrogram.filters import command, group, reply
from pyrogram.types import Message
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ExtBot

import services.database_helpers as db_helpers
from models.configuration import Configuration
from models.group_admin import Permissions
from models.user_warnings import UserWarning
from services.database import Database
from services.reporter import Reporter
from shahla import Shahla, async_injector


@Shahla.on_message(command("admin", ["/", "@"]) & group & reply)  # type: ignore
@async_injector
async def on_admin_requested(
    _: Shahla,
    message: Message,
    reporter: Reporter,
    database: Database,
    application: Application,
):
    if not message.from_user:
        return

    if not message.reply_to_message:
        return

    user = database.user_warnings.find_one({"user_chat_id": message.from_user.id})
    if user and not user.can_report:
        return

    admins = list(database.group_admins.find())
    if not admins:
        return

    report_msg = (
        f"User {escape(message.from_user.first_name)} [<code>{message.from_user.id}</code>] has reported "
        f"{escape(message.reply_to_message.from_user.first_name)} [<code>{message.reply_to_message.from_user.id}</code>] "
        f"On Message: <code>{message.reply_to_message.link}</code>"
    )

    bot: ExtBot = application.bot

    await message.reply_text("Message reported to admins.")

    await reporter.report_full_by_user(
        "User Report",
        report_msg,
        message.from_user,
        message.reply_to_message.from_user,
    )

    for admin in admins:
        try:
            await bot.send_message(
                admin.user_chat_id,
                report_msg,
                parse_mode="html",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("View Report", url=message.link)]]
                ),
            )
        except:
            pass


@Shahla.on_message(command("repoff") & group)  # type: ignore
@async_injector
async def on_repoff_requested(
    _: Shahla,
    message: Message,
    reporter: Reporter,
    database: Database,
    config: Configuration,
):
    if not message.from_user:
        return
    sender_id = message.from_user.id

    # Turn of report for user by admin
    admin = db_helpers.get_group_admin_with_permission(
        database, message.from_user.id, Permissions.Nothing
    )
    if not admin:
        return

    target_user = await _.resolve_target_user_from_command(message)
    if not target_user:
        return

    # admin can mute users ...
    if target_user.id == sender_id:
        await message.reply_text("You can't mute yourself.")
        return

    if target_user in config.super_admins:
        await message.reply_text("You can't mute a super admin.")
        return

    # check if target is not an admin
    if database.group_admins.exists(dict(user_chat_id=target_user.id)):
        await message.reply_text("You can't mute an admin.")
        return

    user = database.user_warnings.find_one({"user_chat_id": target_user.id})
    if not user:
        database.user_warnings.insert_one(
            UserWarning(
                user_chat_id=target_user.id,
                can_report=False,
                warns_count=0,
            )
        )
        await message.reply_text("User report disabled.")
        await reporter.report_full_by_user(
            "User Report Disabled",
            f"User {escape(target_user.first_name)} [<code>{target_user.id}</code>] has disabled report.",
            message.from_user,
            target_user,
        )
    else:

        if user.can_report:
            database.user_warnings.update_one(
                {"user_chat_id": target_user.id},
                {"$set": {"can_report": False}},
            )
            await message.reply_text("User report disabled.")
            await reporter.report_full_by_user(
                "User Report Disabled",
                f"User {escape(target_user.first_name)} [`{target_user.id}`] has disabled report.",
                message.from_user,
                target_user,
            )
        else:
            # Enable report for user
            database.user_warnings.update_one(
                {"user_chat_id": target_user.id},
                {"$set": {"can_report": True}},
            )
            await message.reply_text("User report enabled.")
            await reporter.report_full_by_user(
                "User Report Enabled",
                f"User {escape(target_user.first_name)} [`{target_user.id}`] has enabled report.",
                message.from_user,
                target_user,
            )
