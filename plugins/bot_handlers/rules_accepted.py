import pyrogram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from services.reporter import Reporter
from shahla import Shahla, async_injector_from_ctx


@async_injector_from_ctx
async def _rules_accepted(
    update: Update, _: ContextTypes.DEFAULT_TYPE, shahla: Shahla, reporter: Reporter
):

    if (callback_query := update.callback_query) is None:
        return

    if (data := callback_query.data) is None:
        return

    if (message := callback_query.message) is None:
        return

    user_id = int(data[15:])

    if user_id != callback_query.from_user.id:
        await callback_query.answer("Not for you!", show_alert=True)
        return

    await shahla.restrict_chat_member(
        message.chat.id,
        user_id,
        pyrogram.types.ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_send_polls=True,
        ),
    )

    await callback_query.edit_message_reply_markup(
        InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("قوانین رویداد", url="https://t.me/TaskyEvents")],
                [
                    InlineKeyboardButton(
                        "راهنمای شرکت در رویداد",
                        url="https://t.me/TaskyEventsGuide",
                    )
                ],
            ]
        )
    )
    await callback_query.answer()
    await reporter.report("Rules Accepted", f"User [{user_id}] accepted the rules.")


rules_accepted_handler = CallbackQueryHandler(
    _rules_accepted, "^rules_accepted_([0-9]+)$"
)
