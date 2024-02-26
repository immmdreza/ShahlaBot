from datetime import datetime
from typing import Optional

from pyrogram.client import Client
from pyrogram.types import User

REPORT_FMT = "**[{category}]**:\n{message}\n\n__{datetime}__"
REPORT_FULL_FMT = (
    "**[{category}]**:\n"
    "{message}\n\n"
    "__Executer__: {x_name} [`{x_id}`]\n"
    "__Effected__: {e_name} [`{e_id}`]\n\n"
    "__{datetime}__"
)


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

    async def report_full(
        self,
        category: str,
        message: str,
        executer_name: str,
        executer_id: int,
        effected_name: Optional[str] = None,
        effected_id: Optional[int] = None,
    ):
        await self._client.send_message(
            self._report_chat_id,
            REPORT_FULL_FMT.format(
                category=category,
                message=message,
                x_name=executer_name,
                x_id=executer_id,
                e_name=effected_name,
                e_id=effected_id,
                datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )

    async def report_full_by_user(
        self,
        category: str,
        message: str,
        executer: User,
        effected: Optional[User] = None,
    ):
        await self.report_full(
            category,
            message,
            executer.first_name,
            executer.id,
            effected.first_name if effected is not None else None,
            effected.id if effected is not None else None,
        )
