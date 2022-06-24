import os
from typing import cast

from dotenv import load_dotenv

from shahla import Shahla, LifeTime
from services.reporter import Reporter
from services.database import Database
from models.configuration import Configuration


load_dotenv()
api_id = int(cast(str, os.getenv("API_ID")))
api_hash = cast(str, os.getenv("API_HASH"))
bot_token = cast(str, os.getenv("BOT_TOKEN"))

shahla = Shahla(
    "ShahlaBot",
    api_id,
    api_hash,
    bot_token=bot_token,
    plugins={"root": "plugins"},
)

if __name__ == "__main__":
    shahla.register_type(Database, lambda _: Database("shahla"))
    shahla.register_type(Configuration, lambda s: s.request_instance(Database).set_up())
    shahla.register_type(
        Reporter,
        lambda s: Reporter(s, s.request_instance(Configuration).report_chat_id),
        LifeTime.Scoped,
    )

    shahla.run()
