import pygame

from game.characters import get_character_definition
from game.config.settings import SCREEN_HEIGHT, SCREEN_WIDTH
from game.core.scene import Scene
from game.ui.button import Button


class CharacterSelectScene(Scene):
    def __init__(self, game, scene_manager) -> None:
        super().__init__(game, scene_manager)
        pygame.font.init()
        self.title_font = pygame.font.SysFont(None, 70, bold=True)
        self.label_font = pygame.font.SysFont(None, 26)
        self.card_font = pygame.font.SysFont(None, 42, bold=True)
        self.selection_font = pygame.font.SysFont(None, 26)

        self.character_options = [
            {
                "name": "Jason",
                "color": (104, 166, 255),
                "description": "Freeze power",
                "ability": "freeze",
            },
            {
                "name": "Krrish",
                "color": (106, 197, 118),
                "description": "Double jump power",
                "ability": "double_jump",
            },
        ]
        self.selected_index = 0
        self.card_width = 300
        self.card_height = 330
        self.card_gap = 42
        self.start_x = (SCREEN_WIDTH - (self.card_width * 2 + self.card_gap)) // 2

        self.buttons = [
            Button(
                90,
                SCREEN_HEIGHT - 110,
                220,
                56,
                "Back",
                on_click=lambda: self.manager.change_scene("menu"),
                font_size=26,
                fill_color=(97, 101, 117),
            ),
            Button(
                SCREEN_WIDTH - 310,
                SCREEN_HEIGHT - 110,
                220,
                56,
                "Start Adventure",
                on_click=self.confirm_selection,
                font_size=24,
                fill_color=(36, 152, 98),
            ),
            Button(
                SCREEN_WIDTH // 2 - 110,
                SCREEN_HEIGHT - 110,
                220,
                56,
                "Restaurant Map",
                on_click=self.start_restaurant,
                font_size=22,
                fill_color=(143, 91, 62),
            ),
        ]

    def confirm_selection(self) -> None:
        character_name = self.character_options[self.selected_index]["name"]
        self.state.selected_character = character_name
        self.state.current_scene = "sports_prototype"
        self.state.current_map = "Campus Track"
        self.state.select_character(character_name)
        self.state.select_map("Campus Track")

        if "sports_prototype" in self.manager.scenes:
            self.manager.change_scene("sports_prototype")

    def start_restaurant(self) -> None:
        character_name = self.character_options[self.selected_index]["name"]
        self.state.selected_character = character_name
        self.state.current_scene = "restaurant"
        self.state.current_map = "Canteen"
        self.state.select_character(character_name)
        self.state.select_map("Canteen")

        if "restaurant" in self.manager.scenes:
            self.manager.change_scene("restaurant")

    def on_enter(self) -> None:
        configured = self.state.selected_character
        for index, item in enumerate(self.character_options):
            if item["name"] == configured:
                self.selected_index = index
                break
        else:
            self.selected_index = 1

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, _ in enumerate(self.character_options):
                card_x = self.start_x + index * (self.card_width + self.card_gap)
                card_rect = pygame.Rect(card_x, 190, self.card_width, self.card_height)
                if card_rect.collidepoint(event.pos):
                    self.selected_index = index
                    return

        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((17, 25, 39))

        title = self.title_font.render("Choose a Hero", True, (248, 250, 252))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 74))
        surface.blit(title, title_rect)

        for index, item in enumerate(self.character_options):
            x = self.start_x + index * (self.card_width + self.card_gap)
            y = 190
            rect = pygame.Rect(x, y, self.card_width, self.card_height)
            active = index == self.selected_index

            outline_color = (255, 207, 96) if active else (125, 138, 165)
            card_color = (30, 41, 59) if not active else (40, 56, 83)
            pygame.draw.rect(surface, card_color, rect, border_radius=22)
            pygame.draw.rect(surface, outline_color, rect, width=4, border_radius=22)

            avatar = pygame.Surface((140, 140), pygame.SRCALPHA)
            pygame.draw.ellipse(avatar, item["color"], (0, 25, 140, 140))
            avatar_rect = avatar.get_rect(center=(rect.centerx, rect.top + 110))
            surface.blit(avatar, avatar_rect)

            name_text = self.card_font.render(item["name"], True, (250, 250, 250))
            name_rect = name_text.get_rect(center=(rect.centerx, rect.top + 230))
            surface.blit(name_text, name_rect)

            desc = get_character_definition(item["name"])
            desc_text = self.selection_font.render(f"{desc.ability_label} • {desc.style}", True, (191, 206, 236))
            desc_rect = desc_text.get_rect(center=(rect.centerx, rect.top + 262))
            surface.blit(desc_text, desc_rect)

        selected_name = self.character_options[self.selected_index]["name"]
        selected_text = self.label_font.render(
            f"Selected: {selected_name}",
            True,
            (255, 214, 102),
        )
        selected_rect = selected_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        surface.blit(selected_text, selected_rect)

        for button in self.buttons:
            button.draw(surface)
