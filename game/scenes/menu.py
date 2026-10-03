import pygame

from game.config.settings import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.scene import Scene
from game.ui.button import Button
from game.ui.theme import CORAL, GREEN, INK, SUN, TEAL, draw_backdrop, font


class MenuScene(Scene):
    def __init__(self, game, scene_manager) -> None:
        super().__init__(game, scene_manager)
        pygame.font.init()
        self.title_font = font(58, bold=True)
        self.subtitle_font = font(22)
        self.notice_font = font(17, bold=True)
        self.notice = ""
        self.notice_timer = 0.0

        button_width = min(330, int(SCREEN_WIDTH * 0.28))
        button_height = max(58, int(SCREEN_HEIGHT * 0.09))
        gap_x = max(20, int(SCREEN_WIDTH * 0.035))
        gap_y = max(16, int(SCREEN_HEIGHT * 0.035))
        left = (SCREEN_WIDTH - button_width * 2 - gap_x) // 2
        top = int(SCREEN_HEIGHT * 0.46)
        button_specs = [
            ("PLAY", TEAL, self.start_game),
            ("PLAYERS", GREEN, lambda: self.manager.change_scene("character_select")),
            ("MAPS", CORAL, self.open_maps),
            ("SETTINGS", (67, 91, 96), lambda: self.show_notice("Settings are not available yet.")),
        ]
        self.buttons = []
        for index, (label, color, action) in enumerate(button_specs):
            row, column = divmod(index, 2)
            button = Button(
                left + column * (button_width + gap_x),
                top + row * (button_height + gap_y),
                button_width,
                button_height,
                label,
                on_click=action,
                font_size=26,
                fill_color=color,
                hover_color=tuple(min(255, channel + 20) for channel in color),
                text_color=(255, 255, 247),
                border_color=SUN,
                radius=12,
            )
            self.buttons.append(button)
        self.focus_index = 0
        self.buttons[self.focus_index].is_focused = True

    def show_notice(self, message: str) -> None:
        self.notice = message
        self.notice_timer = 2.5

    def open_maps(self) -> None:
        map_scene = self.manager.scenes.get("map_select")
        if map_scene is not None:
            map_scene.return_scene = "menu"
            self.manager.change_scene("map_select")

    def start_game(self) -> None:
        selected_map = self.state.current_map
        if selected_map not in ("Campus Track", "Canteen"):
            selected_map = "Campus Track"
            self.state.select_map(selected_map)
        scene_name = "sports_prototype" if selected_map == "Campus Track" else "restaurant"
        self.state.current_scene = scene_name
        self.manager.change_scene(scene_name)

    def _set_focus(self, index: int) -> None:
        self.focus_index = index % len(self.buttons)
        for button_index, button in enumerate(self.buttons):
            button.is_focused = button_index == self.focus_index

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RIGHT, pygame.K_DOWN, pygame.K_TAB):
                self._set_focus(self.focus_index + 1)
                return
            if event.key in (pygame.K_LEFT, pygame.K_UP):
                self._set_focus(self.focus_index - 1)
                return
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.buttons[self.focus_index].activate()
                return
        if event.type == pygame.MOUSEMOTION:
            for index, button in enumerate(self.buttons):
                if button.rect.collidepoint(event.pos):
                    self._set_focus(index)
                    break
        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt: float) -> None:
        if self.notice_timer > 0:
            self.notice_timer = max(0.0, self.notice_timer - dt)
            if self.notice_timer == 0:
                self.notice = ""

    def draw(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        draw_backdrop(surface)

        header = pygame.Rect(int(width * 0.16), int(height * 0.065), int(width * 0.68), int(height * 0.31))
        pygame.draw.rect(surface, (248, 249, 237, 235), header.move(0, 7), border_radius=18)
        pygame.draw.rect(surface, (248, 249, 237), header, border_radius=18)
        pygame.draw.rect(surface, (255, 255, 255), header, width=2, border_radius=18)

        title = self.title_font.render("CAMPUS QUEST", True, INK)
        surface.blit(title, title.get_rect(center=(width // 2, int(height * 0.18))))
        pygame.draw.rect(surface, CORAL, (width // 2 - 42, int(height * 0.235), 84, 5), border_radius=3)
        subtitle = self.subtitle_font.render("Explore. Collect. Complete the Quest.", True, (65, 94, 94))
        surface.blit(subtitle, subtitle.get_rect(center=(width // 2, int(height * 0.285))))

        for button in self.buttons:
            button.draw(surface)

        if self.notice:
            notice_rect = pygame.Rect(width // 2 - 190, int(height * 0.87), 380, 38)
            pygame.draw.rect(surface, INK, notice_rect, border_radius=8)
            notice = self.notice_font.render(self.notice, True, (255, 246, 217))
            surface.blit(notice, notice.get_rect(center=notice_rect.center))
