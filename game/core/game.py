import pygame

from game.audio import AudioManager
from game.config.settings import (
    FPS,
    GAME_TITLE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from game.core.game_state import GameState
from game.core.scene_manager import SceneManager
from game.scenes.character_select import CharacterSelectScene
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
        self.audio = AudioManager()
        self.scene_manager = SceneManager(self)
        self.scene_manager.register("menu", MenuScene(self, self.scene_manager))
        self.scene_manager.register(
            "character_select",
            CharacterSelectScene(self, self.scene_manager),
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
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()

    def quit(self) -> None:
        self.running = False
