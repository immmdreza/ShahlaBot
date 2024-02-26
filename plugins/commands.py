from pyrogram.types import Message

import services.database_helpers as db_helpers
from models.group_admin import Permissions
from services.database import Database
from shahla import Shahla, async_injector, shahla_command


@Shahla.on_message(shahla_command("commands", description="Shows this message.", notes=("Admins only")))  # type: ignore
@async_injector
async def on_repoff_requested(
    _: Shahla,
    message: Message,
    database: Database,
):
    if not message.from_user:
        return
    sender_id = message.from_user.id

    # Turn of report for user by admin
    admin = db_helpers.get_group_admin_with_permission(
        database, message.from_user.id, Permissions.Nothing
    )
    if not admin:
        return

    await message.reply_text(
        "Available Commands:\n\n"
        + "\n\n".join(map(lambda x: str(x), Shahla.commands))
    )
