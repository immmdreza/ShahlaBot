from typing import AsyncGenerator, cast
from services.database import Database
from shahla import Shahla, async_injector
from pyrogram.types import Message, ChatMember
from pyrogram import filters
from pyrogram.enums.chat_members_filter import ChatMembersFilter
from models.group_admin import GroupAdmin, Permissions
from models.configuration import Configuration


@Shahla.on_message(filters.command("reload") & filters.group)  # type: ignore
@async_injector
async def reload_admins(
    _: Shahla, message: Message, config: Configuration, database: Database
):
    if not message.chat:
        return

    if not message.from_user:
        return

    if message.from_user.id not in config.super_admins:
        await message.reply("You are not an super admin.")
        return

    # database.group_admins.collection.drop()
    saved_admins = list(database.group_admins.find())
    found_admin_ids = set()
    async for admin in cast(
        AsyncGenerator[ChatMember, None],
        message.chat.get_members(filter=ChatMembersFilter.ADMINISTRATORS),
    ):
        if not admin.user:
            continue

        found_admin_ids.add(admin.user.id)
        if admin.user.is_bot:
            continue

        if any(
            admin.user.id == saved_admin.user_chat_id for saved_admin in saved_admins
        ):
            continue

        database.group_admins.insert_one(
            GroupAdmin(
                user_chat_id=admin.user.id,
                permissions=Permissions.All,
            )
        )

    for saved_admin in saved_admins:
        if saved_admin.user_chat_id not in found_admin_ids:
            database.group_admins.delete_one({"user_chat_id": saved_admin.user_chat_id})
