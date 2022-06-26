import pyrogram

group_id = -1001715439990

@pyrogram.client.Client.on_message(pyrogram.filters.command("reload"))
async def reload_admin_list(
    _: pyrogram.client.Client,
    message: pyrogram.types.Message,
):
    async for admin in _.get_chat_members(group_id, filter=pyrogram.enums.ChatMembersFilter.ADMINISTRATORS):
        print(admin)
        break
    message.reply_text("Admin list has updated!")
