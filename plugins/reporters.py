from typing import cast

from pyrogram.client import Client
from pyrogram.types import ChatMemberUpdated

from shahla import Shahla, async_injector
from services.reporter import Reporter


CHAT_MEMBER_MESSAGE_FMT = """
From: __{old_status}__
To: __{new_status}__
Effected user: **{ed_name}** [`{ed_id}`]
Effective user: **{ev_name}** [`{ev_id}`]
"""


@Client.on_chat_member_updated()  # type: ignore
@async_injector
async def on_chat_member_updated(
    _: Shahla, chat_member_updated: ChatMemberUpdated, reporter: Reporter
):
    if chat_member_updated.new_chat_member.user is None:
        effected_name = "Unknown"
        effected_id = "---"
    else:
        effected_name = cast(str, chat_member_updated.new_chat_member.user.first_name)
        effected_id = str(chat_member_updated.new_chat_member.user.id)

    await reporter.report(
        "Chat Member Updated",
        CHAT_MEMBER_MESSAGE_FMT.format(
            old_status=chat_member_updated.old_chat_member.status,
            new_status=chat_member_updated.new_chat_member.status,
            ed_name=effected_name,
            ed_id=effected_id,
            ev_name=chat_member_updated.from_user.first_name,
            ev_id=chat_member_updated.from_user.id,
        ),
    )
