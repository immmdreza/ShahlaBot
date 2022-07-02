import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

from typing import cast
from telegram import Update
from telegram.ext import ContextTypes

from shahla import Shahla, async_injector_from_ctx
from services.reporter import Reporter


CHAT_MEMBER_MESSAGE_FMT = """
From: __{old_status}__
To: __{new_status}__
Effected user: **{ed_name}** [`{ed_id}`]
Effective user: **{ev_name}** [`{ev_id}`]
"""


@async_injector_from_ctx
async def chat_member_updated(
    update: Update,
    _: ContextTypes.DEFAULT_TYPE,
    __: Shahla,
    reporter: Reporter,
):
    cmu = update.chat_member or update.my_chat_member

    if cmu is None:
        return

    if cmu.new_chat_member.user is None:
        effected_name = "Unknown"
        effected_id = "---"
    else:
        effected_name = cast(str, cmu.new_chat_member.user.first_name)
        effected_id = str(cmu.new_chat_member.user.id)

    await reporter.report(
        "Chat Member Updated",
        CHAT_MEMBER_MESSAGE_FMT.format(
            old_status=cmu.old_chat_member.status,
            new_status=cmu.new_chat_member.status,
            ed_name=effected_name,
            ed_id=effected_id,
            ev_name=cmu.from_user.first_name,
            ev_id=cmu.from_user.id,
        ),
    )
