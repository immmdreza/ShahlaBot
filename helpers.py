import json
import os
import re
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Callable, TypeVar, overload


@overload
def get_from_env(key: str, caster: None = None) -> str: ...


T = TypeVar("T")


@overload
def get_from_env(key: str, caster: Callable[..., T]) -> T: ...


def get_from_env(key: str, caster: Any = None) -> Any:
    if caster is None:
        return os.getenv(key)
    return caster(os.getenv(key))


def deserialize_list(string: str) -> list[Any]:
    return json.loads(string)


_TIME_REGEX = re.compile(
    r"((?P<hours>\d+?)hr)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?"
)


def parse_time(time_str: str) -> timedelta | None:
    parts = _TIME_REGEX.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)


def get_players_list_pattern(lang_txt: str):
    return re.compile(
        lang_txt
        + r" *:.*(?P<alive_players>\d*).*\/.*(?P<all_players>\d*) *\n+(?P<players>(.*: .{1} .* - .*\n)*)"
    )


@dataclass
class RawPlayerInfo:
    name: str
    alive_emoji: str
    alive_text: str
    role: str


def parse_werewolf_list(text: str):
    match = re.match(get_players_list_pattern("بازیکن های زنده"), text + "\n")
    if match:
        players_txt = match.groupdict()["players"]

        def match_to_info(m: re.Match[str]) -> RawPlayerInfo:
            d = m.groupdict()
            return RawPlayerInfo(**d)

        return (
            match_to_info(m)
            for m in re.finditer(
                r"(?P<name>.*): (?P<alive_emoji>.{1}) (?P<alive_text>.*) - (?P<role>.*)",
                players_txt,
            )
        )
    return None


if __name__ == "__main__":
    if (
        (
            roles := parse_werewolf_list(
                """بازیکن های زنده: 3/6
𝒅𝒊𝒂𝒏𝒂༗: 💀 مرده - پیشگو 👳
'𝘔𝘦𝘭𝘪𝘬𝘢: 💀 مرده - گرگ نما 👱🌚
ᯓ⁪⁬⁮⁮⁪⁪⁬⁮⁮⁪⁪⁬⁮⁮⁪⁪⁬⁮⁮⁪⁬⁪⁬⁮⁮⁪⁪⁬ᴍᴏᴢʜɪᴡ🦋 🥉: 💀 مرده - پیشگو 👳
ᴍᴀᴍᴀᴅ🎈: 🙂 زنده
𝓜𝓪𝓱𝓪𝓴🌙: 🙂 زنده
<🐶N4H!D0khT🐶>: 🙂 زنده""",
            )
        )
        is not None
    ):
        for role in list(roles)[-1:]:
            print(role)
