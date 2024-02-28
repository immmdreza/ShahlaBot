import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

from typing import cast

from telegram import Update
from telegram.ext import ChatMemberHandler, ContextTypes

from services.reporter import Reporter
from shahla import Shahla, async_injector_from_ctx

CHAT_MEMBER_MESSAGE_FMT = """From: __{old_status}__
To: __{new_status}__
"""


@async_injector_from_ctx
async def _chat_member_updated(
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
        effected_id = None
    else:
        effected_name = cast(str, cmu.new_chat_member.user.first_name)
        effected_id = cmu.new_chat_member.user.id

    await reporter.report_full(
        "Chat Member Updated",
        CHAT_MEMBER_MESSAGE_FMT.format(
            old_status=cmu.old_chat_member.status,
            new_status=cmu.new_chat_member.status,
        ),
        executer_name=cmu.from_user.first_name,
        executer_id=cmu.from_user.id,
        effected_name=effected_name,
        effected_id=effected_id,
    )


chat_member_updated_handler = ChatMemberHandler(
    _chat_member_updated, ChatMemberHandler.ANY_CHAT_MEMBER
)
