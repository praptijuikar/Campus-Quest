from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygame import Surface

    from game.core.scene_manager import SceneManager


class Scene(ABC):
    def __init__(self, game: object, scene_manager: "SceneManager") -> None:
        self.game = game
        self.manager = scene_manager
        self.state = game.state

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    @abstractmethod
    def handle_event(self, event) -> None:
        raise NotImplementedError

    @abstractmethod
    def update(self, dt: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw(self, surface: "Surface") -> None:
        raise NotImplementedError
