from pyrogram.types import Message
from pyrogram.filters import command, group
from models.group_admin import Permissions
from services.database import Database

import services.database_helpers as db_helpers
from services.reporter import Reporter
from shahla import Shahla, async_injector


@Shahla.on_message(command("shekar") & group)  # type: ignore
@async_injector
async def shekar(
    shahla: Shahla, message: Message, database: Database, reporter: Reporter
):

    if not message.from_user:
        return
    sender_id = message.from_user.id

    target_user = await shahla.resolve_target_user_from_command(message)
    if not target_user:
        await message.reply_text("❌ لطفا یک کاربر را مشخص کنید.")
        return

    admin = db_helpers.get_group_admin_with_permission(
        database, sender_id, Permissions.Nothing
    )

    if admin is None:
        await message.reply_text("❌ شما دسترسی لازم برای اجرای این دستور را ندارید.")
        return

    games = database.game_infos

    game = games.find_one({"chat_id": message.chat.id})
    if game is None:
        await message.reply_text("❌ این گروه در حال حاضر بازی ای در جریان نیست.")
        return

    if game.finished:
        await message.reply_text("❌ این بازی به پایان رسیده است.")
        return

    game.shekar_user_id = target_user.id
    games.update_model(game)

    await message.reply_text(
        f"🎉 کاربر {target_user.first_name} به عنوان شکار در این بازی انتخاب شد."
    )
    await reporter.report_full_by_user(
        "Shekar Set",
        f"\n{target_user.first_name} به عنوان شکار در این بازی انتخاب شد.",
        message.from_user,
        target_user,
    )


@Shahla.on_message(command("ski") & group)  # type: ignore
@async_injector
async def ski(_: Shahla, message: Message, database: Database):
    # A command that only saved shekar can use
    if not message.from_user:
        return

    sender_id = message.from_user.id

    game = database.game_infos.find_one({"chat_id": message.chat.id})
    if game is None:
        return

    if game.finished:
        return

    if not game.shekar_user_id:
        await message.reply_text("🌭 There's no **CultistHunter** in this game.")
        return

    ski_text: str | None = None

    if message.command:
        if len(message.command) > 1:
            ski_text = " ".join(message.command[1:])

    if message.reply_to_message:
        if message.reply_to_message.text:
            ski_text = message.reply_to_message.text

    if ski_text:
        if game.shekar_user_id != sender_id:
            await message.reply_text("🌭 Only **CultistHunter** can set ski text.")
            return
        else:
            # set ski text
            game.ski_text = ski_text
            database.game_infos.update_model(game)

            await message.reply_text(
                "Everyone, listen up to the **CultistHunter** of village!\n\n"
                f"{ski_text}"
            )
    else:
        # cast ski text
        if game.ski_text:
            await message.reply_text(
                "Here is the **CultistHunter**'s order:\n" + game.ski_text
            )
        else:
            await message.reply_text("🌭 There's nothing to ski from!")
            return
