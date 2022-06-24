from datetime import datetime
from typing import Optional

from pyrogram.client import Client


REPORT_FMT = "**[{category}]**:\n{message}\n\n__{datetime}__"


class Reporter:
    def __init__(
        self, client: Optional[Client] = None, report_chat_id: Optional[int] = None
    ):
        if report_chat_id is None:
            raise ValueError("No report chat id found.")
        self._report_chat_id = report_chat_id

        if client is None:
            raise ValueError("No client found.")
        self._client = client

    async def report(self, category: str, message: str):
        await self._client.send_message(
            self._report_chat_id,
            REPORT_FMT.format(
                category=category,
                message=message,
                datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
