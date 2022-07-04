from pyrogram.types import Message
from pyrogram.filters import command

from models.configuration import Configuration
from shahla import Shahla, async_injector


@Shahla.on_message(command("prmedtr"))  # type: ignore
@async_injector
async def request_permission_editor(
    shahla: Shahla, message: Message, config: Configuration
):

    if not message.from_user:
        return

    if not message.from_user.id in config.super_admins:
        await message.reply_text("You are not a super admin.")
        return

    target_user_id = await shahla.resolve_target_user_from_command(message)
    if target_user_id is None:
        return

    results = await shahla.get_inline_bot_results(
        config.bot_username, "prmedtr " + str(target_user_id.id)
    )

    result = results.results[0]
    await shahla.send_inline_bot_result(message.chat.id, results.query_id, result.id)
