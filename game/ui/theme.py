from __future__ import annotations

import pygame

INK = (27, 47, 55)
MUTED_INK = (80, 105, 107)
PAPER = (248, 249, 237)
PAPER_LINE = (207, 222, 209)
TEAL = (28, 116, 112)
GREEN = (58, 142, 102)
CORAL = (219, 91, 71)
SUN = (244, 185, 71)
WHITE = (255, 255, 255)


def font(size: int, *, bold: bool = False) -> pygame.font.Font:
    pygame.font.init()
    return pygame.font.SysFont("trebuchetms", size, bold=bold)


def draw_backdrop(surface: pygame.Surface) -> None:
    width, height = surface.get_size()
    surface.fill((170, 216, 218))
    pygame.draw.circle(surface, (249, 198, 101), (int(width * 0.83), int(height * 0.16)), max(36, int(height * 0.075)))

    far_hill = [
        (0, int(height * 0.64)),
        (int(width * 0.18), int(height * 0.45)),
        (int(width * 0.38), int(height * 0.63)),
        (int(width * 0.63), int(height * 0.42)),
        (width, int(height * 0.61)),
        (width, height),
        (0, height),
    ]
    pygame.draw.polygon(surface, (131, 190, 158), far_hill)

    building = pygame.Rect(int(width * 0.12), int(height * 0.32), int(width * 0.25), int(height * 0.35))
    pygame.draw.rect(surface, (235, 228, 194), building, border_radius=8)
    pygame.draw.rect(surface, (46, 91, 93), (building.x, building.y, building.width, max(12, int(height * 0.035))))
    pygame.draw.rect(surface, (193, 125, 88), (building.x + int(building.width * 0.44), building.y + int(building.height * 0.57), int(building.width * 0.14), int(building.height * 0.43)))
    window_color = (90, 151, 157)
    for row in range(2):
        for col in range(3):
            window = pygame.Rect(
                building.x + int(building.width * (0.12 + col * 0.29)),
                building.y + int(building.height * (0.2 + row * 0.25)),
                max(10, int(building.width * 0.15)),
                max(10, int(building.height * 0.12)),
            )
            pygame.draw.rect(surface, window_color, window, border_radius=3)

    close_hill = [
        (0, int(height * 0.79)),
        (int(width * 0.24), int(height * 0.67)),
        (int(width * 0.5), int(height * 0.81)),
        (int(width * 0.74), int(height * 0.66)),
        (width, int(height * 0.78)),
        (width, height),
        (0, height),
    ]
    pygame.draw.polygon(surface, (70, 145, 106), close_hill)
    pygame.draw.rect(surface, (54, 119, 94), (0, int(height * 0.9), width, int(height * 0.1)))

    for index, x_ratio in enumerate((0.04, 0.42, 0.92)):
        x = int(width * x_ratio)
        y = int(height * (0.66 + (index % 2) * 0.08))
        pygame.draw.line(surface, (53, 99, 76), (x, y), (x, y - int(height * 0.11)), 5)
        pygame.draw.circle(surface, (52, 122, 84), (x, y - int(height * 0.14)), max(12, int(height * 0.04)))


def draw_heading(surface: pygame.Surface, title: str, subtitle: str, *, center_y_ratio: float = 0.1) -> None:
    width, height = surface.get_size()
    title_font = font(max(28, min(48, int(height * 0.064))), bold=True)
    subtitle_font = font(max(16, min(21, int(height * 0.027))))
    title_surface = title_font.render(title, True, INK)
    subtitle_surface = subtitle_font.render(subtitle, True, MUTED_INK)
    center_y = int(height * center_y_ratio)
    surface.blit(title_surface, title_surface.get_rect(center=(width // 2, center_y)))
    surface.blit(subtitle_surface, subtitle_surface.get_rect(center=(width // 2, center_y + title_surface.get_height() // 2 + subtitle_surface.get_height() // 2 + 7)))


def draw_wrapped_text(
    surface: pygame.Surface,
    text: str,
    text_font: pygame.font.Font,
    color: tuple[int, int, int],
    rect: pygame.Rect,
    *,
    line_gap: int = 4,
) -> int:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if line and text_font.size(candidate)[0] > rect.width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)

    y = rect.y
    line_height = text_font.get_linesize()
    for line in lines:
        if y + line_height > rect.bottom:
            break
        rendered = text_font.render(line, True, color)
        surface.blit(rendered, (rect.x, y))
        y += line_height + line_gap
    return y


def draw_card(surface: pygame.Surface, rect: pygame.Rect, *, selected: bool = False, accent: tuple[int, int, int] = TEAL) -> None:
    shadow = rect.move(0, 6)
    pygame.draw.rect(surface, (44, 83, 77), shadow, border_radius=12)
    pygame.draw.rect(surface, PAPER, rect, border_radius=12)
    pygame.draw.rect(surface, accent if selected else PAPER_LINE, rect, width=4 if selected else 2, border_radius=12)
