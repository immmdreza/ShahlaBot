from services.database import Database
from shahla import Shahla, async_injector
from pyrogram.types import Message
from pyrogram import filters
from pyrogram.enums.chat_members_filter import ChatMembersFilter
from models.group_admin import GroupAdmin , Permissions
from models.configuration import Configuration


@Shahla.on_message(filters.command("reload") & filters.group)  # type: ignore
@async_injector
async def reload_admins(
    shahla: Shahla,
    message: Message,
    config: Configuration,
    database: Database
):
    database.group_admins.collection.drop()
    async for admin in shahla.get_chat_members(
        config.functional_chat , filter=ChatMembersFilter.ADMINISTRATORS
    ):
        if admin.user.is_bot != True:
            a = GroupAdmin(admin.user.id, Permissions.All)      
            database.group_admins.insert_one(a)
    await message.reply_text("Admin list has updated!")