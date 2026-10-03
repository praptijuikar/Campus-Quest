import pygame

from game.config.settings import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.scene import Scene
from game.ui.button import Button
from game.ui.theme import (
    CORAL,
    GREEN,
    INK,
    MUTED_INK,
    PAPER,
    SUN,
    TEAL,
    WHITE,
    draw_backdrop,
    draw_card,
    draw_heading,
    draw_wrapped_text,
    font,
)


class MapSelectScene(Scene):
    def __init__(self, game, scene_manager) -> None:
        super().__init__(game, scene_manager)
        self.maps = [
            {
                "name": "Campus Track",
                "description": "Run through the campus track, collect marks, and reach the finish.",
                "scene": "sports_prototype",
                "accent": GREEN,
            },
            {
                "name": "Canteen",
                "description": "Navigate the campus canteen, collect marks, and find the exit.",
                "scene": "restaurant",
                "accent": CORAL,
            },
        ]
        self.selected_index = 0
        self.return_scene = "menu"
        card_width = min(520, int(SCREEN_WIDTH * 0.43))
        card_height = min(405, int(SCREEN_HEIGHT * 0.57))
        gap = max(24, int(SCREEN_WIDTH * 0.035))
        self.card_rects = [
            pygame.Rect((SCREEN_WIDTH - card_width * 2 - gap) // 2 + index * (card_width + gap), int(SCREEN_HEIGHT * 0.27), card_width, card_height)
            for index in range(2)
        ]
        button_width = min(250, int(SCREEN_WIDTH * 0.22))
        button_height = max(54, int(SCREEN_HEIGHT * 0.075))
        self.back_button = Button(
            int(SCREEN_WIDTH * 0.07), SCREEN_HEIGHT - button_height - 26, button_width, button_height,
            "BACK", on_click=self.go_back, font_size=21,
            fill_color=(71, 91, 95), hover_color=(91, 118, 119), border_color=WHITE, radius=10,
        )
        self.play_button = Button(
            SCREEN_WIDTH - int(SCREEN_WIDTH * 0.07) - button_width, SCREEN_HEIGHT - button_height - 26,
            button_width, button_height, "PLAY", on_click=self.start_game, font_size=23,
            fill_color=TEAL, hover_color=(43, 143, 136), border_color=SUN, radius=10,
        )
        self.buttons = [self.back_button, self.play_button]
        self.preview_cache: dict[str, pygame.Surface] = {}

    def on_enter(self) -> None:
        selected_map = self.state.current_map
        if selected_map not in {item["name"] for item in self.maps}:
            self.state.select_map("Campus Track")
            selected_map = "Campus Track"
        self.selected_index = next(index for index, item in enumerate(self.maps) if item["name"] == selected_map)

    def select_map(self, index: int) -> None:
        self.selected_index = index % len(self.maps)
        self.state.select_map(self.maps[self.selected_index]["name"])

    def go_back(self) -> None:
        self.manager.change_scene(self.return_scene)

    def start_game(self) -> None:
        selected = self.maps[self.selected_index]
        self.state.select_map(selected["name"])
        self.state.current_scene = selected["scene"]
        if selected["scene"] in self.manager.scenes:
            self.manager.change_scene(selected["scene"])

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.select_map(self.selected_index + (-1 if event.key == pygame.K_LEFT else 1))
                return
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_game()
                return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, card_rect in enumerate(self.card_rects):
                if card_rect.collidepoint(event.pos):
                    self.select_map(index)
                    return
        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt: float) -> None:
        pass

    def _make_preview(self, map_name: str) -> pygame.Surface | None:
        if map_name in self.preview_cache:
            return self.preview_cache[map_name]

        scene_name = "sports_prototype" if map_name == "Campus Track" else "restaurant"
        scene = self.manager.scenes.get(scene_name)
        if scene is None:
            return None
        preview = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        preview.fill((170, 216, 218))
        if scene_name == "sports_prototype" and scene.stadium_renderer is not None:
            renderer = scene.stadium_renderer
            renderer.draw_background(preview, 0)
            renderer.draw_field_and_track(preview, 0, scene.ground_y)
            renderer.draw_landmarks(preview, 0, 0)
        elif scene_name == "restaurant" and hasattr(scene, "restaurant_renderer"):
            scene.restaurant_renderer.draw_background(preview, 0, scene.ground_y, 0)
        self.preview_cache[map_name] = preview
        return preview

    def draw(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        draw_backdrop(surface)
        draw_heading(surface, "CHOOSE YOUR MAP", "Pick a place to explore. Your player stays selected.", center_y_ratio=0.085)

        status_font = font(16, bold=True)
        player_status = status_font.render(f"PLAYER: {self.state.selected_character.upper()}", True, INK)
        status_rect = pygame.Rect(width // 2 - 100, int(height * 0.17), 200, 28)
        pygame.draw.rect(surface, (248, 249, 237), status_rect, border_radius=8)
        surface.blit(player_status, player_status.get_rect(center=status_rect.center))

        for index, item in enumerate(self.maps):
            base_rect = self.card_rects[index]
            rect = pygame.Rect(
                round(base_rect.x * width / SCREEN_WIDTH),
                round(base_rect.y * height / SCREEN_HEIGHT),
                round(base_rect.width * width / SCREEN_WIDTH),
                round(base_rect.height * height / SCREEN_HEIGHT),
            )
            selected = index == self.selected_index
            draw_card(surface, rect, selected=selected, accent=item["accent"])
            title = font(26, bold=True).render(item["name"].upper(), True, INK)
            surface.blit(title, title.get_rect(center=(rect.centerx, rect.y + 31)))

            preview_rect = pygame.Rect(rect.x + 22, rect.y + 56, rect.width - 44, int(rect.height * 0.48))
            preview = self._make_preview(item["name"])
            if preview is not None:
                scaled_preview = pygame.transform.smoothscale(preview, preview_rect.size)
                surface.blit(scaled_preview, preview_rect)
            else:
                pygame.draw.rect(surface, (162, 207, 194), preview_rect)
            pygame.draw.rect(surface, (69, 103, 98), preview_rect, width=2)

            description_rect = pygame.Rect(rect.x + 28, preview_rect.bottom + 14, rect.width - 56, 48)
            draw_wrapped_text(surface, item["description"], font(17), MUTED_INK, description_rect, line_gap=2)

            state_text = "SELECTED" if selected else "SELECT MAP"
            state_color = CORAL if selected else TEAL
            state_surface = font(14, bold=True).render(state_text, True, state_color)
            surface.blit(state_surface, state_surface.get_rect(center=(rect.centerx, rect.bottom - 20)))

        for button in self.buttons:
            button.draw(surface)
