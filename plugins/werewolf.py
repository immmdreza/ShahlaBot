import re

from pyrogram.types import Message
from pyrogram.filters import user, text, group

from shahla import Shahla


PLAYERS_MESSAGE_PATTERN = re.compile(
    r"^(.*): (?P<alive_players>\d{1,2}) ?/ ?(?P<all_players>\d{1,2})\n"
)
END_GAME_PATTERN = re.compile(
    r"(.*): (?P<hours>\d{1,2}):(?P<minutes>\d{1,2}):(?P<seconds>\d{1,2})$"
)

# user(175844556)
@Shahla.on_message(text & group, group=-1)  # type: ignore
async def from_werewolf(_, message: Message):

    if not message.text:
        return

    text = message.text
    match = PLAYERS_MESSAGE_PATTERN.match(text)
    if match:
        groups = match.groupdict()
        alive_players = groups["alive_players"]
        all_players = groups["all_players"]

        if alive_players == all_players:
            # All players are alive, first message
            await message.reply_text("/new", quote=True)
        else:
            end_match = END_GAME_PATTERN.search(text)
            if end_match:
                await message.reply_text("/confirm", quote=True)
                await message.reply_text("/clear", quote=True)
            else:
                await message.reply_text("/stsup", quote=True)
