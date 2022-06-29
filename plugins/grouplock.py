from datetime import datetime
from threading import Timer
from shahla import Shahla
from models.configuration import Configuration


def every_second(
    shahla: Shahla,
    config: Configuration

):
    group_id = config.functional_chat_id
    now = datetime.now()
    if now.hour == 24 and now.minute == 30:
        shahla.send_message(group_id, "زمان بازی کردن نیم ساعت دیگر به پایان میرسد")
        Timer(1.0, every_second).start()
    elif now.hour == 1 and now.minute == 0:
        shahla.send_message(group_id,"زمان بازی کردن به پایان رسیده است")
    elif now.hour == 8 and now.minute == 0:
        shahla.send_message(group_id,"گروه هم اکنون باز است")
    else:
        Timer(1.0, every_second).start()

Timer(1.0, every_second).start()