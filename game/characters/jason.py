from __future__ import annotations

from game.characters.base_character import CharacterDefinition


class JasonCharacter(CharacterDefinition):
    def __init__(self) -> None:
        super().__init__(
            name="Jason",
            ability_name="freeze",
            ability_label="Freeze",
            description="Create a brief ice pulse that stops enemy motion and platform drift.",
            style="precision, control, and area denial",
            cooldown=5.0,
            freeze_duration=2.4,
        )
        self.cooldown_remaining = 0.0
        self.is_active = False
        self.freeze_remaining = 0.0

    def activate(self) -> bool:
        if self.cooldown_remaining > 0.0:
            return False
        self.is_active = True
        self.freeze_remaining = self.freeze_duration
        self.cooldown_remaining = self.cooldown
        return True

    def update(self, dt: float) -> None:
        if self.cooldown_remaining > 0.0:
            self.cooldown_remaining = max(0.0, self.cooldown_remaining - dt)
        if self.is_active:
            self.freeze_remaining = max(0.0, self.freeze_remaining - dt)
            if self.freeze_remaining == 0.0:
                self.is_active = False
