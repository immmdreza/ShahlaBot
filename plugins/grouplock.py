from datetime import datetime, timedelta
from threading import Timer
from shahla import Shahla,async_injector
from models.configuration import Configuration
from pyrogram.types import ChatPermissions

@async_injector
def every_second(
    shahla: Shahla,
    config: Configuration

):
    group_id = config.functional_chat_id
    now = datetime.now()
    if now.hour == 24 and now.minute == 30:
        shahla.send_message(group_id, "زمان بازی کردن نیم ساعت دیگر به پایان میرسد")
        
        Timer(1800.0, every_second).start()
    elif now.hour == 1 and now.minute == 0:
        shahla.send_message(group_id,"زمان بازی کردن به پایان رسیده است")
        Timer(82800.0, every_second).start()
        shahla.restrict_chat_member(
            group_id,
            175844556,
            ChatPermissions(
                can_send_media_messages=False
            ),
            now + timedelta(hours=7)
        )
    else:
        Timer(60.0, every_second).start()

Timer(60.0, every_second).start()