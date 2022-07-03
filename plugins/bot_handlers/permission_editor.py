from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes, CallbackQueryHandler, InlineQueryHandler
from models.configuration import Configuration

from models.group_admin import Permissions
from services.database import Database
from shahla import async_injector_from_ctx


def generate_button_from_permission(perms: Permissions, user_id: int):
    buttons: list[list[InlineKeyboardButton]] = [[]]
    for perm in Permissions.iter_permissions():
        if perm == Permissions.Nothing:
            continue

        if perm in perms:
            buttons[-1].append(
                InlineKeyboardButton(
                    Permissions.to_string(perm) + " ✅",
                    callback_data=f"prm_switch_{user_id}_{perm.value}",
                )
            )
        else:
            buttons[-1].append(
                InlineKeyboardButton(
                    Permissions.to_string(perm) + " ❌",
                    callback_data=f"prm_switch_{user_id}_{perm.value}",
                )
            )
        if len(buttons[-1]) == 2:
            buttons.append([])

    buttons.append([InlineKeyboardButton("🔙", callback_data=f"prm_close")])
    return buttons


@async_injector_from_ctx
async def _open_permission_editor(
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
            ],
            cache_time=0,
        )
    else:
        await update.inline_query.answer(
            [
                InlineQueryResultArticle(
                    "1",
                    "Admin permissions",
                    input_message_content=InputTextMessageContent(
                        f"User with id {user_id} permission editor ..."
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        generate_button_from_permission(
                            Permissions(admin.permissions), user_id
                        )
                    ),
                )
            ],
            cache_time=0,
        )


open_permission_editor_handler = InlineQueryHandler(
    _open_permission_editor, pattern="^prmedtr"
)


@async_injector_from_ctx
async def _edit_permission(
    update: Update,
    _: ContextTypes.DEFAULT_TYPE,
    database: Database,
    config: Configuration,
):
    if not update.callback_query:
        return

    if not update.callback_query.data:
        return

    if not update.callback_query.data.startswith("prm_switch_"):
        return

    if not update.callback_query.from_user:
        return

    if update.callback_query.from_user.id not in config.super_admins:
        return

    target_user_id = int(update.callback_query.data.split("_")[2])
    permission = Permissions(int(update.callback_query.data.split("_")[3]))

    admins_col = database.group_admins

    admin = admins_col.find_one({"user_chat_id": target_user_id})
    if admin is None:
        return

    current_permissions = Permissions(admin.permissions)

    if permission in current_permissions:
        current_permissions &= ~permission
    else:
        current_permissions |= permission

    admin.permissions = current_permissions
    admins_col.update_model(admin)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        f"User with id {target_user_id} permission editor ...",
        reply_markup=InlineKeyboardMarkup(
            generate_button_from_permission(
                Permissions(admin.permissions), target_user_id
            )
        ),
    )


edit_permissions_handler = CallbackQueryHandler(
    _edit_permission, pattern="^prm_switch_.*"
)


async def _close_editor(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("Closed!")


close_editor_handler = CallbackQueryHandler(_close_editor, pattern="^prm_close$")
