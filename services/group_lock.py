from datetime import datetime, timedelta
from pyrogram.types import ChatPermissions

from shahla import Shahla, async_injector
from models.configuration import Configuration


@async_injector
async def notify_before_lock(shahla: Shahla, configuration: Configuration):
    group_id = configuration.functional_chat
    if not group_id:
        return

    a = await shahla.send_message(
        group_id, "یادتون نره گروه راس ساعت 24، بسته میشه! سریع جمش کنید."
    )
    a.pin()


@async_injector
async def group_locker(shahla: Shahla, config: Configuration):
    group_id = config.functional_chat
    if not group_id:
        return

    a = await shahla.send_message(group_id, "زمان بازی کردن به پایان رسیده است")
    a.pin()
    await shahla.restrict_chat_member(
        group_id,
        175844556,
        ChatPermissions(can_send_media_messages=False),
        # The restriction will be removed in 8:00 AM (Asia/Tehran).
        # Since this will be ran every day at 24:00 (Asia/Tehran),
        datetime.utcnow() + timedelta(hours=8),
    )
