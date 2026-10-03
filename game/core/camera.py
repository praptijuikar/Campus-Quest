from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ParallaxLayer:
    speed: float
    color: tuple[int, int, int]
    y: int
    height: int = 200

    def draw(self, surface, camera_x: float, world_width: int, screen_width: int) -> None:
        offset = camera_x * self.speed
        start = int(-offset % (screen_width + 300))
        for x in range(start - 500, world_width + 500, screen_width + 280):
            layer_rect = (x, self.y, screen_width + 320, self.height)
            surface.fill(self.color, layer_rect)


class Camera:
    def __init__(self, world_width: int, screen_width: int, smoothing: float = 0.12) -> None:
        self.world_width = world_width
        self.screen_width = screen_width
        self.smoothing = smoothing
        self.x = 0.0
        self.target_x = 0.0

    def update(self, target_x: float) -> None:
        max_x = max(0, self.world_width - self.screen_width)
        self.target_x = max(0.0, min(float(target_x) - self.screen_width * 0.35, float(max_x)))
        self.x += (self.target_x - self.x) * self.smoothing
        self.x = max(0.0, min(self.x, float(max_x)))

    def apply(self, x: float) -> float:
        return x - self.x
