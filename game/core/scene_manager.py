from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.core.scene import Scene


class SceneManager:
    def __init__(self, game: object) -> None:
        self.game = game
        self.scenes: dict[str, Scene] = {}
        self.current_scene: Scene | None = None
        self.current_scene_name: str | None = None

    def register(self, name: str, scene: "Scene") -> None:
        self.scenes[name] = scene

    def change_scene(self, name: str) -> None:
        if name not in self.scenes:
            raise KeyError(f"Scene '{name}' is not registered.")

        if self.current_scene is not None:
            self.current_scene.on_exit()

        self.current_scene = self.scenes[name]
        self.current_scene_name = name
        self.current_scene.on_enter()

    def handle_event(self, event) -> None:
        if self.current_scene is not None:
            self.current_scene.handle_event(event)

    def update(self, dt: float) -> None:
        if self.current_scene is not None:
            self.current_scene.update(dt)

    def draw(self, surface) -> None:
        if self.current_scene is not None:
            self.current_scene.draw(surface)
