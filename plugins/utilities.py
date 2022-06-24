import pyrogram


@pyrogram.client.Client.on_message(pyrogram.filters.command("id"))  # type: ignore
async def on_id_requested(
    _: pyrogram.client.Client,
    message: pyrogram.types.Message,
):
    if message.reply_to_message:
        sender = message.reply_to_message.from_user
    else:
        sender = message.from_user

    if sender is None:
        await message.reply_text("I can't find the sender of this message.")
        return

    if sender.is_self:
        return

    await message.reply_text(f"{sender.first_name}'s id: `{sender.id}`", quote=True)


# Request chat id with chat_id command
@pyrogram.client.Client.on_message(pyrogram.filters.command("chat_id"))  # type: ignore
async def on_chat_id_requested(
    _: pyrogram.client.Client,
    message: pyrogram.types.Message,
):
    if message.reply_to_message:
        chat = message.reply_to_message.chat
    else:
        chat = message.chat

    if chat is None:
        await message.reply_text("I can't find the chat of this message.")
        return

    await message.reply_text(f"{chat.title}'s id: `{chat.id}`", quote=True)
