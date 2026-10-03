import sqlite3
from pathlib import Path

import pygame

from game.audio import AudioManager
from game.backend.database import DatabaseStore
from game.config.settings import (
    FPS,
    GAME_TITLE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from game.core.game_state import GameState
from game.core.scene_manager import SceneManager
from game.scenes.character_select import CharacterSelectScene
from game.scenes.completion import CompletionScene
from game.scenes.map_select import MapSelectScene
from game.scenes.menu import MenuScene
from game.scenes.restaurant import RestaurantScene
from game.scenes.sports_prototype import SportsPrototypeScene


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState()
        database_path = Path(__file__).resolve().parents[2] / "game_progress.db"
        try:
            self.progress_store: DatabaseStore | None = DatabaseStore(str(database_path))
            self.saved_progress = self.progress_store.get_progress(player_id="local")
        except sqlite3.Error:
            self.progress_store = None
            self.saved_progress = {
                "character": "",
                "map_name": "",
                "score": 0,
                "checkpoint": 0,
                "collected_count": 0,
                "collected_items": [],
                "completed": 0,
            }
        if self.saved_progress["character"] in {"Jason", "Krrish"}:
            self.state.select_character(self.saved_progress["character"])
        if self.saved_progress["map_name"] in {"Campus Track", "Canteen"}:
            self.state.select_map(self.saved_progress["map_name"])
        self.state.score = int(self.saved_progress["score"])
        self.audio = AudioManager()
        self.scene_manager = SceneManager(self)
        self.scene_manager.register("menu", MenuScene(self, self.scene_manager))
        self.scene_manager.register(
            "character_select",
            CharacterSelectScene(self, self.scene_manager),
        )
        self.scene_manager.register(
            "map_select",
            MapSelectScene(self, self.scene_manager),
        )
        self.scene_manager.register(
            "completion",
            CompletionScene(self, self.scene_manager),
        )
        self.scene_manager.register(
            "sports_prototype",
            SportsPrototypeScene(self, self.scene_manager),
        )
        self.scene_manager.register(
            "restaurant",
            RestaurantScene(self, self.scene_manager),
        )
        self.scene_manager.change_scene("menu")

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.scene_manager.handle_event(event)

    def update(self, dt: float) -> None:
        self.scene_manager.update(dt)

    def draw(self) -> None:
        self.screen.fill((18, 28, 38))
        self.scene_manager.draw(self.screen)
        pygame.display.flip()

    def run(self) -> None:
        try:
            while self.running:
                dt = self.clock.tick(FPS) / 1000.0
                self.handle_events()
                self.update(dt)
                self.draw()
        finally:
            if self.progress_store is not None:
                self.progress_store.close()
            pygame.quit()

    def save_progress(
        self,
        *,
        checkpoint: int,
        collected_items: list[int],
        completed: bool = False,
    ) -> None:
        self.state.score = len(collected_items) * 100
        self.state.game_completed = completed
        if self.progress_store is None:
            return
        try:
            self.saved_progress = self.progress_store.save_progress(
                player_id="local",
                character=self.state.selected_character,
                map_name=self.state.current_map,
                score=self.state.score,
                checkpoint=checkpoint,
                collected_count=len(collected_items),
                collected_items=collected_items,
                completed=completed,
            )
        except sqlite3.Error:
            self.progress_store.close()
            self.progress_store = None

    def quit(self) -> None:
        self.running = False
