from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import ContextTypes
from models.configuration import Configuration

from services.database import Database
from shahla import async_injector_from_ctx


@async_injector_from_ctx
async def open_permission_editor(
    update: Update,
    _: ContextTypes.DEFAULT_TYPE,
    database: Database,
    config: Configuration,
):
    if not update.inline_query:
        return

    if not update.inline_query.query:
        return

    if not update.inline_query.query.startswith("prmedtr"):
        return

    if not update.inline_query.from_user:
        return

    if (
        not update.inline_query.from_user.username
        or update.inline_query.from_user.username != config.self_username
    ):
        return

    target_user_id = update.inline_query.query.split(" ")[1]

    if not target_user_id.isdigit():
        return

    user_id = int(target_user_id)
    admins_col = database.group_admins

    admin = admins_col.find_one({"user_chat_id": user_id})
    if admin is None:
        await update.inline_query.answer(
            [
                InlineQueryResultArticle(
                    "1",
                    "Not an admin",
                    input_message_content=InputTextMessageContent(
                        f"User with id {user_id} is not an admin."
                    ),
                )
            ]
        )
    else:
        await update.inline_query.answer(
            [
                InlineQueryResultArticle(
                    "1",
                    "Admin permissions",
                    input_message_content=InputTextMessageContent(
                        f"User with id {user_id} has permissions: {admin.permissions}"
                    ),
                )
            ]
        )
