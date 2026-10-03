import pygame


class Button:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        on_click=None,
        font_size: int = 28,
        fill_color=(76, 120, 215),
        hover_color=(97, 152, 255),
        text_color=(255, 255, 255),
        border_color=(255, 255, 255),
        radius: int = 16,
    ) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.on_click = on_click
        self.font = pygame.font.SysFont(None, font_size)
        self.fill_color = fill_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.radius = radius
        self.is_hovered = False

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.on_click is not None:
                self.on_click()

    def draw(self, surface: pygame.Surface) -> None:
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        color = self.hover_color if self.is_hovered else self.fill_color

        pygame.draw.rect(surface, color, self.rect, border_radius=self.radius)
        pygame.draw.rect(surface, self.border_color, self.rect, width=2, border_radius=self.radius)

        label = self.font.render(self.text, True, self.text_color)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)
