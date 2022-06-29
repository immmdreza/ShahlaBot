from shahla import Shahla
from pyrogram.types import Message
from pyrogram.filters import regex ,user


@Shahla.on_message(regex("مدت زمان بازی:") & user(175844556))  # type: ignore
async def confirm(
    _: Shahla,
    message: Message,
):
    await message.reply_text("/confirm@TsWwPlus_bot")