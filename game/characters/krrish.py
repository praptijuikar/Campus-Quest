from __future__ import annotations

from game.characters.base_character import CharacterDefinition


class KrrishCharacter(CharacterDefinition):
    def __init__(self) -> None:
        super().__init__(
            name="Krrish",
            ability_name="double_jump",
            ability_label="Double Jump",
            description="Gain an extra airborne jump to clear momentum-heavy gaps and hazards.",
            style="agility, vertical control, and mobility",
            cooldown=0.0,
            freeze_duration=0.0,
        )
