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
        selected: bool = False,
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
        self.is_pressed = False
        self.is_focused = False
        self.selected = selected

    def activate(self) -> None:
        if self.on_click is not None:
            self.on_click()

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_pressed = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.is_pressed
            self.is_pressed = False
            if was_pressed and self.rect.collidepoint(event.pos):
                self.activate()

    def draw(self, surface: pygame.Surface) -> None:
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        color = self.fill_color
        if self.is_hovered or self.is_focused:
            color = self.hover_color
        if self.is_pressed:
            color = tuple(max(0, channel - 24) for channel in color)

        pygame.draw.rect(surface, color, self.rect, border_radius=self.radius)
        border = self.border_color if self.selected or self.is_focused else (255, 255, 255, 150)
        pygame.draw.rect(surface, border, self.rect, width=3 if self.selected or self.is_focused else 1, border_radius=self.radius)

        label = self.font.render(self.text, True, self.text_color)
        if label.get_width() > self.rect.width - 28:
            label = pygame.transform.smoothscale(label, (self.rect.width - 28, label.get_height()))
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)
