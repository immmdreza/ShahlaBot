from dataclasses import dataclass
from enum import Enum
from typing import Optional

from models.model_base import ModelBase

# /aboutVillager - روستایی 👱
# /aboutWerewolf - گرگینه 🐺
# /aboutDrunk - مست 🍻
# /aboutSeer - پیشگو 👳
# /aboutCursed - نفرین شده 😾
# /aboutHarlot - فاحشه 💋
# /aboutBeholder - ناظر 👁
# /aboutGunner - تفنگدار 🔫
# /aboutTraitor - خائن 🖕
# /aboutGuardingAngle - فرشته نگهبان 👼
# /aboutDetective - کاراگاه 🕵
# /aboutAppS - پیشگوی رزرو 🙇
# /aboutCult - فرقه گرا 👤
# /aboutCultHunter - شکارچی 💂
# /aboutWildChild - بچه وحشی 👶
# /aboutFool - احمق 🃏
# /aboutMason - فراماسون 👷
# /aboutDoppleGanger - همزاد🎭
# /aboutCupid - الهه عشق💘
# /aboutHunter - کلانتر🎯
# /aboutSerialKiller - 🔪قاتل زنجیره ای
# /aboutTanner - منافق 👺
# /aboutMayor - کدخدا 🎖
# /aboutPrince - شاهزاده 👑
# /aboutSorcerer - جادوگر 🔮
# /aboutClumsy - پسر گیج 🤕
# /aboutBlacksmith - آهنگر ⚒
# /aboutAlphaWolf - گرگ آلفا ⚡️
# /aboutWolfCub - توله گرگ 🐶
# /aboutSandman - خواب گذار 💤
# /aboutOracle - پیشگوی نگاتیوی 🌀
# /aboutWolfMan - گرگ نما 👱🌚
# /aboutLycan - گرگ ایکس 🐺🌝
# /aboutPacifist - صلح گرا☮️
# /aboutWiseElder - ریش سفید 📚
# /aboutThief - دزد😈
# /aboutTroublemaker -  دردسرساز 🤯
# /aboutChemist -  شیمیدان 👨‍🔬
# /aboutSnowWolf -  گرگ برفی 🐺☃️
# /aboutGraveDigger -  گورکن ☠️
# /aboutArsonist -  آتش زن 🔥
# /aboutAugur -  رمال 🦅


class WerewolfRole(Enum):
    Villager = 0
    Werewolf = 1
    Drunk = 2
    Seer = 3
    Cursed = 4
    Harlot = 5
    Beholder = 6
    Gunner = 7
    Traitor = 8
    GuardingAngle = 9
    Detective = 10
    AppS = 11
    Cult = 12
    CultHunter = 13
    WildChild = 14
    Fool = 15
    Mason = 16
    DoppleGanger = 17
    Cupid = 18
    Hunter = 19
    SerialKiller = 20
    Tanner = 21
    Mayor = 22
    Prince = 23
    Sorcerer = 24
    Clumsy = 25
    Blacksmith = 26
    AlphaWolf = 27
    WolfCub = 28
    Sandman = 29
    Oracle = 30
    WolfMan = 31
    Lycan = 32
    Pacifist = 33
    WiseElder = 34
    Thief = 35
    Troublemaker = 36
    Chemist = 37
    SnowWolf = 38
    GraveDigger = 39
    Arsonist = 40
    Augur = 41

    def to_role_text(self):
        match self:
            case WerewolfRole.Villager:
                return "روستایی 👱"
            case WerewolfRole.Werewolf:
                return "گرگینه 🐺"
            case WerewolfRole.Drunk:
                return "مست 🍻"
            case WerewolfRole.Seer:
                return "پیشگو 👳"
            case WerewolfRole.Cursed:
                return "نفرین شده 😾"
            case WerewolfRole.Harlot:
                return "فاحشه 💋"
            case WerewolfRole.Beholder:
                return "ناظر 👁"
            case WerewolfRole.Gunner:
                return "تفنگدار 🔫"
            case WerewolfRole.Traitor:
                return "خائن 🖕"
            case WerewolfRole.GuardingAngle:
                return "فرشته نگهبان 👼"
            case WerewolfRole.Detective:
                return "کاراگاه 🕵"
            case WerewolfRole.AppS:
                return "پیشگوی رزرو 🙇"
            case WerewolfRole.Cult:
                return "فرقه گرا 👤"
            case WerewolfRole.CultHunter:
                return "شکارچی 💂"
            case WerewolfRole.WildChild:
                return "بچه وحشی 👶"
            case WerewolfRole.Fool:
                return "احمق 🃏"
            case WerewolfRole.Mason:
                return "فراماسون 👷"
            case WerewolfRole.DoppleGanger:
                return "همزاد🎭"
            case WerewolfRole.Cupid:
                return "الهه عشق💘"
            case WerewolfRole.Hunter:
                return "کلانتر🎯"
            case WerewolfRole.SerialKiller:
                return "🔪قاتل زنجیره ای"
            case WerewolfRole.Tanner:
                return "منافق 👺"
            case WerewolfRole.Mayor:
                return "کدخدا 🎖"
            case WerewolfRole.Prince:
                return "شاهزاده 👑"
            case WerewolfRole.Sorcerer:
                return "جادوگر 🔮"
            case WerewolfRole.Clumsy:
                return "پسر گیج 🤕"
            case WerewolfRole.Blacksmith:
                return "آهنگر ⚒"
            case WerewolfRole.AlphaWolf:
                return "گرگ آلفا ⚡️"
            case WerewolfRole.WolfCub:
                return "توله گرگ 🐶"
            case WerewolfRole.Sandman:
                return "خواب گذار 💤"
            case WerewolfRole.Oracle:
                return "پیشگوی نگاتیوی 🌀"
            case WerewolfRole.WolfMan:
                return "گرگ نما 👱🌚"
            case WerewolfRole.Lycan:
                return "گرگ ایکس 🐺🌝"
            case WerewolfRole.Pacifist:
                return "صلح گرا☮️"
            case WerewolfRole.WiseElder:
                return "ریش سفید 📚"
            case WerewolfRole.Thief:
                return "دزد😈"
            case WerewolfRole.Troublemaker:
                return " دردسرساز 🤯"
            case WerewolfRole.Chemist:
                return " شیمیدان 👨‍🔬"
            case WerewolfRole.SnowWolf:
                return " گرگ برفی 🐺☃️"
            case WerewolfRole.GraveDigger:
                return " گورکن ☠️"
            case WerewolfRole.Arsonist:
                return " آتش زن 🔥"
            case WerewolfRole.Augur:
                return " رمال 🦅"

    @staticmethod
    def from_role_text(text: str) -> "WerewolfRole":
        match text:

            case "روستایی 👱":
                return WerewolfRole.Villager
            case "گرگینه 🐺":
                return WerewolfRole.Werewolf
            case "مست 🍻":
                return WerewolfRole.Drunk
            case "پیشگو 👳":
                return WerewolfRole.Seer
            case "نفرین شده 😾":
                return WerewolfRole.Cursed
            case "فاحشه 💋":
                return WerewolfRole.Harlot
            case "ناظر 👁":
                return WerewolfRole.Beholder
            case "تفنگدار 🔫":
                return WerewolfRole.Gunner
            case "خائن 🖕":
                return WerewolfRole.Traitor
            case "فرشته نگهبان 👼":
                return WerewolfRole.GuardingAngle
            case "کاراگاه 🕵":
                return WerewolfRole.Detective
            case "پیشگوی رزرو 🙇":
                return WerewolfRole.AppS
            case "فرقه گرا 👤":
                return WerewolfRole.Cult
            case "شکارچی 💂":
                return WerewolfRole.CultHunter
            case "بچه وحشی 👶":
                return WerewolfRole.WildChild
            case "احمق 🃏":
                return WerewolfRole.Fool
            case "فراماسون 👷":
                return WerewolfRole.Mason
            case "همزاد🎭":
                return WerewolfRole.DoppleGanger
            case "الهه عشق💘":
                return WerewolfRole.Cupid
            case "کلانتر🎯":
                return WerewolfRole.Hunter
            case "🔪قاتل زنجیره ای":
                return WerewolfRole.SerialKiller
            case "منافق 👺":
                return WerewolfRole.Tanner
            case "کدخدا 🎖":
                return WerewolfRole.Mayor
            case "شاهزاده 👑":
                return WerewolfRole.Prince
            case "جادوگر 🔮":
                return WerewolfRole.Sorcerer
            case "پسر گیج 🤕":
                return WerewolfRole.Clumsy
            case "آهنگر ⚒":
                return WerewolfRole.Blacksmith
            case "گرگ آلفا ⚡️":
                return WerewolfRole.AlphaWolf
            case "توله گرگ 🐶":
                return WerewolfRole.WolfCub
            case "خواب گذار 💤":
                return WerewolfRole.Sandman
            case "پیشگوی نگاتیوی 🌀":
                return WerewolfRole.Oracle
            case "گرگ نما 👱🌚":
                return WerewolfRole.WolfMan
            case "گرگ ایکس 🐺🌝":
                return WerewolfRole.Lycan
            case "صلح گرا☮️":
                return WerewolfRole.Pacifist
            case "ریش سفید 📚":
                return WerewolfRole.WiseElder
            case "دزد😈":
                return WerewolfRole.Thief
            case " دردسرساز 🤯":
                return WerewolfRole.Troublemaker
            case " شیمیدان 👨‍🔬":
                return WerewolfRole.Chemist
            case " گرگ برفی 🐺☃️":
                return WerewolfRole.SnowWolf
            case " گورکن ☠️":
                return WerewolfRole.GraveDigger
            case " آتش زن 🔥":
                return WerewolfRole.Arsonist
            case " رمال 🦅":
                return WerewolfRole.Augur
            case r:
                raise Exception(f"No such werewolf role: {r}")


villager_enemies = [
    WerewolfRole.Werewolf,
    WerewolfRole.AlphaWolf,
    WerewolfRole.Arsonist,
    WerewolfRole.Cult,
    WerewolfRole.Lycan,
    WerewolfRole.WolfCub,
    WerewolfRole.SerialKiller,
    WerewolfRole.SnowWolf,
    WerewolfRole.Sorcerer,
    WerewolfRole.Traitor,
]


@dataclass
class RoleInfo(ModelBase):
    in_game_name: str
    user_id: int
    role: Optional[str] = None
    alive: bool = True
    said_role: Optional[str] = None

    def as_werewolf_role(self):
        if self.role is not None:
            return WerewolfRole.from_role_text(self.role)
        else:
            return None


if __name__ == "__main__":
    for role in [
        WerewolfRole.Villager,
        WerewolfRole.Werewolf,
        WerewolfRole.Drunk,
        WerewolfRole.Seer,
        WerewolfRole.Cursed,
        WerewolfRole.Harlot,
        WerewolfRole.Beholder,
        WerewolfRole.Gunner,
        WerewolfRole.Traitor,
        WerewolfRole.GuardingAngle,
        WerewolfRole.Detective,
        WerewolfRole.AppS,
        WerewolfRole.Cult,
        WerewolfRole.CultHunter,
        WerewolfRole.WildChild,
        WerewolfRole.Fool,
        WerewolfRole.Mason,
        WerewolfRole.DoppleGanger,
        WerewolfRole.Cupid,
        WerewolfRole.Hunter,
        WerewolfRole.SerialKiller,
        WerewolfRole.Tanner,
        WerewolfRole.Mayor,
        WerewolfRole.Prince,
        WerewolfRole.Sorcerer,
        WerewolfRole.Clumsy,
        WerewolfRole.Blacksmith,
        WerewolfRole.AlphaWolf,
        WerewolfRole.WolfCub,
        WerewolfRole.Sandman,
        WerewolfRole.Oracle,
        WerewolfRole.WolfMan,
        WerewolfRole.Lycan,
        WerewolfRole.Pacifist,
        WerewolfRole.WiseElder,
        WerewolfRole.Thief,
        WerewolfRole.Troublemaker,
        WerewolfRole.Chemist,
        WerewolfRole.SnowWolf,
        WerewolfRole.GraveDigger,
        WerewolfRole.Arsonist,
        WerewolfRole.Augur,
    ]:
        text = role.to_role_text()
        print(text)
        restored = WerewolfRole.from_role_text(text)
        print(restored)
        assert restored == role, "Roles not mathced."
        print("<----------->")
