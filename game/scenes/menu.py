import pygame

from game.config.settings import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.scene import Scene
from game.ui.button import Button


class MenuScene(Scene):
    def __init__(self, game, scene_manager) -> None:
        super().__init__(game, scene_manager)
        pygame.font.init()

        self.title_font = pygame.font.SysFont(None, 88, bold=True)
        self.subtitle_font = pygame.font.SysFont(None, 30)
        self.button_font = pygame.font.SysFont(None, 30)

        self.buttons = [
            Button(
                SCREEN_WIDTH // 2 - 170,
                240,
                340,
                58,
                "Play",
                on_click=lambda: self.manager.change_scene("character_select"),
                font_size=30,
            ),
            Button(
                SCREEN_WIDTH // 2 - 170,
                315,
                340,
                58,
                "Levels",
                on_click=lambda: self.manager.change_scene("character_select"),
                font_size=28,
            ),
            Button(
                SCREEN_WIDTH // 2 - 170,
                390,
                340,
                58,
                "Character",
                on_click=lambda: self.manager.change_scene("character_select"),
                font_size=28,
            ),
            Button(
                SCREEN_WIDTH // 2 - 170,
                465,
                340,
                58,
                "Settings",
                on_click=lambda: self.show_placeholder_message("Settings are coming soon."),
                font_size=28,
            ),
            Button(
                SCREEN_WIDTH // 2 - 170,
                540,
                340,
                58,
                "Exit",
                on_click=self.game.quit,
                font_size=28,
            ),
        ]
        self.placeholder_message = ""

    def show_placeholder_message(self, message: str) -> None:
        self.placeholder_message = message

    def handle_event(self, event) -> None:
        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((19, 28, 46))

        glow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (86, 141, 255, 75), (220, 90, 840, 220))
        surface.blit(glow, (0, 0))

        title = self.title_font.render("Campus Quest", True, (242, 247, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        surface.blit(title, title_rect)

        subtitle = self.subtitle_font.render(
            "Choose your path. Chase the finish.",
            True,
            (194, 208, 236),
        )
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 205))
        surface.blit(subtitle, subtitle_rect)

        for button in self.buttons:
            button.draw(surface)

        if self.placeholder_message:
            hint = self.subtitle_font.render(self.placeholder_message, True, (255, 214, 102))
            hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, 620))
            surface.blit(hint, hint_rect)
