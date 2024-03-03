import re

import pyrogram
from pyrogram.filters import group, text, user
from pyrogram.types import Message

from helpers import parse_werewolf_list
from models.action_reward_log import ActionRewardLog
from models.game_actions import GameAction
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

            if game.finished:
                old_alive_players = game.players_count
            else:
                old_alive_players = game.alive_players

            game.players_count = int(all_players)
            game.alive_players = int(alive_players)

            end_match = END_GAME_PATTERN.search(text) is not None

            print(f"{old_alive_players=}, {game.alive_players=}")
            if (players := parse_werewolf_list(message.text, end_match)) is not None:
                if end_match:
                    # if it's end game check all alive + new dead
                    players_to_check = list(x for x in players)[
                        (game.alive_players - old_alive_players) - game.alive_players :
                    ]
                else:
                    # Check only new dead players
                    players_to_check = list(
                        x for x in players if x.alive_emoji == "💀"
                    )[game.alive_players - old_alive_players :]

                await message.reply_text(
                    f"Checking {len(players_to_check)} last players."
                )

                for player in players_to_check:
                    result = database.role_infos.update_one(
                        {"in_game_name": player.name},
                        {"$set": {"role": player.role, "alive": False}},
                    )
                    if result.modified_count == 1:
                        user_id = database.role_infos.find_one({"role": player.role}).user_id  # type: ignore
                        if (
                            game_action := database.game_actions.find_one(
                                {"done_by_role": player.role}
                            )
                        ) is not None:
                            if game_action.one_time:
                                database.game_actions.delete_one(
                                    {"_id": game_action.id}
                                )

                            database.action_reward_log.insert_one(
                                ActionRewardLog(
                                    user_id=user_id, reward_worth=game_action.worth
                                )
                            )
                            await message.reply_text(
                                f"کاربر {player.name} [{user_id}]، {game_action.worth} امتیاز به خاطر حرکتش حین بازی دریافت میکنه."
                            )
                            await message.reply_text(
                                f"/cup {user_id} +{game_action.worth}", quote=False
                            )

            if end_match:
                game.finished = True
                games.update_model(game)
                database.game_actions.clear()
                # Clear old roles
                database.role_infos.clear()

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
            # save action!
            if worth > 0:
                await message.reply_text(
                    f"{action.done_by_role.to_role_text()} تونست حرکت '{action.name}' رو به ارزش {worth} امتیاز انجام بده."
                )
                database.game_actions.insert_one(
                    GameAction(
                        done_by_role=data.done_by_role.to_role_text(),
                        worth=worth,
                        one_time=action.is_one_time,
                    )
                )
