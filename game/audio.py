from __future__ import annotations

import array
import math

import pygame


class AudioManager:
    def __init__(self) -> None:
        self.enabled = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=256)
            self.enabled = True
            self._build_sfx()
        except pygame.error:
            self.enabled = False

    def _build_sfx(self) -> None:
        self.sounds["jump"] = self._tone(420.0, 0.08, 0.25)
        self.sounds["collect"] = self._tone(760.0, 0.10, 0.25)
        self.sounds["checkpoint"] = self._tone(960.0, 0.18, 0.30)
        self.sounds["death"] = self._tone(140.0, 0.25, 0.28)
        self.sounds["goal"] = self._tone(520.0, 0.18, 0.35)
        self.sounds["button"] = self._tone(600.0, 0.08, 0.20)
        self.sounds["freeze"] = self._tone(260.0, 0.22, 0.32)

    def _tone(self, frequency: float, duration: float, volume: float) -> pygame.mixer.Sound:
        sample_rate = 22050
        total_samples = int(sample_rate * duration)
        samples = array.array("h")
        for i in range(total_samples):
            t = i / sample_rate
            envelope = min(1.0, t / 0.01) * max(0.0, 1.0 - t / duration)
            value = int(32767 * volume * envelope * math.sin(2 * math.pi * frequency * t))
            samples.append(value)
        return pygame.mixer.Sound(buffer=samples)

    def play_sfx(self, name: str) -> None:
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()
