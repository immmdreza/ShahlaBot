import asyncio
import re

from pyrogram.filters import group, reply, text
from pyrogram.types import Message

from shahla import Shahla, async_injector

TASK_LIST_PAT_1 = re.compile(r"اوکی لیست بازیکنان آپدیت شد:")
TASK_LIST_PAT_2 = re.compile(r"لیست نقشها تا به اینجا:")


@Shahla.on_message(text & group & reply, group=-2)  # type: ignore
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

    if (
        TASK_LIST_PAT_2.match(replied_text) or TASK_LIST_PAT_1.match(replied_text)
    ) is not None:
        msg = await message.reply_text(f"/ts {text}")
        await asyncio.sleep(1)
        await msg.delete()
