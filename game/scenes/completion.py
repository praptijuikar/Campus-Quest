import pygame

from game.config.settings import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.scene import Scene
from game.ui.button import Button
from game.ui.theme import CORAL, GREEN, INK, SUN, TEAL, WHITE, draw_backdrop, font


class CompletionScene(Scene):
    def __init__(self, game, scene_manager) -> None:
        super().__init__(game, scene_manager)
        button_width = min(270, int(SCREEN_WIDTH * 0.23))
        button_height = max(54, int(SCREEN_HEIGHT * 0.075))
        gap = max(18, int(SCREEN_WIDTH * 0.025))
        left = (SCREEN_WIDTH - button_width * 3 - gap * 2) // 2
        y = int(SCREEN_HEIGHT * 0.77)
        self.buttons = [
            Button(
                left,
                y,
                button_width,
                button_height,
                "PLAY AGAIN",
                on_click=self.replay,
                font_size=20,
                fill_color=TEAL,
                hover_color=(43, 143, 136),
                border_color=SUN,
                radius=10,
            ),
            Button(
                left + button_width + gap,
                y,
                button_width,
                button_height,
                "CHOOSE MAP",
                on_click=self.choose_map,
                font_size=20,
                fill_color=GREEN,
                hover_color=(79, 164, 119),
                border_color=WHITE,
                radius=10,
            ),
            Button(
                left + (button_width + gap) * 2,
                y,
                button_width,
                button_height,
                "HOME",
                on_click=lambda: self.manager.change_scene("menu"),
                font_size=20,
                fill_color=CORAL,
                hover_color=(232, 116, 91),
                border_color=WHITE,
                radius=10,
            ),
        ]

    def on_enter(self) -> None:
        self.state.game_completed = True

    def replay(self) -> None:
        scene_name = "sports_prototype" if self.state.current_map == "Campus Track" else "restaurant"
        self.manager.change_scene(scene_name)

    def choose_map(self) -> None:
        map_scene = self.manager.scenes.get("map_select")
        if map_scene is not None:
            map_scene.return_scene = "completion"
        self.manager.change_scene("map_select")

    def handle_event(self, event) -> None:
        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        draw_backdrop(surface)
        panel = pygame.Rect(int(width * 0.17), int(height * 0.13), int(width * 0.66), int(height * 0.53))
        pygame.draw.rect(surface, (44, 83, 77), panel.move(0, 7), border_radius=16)
        pygame.draw.rect(surface, (248, 249, 237), panel, border_radius=16)
        pygame.draw.rect(surface, (255, 255, 255), panel, width=2, border_radius=16)

        title_font = font(max(34, min(52, int(height * 0.07))), bold=True)
        subtitle_font = font(23, bold=True)
        detail_font = font(19)
        title = title_font.render("QUEST COMPLETE!", True, INK)
        surface.blit(title, title.get_rect(center=(width // 2, int(height * 0.25))))
        pygame.draw.rect(surface, CORAL, (width // 2 - 40, int(height * 0.31), 80, 5), border_radius=3)

        map_name = self.state.current_map if self.state.current_map in {"Campus Track", "Canteen"} else "Campus Track"
        subtitle = subtitle_font.render(f"{map_name} finished", True, TEAL)
        surface.blit(subtitle, subtitle.get_rect(center=(width // 2, int(height * 0.39))))

        details = (
            f"Player: {self.state.selected_character}",
            f"Marks collected: {self.state.score // 100}",
        )
        for index, detail in enumerate(details):
            rendered = detail_font.render(detail, True, (73, 101, 101))
            surface.blit(rendered, rendered.get_rect(center=(width // 2, int(height * 0.49) + index * 36)))

        for button in self.buttons:
            button.draw(surface)
