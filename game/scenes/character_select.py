import pygame

from game.characters import get_character_definition
from game.config.settings import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.scene import Scene
from game.graphics import SpriteSheetLoader
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
    font,
)


class CharacterSelectScene(Scene):
    def __init__(self, game, scene_manager) -> None:
        super().__init__(game, scene_manager)
        self.title_font = font(31, bold=True)
        self.role_font = font(20, bold=True)
        self.body_font = font(17)
        self.label_font = font(14, bold=True)
        self.character_options = [
            {
                "name": "Jason",
                "role": "Student Adventurer",
                "description": "A steady explorer who controls the pace of a challenge.",
                "ability": "freeze",
                "ability_label": "Freeze",
                "accent": (79, 139, 197),
            },
            {
                "name": "Krrish",
                "role": "Creative Student",
                "description": "A quick thinker who can reach higher routes in the air.",
                "ability": "double_jump",
                "ability_label": "Double Jump",
                "accent": GREEN,
            },
        ]
        self.selected_index = 0
        self.sprite_loader = SpriteSheetLoader()
        card_width = min(390, int(SCREEN_WIDTH * 0.34))
        card_height = min(430, int(SCREEN_HEIGHT * 0.61))
        gap = max(24, int(SCREEN_WIDTH * 0.045))
        self.card_rects = [
            pygame.Rect((SCREEN_WIDTH - card_width * 2 - gap) // 2 + index * (card_width + gap), int(SCREEN_HEIGHT * 0.235), card_width, card_height)
            for index in range(2)
        ]
        button_width = min(260, int(SCREEN_WIDTH * 0.23))
        button_height = max(54, int(SCREEN_HEIGHT * 0.075))
        self.back_button = Button(
            int(SCREEN_WIDTH * 0.07), SCREEN_HEIGHT - button_height - 28, button_width, button_height,
            "BACK", on_click=lambda: self.manager.change_scene("menu"), font_size=21,
            fill_color=(71, 91, 95), hover_color=(91, 118, 119), border_color=WHITE, radius=10,
        )
        self.continue_button = Button(
            SCREEN_WIDTH - int(SCREEN_WIDTH * 0.07) - button_width, SCREEN_HEIGHT - button_height - 28,
            button_width, button_height, "CONTINUE TO MAPS", on_click=self.confirm_selection, font_size=20,
            fill_color=TEAL, hover_color=(43, 143, 136), border_color=SUN, radius=10,
        )
        self.buttons = [self.back_button, self.continue_button]

    def confirm_selection(self) -> None:
        character_name = self.character_options[self.selected_index]["name"]
        self.state.select_character(character_name)
        map_scene = self.manager.scenes.get("map_select")
        if map_scene is not None:
            map_scene.return_scene = "character_select"
        self.manager.change_scene("map_select")

    def on_enter(self) -> None:
        self.selected_index = next(
            (index for index, item in enumerate(self.character_options) if item["name"] == self.state.selected_character),
            0,
        )

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            delta = -1 if event.key == pygame.K_LEFT else 1
            self.selected_index = (self.selected_index + delta) % len(self.character_options)
            self.state.select_character(self.character_options[self.selected_index]["name"])
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, card_rect in enumerate(self.card_rects):
                if card_rect.collidepoint(event.pos):
                    self.selected_index = index
                    self.state.select_character(self.character_options[index]["name"])
                    return
        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt: float) -> None:
        pass

    def _draw_character_sprite(self, surface: pygame.Surface, name: str, center: tuple[int, int]) -> None:
        frames = self.sprite_loader.get_animation(name, "idle")
        if not frames:
            return
        sprite = pygame.transform.smoothscale(frames[0], (128, 128))
        surface.blit(sprite, sprite.get_rect(center=center))

    def draw(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        draw_backdrop(surface)
        draw_heading(surface, "CHOOSE YOUR PLAYER", "Two students. Two very different ways to explore.", center_y_ratio=0.09)

        for index, item in enumerate(self.character_options):
            rect = self.card_rects[index]
            rect = pygame.Rect(
                round(rect.x * width / SCREEN_WIDTH),
                round(rect.y * height / SCREEN_HEIGHT),
                round(rect.width * width / SCREEN_WIDTH),
                round(rect.height * height / SCREEN_HEIGHT),
            )
            selected = index == self.selected_index
            draw_card(surface, rect, selected=selected, accent=item["accent"])
            pygame.draw.rect(surface, item["accent"], (rect.x + 3, rect.y + 3, rect.width - 6, 9), border_radius=5)

            name_surface = self.title_font.render(item["name"].upper(), True, INK)
            surface.blit(name_surface, name_surface.get_rect(center=(rect.centerx, rect.y + 48)))
            self._draw_character_sprite(surface, item["name"], (rect.centerx, rect.y + int(rect.height * 0.39)))

            role_surface = self.role_font.render(item["role"], True, TEAL)
            surface.blit(role_surface, role_surface.get_rect(center=(rect.centerx, rect.y + int(rect.height * 0.63))))
            description_font = font(max(15, min(17, int(height * 0.024))))
            description = description_font.render(item["description"], True, MUTED_INK)
            if description.get_width() > rect.width - 44:
                description = pygame.transform.smoothscale(description, (rect.width - 44, description.get_height()))
            surface.blit(description, description.get_rect(center=(rect.centerx, rect.y + int(rect.height * 0.72))))

            ability_rect = pygame.Rect(rect.x + 26, rect.y + int(rect.height * 0.79), rect.width - 52, 48)
            pygame.draw.rect(surface, (226, 239, 226), ability_rect, border_radius=8)
            ability_label = self.label_font.render("SPECIAL ABILITY", True, MUTED_INK)
            ability = self.body_font.render(item["ability_label"], True, INK)
            surface.blit(ability_label, ability_label.get_rect(center=(ability_rect.centerx, ability_rect.y + 13)))
            surface.blit(ability, ability.get_rect(center=(ability_rect.centerx, ability_rect.y + 33)))

            marker = "SELECTED" if selected else "SELECT"
            marker_color = CORAL if selected else TEAL
            marker_surface = self.label_font.render(marker, True, marker_color)
            surface.blit(marker_surface, marker_surface.get_rect(center=(rect.centerx, rect.bottom - 19)))

        for button in self.buttons:
            button.draw(surface)
