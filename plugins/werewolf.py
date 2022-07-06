import re

from pyrogram.types import Message
from pyrogram.filters import user, text, group

from services.database import Database
from models.game_info import GameInfo
from shahla import Shahla, async_injector


PLAYERS_MESSAGE_PATTERN = re.compile(
    r"^(.*): (?P<alive_players>\d{1,2}) ?/ ?(?P<all_players>\d{1,2})\n"
)
END_GAME_PATTERN = re.compile(
    r"(.*): (?P<hours>\d{1,2}):(?P<minutes>\d{1,2}):(?P<seconds>\d{1,2})$"
)


@Shahla.on_message(user(175844556) & text & group, group=-1)  # type: ignore
@async_injector
async def from_werewolf(_: Shahla, message: Message, database: Database):

    if not message.text:
        return

    games = database.game_infos

    text = message.text
    match = PLAYERS_MESSAGE_PATTERN.match(text)
    if match:
        groups = match.groupdict()
        alive_players = groups["alive_players"]
        all_players = groups["all_players"]

        game = games.find_one(dict(chat_id=message.chat.id))
        if alive_players == all_players:
            # All players are alive, first message
            if game is None:
                game = GameInfo(
                    chat_id=message.chat.id,
                    players_count=int(all_players),
                    alive_players=int(alive_players),
                    finished=False,
                )
                games.insert_one(game)
            else:
                game.players_count = int(all_players)
                game.alive_players = int(alive_players)
                game.finished = False
                games.update_model(game)

            await message.reply_text("/new", quote=True)
        else:
            end_match = END_GAME_PATTERN.search(text)
            if end_match:
                if game is None:
                    return

                game.alive_players = int(alive_players)
                game.finished = True
                games.update_model(game)

                await message.reply_text("/confirm", quote=True)
                await message.reply_text("/clear", quote=True)
            else:
                if game is None:
                    return

                game.alive_players = int(alive_players)
                games.update_model(game)

                await message.reply_text("/stsup", quote=True)
