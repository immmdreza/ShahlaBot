import re
from abc import ABC, abstractmethod, abstractproperty
from dataclasses import dataclass
from typing import Optional

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

    @abstractproperty
    def name(self) -> str: ...

    @abstractproperty
    def done_by_role(self) -> WerewolfRole: ...

    @abstractmethod
    def _extract_data(
        self, message_text: str
    ) -> Optional[WerewolfActionPartialData]: ...

    @abstractmethod
    def worth(self, data: WerewolfActionData) -> int: ...

    def extract_data(self, message_text: str) -> Optional[WerewolfActionData]:
        if (partial := self._extract_data(message_text)) is not None:
            return WerewolfActionData(done_by_role=self.done_by_role, partial=partial)


class GunnerShot(WerewolfAction):

    @property
    def name(self) -> str:
        return "Gunner shot"

    @property
    def done_by_role(self):
        return WerewolfRole.Gunner

    def _extract_data(self, message_text: str) -> Optional[WerewolfActionPartialData]:
        if (
            matched := re.match(
                "با شنیدن صدای تیر، روستاییا دور تفنگدار جمع میشن. جناب (?P<gunner>.*) زده (.*) رو کشته (.*) چیزی نبود جز یک (?P<role>.*)",
                message_text,
            )
        ) is not None:
            role_text = matched.groupdict()["role"]
            role = WerewolfRole.from_role_text(role_text)
            return WerewolfActionPartialData(done_to_role=role)

    def worth(self, data: WerewolfActionData) -> int:
        if data.done_to_role in villager_enemies:
            return 10
        return 0


available_actions: list[WerewolfAction] = [GunnerShot()]


def matched_actions(message_text: str):
    return (
        (action, data)
        for action in available_actions
        if (data := action.extract_data(message_text)) is not None
    )


if __name__ == "__main__":
    message_texts = [
        "با شنیدن صدای تیر، روستاییا دور تفنگدار جمع میشن. جناب Amir² زده •|Green°🌸 رو کشته •|Green°🌸 چیزی نبود جز یک  آتش زن 🔥",
        "با شنیدن صدای تیر، روستاییا دور تفنگدار جمع میشن. جناب Cahr؛ زده •|white°🌸 رو کشته •|white°🌸 چیزی نبود جز یک گرگینه 🐺",
        "با شنیدن صدای تیر، روستاییا دور تفنگدار جمع میشن. جناب 𝐴𝑚𝑖𝑟𝑅𝑒𝑧𝑎 زده мα⁴ رو کشته мα⁴ چیزی نبود جز یک گرگ آلفا ⚡️",
        "با شنیدن صدای تیر، روستاییا دور تفنگدار جمع میشن. جناب •𝑓𝑎𝑡𝑒𝑚𝑒ℎ♡♫ زده s🌸7 رو کشته s🌸7 چیزی نبود جز یک 🔪قاتل زنجیره ای",
    ]

    for message_text in message_texts:
        for action, data in matched_actions(message_text):
            print(action, data)
            print(f"{action.worth(data)=}")
        print("------------------")
