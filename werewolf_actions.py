import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, final

from models.role_info import WerewolfRole, villager_enemies


@dataclass
class WerewolfActionPartialData:
    done_to_role: WerewolfRole


@dataclass
class WerewolfActionData:
    done_by_role: WerewolfRole
    partial: WerewolfActionPartialData

    @property
    def done_to_role(self):
        return self.partial.done_to_role


class WerewolfAction(ABC):
    def __init__(
        self,
        name: str,
        done_by_role: WerewolfRole,
        is_one_time: bool,
        default_worth: int,
    ) -> None:
        self._name = name
        self._done_by_role = done_by_role
        self._is_one_time = is_one_time
        self._default_worth = default_worth

    @property
    def name(self) -> str:
        return self._name

    @property
    def done_by_role(self) -> WerewolfRole:
        return self._done_by_role

    @property
    def is_one_time(self) -> bool:
        return self._is_one_time

    @abstractmethod
    def _extract_data(
        self, message_text: str
    ) -> Optional[WerewolfActionPartialData]: ...

    def _worth(self, data: WerewolfActionData) -> Optional[int]:
        return None

    @final
    def worth(self, data: WerewolfActionData) -> int:
        if (worth := self._worth(data)) is not None:
            return worth
        else:
            return self._default_worth

    @final
    def extract_data(self, message_text: str) -> Optional[WerewolfActionData]:
        if (partial := self._extract_data(message_text)) is not None:
            return WerewolfActionData(done_by_role=self.done_by_role, partial=partial)

    @staticmethod
    def done_to_role_data_extraction(patterns: list[str]):
        def __extractor(message_text: str):
            if (
                matched := next(
                    (
                        match
                        for pattern in patterns
                        if (
                            match := re.search(
                                pattern,
                                message_text,
                            )
                        )
                        is not None
                    ),
                    None,
                )
            ) is not None:
                role_text = matched.groupdict()["role"]
                role = WerewolfRole.from_role_text(role_text)
                return role

        return __extractor

    @staticmethod
    def match_only_data_extraction(patterns: dict[str, str]):
        def __extractor(message_text: str):
            return (
                matched := next(
                    (
                        key
                        for (key, pattern) in patterns.items()
                        if (
                            match := re.search(
                                pattern,
                                message_text,
                            )
                        )
                        is not None
                    ),
                    None,
                )
            )

        return __extractor


class OnetimeWerewolfAction(WerewolfAction, ABC):
    def __init__(
        self,
        name: str,
        done_by_role: WerewolfRole,
        default_worth: int,
    ) -> None:
        super().__init__(name, done_by_role, True, default_worth)


class GunnerShot(OnetimeWerewolfAction):
    def __init__(self) -> None:
        super().__init__("تیر موفق به نقش های ضد روستایی", WerewolfRole.Gunner, 0)

    def _extract_data(self, message_text: str) -> Optional[WerewolfActionPartialData]:
        extractor = WerewolfAction.done_to_role_data_extraction(
            [
                r"با شنیدن صدای تیر، روستاییا دور تفنگدار جمع میشن. جناب (?P<gunner>.*) زده (.*) رو کشته (.*) چیزی نبود جز یک (?P<role>.*)"
            ]
        )
        role = extractor(message_text)
        if role is not None:
            return WerewolfActionPartialData(done_to_role=role)

    def _worth(self, data: WerewolfActionData) -> Optional[int]:
        if data.done_to_role in villager_enemies:
            return 10


class HunterFinalShot(OnetimeWerewolfAction):
    def __init__(self) -> None:
        super().__init__("اخرین تیر موفق به نقش ضد روستایی", WerewolfRole.Hunter, 0)

    def _worth(self, data: WerewolfActionData) -> Optional[int]:
        if data.done_to_role in villager_enemies:
            return 10

    def _extract_data(self, message_text: str) -> WerewolfActionPartialData | None:
        extractor = WerewolfAction.done_to_role_data_extraction(
            [
                r"کلانتر یعنی (.*) لحظاتی قبل از مرگش اسلحه رو درآورد و به (.*) شلیک کرد به امید اینکه یه گرگ رو هم با خودش کشته باشه. (.*) چیزی نبود جز یک (?P<role>.*)",
                r"کلانتر یعنی (.*) آخرین لحظه تفنگشو در آورد و (.*) رو کشت. (.*) چیزی نبود جز یک (?P<role>.*)",
            ]
        )
        role = extractor(message_text)
        if role is not None:
            return WerewolfActionPartialData(done_to_role=role)


class ChemistSuccessfulKill(OnetimeWerewolfAction):
    def __init__(self) -> None:
        super().__init__("سم دادن موفق شیمی به نقش منفی", WerewolfRole.Chemist, 0)

    def _worth(self, data: WerewolfActionData) -> Optional[int]:
        if data.done_to_role in villager_enemies:
            return 10

    def _extract_data(self, message_text: str) -> WerewolfActionPartialData | None:
        extractor = WerewolfAction.done_to_role_data_extraction(
            [
                r"(.*) به دیدن (.*) رفت تا باهم نوشیدنی بخورند اما (.*) انتخاب خوبی نداشت و سم رو انتخاب کرد، (.*) چیزی نبود جز یک (?P<role>.*)",
            ]
        )
        role = extractor(message_text)
        if role is not None:
            return WerewolfActionPartialData(done_to_role=role)


class CultHunterCultHunt(OnetimeWerewolfAction):
    def __init__(self) -> None:
        super().__init__("شکار فرقه توسط شکارچی", WerewolfRole.CultHunter, 2)

    def _extract_data(self, message_text: str) -> WerewolfActionPartialData | None:
        extractor = WerewolfAction.match_only_data_extraction(
            {"cult": r"اینطور که معلومه شکارچی دیشب زده یکی از اعضای فرقه (.*) رو کشته"}
        )
        if extractor(message_text) is not None:
            return WerewolfActionPartialData(done_to_role=WerewolfRole.Cult)


class HarlotVisitingWolfOrSk(OnetimeWerewolfAction):
    def __init__(self) -> None:
        super().__init__("ملاقات فاحشه با گرگ یا قاتل", WerewolfRole.Harlot, 10)

    def _extract_data(self, message_text: str) -> WerewolfActionPartialData | None:
        extractor = WerewolfAction.match_only_data_extraction(
            {
                "wolf": r"دیشب فاحشه (.*) پیش یکی از روستایی ها رفت که یه حالی بهش بده ولی گرگینه بود و کشتش😰",
                "sk": r"فاحشه (.*) رفت خونه قاتل زنجیره ای 🔫😭",
            }
        )
        if (key := extractor(message_text)) is not None:
            return WerewolfActionPartialData(
                done_to_role=(
                    WerewolfRole.Werewolf
                    if key == "wolf"
                    else WerewolfRole.SerialKiller
                )
            )


class SerialKillerBigKill(OnetimeWerewolfAction):
    def __init__(self) -> None:
        super().__init__("کشته شدن نقش تپل توسط قاتل", WerewolfRole.SerialKiller, 0)

    def _extract_data(self, message_text: str) -> WerewolfActionPartialData | None:
        extractor = WerewolfAction.done_to_role_data_extraction(
            [
                r"صبح روز بعد اعضای روستا بدن تیکه تیکه شده ی (.*) رو دیدن که روی زمین افتاده. قاتل زنجیره ای بازم به یه نفر حمله کرده (.*) چیزی نبود جز یک (?P<role>.*)",
            ]
        )
        role = extractor(message_text)
        if role is not None:
            return WerewolfActionPartialData(done_to_role=role)

    def _worth(self, data: WerewolfActionData) -> int | None:
        if data.done_to_role in [
            WerewolfRole.Arsonist,
            WerewolfRole.Detective,
            WerewolfRole.GuardingAngle,
            WerewolfRole.Seer,
            WerewolfRole.AlphaWolf,
            WerewolfRole.Harlot,
            WerewolfRole.Lycan,
            WerewolfRole.Werewolf,
            WerewolfRole.SnowWolf,
            WerewolfRole.WolfCub,
        ]:
            return 10


class ArsonistBigBurn(OnetimeWerewolfAction):
    def __init__(self) -> None:
        super().__init__("سوزاندن نقش های تپل", WerewolfRole.Arsonist, 0)

    def _extract_data(self, message_text: str) -> WerewolfActionPartialData | None:
        m = patten = re.compile(
            r"روستایی ها با حس کردن بوی آتش بیدار شدند... مثل اینکه آتش سوزی رخ داده! شما تلاش میکنید آتش را خاموش کنید، اما بسیار دیر برای نجات افرادی که خانه هایشان بطور عجیبی به نفت آغشته شده بود اقدام کردید. امروز شما برای این افراد عزاداری میکنید:\n"
        )
        if m.match(message_text):
            ...

        # ((.*) چیزی نبود جز یک (.*)\n?)+


available_actions: list[WerewolfAction] = [
    GunnerShot(),
    HunterFinalShot(),
    ChemistSuccessfulKill(),
    CultHunterCultHunt(),
    HarlotVisitingWolfOrSk(),
    SerialKillerBigKill(),
]


def matched_actions(message_text: str):
    return (
        (action, data)
        for action in available_actions
        if (data := action.extract_data(message_text)) is not None
    )


if __name__ == "__main__":
    #     message_texts = [
    #         "با شنیدن صدای تیر، روستاییا دور تفنگدار جمع میشن. جناب Amir² زده •|Green°🌸 رو کشته •|Green°🌸 چیزی نبود جز یک  آتش زن 🔥",
    #         "کلانتر یعنی яσʑԋαи↬|♬| آخرین لحظه تفنگشو در آورد و Saeed.N رو کشت. Saeed.N چیزی نبود جز یک توله گرگ 🐶",
    #         "شیمیدان 👨‍🔬 به دیدن 🈂️иιкαи رفت تا باهم نوشیدنی بخورند اما 🈂️иιкαи انتخاب خوبی نداشت و سم رو انتخاب کرد، 🈂️иιкαи چیزی نبود جز یک گرگ آلفا ⚡️",
    #         "اینطور که معلومه شکارچی دیشب زده یکی از اعضای فرقه s🌸12 رو کشته",
    #         "دیشب فاحشه Baran🔥 پیش یکی از روستایی ها رفت که یه حالی بهش بده ولی گرگینه بود و کشتش😰",
    #         """فاحشه ⁭⁫⁭⁭⁫⁭⁫⁭⁭⁫⁭⁭⁫⁭⁫paradox رفت خونه قاتل زنجیره ای 🔫😭

    # خب روز شد. شما 90 ثانیه وقت دارین بحث کنین

    # روز 1""",
    #         """صبح روز بعد اعضای روستا بدن تیکه تیکه شده ی ⚡️Aʀʏᴀ✞Mᴀsᴛᴇʀsʰᵉʳᵒ⚡️ رو دیدن که روی زمین افتاده. قاتل زنجیره ای بازم به یه نفر حمله کرده ⚡️Aʀʏᴀ✞Mᴀsᴛᴇʀsʰᵉʳᵒ⚡️ چیزی نبود جز یک فراماسون 👷

    # خب روز شد. شما 90 ثانیه وقت دارین بحث کنین""",
    #         "صبح روز بعد اعضای روستا بدن تیکه تیکه شده ی 𝑺𝒂𝒉𝒂𝒓 ᴹᵒᵘˢᵃᵛⁱ رو دیدن که روی زمین افتاده. قاتل زنجیره ای بازم به یه نفر حمله کرده 𝑺𝒂𝒉𝒂𝒓 ᴹᵒᵘˢᵃᵛⁱ چیزی نبود جز یک کاراگاه 🕵️",
    #     ]

    #     for message_text in message_texts:
    #         for action, data in matched_actions(message_text):
    #             print(action, data)
    #             print(f"{action.worth(data)=}")
    #         print("------------------")

    patten = re.compile(
        r"""روستایی ها با حس کردن بوی آتش بیدار شدند... مثل اینکه آتش سوزی رخ داده! شما تلاش میکنید آتش را خاموش کنید، اما بسیار دیر برای نجات افرادی که خانه هایشان بطور عجیبی به نفت آغشته شده بود اقدام کردید. امروز شما برای این افراد عزاداری میکنید:
((.*) چیزی نبود جز یک (.*)\n?)+"""
    )

    matchs = patten.findall(
        """روستایی ها با حس کردن بوی آتش بیدار شدند... مثل اینکه آتش سوزی رخ داده! شما تلاش میکنید آتش را خاموش کنید، اما بسیار دیر برای نجات افرادی که خانه هایشان بطور عجیبی به نفت آغشته شده بود اقدام کردید. امروز شما برای این افراد عزاداری میکنید:
s🌸7 چیزی نبود جز یک گرگینه 🐺
s🌸16 چیزی نبود جز یک روستایی 👱
мα¹ چیزی نبود جز یک روستایی 👱
•|ultraviolet°🌸 چیزی نبود جز یک روستایی 👱
s🌸3 چیزی نبود جز یک پیشگو 👳
•|Green°🌸 چیزی نبود جز یک روستایی 👱
•|Yellow°🌸 چیزی نبود جز یک گرگینه 🐺
мα² چیزی نبود جز یک روستایی 👱
мα⁷ چیزی نبود جز یک ناظر 👁
•|Blue°🌸 چیزی نبود جز یک روستایی 👱"""
    )

    for m in matchs:
        print(m)
