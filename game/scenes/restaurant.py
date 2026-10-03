import pygame

from game.characters import get_character_definition
from game.config.settings import SCREEN_HEIGHT, SCREEN_WIDTH
from game.scenes.sports_prototype import SportsPrototypeScene
from game.systems.restaurant_renderer import RestaurantRenderer


class RestaurantScene(SportsPrototypeScene):
    def __init__(self, game, scene_manager) -> None:
        super().__init__(game, scene_manager, use_stadium_renderer=False)
        self.level_name = "Canteen"
        self.world_width = 7000
        self.ground_y = 610
        self.player.rect.topleft = (140, self.ground_y - 64)
        self.player.set_ground(self.ground_y)
        self.platforms = [
            pygame.Rect(0, self.ground_y, self.world_width, 120),
            pygame.Rect(140, 560, 180, 18),
            pygame.Rect(490, 515, 200, 18),
            pygame.Rect(840, 470, 190, 18),
            pygame.Rect(1180, 430, 190, 18),
            pygame.Rect(1530, 380, 220, 18),
            pygame.Rect(1930, 335, 180, 18),
            pygame.Rect(2330, 420, 200, 18),
            pygame.Rect(2730, 360, 190, 18),
            pygame.Rect(3130, 305, 210, 18),
            pygame.Rect(3520, 415, 210, 18),
            pygame.Rect(3900, 360, 180, 18),
            pygame.Rect(4320, 470, 210, 18),
            pygame.Rect(4740, 405, 220, 18),
            pygame.Rect(5200, 340, 180, 18),
            pygame.Rect(5580, 300, 220, 18),
            pygame.Rect(5980, 360, 210, 18),
            pygame.Rect(6370, 290, 220, 18),
        ]
        self.moving_platforms = [
            {"rect": pygame.Rect(2650, 260, 160, 18), "min_x": 2500, "max_x": 3400, "speed": 72, "direction": 1},
            {"rect": pygame.Rect(5060, 250, 170, 18), "min_x": 4880, "max_x": 5650, "speed": 90, "direction": 1},
        ]
        self.hazards = [
            pygame.Rect(260, self.ground_y - 18, 48, 18),
            pygame.Rect(610, self.ground_y - 18, 56, 18),
            pygame.Rect(955, self.ground_y - 18, 52, 18),
            pygame.Rect(1500, self.ground_y - 18, 60, 18),
            pygame.Rect(2240, self.ground_y - 18, 52, 18),
            pygame.Rect(2960, self.ground_y - 18, 60, 18),
            pygame.Rect(4240, self.ground_y - 18, 54, 18),
            pygame.Rect(5470, self.ground_y - 18, 52, 18),
        ]
        self.collectibles = [
            {"rect": pygame.Rect(220, 530, 18, 18), "collected": False},
            {"rect": pygame.Rect(550, 481, 18, 18), "collected": False},
            {"rect": pygame.Rect(930, 435, 18, 18), "collected": False},
            {"rect": pygame.Rect(1225, 392, 18, 18), "collected": False},
            {"rect": pygame.Rect(1605, 341, 18, 18), "collected": False},
            {"rect": pygame.Rect(2050, 290, 18, 18), "collected": False},
            {"rect": pygame.Rect(2780, 320, 18, 18), "collected": False},
            {"rect": pygame.Rect(3200, 260, 18, 18), "collected": False},
            {"rect": pygame.Rect(3600, 372, 18, 18), "collected": False},
            {"rect": pygame.Rect(4445, 432, 18, 18), "collected": False},
            {"rect": pygame.Rect(5280, 300, 18, 18), "collected": False},
            {"rect": pygame.Rect(6100, 320, 18, 18), "collected": False},
        ]
        self.checkpoints = [
            {"rect": pygame.Rect(2120, self.ground_y - 120, 26, 120), "spawn": (2140, self.ground_y - 64), "active": False},
            {"rect": pygame.Rect(5200, self.ground_y - 120, 26, 120), "spawn": (5200, self.ground_y - 64), "active": False},
        ]
        self.current_checkpoint = (140, self.ground_y - 64)
        self.goal_rect = pygame.Rect(6600, self.ground_y - 180, 42, 180)
        self.total_collectibles = len(self.collectibles)
        self.double_jump_goal = max(4, self.total_collectibles // 3)
        self.collected_count = 0
        self.restaurant_renderer = RestaurantRenderer((SCREEN_WIDTH, SCREEN_HEIGHT), self.world_width)
        self.reset_level()

    def on_enter(self) -> None:
        self.state.current_scene = "restaurant"
        self.state.current_map = "Canteen"
        self.state.select_map("Canteen")
        self.player.set_character(get_character_definition(self.state.selected_character))
        self.reset_level()
        self._restore_progress()

    def draw(self, surface: pygame.Surface) -> None:
        self.restaurant_renderer.draw_background(
            surface,
            self.camera_x,
            self.ground_y,
            self.visual_time,
        )
        self.restaurant_renderer.draw_gameplay_objects(
            surface,
            self.camera_x,
            self.ground_y,
            self.platforms,
            self.moving_platforms,
            self.hazards,
            self.checkpoints,
            self.collectibles,
            self.goal_rect,
            self.player.rect,
            self.visual_time,
            self.collection_bursts,
        )
        self.player.draw(surface, self.camera_x)

        panel = pygame.Rect(16, 14, 248, 62)
        pygame.draw.rect(surface, (54, 39, 42), panel, border_radius=8)
        pygame.draw.rect(surface, (221, 183, 133), panel, width=2, border_radius=8)
        name = self.label_font.render(f"RUNNER  {self.state.selected_character.upper()}", True, (255, 240, 213))
        marks = self.label_font.render(f"MARKS  {self.collected_count:02} / {self.total_collectibles:02}", True, (255, 211, 121))
        surface.blit(name, (28, 22))
        surface.blit(marks, (28, 48))

        if self.collection_message:
            text = self.hint_font.render(self.collection_message, True, (255, 233, 190))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 112))
            backing = text_rect.inflate(30, 14)
            pygame.draw.rect(surface, (65, 48, 43), backing, border_radius=9)
            pygame.draw.rect(surface, (218, 175, 121), backing, width=2, border_radius=9)
            surface.blit(text, text_rect)

        if self.level_complete:
            message = "CANTEEN COMPLETE!"
        elif self.player_dead:
            message = "Returning to the checkpoint..."
        elif self.player.rect.x < 1200:
            message = "Explore the canteen. Jump with Space."
        else:
            message = "CANTEEN  |  LEVEL 1"
        status = self.hint_font.render(message, True, (255, 244, 216))
        status_rect = status.get_rect(center=(SCREEN_WIDTH // 2, 34)).inflate(26, 12)
        pygame.draw.rect(surface, (54, 39, 42), status_rect, border_radius=7)
        pygame.draw.rect(surface, (217, 179, 133), status_rect, width=1, border_radius=7)
        surface.blit(status, status.get_rect(center=status_rect.center))