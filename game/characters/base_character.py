from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CharacterDefinition:
    name: str
    ability_name: str
    ability_label: str
    description: str
    style: str
    cooldown: float = 5.0
    freeze_duration: float = 2.5

    def activate(self) -> bool:
        return True

    def update(self, dt: float) -> None:
        return None


def get_character_definitions() -> dict[str, CharacterDefinition]:
    from game.characters.jason import JasonCharacter
    from game.characters.krrish import KrrishCharacter

    return {
        "Jason": JasonCharacter(),
        "Krrish": KrrishCharacter(),
    }


def get_character_definition(character_name: str) -> CharacterDefinition:
    definitions = get_character_definitions()
    key = character_name.strip().title()
    return definitions.get(key, definitions["Krrish"])
