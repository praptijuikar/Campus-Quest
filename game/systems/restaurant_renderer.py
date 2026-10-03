from __future__ import annotations

import math

import pygame


class RestaurantRenderer:
    TILE_WIDTH = 2560

    def __init__(self, screen_size: tuple[int, int], world_width: int) -> None:
        pygame.font.init()
        self.screen_width, self.screen_height = screen_size
        self.world_width = world_width
        self.sign_font = pygame.font.SysFont("arial", 16, bold=True)
        self.detail_font = pygame.font.SysFont("arial", 13, bold=True)
        self._build_background()
        self._build_room_panels()
        self._build_effects()

    def _build_background(self) -> None:
        self.base = pygame.Surface((self.screen_width, self.screen_height))
        for y in range(self.screen_height):
            blend = y / self.screen_height
            color = (
                int(61 + 112 * blend),
                int(43 + 68 * blend),
                int(49 + 51 * blend),
            )
            pygame.draw.line(self.base, color, (0, y), (self.screen_width, y))

        self.wall_layer = pygame.Surface((self.TILE_WIDTH, self.screen_height), pygame.SRCALPHA)
        pygame.draw.rect(self.wall_layer, (112, 70, 60, 225), (0, 170, self.TILE_WIDTH, 360))
        for x in range(0, self.TILE_WIDTH, 96):
            pygame.draw.rect(self.wall_layer, (130, 85, 69, 135), (x, 183, 5, 333))
            pygame.draw.line(self.wall_layer, (183, 126, 87, 180), (x + 8, 199), (x + 75, 199), 2)
        pygame.draw.rect(self.wall_layer, (210, 160, 112, 225), (0, 507, self.TILE_WIDTH, 15))
        pygame.draw.rect(self.wall_layer, (66, 45, 48, 235), (0, 522, self.TILE_WIDTH, 18))

        for x in (130, 780, 1440, 2110):
            window = pygame.Rect(x, 238, 280, 205)
            pygame.draw.rect(self.wall_layer, (52, 78, 91, 245), window, border_radius=10)
            pygame.draw.rect(self.wall_layer, (231, 190, 137, 245), window, width=9, border_radius=10)
            pygame.draw.rect(self.wall_layer, (117, 152, 155, 220), (x + 13, 251, 254, 178), border_radius=5)
            pygame.draw.ellipse(self.wall_layer, (229, 174, 114, 125), (x + 28, 266, 200, 65))
            pygame.draw.polygon(self.wall_layer, (69, 102, 99, 230), [(x + 13, 391), (x + 68, 342), (x + 120, 385), (x + 175, 340), (x + 267, 398), (x + 267, 430), (x + 13, 430)])
            pygame.draw.line(self.wall_layer, (238, 218, 181, 235), (x + 140, 244), (x + 140, 438), 7)
            pygame.draw.line(self.wall_layer, (238, 218, 181, 235), (x + 7, 340), (x + 273, 340), 7)

        self.ceiling_layer = pygame.Surface((self.TILE_WIDTH, self.screen_height), pygame.SRCALPHA)
        pygame.draw.rect(self.ceiling_layer, (48, 38, 45, 240), (0, 0, self.TILE_WIDTH, 174))
        pygame.draw.rect(self.ceiling_layer, (113, 68, 57, 245), (0, 154, self.TILE_WIDTH, 25))
        for x in range(-80, self.TILE_WIDTH + 320, 320):
            pygame.draw.polygon(self.ceiling_layer, (146, 96, 69, 235), [(x, 0), (x + 35, 0), (x + 190, 169), (x + 153, 169)])
            pygame.draw.line(self.ceiling_layer, (204, 148, 98, 230), (x + 12, 20), (x + 169, 161), 4)
            pygame.draw.line(self.ceiling_layer, (75, 52, 53, 245), (x + 152, 167), (x + 152, 220), 5)
            pygame.draw.ellipse(self.ceiling_layer, (237, 176, 101, 245), (x + 119, 213, 70, 16))
            pygame.draw.ellipse(self.ceiling_layer, (255, 218, 153, 225), (x + 127, 215, 54, 8))

    def _make_panel(self, width: int) -> pygame.Surface:
        return pygame.Surface((width, self.screen_height), pygame.SRCALPHA)

    def _draw_sign(self, surface: pygame.Surface, rect: pygame.Rect, text: str, fill: tuple[int, int, int]) -> None:
        pygame.draw.rect(surface, (53, 39, 43), rect.move(0, 5), border_radius=7)
        pygame.draw.rect(surface, fill, rect, border_radius=7)
        pygame.draw.rect(surface, (238, 195, 139), rect, width=3, border_radius=7)
        label = self.sign_font.render(text, True, (255, 240, 211))
        surface.blit(label, label.get_rect(center=rect.center))

    def _draw_window(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        pygame.draw.rect(surface, (41, 70, 80), rect, border_radius=9)
        pygame.draw.rect(surface, (238, 191, 131), rect, width=7, border_radius=9)
        pygame.draw.rect(surface, (125, 162, 155), rect.inflate(-14, -14), border_radius=5)
        pygame.draw.polygon(surface, (76, 113, 103), [(rect.left + 8, rect.bottom - 45), (rect.left + 43, rect.top + 52), (rect.left + 82, rect.bottom - 59), (rect.centerx, rect.top + 46), (rect.right - 7, rect.bottom - 39), (rect.right - 7, rect.bottom - 8), (rect.left + 8, rect.bottom - 8)])
        pygame.draw.line(surface, (246, 218, 178), (rect.centerx, rect.top + 4), (rect.centerx, rect.bottom - 4), 5)
        pygame.draw.line(surface, (246, 218, 178), (rect.left + 4, rect.centery), (rect.right - 4, rect.centery), 5)

    def _draw_entrance(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (93, 58, 55), (0, 246, 740, 283))
        pygame.draw.rect(surface, (55, 43, 48), (0, 242, 740, 17))
        self._draw_sign(surface, pygame.Rect(166, 182, 394, 64), "CAMPUS CAFE", (47, 91, 83))
        for x in range(38, 708, 42):
            color = (201, 82, 71) if ((x - 38) // 42) % 2 == 0 else (244, 206, 151)
            pygame.draw.polygon(surface, color, [(x, 261), (x + 42, 261), (x + 31, 297), (x + 10, 297)])
        pygame.draw.rect(surface, (232, 193, 142), (35, 255, 670, 13), border_radius=4)

        pygame.draw.rect(surface, (45, 67, 73), (69, 335, 225, 190), border_radius=7)
        pygame.draw.rect(surface, (220, 187, 143), (69, 335, 225, 190), width=8, border_radius=7)
        pygame.draw.rect(surface, (111, 159, 156), (84, 350, 91, 164), border_radius=5)
        pygame.draw.rect(surface, (85, 131, 139), (184, 350, 95, 164), border_radius=5)
        pygame.draw.line(surface, (238, 205, 157), (180, 345), (180, 520), 7)
        pygame.draw.circle(surface, (242, 208, 153), (263, 439), 5)

        self._draw_window(surface, pygame.Rect(355, 332, 187, 151))
        pygame.draw.rect(surface, (44, 53, 57), (577, 325, 112, 161), border_radius=5)
        pygame.draw.rect(surface, (207, 173, 130), (577, 325, 112, 161), width=4, border_radius=5)
        menu = self.detail_font.render("TODAY'S MENU", True, (255, 228, 178))
        surface.blit(menu, (588, 337))
        for index, color in enumerate(((231, 195, 139), (215, 138, 99), (230, 206, 159), (215, 138, 99))):
            pygame.draw.line(surface, color, (590, 365 + index * 26), (671, 365 + index * 26), 3)

        for plant_x in (18, 695):
            pygame.draw.rect(surface, (115, 70, 55), (plant_x, 470, 46, 50), border_radius=6)
            for leaf in range(5):
                leaf_x = plant_x + 5 + leaf * 9
                pygame.draw.ellipse(surface, (75, 133, 91), (leaf_x, 432 - abs(2 - leaf) * 6, 19, 40))

    def _draw_dining(self, surface: pygame.Surface) -> None:
        for rect in (pygame.Rect(70, 226, 235, 194), pygame.Rect(430, 226, 235, 194), pygame.Rect(800, 226, 190, 194)):
            self._draw_window(surface, rect)

        for x in (112, 390, 688, 900):
            pygame.draw.rect(surface, (98, 51, 48), (x, 379, 90, 86), border_radius=13)
            pygame.draw.rect(surface, (177, 107, 74), (x - 9, 371, 108, 25), border_radius=10)

        for x in (157, 465, 745, 896):
            pygame.draw.ellipse(surface, (73, 48, 44), (x - 58, 465, 116, 20))
            pygame.draw.rect(surface, (116, 71, 53), (x - 5, 444, 10, 55))
            pygame.draw.ellipse(surface, (191, 133, 84), (x - 66, 425, 132, 31))
            pygame.draw.ellipse(surface, (233, 193, 140), (x - 62, 422, 124, 20))
            pygame.draw.circle(surface, (248, 231, 204), (x - 18, 430), 8)
            pygame.draw.arc(surface, (76, 111, 103), (x + 16, 421, 26, 18), 0, math.tau, 3)
            for chair_x in (x - 62, x + 53):
                pygame.draw.rect(surface, (49, 72, 71), (chair_x, 447, 19, 29), border_radius=5)
                pygame.draw.rect(surface, (178, 111, 75), (chair_x - 3, 443, 25, 9), border_radius=4)

        for x in (130, 460, 780):
            pygame.draw.line(surface, (82, 59, 52), (x, 190), (x, 274), 4)
            pygame.draw.polygon(surface, (214, 145, 86), [(x - 36, 269), (x + 36, 269), (x + 22, 286), (x - 22, 286)])
            pygame.draw.ellipse(surface, (255, 218, 158, 210), (x - 20, 287, 40, 8))

        for x in (35, 950):
            pygame.draw.rect(surface, (106, 64, 51), (x, 468, 52, 48), border_radius=8)
            for leaf in range(4):
                pygame.draw.ellipse(surface, (64, 131, 92), (x + leaf * 10, 425 - leaf % 2 * 10, 22, 48))

    def _draw_counter(self, surface: pygame.Surface) -> None:
        self._draw_sign(surface, pygame.Rect(120, 204, 278, 54), "ORDER  •  PICK UP", (50, 91, 85))
        self._draw_sign(surface, pygame.Rect(524, 204, 278, 54), "FRESH TODAY", (124, 67, 59))
        for x in (126, 235, 344, 453, 562, 671, 780):
            pygame.draw.line(surface, (76, 53, 48), (x, 159), (x, 196), 4)
            pygame.draw.polygon(surface, (224, 167, 105), [(x - 15, 190), (x + 15, 190), (x + 9, 202), (x - 9, 202)])

        pygame.draw.rect(surface, (85, 51, 47), (64, 404, 814, 118), border_radius=9)
        pygame.draw.rect(surface, (128, 74, 56), (52, 391, 838, 29), border_radius=8)
        pygame.draw.rect(surface, (234, 198, 148), (52, 386, 838, 13), border_radius=6)
        for x in range(82, 856, 96):
            pygame.draw.rect(surface, (105, 64, 51), (x, 434, 74, 72), border_radius=5)
            pygame.draw.line(surface, (180, 116, 77), (x + 8, 442), (x + 66, 442), 3)

        pygame.draw.rect(surface, (48, 61, 62), (124, 306, 302, 73), border_radius=7)
        pygame.draw.rect(surface, (220, 180, 129), (124, 306, 302, 73), width=4, border_radius=7)
        for index, color in enumerate(((218, 110, 80), (228, 191, 133), (96, 157, 138))):
            pygame.draw.rect(surface, color, (144 + index * 91, 326, 74, 33), border_radius=5)
            pygame.draw.ellipse(surface, (248, 227, 190), (151 + index * 91, 331, 60, 20))

        pygame.draw.rect(surface, (45, 52, 58), (648, 333, 83, 49), border_radius=6)
        pygame.draw.rect(surface, (204, 159, 104), (648, 333, 83, 49), width=3, border_radius=6)
        pygame.draw.rect(surface, (235, 205, 163), (692, 347, 31, 21), border_radius=3)
        for cup_x in (493, 526, 559, 760, 790):
            pygame.draw.rect(surface, (242, 228, 202), (cup_x, 357, 23, 29), border_radius=4)
            pygame.draw.ellipse(surface, (255, 245, 223), (cup_x, 354, 23, 8))

    def _draw_kitchen(self, surface: pygame.Surface) -> None:
        for row in range(5):
            for column in range(10):
                color = (180, 198, 184) if (row + column) % 2 else (201, 211, 192)
                pygame.draw.rect(surface, color, (column * 112 + 6, 245 + row * 48, 106, 44))
                pygame.draw.line(surface, (226, 228, 207), (column * 112 + 6, 245 + row * 48), (column * 112 + 112, 245 + row * 48), 2)

        pygame.draw.rect(surface, (58, 66, 65), (85, 285, 365, 62), border_radius=7)
        pygame.draw.polygon(surface, (78, 84, 79), [(75, 286), (455, 286), (416, 250), (116, 250)])
        pygame.draw.rect(surface, (49, 57, 57), (132, 208, 270, 43), border_radius=6)
        for x in (184, 268, 352):
            pygame.draw.ellipse(surface, (113, 119, 107), (x - 27, 300, 54, 20))
            pygame.draw.ellipse(surface, (198, 105, 69), (x - 20, 304, 40, 10))

        pygame.draw.rect(surface, (84, 62, 54), (35, 400, 788, 115), border_radius=7)
        pygame.draw.rect(surface, (227, 196, 151), (25, 385, 807, 27), border_radius=7)
        for x in (60, 235, 410, 585, 760):
            pygame.draw.rect(surface, (47, 57, 59), (x, 428, 142, 73), border_radius=8)
            pygame.draw.rect(surface, (186, 123, 79), (x + 9, 437, 124, 55), border_radius=6)
            pygame.draw.rect(surface, (63, 63, 60), (x + 20, 447, 101, 38), border_radius=5)
            pygame.draw.circle(surface, (237, 183, 119), (x + 30, 480), 4)

        pygame.draw.rect(surface, (93, 61, 52), (845, 275, 118, 244), border_radius=8)
        pygame.draw.rect(surface, (222, 205, 177), (845, 275, 118, 244), width=7, border_radius=8)
        pygame.draw.rect(surface, (143, 179, 166), (858, 291, 92, 125), border_radius=5)
        pygame.draw.rect(surface, (62, 73, 71), (858, 427, 92, 75), border_radius=4)
        for shelf_y in (300, 354, 468):
            pygame.draw.line(surface, (211, 159, 105), (35, shelf_y), (220, shelf_y), 5)
        for pan_x in (76, 142, 828):
            pygame.draw.ellipse(surface, (64, 71, 70), (pan_x, 319, 48, 12))
            pygame.draw.line(surface, (65, 70, 68), (pan_x + 39, 325), (pan_x + 65, 319), 4)

    def _draw_prep(self, surface: pygame.Surface) -> None:
        self._draw_sign(surface, pygame.Rect(286, 216, 352, 52), "PREP  •  PLATE  •  SERVE", (52, 90, 82))
        for shelf_y in (301, 353):
            pygame.draw.rect(surface, (83, 55, 48), (56, shelf_y, 800, 12), border_radius=4)
            pygame.draw.line(surface, (213, 163, 107), (60, shelf_y), (852, shelf_y), 4)
            for jar_x in range(82, 835, 73):
                pygame.draw.rect(surface, (219, 197, 160), (jar_x, shelf_y - 34, 31, 31), border_radius=5)
                pygame.draw.rect(surface, (123, 151, 127), (jar_x + 4, shelf_y - 27, 23, 17), border_radius=3)
                pygame.draw.rect(surface, (91, 67, 54), (jar_x + 7, shelf_y - 39, 17, 6), border_radius=2)

        pygame.draw.rect(surface, (82, 55, 48), (80, 439, 760, 78), border_radius=7)
        pygame.draw.rect(surface, (232, 202, 157), (56, 421, 806, 24), border_radius=7)
        pygame.draw.rect(surface, (66, 103, 96), (205, 368, 220, 49), border_radius=6)
        pygame.draw.rect(surface, (210, 170, 120), (220, 376, 190, 31), border_radius=4)
        pygame.draw.ellipse(surface, (241, 225, 194), (235, 377, 62, 26))
        pygame.draw.ellipse(surface, (241, 225, 194), (320, 377, 62, 26))
        pygame.draw.rect(surface, (100, 63, 52), (585, 369, 144, 51), border_radius=7)
        pygame.draw.rect(surface, (195, 146, 91), (597, 377, 120, 35), border_radius=6)
        for x in (613, 655, 697):
            pygame.draw.circle(surface, (236, 219, 186), (x, 394), 11)

    def _draw_storage(self, surface: pygame.Surface) -> None:
        for shelf_x in (69, 355, 641):
            pygame.draw.rect(surface, (53, 61, 61), (shelf_x, 246, 17, 277), border_radius=4)
            pygame.draw.rect(surface, (53, 61, 61), (shelf_x + 247, 246, 17, 277), border_radius=4)
            for y in (301, 385, 469):
                pygame.draw.rect(surface, (132, 86, 59), (shelf_x, y, 264, 12), border_radius=3)
                pygame.draw.line(surface, (210, 157, 99), (shelf_x + 5, y), (shelf_x + 259, y), 3)
            for y, color in ((264, (173, 115, 70)), (315, (118, 132, 94)), (398, (176, 123, 74)), (426, (137, 103, 72))):
                pygame.draw.rect(surface, (82, 58, 51), (shelf_x + 27, y + 4, 77, 35), border_radius=4)
                pygame.draw.rect(surface, color, (shelf_x + 31, y, 69, 34), border_radius=4)
                pygame.draw.line(surface, (226, 192, 140), (shelf_x + 38, y + 9), (shelf_x + 91, y + 9), 2)
                pygame.draw.line(surface, (98, 71, 54), (shelf_x + 64, y + 1), (shelf_x + 64, y + 32), 2)
            pygame.draw.rect(surface, (64, 106, 101), (shelf_x + 132, 349, 96, 70), border_radius=6)
            pygame.draw.rect(surface, (218, 193, 155), (shelf_x + 132, 349, 96, 70), width=4, border_radius=6)
            pygame.draw.line(surface, (228, 211, 179), (shelf_x + 146, 361), (shelf_x + 214, 361), 3)

    def _draw_challenge(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (51, 58, 58), (35, 207, 575, 17), border_radius=5)
        for x in (78, 253, 428, 585):
            pygame.draw.rect(surface, (82, 91, 83), (x, 223, 13, 296))
            pygame.draw.rect(surface, (179, 124, 78), (x - 22, 293, 56, 12), border_radius=3)
            pygame.draw.rect(surface, (179, 124, 78), (x - 22, 373, 56, 12), border_radius=3)
        self._draw_sign(surface, pygame.Rect(176, 246, 272, 51), "STAFF ONLY", (126, 67, 57))
        pygame.draw.rect(surface, (53, 59, 57), (130, 408, 400, 82), border_radius=6)
        pygame.draw.rect(surface, (184, 117, 71), (112, 393, 436, 21), border_radius=7)
        for x in range(136, 535, 31):
            pygame.draw.line(surface, (219, 173, 112), (x, 395), (x + 14, 410), 3)
        for x in (43, 553):
            pygame.draw.circle(surface, (204, 91, 66), (x, 331), 9)
            pygame.draw.circle(surface, (246, 178, 112), (x, 331), 4)

    def _draw_exit(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (70, 88, 78), (0, 230, 650, 300))
        self._draw_sign(surface, pygame.Rect(187, 181, 276, 55), "SEE YOU SOON", (50, 94, 82))
        pygame.draw.rect(surface, (50, 69, 73), (98, 419, 145, 195), border_radius=12)
        pygame.draw.rect(surface, (225, 187, 135), (98, 419, 145, 195), width=8, border_radius=12)
        pygame.draw.rect(surface, (105, 67, 52), (42, 429, 52, 74), border_radius=8)
        pygame.draw.rect(surface, (108, 72, 52), (552, 429, 52, 74), border_radius=8)
        for x in (38, 72, 106, 546, 580, 614):
            pygame.draw.ellipse(surface, (79, 138, 91), (x, 374 - (x % 3) * 11, 30, 77))

    def _build_room_panels(self) -> None:
        room_specs = (
            (0, 740, self._draw_entrance),
            (740, 1770, self._draw_dining),
            (1770, 2670, self._draw_counter),
            (2670, 3840, self._draw_kitchen),
            (3840, 4770, self._draw_prep),
            (4770, 5720, self._draw_storage),
            (5720, 6350, self._draw_challenge),
            (6350, 7000, self._draw_exit),
        )
        self.room_panels = []
        for start_x, end_x, draw_panel in room_specs:
            panel = self._make_panel(end_x - start_x)
            draw_panel(panel)
            self.room_panels.append((start_x, panel))

    def _build_effects(self) -> None:
        self.lamp_glow = pygame.Surface((126, 126), pygame.SRCALPHA)
        for radius, alpha in ((60, 9), (42, 16), (27, 29), (13, 48)):
            pygame.draw.circle(self.lamp_glow, (255, 193, 118, alpha), (63, 63), radius)

        self.collectible_glow = pygame.Surface((58, 58), pygame.SRCALPHA)
        for radius, alpha in ((28, 18), (20, 34), (12, 66)):
            pygame.draw.circle(self.collectible_glow, (255, 189, 92, alpha), (29, 29), radius)

        self.shadow = pygame.Surface((70, 18), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow, (39, 28, 31, 100), (0, 0, 70, 18))

    def _draw_tiled(self, surface: pygame.Surface, layer: pygame.Surface, camera_x: float, speed: float) -> None:
        offset = int(camera_x * speed) % layer.get_width()
        x = -offset
        while x < self.screen_width:
            surface.blit(layer, (x, 0))
            x += layer.get_width()

    def _draw_floor(self, surface: pygame.Surface, camera_x: float, ground_y: int) -> None:
        pygame.draw.rect(surface, (136, 92, 69), (0, 500, self.screen_width, ground_y - 500))
        pygame.draw.rect(surface, (177, 127, 87), (0, 500, self.screen_width, 8))
        for world_x in range(0, self.world_width + 100, 80):
            x = int(world_x - camera_x)
            if -80 < x < self.screen_width + 80:
                pygame.draw.line(surface, (119, 78, 63), (x, 510), (x, ground_y), 2)
        for y in range(531, ground_y, 42):
            offset = int(camera_x * 0.35) % 160
            pygame.draw.line(surface, (159, 111, 79), (-offset, y), (self.screen_width, y), 2)
            for x in range(-offset, self.screen_width, 160):
                pygame.draw.circle(surface, (192, 145, 101), (x, y + 20), 2)

        track = pygame.Rect(0, ground_y, self.screen_width, self.screen_height - ground_y)
        pygame.draw.rect(surface, (111, 71, 62), track)
        pygame.draw.rect(surface, (188, 132, 88), (0, ground_y, self.screen_width, 8))
        for world_x in range(0, self.world_width + 60, 60):
            x = int(world_x - camera_x)
            if -60 < x < self.screen_width + 60:
                pygame.draw.line(surface, (140, 93, 73), (x, ground_y + 8), (x, self.screen_height), 1)
        for y in range(ground_y + 30, self.screen_height, 34):
            pygame.draw.line(surface, (132, 85, 70), (0, y), (self.screen_width, y), 1)

    def draw_background(self, surface: pygame.Surface, camera_x: float, ground_y: int, time: float) -> None:
        surface.blit(self.base, (0, 0))
        self._draw_tiled(surface, self.wall_layer, camera_x, 0.12)
        self._draw_tiled(surface, self.ceiling_layer, camera_x, 0.32)
        self._draw_floor(surface, camera_x, ground_y)

        for world_x, panel in self.room_panels:
            screen_x = int(world_x - camera_x)
            if screen_x < self.screen_width and screen_x + panel.get_width() > 0:
                surface.blit(panel, (screen_x, 0))

        for world_x in (160, 450, 930, 1320, 1880, 2320, 2820, 3380, 4120, 4560, 5130, 5480, 6010, 6660):
            x = int(world_x - camera_x * 0.42)
            if -80 <= x <= self.screen_width + 80:
                pulse = 0.92 + 0.08 * math.sin(time * 2.2 + world_x)
                self.lamp_glow.set_alpha(int(190 * pulse))
                surface.blit(self.lamp_glow, (x - 63, 220), special_flags=pygame.BLEND_RGBA_ADD)

        for world_x in (2860, 3070, 3290, 3520, 3710, 3950):
            x = int(world_x - camera_x)
            if -30 < x < self.screen_width + 30:
                steam_y = 397 - int((time * 19 + world_x) % 30)
                pygame.draw.circle(surface, (233, 222, 198), (x, steam_y), 8)
                pygame.draw.circle(surface, (242, 230, 207), (x + 9, steam_y - 7), 6)
                pygame.draw.circle(surface, (220, 214, 194), (x - 8, steam_y - 12), 5)

        sections = (
            (825, "DINING ROOM", (68, 91, 75)),
            (1840, "ORDER HERE", (104, 61, 54)),
            (2825, "KITCHEN", (59, 95, 89)),
            (3905, "PREPARATION", (87, 80, 57)),
            (4935, "STORAGE", (70, 81, 73)),
            (5775, "BACK OF HOUSE", (119, 69, 55)),
        )
        for world_x, text, color in sections:
            x = int(world_x - camera_x * 0.9)
            if -230 < x < self.screen_width + 230:
                sign = pygame.Rect(x, 271, 190, 45)
                pygame.draw.rect(surface, (47, 35, 38), sign.move(0, 4), border_radius=6)
                pygame.draw.rect(surface, color, sign, border_radius=6)
                pygame.draw.rect(surface, (233, 192, 140), sign, width=2, border_radius=6)
                label = self.sign_font.render(text, True, (255, 239, 208))
                surface.blit(label, label.get_rect(center=sign.center))

    def draw_gameplay_objects(
        self,
        surface: pygame.Surface,
        camera_x: float,
        ground_y: int,
        platforms: list[pygame.Rect],
        moving_platforms: list[dict],
        hazards: list[pygame.Rect],
        checkpoints: list[dict],
        collectibles: list[dict],
        goal_rect: pygame.Rect,
        player_rect: pygame.Rect,
        time: float,
        collection_bursts: list[dict],
    ) -> None:
        shadow_y = ground_y
        for platform in platforms[1:]:
            if platform.left < player_rect.centerx < platform.right and platform.top >= player_rect.bottom - 2:
                shadow_y = min(shadow_y, platform.top)
        shadow_rect = self.shadow.get_rect(midbottom=(int(player_rect.centerx - camera_x), shadow_y + 5))
        surface.blit(self.shadow, shadow_rect)

        for platform in platforms[1:]:
            rect = platform.move(-camera_x, 0)
            pygame.draw.rect(surface, (68, 44, 43), (rect.x, rect.y + 9, rect.width, rect.height), border_radius=6)
            pygame.draw.rect(surface, (116, 69, 54), rect, border_radius=6)
            pygame.draw.rect(surface, (224, 187, 137), (rect.x + 2, rect.y, rect.width - 4, 5), border_radius=3)
            pygame.draw.line(surface, (167, 111, 72), (rect.x + 10, rect.y + 10), (rect.right - 10, rect.y + 10), 2)
            for knob_x in range(rect.x + 24, rect.right - 8, 48):
                pygame.draw.circle(surface, (227, 181, 120), (knob_x, rect.centery + 3), 2)

        for platform_data in moving_platforms:
            rect = platform_data["rect"].move(-camera_x, 0)
            pygame.draw.ellipse(surface, (50, 39, 40), (rect.x - 10, rect.bottom + 11, rect.width + 20, 11))
            pygame.draw.line(surface, (90, 99, 91), (rect.centerx, rect.bottom), (rect.centerx, rect.bottom + 10), 3)
            pygame.draw.rect(surface, (76, 55, 48), rect.move(0, 5), border_radius=8)
            pygame.draw.rect(surface, (181, 157, 123), rect, border_radius=8)
            pygame.draw.rect(surface, (246, 226, 187), (rect.x + 8, rect.y + 2, rect.width - 16, 4), border_radius=2)
            pygame.draw.ellipse(surface, (218, 195, 156), (rect.x + 18, rect.y + 6, rect.width - 36, 8), 2)
            direction = platform_data["direction"]
            for x in (rect.x + 17, rect.right - 17):
                pygame.draw.polygon(surface, (77, 113, 98), [(x - 5 * direction, rect.centery - 4), (x + 2 * direction, rect.centery), (x - 5 * direction, rect.centery + 4)])

        for hazard in hazards:
            rect = hazard.move(-camera_x, 0)
            pygame.draw.ellipse(surface, (49, 39, 38), (rect.x - 5, rect.bottom - 1, rect.width + 10, 8))
            if hazard.centerx < 4700:
                pygame.draw.rect(surface, (144, 79, 56), (rect.x, rect.y + 10, rect.width, 13), border_radius=4)
                pygame.draw.rect(surface, (234, 145, 83), (rect.x, rect.y + 3, rect.width, 8), border_radius=4)
                pygame.draw.line(surface, (255, 212, 150), (rect.x + 5, rect.y + 6), (rect.right - 5, rect.y + 6), 3)
                pygame.draw.arc(surface, (243, 207, 164), (rect.centerx - 9, rect.y - 9, 18, 23), 0.2, 2.9, 2)
            else:
                pygame.draw.ellipse(surface, (75, 120, 123), (rect.x - 4, rect.y + 9, rect.width + 8, 15))
                pygame.draw.ellipse(surface, (118, 172, 168), (rect.x + 2, rect.y + 10, rect.width - 4, 8))
                pygame.draw.rect(surface, (236, 217, 177), (rect.x + 4, rect.y + 2, 14, 4), border_radius=2)

        for checkpoint in checkpoints:
            rect = checkpoint["rect"].move(-camera_x, 0)
            pulse = 0.5 + 0.5 * math.sin(time * 3.2)
            fill = (int(114 + pulse * 49), int(190 + pulse * 40), int(131 + pulse * 27)) if checkpoint["active"] else (231, 199, 151)
            pygame.draw.ellipse(surface, (57, 42, 39), (rect.x - 11, rect.bottom - 2, 50, 12))
            pygame.draw.rect(surface, (68, 54, 49), (rect.x + 8, rect.y, 9, rect.height), border_radius=3)
            pygame.draw.rect(surface, (236, 203, 154), (rect.x + 5, rect.y + 4, 16, 8), border_radius=3)
            pygame.draw.rect(surface, (54, 85, 77), (rect.x + 18, rect.y + 12, 86, 28), border_radius=5)
            pygame.draw.rect(surface, fill, (rect.x + 21, rect.y + 15, 80, 22), border_radius=4)
            text = self.detail_font.render("SAVED" if checkpoint["active"] else "CHECKPOINT", True, (46, 58, 52))
            surface.blit(text, text.get_rect(center=(rect.x + 61, rect.y + 26)))

        for item in collectibles:
            if item["collected"]:
                continue
            base_rect = item["rect"]
            bob = math.sin(time * 4.0 + base_rect.x * 0.04) * 4
            center = (int(base_rect.centerx - camera_x), int(base_rect.centery + bob))
            surface.blit(self.collectible_glow, self.collectible_glow.get_rect(center=center))
            pygame.draw.circle(surface, (154, 76, 54), center, 12)
            pygame.draw.circle(surface, (239, 177, 92), center, 9)
            pygame.draw.ellipse(surface, (231, 101, 73), (center[0] - 6, center[1] - 6, 12, 12))
            pygame.draw.polygon(surface, (83, 142, 83), [(center[0], center[1] - 6), (center[0] - 4, center[1] - 11), (center[0] - 1, center[1] - 10), (center[0] + 1, center[1] - 13), (center[0] + 3, center[1] - 9), (center[0] + 7, center[1] - 10), (center[0] + 4, center[1] - 5)])
            pygame.draw.circle(surface, (255, 239, 195), (center[0] - 3, center[1] - 3), 2)

        for burst in collection_bursts:
            progress = burst["age"] / burst["duration"]
            radius = 4 + int(progress * 17)
            color = (255, int(215 - progress * 60), 148)
            center = (int(burst["x"] - camera_x), int(burst["y"]))
            pygame.draw.circle(surface, color, center, radius, 2)
            for point in range(6):
                angle = point * math.tau / 6
                sparkle = (center[0] + int(math.cos(angle) * radius), center[1] + int(math.sin(angle) * radius))
                pygame.draw.circle(surface, (255, 239, 196), sparkle, 2)

        goal = goal_rect.move(-camera_x, 0)
        door = pygame.Rect(goal.x - 46, goal.y + 10, goal.width + 90, goal.height - 10)
        pygame.draw.rect(surface, (54, 42, 45), door.move(0, 6), border_radius=11)
        pygame.draw.rect(surface, (80, 113, 100), door, border_radius=11)
        pygame.draw.rect(surface, (242, 206, 149), door, width=6, border_radius=11)
        pygame.draw.rect(surface, (136, 181, 165), door.inflate(-18, -22), border_radius=7)
        pygame.draw.line(surface, (244, 213, 166), (door.centerx, door.y + 12), (door.centerx, door.bottom - 12), 4)
        pygame.draw.circle(surface, (255, 220, 147), (door.right - 13, door.centery), 4)
        sign = pygame.Rect(door.x - 16, door.y - 55, door.width + 32, 40)
        pygame.draw.rect(surface, (49, 82, 76), sign, border_radius=7)
        pygame.draw.rect(surface, (236, 197, 143), sign, width=3, border_radius=7)
        exit_text = self.sign_font.render("EXIT", True, (255, 242, 212))
        surface.blit(exit_text, exit_text.get_rect(center=sign.center))
