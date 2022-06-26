import pyrogram


@pyrogram.client.Client.on_message(pyrogram.filters.command("id"))  # type: ignore
async def on_id_requested(
    _: pyrogram.client.Client,
    message: pyrogram.types.Message,
):

    if len(message.command) > 1:
        if message.command[1][0] == "@":
            user = await _.get_users(message.command[1])
            id = user.id
            name = user.first_name
        elif await _.get_users(message.command[1]): 
            user = await _.get_users(message.command[1])
            id = user.id
            name = user.first_name
        else:
            pass
    elif message.reply_to_message:
        id = message.reply_to_message.from_user.id
        name = message.reply_to_message.from_user.first_name
    else:
        id = message.chat.id
        name = message.chat.title

    if message.from_user is None:
        await message.reply_text("I can't find the sender of this message.")
        return

    if message.from_user.is_self:
        return

    await message.reply_text(f"{name}'s id: `{id}`", quote=True)

