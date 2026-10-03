from __future__ import annotations

import math
import random

import pygame


class StadiumRenderer:
    TILE_WIDTH = 2560

    def __init__(self, screen_size: tuple[int, int], world_width: int) -> None:
        pygame.font.init()
        self.screen_width, self.screen_height = screen_size
        self.world_width = world_width
        self.sign_font = pygame.font.SysFont("arial", 17, bold=True)
        self.gate_font = pygame.font.SysFont("arial", 19, bold=True)
        self._build_layers()
        self._build_effects()

    def _build_layers(self) -> None:
        self.sky = pygame.Surface((self.screen_width, self.screen_height))
        for y in range(self.screen_height):
            blend = y / self.screen_height
            color = (
                int(48 + 52 * blend),
                int(91 + 75 * blend),
                int(139 + 54 * blend),
            )
            pygame.draw.line(self.sky, color, (0, y), (self.screen_width, y))
        pygame.draw.ellipse(self.sky, (244, 189, 133), (self.screen_width - 340, 96, 230, 110))
        pygame.draw.ellipse(self.sky, (239, 203, 158), (self.screen_width - 315, 112, 180, 78))

        self.far_layer = pygame.Surface((self.TILE_WIDTH, self.screen_height), pygame.SRCALPHA)
        self._draw_skyline(self.far_layer)

        self.seating_layer = pygame.Surface((self.TILE_WIDTH, self.screen_height), pygame.SRCALPHA)
        self._draw_seating(self.seating_layer)

        self.roof_layer = pygame.Surface((self.TILE_WIDTH, self.screen_height), pygame.SRCALPHA)
        self._draw_roof(self.roof_layer)

    def _draw_skyline(self, surface: pygame.Surface) -> None:
        buildings = [
            (0, 280, 170, 145), (150, 244, 118, 181), (246, 292, 185, 133),
            (410, 258, 150, 167), (535, 222, 134, 203), (650, 278, 204, 147),
            (830, 246, 132, 179), (944, 286, 190, 139), (1114, 237, 156, 188),
            (1252, 274, 188, 151), (1418, 225, 140, 200), (1540, 267, 205, 158),
            (1725, 245, 150, 180), (1854, 285, 191, 140), (2024, 227, 154, 198),
            (2160, 272, 210, 153), (2348, 244, 172, 181),
        ]
        for index, (x, y, width, height) in enumerate(buildings):
            color = (58, 96, 119, 255) if index % 2 else (70, 109, 130, 255)
            pygame.draw.rect(surface, color, (x, y, width, height))
            pygame.draw.rect(surface, (115, 153, 166, 180), (x, y, width, 8))
            for window_x in range(x + 15, x + width - 8, 28):
                for window_y in range(y + 20, y + height - 10, 29):
                    window_color = (234, 198, 137, 155) if (window_x + window_y) % 3 else (137, 179, 189, 140)
                    pygame.draw.rect(surface, window_color, (window_x, window_y, 9, 12), border_radius=2)

        pygame.draw.line(surface, (154, 180, 185, 170), (0, 425), (self.TILE_WIDTH, 425), 3)

    def _draw_seating(self, surface: pygame.Surface) -> None:
        crowd_colors = (
            (202, 126, 92, 220), (225, 190, 123, 220), (113, 170, 157, 220),
            (171, 177, 191, 220), (193, 111, 112, 220),
        )
        rng = random.Random(7319)
        for section_x in range(0, self.TILE_WIDTH, 640):
            pygame.draw.polygon(
                surface,
                (35, 68, 91, 250),
                [(section_x - 34, 452), (section_x + 76, 259), (section_x + 566, 259), (section_x + 676, 452)],
            )
            pygame.draw.polygon(
                surface,
                (186, 198, 190, 255),
                [(section_x - 30, 290), (section_x + 76, 250), (section_x + 566, 250), (section_x + 670, 290)],
            )
            for row in range(6):
                row_y = 307 + row * 23
                left = section_x + 24 - row * 17
                right = section_x + 616 + row * 17
                pygame.draw.line(surface, (100, 131, 147, 220), (left, row_y + 13), (right, row_y + 13), 4)
                for person_x in range(section_x + 8, section_x + 634, 14):
                    jitter_x = rng.randint(-2, 2)
                    jitter_y = rng.randint(-3, 3)
                    color = crowd_colors[rng.randrange(len(crowd_colors))]
                    person = person_x + jitter_x
                    pygame.draw.ellipse(surface, color, (person, row_y + jitter_y + 4, 5, 8))
                    pygame.draw.circle(surface, (229, 199, 170, 225), (person + 2, row_y + jitter_y + 2), 3)

            stair_x = section_x + 314
            pygame.draw.polygon(
                surface,
                (50, 83, 103, 255),
                [(stair_x - 19, 303), (stair_x + 19, 303), (stair_x + 76, 452), (stair_x - 76, 452)],
            )
            pygame.draw.rect(surface, (221, 179, 119, 245), (section_x + 82, 447, 476, 27), border_radius=4)
            pygame.draw.rect(surface, (52, 79, 96, 255), (section_x + 90, 451, 460, 18), border_radius=3)
            pygame.draw.circle(surface, (230, 198, 143, 255), (section_x + 63, 277), 5)
            pygame.draw.circle(surface, (230, 198, 143, 255), (section_x + 577, 277), 5)

    def _draw_roof(self, surface: pygame.Surface) -> None:
        for section_x in range(-100, self.TILE_WIDTH + 640, 640):
            pygame.draw.polygon(
                surface,
                (202, 216, 210, 245),
                [(section_x, 244), (section_x + 112, 166), (section_x + 500, 166), (section_x + 620, 244)],
            )
            pygame.draw.polygon(
                surface,
                (73, 105, 124, 255),
                [(section_x + 46, 238), (section_x + 142, 187), (section_x + 478, 187), (section_x + 574, 238)],
            )
            pygame.draw.line(surface, (242, 220, 174, 220), (section_x + 110, 167), (section_x + 545, 240), 5)
            pygame.draw.line(surface, (242, 220, 174, 220), (section_x + 525, 167), (section_x + 90, 240), 5)
            pygame.draw.line(surface, (231, 237, 225, 230), (section_x + 10, 245), (section_x + 610, 245), 9)
            for support_x in (section_x + 84, section_x + 536):
                pygame.draw.polygon(
                    surface,
                    (104, 132, 143, 245),
                    [(support_x - 10, 243), (support_x + 10, 243), (support_x + 28, 463), (support_x - 28, 463)],
                )

    def _build_effects(self) -> None:
        self.light_glow = pygame.Surface((150, 150), pygame.SRCALPHA)
        for radius, alpha in ((72, 7), (52, 10), (34, 16), (18, 28)):
            pygame.draw.circle(self.light_glow, (255, 226, 166, alpha), (75, 75), radius)
        self.light_glow.set_alpha(170)

        self.mark_glow = pygame.Surface((60, 60), pygame.SRCALPHA)
        for radius, alpha in ((29, 20), (21, 35), (14, 65)):
            pygame.draw.circle(self.mark_glow, (255, 202, 92, alpha), (30, 30), radius)

        self.player_shadow = pygame.Surface((68, 18), pygame.SRCALPHA)
        pygame.draw.ellipse(self.player_shadow, (22, 42, 39, 100), (0, 0, 68, 18))

        self.collection_burst_frames = []
        for frame in range(8):
            progress = frame / 7
            radius = 5 + int(progress * 18)
            alpha = max(0, int(255 * (1 - progress)))
            burst_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(burst_surface, (255, 219, 129, alpha), (25, 25), radius, 2)
            for sparkle in range(6):
                angle = sparkle * math.tau / 6
                distance = radius + 2
                x = int(25 + math.cos(angle) * distance)
                y = int(25 + math.sin(angle) * distance)
                pygame.draw.circle(burst_surface, (255, 242, 192, alpha), (x, y), 2)
            self.collection_burst_frames.append(burst_surface)

    def _draw_tiled_layer(self, surface: pygame.Surface, layer: pygame.Surface, camera_x: float, speed: float) -> None:
        offset = int(camera_x * speed) % layer.get_width()
        x = -offset
        while x < self.screen_width:
            surface.blit(layer, (x, 0))
            x += layer.get_width()

    def draw_background(self, surface: pygame.Surface, camera_x: float) -> None:
        surface.blit(self.sky, (0, 0))
        self._draw_tiled_layer(surface, self.far_layer, camera_x, 0.10)
        self._draw_tiled_layer(surface, self.seating_layer, camera_x, 0.34)
        self._draw_tiled_layer(surface, self.roof_layer, camera_x, 0.62)

        for world_x in (520, 1780, 3060, 4380, 5660, 6820):
            x = int(world_x - camera_x * 0.62)
            if -100 <= x <= self.screen_width + 100:
                surface.blit(self.light_glow, (x - 75, 190), special_flags=pygame.BLEND_RGBA_ADD)
                pygame.draw.polygon(surface, (85, 111, 124), [(x - 13, 221), (x + 13, 221), (x + 27, 455), (x - 27, 455)])
                pygame.draw.line(surface, (218, 224, 208), (x - 28, 220), (x + 28, 220), 8)
                for lamp_x in (x - 20, x - 7, x + 7, x + 20):
                    pygame.draw.circle(surface, (255, 239, 190), (lamp_x, 225), 5)

    def draw_field_and_track(self, surface: pygame.Surface, camera_x: float, ground_y: int) -> None:
        field_rect = pygame.Rect(0, 470, self.screen_width, ground_y - 470)
        pygame.draw.rect(surface, (71, 126, 91), field_rect)
        pygame.draw.rect(surface, (88, 143, 101), (0, 470, self.screen_width, 8))

        field_center_x = int(420 - camera_x * 0.84)
        pygame.draw.ellipse(surface, (76, 134, 95), (field_center_x - 470, 487, 940, 205))
        pygame.draw.ellipse(surface, (122, 169, 115), (field_center_x - 460, 495, 920, 187), width=3)
        pygame.draw.ellipse(surface, (129, 174, 119), (field_center_x - 104, 516, 208, 128), width=3)
        pygame.draw.line(surface, (129, 174, 119), (field_center_x, 510), (field_center_x, ground_y), 3)
        for stripe_x in range(-80, self.screen_width + 160, 190):
            world_x = stripe_x + int(camera_x * 0.84)
            x = int(world_x - camera_x * 0.84)
            pygame.draw.line(surface, (84, 144, 101), (x, 486), (x + 80, ground_y), 2)

        track = pygame.Rect(0, ground_y, self.screen_width, self.screen_height - ground_y)
        pygame.draw.rect(surface, (151, 57, 69), track)
        pygame.draw.rect(surface, (199, 78, 78), (0, ground_y, self.screen_width, 8))
        pygame.draw.line(surface, (230, 129, 112), (0, ground_y + 11), (self.screen_width, ground_y + 11), 3)
        lane_height = max(18, (self.screen_height - ground_y - 18) // 4)
        for lane in range(1, 5):
            y = ground_y + 12 + lane * lane_height
            if y < self.screen_height:
                pygame.draw.line(surface, (236, 190, 162), (0, y), (self.screen_width, y), 2)

        for world_x in range(0, self.world_width + 180, 180):
            x = int(world_x - camera_x)
            if -30 < x < self.screen_width + 30:
                pygame.draw.line(surface, (248, 226, 193), (x, ground_y + 16), (x, self.screen_height), 2)

    def _draw_flag(self, surface: pygame.Surface, world_x: int, camera_x: float, y: int, color: tuple[int, int, int], time: float) -> None:
        x = int(world_x - camera_x)
        if not -48 <= x <= self.screen_width + 48:
            return
        wave = math.sin(time * 3.1 + world_x * 0.02) * 5
        pygame.draw.line(surface, (235, 225, 199), (x, y), (x, y + 52), 3)
        pygame.draw.polygon(
            surface,
            color,
            [(x + 2, y + 3), (x + 22, y + 8 + wave), (x + 42, y + 3), (x + 38, y + 27 + wave), (x + 19, y + 20), (x + 2, y + 28)],
        )
        pygame.draw.line(surface, (255, 227, 181), (x + 3, y + 4), (x + 35, y + 5 + wave), 2)

    def draw_landmarks(self, surface: pygame.Surface, camera_x: float, time: float) -> None:
        gate_x = int(26 - camera_x)
        if -430 < gate_x < self.screen_width:
            pygame.draw.polygon(surface, (47, 77, 94), [(gate_x, 410), (gate_x + 38, 365), (gate_x + 368, 365), (gate_x + 406, 410)])
            pygame.draw.rect(surface, (226, 213, 182), (gate_x + 10, 385, 24, 120), border_radius=7)
            pygame.draw.rect(surface, (226, 213, 182), (gate_x + 372, 385, 24, 120), border_radius=7)
            pygame.draw.rect(surface, (231, 220, 190), (gate_x + 20, 367, 366, 25), border_radius=8)
            pygame.draw.rect(surface, (42, 73, 90), (gate_x + 59, 405, 288, 49), border_radius=8)
            pygame.draw.rect(surface, (204, 105, 78), (gate_x + 59, 405, 288, 6), border_radius=3)
            text = self.gate_font.render("CAMPUS STADIUM", True, (250, 236, 203))
            surface.blit(text, text.get_rect(center=(gate_x + 203, 431)))

        for world_x, color in ((70, (228, 107, 78)), (365, (79, 171, 151)), (900, (230, 182, 97)), (1840, (224, 106, 79)), (3330, (82, 173, 157)), (4950, (235, 184, 97)), (6120, (221, 106, 78))):
            self._draw_flag(surface, world_x, camera_x, 334, color, time)

        sections = (
            (860, "MAIN TRACK", (42, 82, 100)),
            (2220, "TRAINING ZONE", (46, 102, 98)),
            (3950, "CHALLENGE", (114, 72, 67)),
            (5350, "FINAL SPRINT", (42, 82, 100)),
        )
        for world_x, label, color in sections:
            x = int(world_x - camera_x * 0.92)
            if -250 < x < self.screen_width + 250:
                board = pygame.Rect(x, 270, 222, 52)
                pygame.draw.rect(surface, (33, 61, 77), board.move(0, 5), border_radius=7)
                pygame.draw.rect(surface, color, board, border_radius=7)
                pygame.draw.rect(surface, (229, 202, 149), board, width=2, border_radius=7)
                text = self.sign_font.render(label, True, (250, 241, 216))
                surface.blit(text, text.get_rect(center=board.center))
                pygame.draw.line(surface, (222, 204, 164), (x + 12, 327), (x + 210, 327), 3)

            for world_x, lane, result in ((1430, "LANE 04", "00:48.2"), (4230, "HEAT 02", "READY"), (6020, "FINAL", "00:00.0")):
                x = int(world_x - camera_x * 0.78)
                if -300 < x < self.screen_width + 300:
                    board = pygame.Rect(x, 346, 252, 76)
                    pygame.draw.rect(surface, (38, 57, 69), board.move(0, 5), border_radius=7)
                    pygame.draw.rect(surface, (42, 73, 87), board, border_radius=7)
                    pygame.draw.rect(surface, (224, 188, 128), board, width=3, border_radius=7)
                    pygame.draw.rect(surface, (77, 112, 116), (x + 10, 355, 232, 20), border_radius=4)
                    title = self.sign_font.render("CAMPUS ATHLETICS", True, (250, 233, 197))
                    value = self.gate_font.render(f"{lane}   {result}", True, (245, 207, 121))
                    surface.blit(title, (x + 17, 357))
                    surface.blit(value, (x + 17, 384))

        for world_x in (650, 1520, 2700, 3650, 4740, 5850, 6600):
            x = int(world_x - camera_x)
            if -44 < x < self.screen_width + 44:
                pygame.draw.polygon(surface, (228, 137, 80), [(x - 15, 485), (x + 15, 485), (x, 453)])
                pygame.draw.ellipse(surface, (247, 213, 160), (x - 15, 481, 30, 9))

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
        shadow = self.player_shadow.get_rect(midbottom=(int(player_rect.centerx - camera_x), shadow_y + 5))
        surface.blit(self.player_shadow, shadow)

        for platform in platforms[1:]:
            rect = platform.move(-camera_x, 0)
            pygame.draw.rect(surface, (37, 63, 60), (rect.x, rect.y + 8, rect.width, rect.height), border_radius=7)
            pygame.draw.rect(surface, (56, 112, 88), rect, border_radius=7)
            pygame.draw.rect(surface, (143, 182, 132), (rect.x + 2, rect.y, rect.width - 4, 5), border_radius=3)
            pygame.draw.line(surface, (90, 146, 108), (rect.x + 9, rect.y + 10), (rect.right - 9, rect.y + 10), 2)

        for platform_data in moving_platforms:
            rect = platform_data["rect"].move(-camera_x, 0)
            shadow_width = rect.width + 24
            shadow_x = rect.centerx - shadow_width // 2
            pygame.draw.ellipse(surface, (35, 54, 57), (shadow_x, rect.bottom + 12, shadow_width, 10))
            pygame.draw.line(surface, (92, 126, 135), (rect.centerx, rect.bottom), (rect.centerx, rect.bottom + 10), 3)
            pygame.draw.rect(surface, (43, 75, 91), rect.move(0, 5), border_radius=7)
            pygame.draw.rect(surface, (75, 143, 157), rect, border_radius=7)
            pygame.draw.rect(surface, (179, 219, 206), (rect.x + 8, rect.y + 2, rect.width - 16, 4), border_radius=2)
            arrow_y = rect.centery
            for arrow_x in (rect.x + 19, rect.right - 19):
                direction = platform_data["direction"]
                points = [(arrow_x - 5 * direction, arrow_y - 5), (arrow_x + 2 * direction, arrow_y), (arrow_x - 5 * direction, arrow_y + 5)]
                pygame.draw.lines(surface, (232, 240, 215), False, points, 2)

        for hazard in hazards:
            rect = hazard.move(-camera_x, 0)
            pygame.draw.ellipse(surface, (39, 58, 54), (rect.x - 6, rect.bottom - 2, rect.width + 12, 8))
            pygame.draw.line(surface, (67, 61, 57), (rect.x + 5, rect.bottom), (rect.x + 9, rect.y + 3), 4)
            pygame.draw.line(surface, (67, 61, 57), (rect.right - 5, rect.bottom), (rect.right - 9, rect.y + 3), 4)
            pygame.draw.rect(surface, (220, 118, 71), (rect.x, rect.y + 2, rect.width, 7), border_radius=3)
            pygame.draw.rect(surface, (251, 218, 165), (rect.x, rect.y, rect.width, 4), border_radius=2)
            for stripe_x in range(rect.x + 5, rect.right - 3, 12):
                pygame.draw.line(surface, (248, 231, 190), (stripe_x, rect.y + 2), (stripe_x + 6, rect.y + 8), 2)

        for checkpoint in checkpoints:
            rect = checkpoint["rect"].move(-camera_x, 0)
            pulse = 0.5 + 0.5 * math.sin(time * 3.4)
            color = (int(133 + 55 * pulse), 224, int(151 + 35 * pulse)) if checkpoint["active"] else (222, 213, 185)
            pygame.draw.ellipse(surface, (24, 49, 42), (rect.x - 10, rect.bottom - 2, 48, 12))
            pygame.draw.rect(surface, (47, 69, 70), (rect.x + 8, rect.y, 9, rect.height), border_radius=3)
            pygame.draw.rect(surface, (207, 216, 198), (rect.x + 6, rect.y + 5, 13, 7), border_radius=3)
            pygame.draw.polygon(surface, color, [(rect.x + 17, rect.y + 10), (rect.x + 58, rect.y + 23), (rect.x + 17, rect.y + 40)])
            pygame.draw.line(surface, (249, 242, 210), (rect.x + 20, rect.y + 14), (rect.x + 49, rect.y + 22), 2)
            if checkpoint["active"]:
                pygame.draw.circle(surface, (179, 242, 168), (rect.x + 12, rect.y + 9), 4)

        for item in collectibles:
            if item["collected"]:
                continue
            base_rect = item["rect"]
            bob = math.sin(time * 3.8 + base_rect.x * 0.03) * 4
            center = (int(base_rect.centerx - camera_x), int(base_rect.centery + bob))
            glow_rect = self.mark_glow.get_rect(center=center)
            surface.blit(self.mark_glow, glow_rect)
            pygame.draw.circle(surface, (148, 103, 48), center, 13)
            pygame.draw.circle(surface, (255, 207, 92), center, 10)
            pygame.draw.polygon(surface, (255, 239, 174), [(center[0], center[1] - 7), (center[0] + 3, center[1] - 1), (center[0] + 8, center[1]), (center[0] + 3, center[1] + 3), (center[0], center[1] + 8), (center[0] - 3, center[1] + 3), (center[0] - 8, center[1]), (center[0] - 3, center[1] - 1)])
            pygame.draw.circle(surface, (255, 252, 222), (center[0] - 2, center[1] - 3), 2)

        for burst in collection_bursts:
            progress = burst["age"] / burst["duration"]
            frame = min(len(self.collection_burst_frames) - 1, int(progress * len(self.collection_burst_frames)))
            burst_surface = self.collection_burst_frames[frame]
            surface.blit(burst_surface, (int(burst["x"] - camera_x - 25), int(burst["y"] - 25)))

        goal = goal_rect.move(-camera_x, 0)
        banner = pygame.Rect(goal.x - 148, 367, 338, 52)
        pygame.draw.rect(surface, (34, 59, 75), banner.move(0, 6), border_radius=8)
        pygame.draw.rect(surface, (179, 66, 69), banner, border_radius=8)
        pygame.draw.rect(surface, (248, 221, 171), banner, width=3, border_radius=8)
        finish_text = self.gate_font.render("FINISH", True, (255, 244, 214))
        surface.blit(finish_text, finish_text.get_rect(center=banner.center))
        pygame.draw.rect(surface, (245, 239, 218), goal)
        pygame.draw.rect(surface, (191, 67, 66), (goal.x, goal.y, 13, goal.height))
        pygame.draw.rect(surface, (255, 255, 242), (goal.x + 13, goal.y, 13, goal.height))
        pygame.draw.rect(surface, (47, 68, 78), (goal.x - 32, goal.y, 9, goal.height))

        line_x = goal.x - 50
        tile = 12
        for row in range(4):
            for column in range(5):
                color = (250, 244, 223) if (row + column) % 2 == 0 else (52, 65, 71)
                pygame.draw.rect(surface, color, (line_x + column * tile, ground_y - 25 + row * 6, tile, 6))