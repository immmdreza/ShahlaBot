import re

import pyrogram
from pyrogram.filters import group, text, user
from pyrogram.types import Message

from helpers import parse_werewolf_list
from models.game_info import GameInfo
from models.role_info import RoleInfo
from services.database import Database
from shahla import Shahla, async_injector
from werewolf_actions import matched_actions

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

        game = games.find_one({"chat_id": message.chat.id})
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

            # Clear old roles
            database.role_infos.clear()

            infos = (
                RoleInfo(in_game_name=x.user.first_name, user_id=x.user.id)
                for x in message.entities
                if x.type == pyrogram.enums.MessageEntityType.TEXT_MENTION
            )
            database.role_infos.insert_many(infos)

            await message.reply_text("/new", quote=True)
        else:
            if game is None:
                return

            old_alive_players = game.alive_players

            game.players_count = int(all_players)
            game.alive_players = int(alive_players)

            print(f"{old_alive_players=}, {game.alive_players=}")
            if (players := parse_werewolf_list(message.text)) is not None:
                new_dead_players = list(x for x in players if x.alive_emoji == "💀")[
                    game.alive_players - old_alive_players :
                ]
                for player in new_dead_players:
                    result = database.role_infos.update_one(
                        {"in_game_name": player.name},
                        {"$set": {"role": player.role, "alive": False}},
                    )
                    if result.modified_count == 1:
                        user_id = database.role_infos.find_one({"role": player.role}).user_id  # type: ignore
                        await message.reply_text(
                            f"User {player.name} [{user_id}] is dead with role {player.role}"
                        )

            end_match = END_GAME_PATTERN.search(text)
            if end_match:
                game.finished = True
                games.update_model(game)

                await message.reply_text("/confirm", quote=True)
                await message.reply_text("/clear", quote=True)
            else:

                game.finished = False
                games.update_model(game)

                await message.reply_text("/stsup", quote=True)

    else:
        # It's not a players list message
        # Let's check for in game performance

        for action, data in matched_actions(text):
            worth = action.worth(data)
            await message.reply_text(
                f"Got {action.name} done on {data.done_to_role.to_role_text()}, worths {worth}"
            )
