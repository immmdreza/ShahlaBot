import asyncio

from pyrogram.filters import group, reply, text, user
from pyrogram.types import Message

from services.database import Database
from shahla import Shahla, async_injector


@Shahla.on_message(text & group & reply, group=-1)  # type: ignore
@async_injector
async def replies_from_task_system(_: Shahla, message: Message):
    if (text := message.text) is None:
        return

    if (replied_message := message.reply_to_message) is None:
        return

    # Replied to task
    if replied_message.from_user.id != 724104884:
        return

    if (replied_text := replied_message.text) is None:
        return

    if replied_text.startswith("اوکی لیست بازیکنان آپدیت شد: "):
        msg = await message.reply_text(f"/ts {text}")
        await asyncio.sleep(1)
        await msg.delete()
