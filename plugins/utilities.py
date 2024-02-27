from pyrogram.filters import command
from pyrogram.types import Message

from shahla import Shahla, shahla_command


@Shahla.on_message(shahla_command("id", description="Identify a user."))  # type: ignore
async def on_id_requested(client: Shahla, message: Message):

    if message.from_user is None:
        await message.reply_text("I can't find the sender of this message.")
        return

    target_user = await client.resolve_target_user_from_command(message)

    if target_user is not None:
        user_id = target_user.id
        name = target_user.first_name
    else:
        if message.chat:
            user_id = message.chat.id
            name = message.chat.title
        else:
            user_id = message.from_user.id
            name = message.from_user.first_name

    if message.from_user.is_self:
        return

    await message.reply_text(f"{name}'s id: `{user_id}`", quote=True)
