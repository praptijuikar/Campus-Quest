import pygame

from game.characters import get_character_definition
from game.config.settings import (
    FINISH_X,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SPORTS_GROUND_Y,
    SPORTS_WORLD_WIDTH,
    START_X,
)
from game.core.camera import Camera, ParallaxLayer
from game.core.scene import Scene
from game.entities.player import Player
from game.systems.stadium_renderer import StadiumRenderer


class SportsPrototypeScene(Scene):
    def __init__(self, game, scene_manager, *, use_stadium_renderer: bool = True) -> None:
        super().__init__(game, scene_manager)
        pygame.font.init()

        self.world_width = SPORTS_WORLD_WIDTH
        self.ground_y = SPORTS_GROUND_Y
        self.player = Player(START_X, self.ground_y - 64)
        self.player.set_ground(self.ground_y)
        self.stadium_renderer = (
            StadiumRenderer((SCREEN_WIDTH, SCREEN_HEIGHT), self.world_width)
            if use_stadium_renderer
            else None
        )

        self.level_name = "Campus Track"
        self.camera = Camera(self.world_width, SCREEN_WIDTH)
        self.camera_x = 0.0
        self.collection_message = ""
        self.message_timer = 0.0
        self.visual_time = 0.0
        self.collection_bursts = []
        self.double_jump_unlocked = False
        self.player.audio = getattr(self.game, "audio", None)

        self.parallax_layers = [
            ParallaxLayer(0.05, (150, 183, 241), 0, 280),
            ParallaxLayer(0.08, (185, 208, 235), 80, 220),
            ParallaxLayer(0.15, (130, 160, 124), 220, 210),
            ParallaxLayer(0.30, (82, 104, 105), 300, 180),
            ParallaxLayer(0.50, (67, 82, 83), 360, 150),
            ParallaxLayer(1.00, (90, 120, 102), 470, 140),
            ParallaxLayer(1.10, (40, 58, 48), 540, 180),
        ]

        self.platforms = [
            pygame.Rect(0, self.ground_y, self.world_width, 120),
            pygame.Rect(220, 540, 180, 18),
            pygame.Rect(520, 500, 180, 18),
            pygame.Rect(820, 470, 180, 18),
            pygame.Rect(1160, 430, 180, 18),
            pygame.Rect(1500, 380, 180, 18),
            pygame.Rect(1880, 500, 220, 18),
            pygame.Rect(2250, 430, 180, 18),
            pygame.Rect(2600, 360, 220, 18),
            pygame.Rect(2980, 500, 220, 18),
            pygame.Rect(3360, 420, 180, 18),
            pygame.Rect(3720, 350, 200, 18),
            pygame.Rect(4060, 490, 220, 18),
            pygame.Rect(4420, 420, 200, 18),
            pygame.Rect(4800, 360, 200, 18),
            pygame.Rect(5200, 300, 220, 18),
            pygame.Rect(5600, 430, 220, 18),
            pygame.Rect(5940, 380, 260, 18),
        ]

        self.moving_platforms = [
            {"rect": pygame.Rect(2850, 300, 140, 18), "min_x": 2800, "max_x": 3320, "speed": 80, "direction": 1},
            {"rect": pygame.Rect(4680, 280, 140, 18), "min_x": 4560, "max_x": 5200, "speed": 90, "direction": 1},
        ]

        self.hazards = [
            pygame.Rect(420, self.ground_y - 26, 46, 26),
            pygame.Rect(760, self.ground_y - 26, 46, 26),
            pygame.Rect(1010, self.ground_y - 26, 46, 26),
            pygame.Rect(1720, self.ground_y - 26, 46, 26),
            pygame.Rect(2460, self.ground_y - 26, 46, 26),
            pygame.Rect(3200, self.ground_y - 26, 46, 26),
            pygame.Rect(4550, self.ground_y - 26, 46, 26),
            pygame.Rect(5480, self.ground_y - 26, 46, 26),
        ]

        self.collectibles = [
            {"rect": pygame.Rect(260, 500, 18, 18), "collected": False},
            {"rect": pygame.Rect(620, 460, 18, 18), "collected": False},
            {"rect": pygame.Rect(870, 430, 18, 18), "collected": False},
            {"rect": pygame.Rect(1190, 390, 18, 18), "collected": False},
            {"rect": pygame.Rect(1650, 340, 18, 18), "collected": False},
            {"rect": pygame.Rect(1980, 460, 18, 18), "collected": False},
            {"rect": pygame.Rect(2710, 320, 18, 18), "collected": False},
            {"rect": pygame.Rect(3430, 380, 18, 18), "collected": False},
            {"rect": pygame.Rect(4320, 380, 18, 18), "collected": False},
            {"rect": pygame.Rect(4870, 320, 18, 18), "collected": False},
            {"rect": pygame.Rect(5280, 260, 18, 18), "collected": False},
            {"rect": pygame.Rect(6080, 340, 18, 18), "collected": False},
        ]

        self.checkpoints = [
            {"rect": pygame.Rect(1980, self.ground_y - 120, 26, 120), "spawn": (1980, self.ground_y - 64), "active": False},
            {"rect": pygame.Rect(5200, self.ground_y - 120, 26, 120), "spawn": (5200, self.ground_y - 64), "active": False},
        ]

        self.current_checkpoint = (START_X, self.ground_y - 64)
        self.goal_rect = pygame.Rect(FINISH_X, self.ground_y - 180, 42, 180)
        self.level_complete = False
        self.player_dead = False
        self.respawn_timer = 0.0
        self.collected_count = 0
        self.total_collectibles = len(self.collectibles)
        self.double_jump_goal = max(4, self.total_collectibles // 3)
        self.double_jump_unlocked = False

        self.title_font = pygame.font.SysFont(None, 42, bold=True)
        self.label_font = pygame.font.SysFont(None, 24)
        self.hint_font = pygame.font.SysFont(None, 30)

    def reset_level(self) -> None:
        self.current_checkpoint = (START_X, self.ground_y - 64)
        self.player.rect.topleft = self.current_checkpoint
        self.player.velocity = pygame.Vector2(0, 0)
        self.player.on_ground = True
        self.player.set_ground(self.ground_y)
        self.player.state = Player.IDLE
        self.level_complete = False
        self.player_dead = False
        self.respawn_timer = 0.0
        self.camera_x = 0.0
        self.camera.x = 0.0
        self.camera.target_x = 0.0
        self.collection_message = ""
        self.message_timer = 0.0
        self.visual_time = 0.0
        self.collection_bursts.clear()
        self.double_jump_unlocked = False
        self.player.reset_jump_state()
        for item in self.collectibles:
            item["collected"] = False
        for checkpoint in self.checkpoints:
            checkpoint["active"] = False
        self.collected_count = 0

    def on_enter(self) -> None:
        self.state.current_scene = "sports_prototype"
        self.state.current_map = "Campus Track"
        self.state.select_map("Campus Track")
        self.player.set_character(get_character_definition(self.state.selected_character))
        self.reset_level()

    def trigger_death(self) -> None:
        if self.player_dead or self.level_complete:
            return
        self.player_dead = True
        self.respawn_timer = 1.0
        self.player.velocity.x = 0
        self.player.velocity.y = 0
        if hasattr(self.game, "audio"):
            self.game.audio.play_sfx("death")

    def respawn(self) -> None:
        self.player.rect.topleft = self.current_checkpoint
        self.player.velocity = pygame.Vector2(0, 0)
        self.player.on_ground = True
        self.player.state = Player.IDLE
        self.player_dead = False
        self.respawn_timer = 0.0

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.manager.change_scene("menu")

    def update(self, dt: float) -> None:
        self.visual_time += dt
        for burst in self.collection_bursts:
            burst["age"] += dt
        self.collection_bursts = [
            burst for burst in self.collection_bursts if burst["age"] < burst["duration"]
        ]

        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.collection_message = ""

        if self.level_complete:
            return

        if self.player_dead:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.respawn()
            return

        if not self.player.freeze_active:
            for platform in self.moving_platforms:
                rect = platform["rect"]
                rect.x += platform["speed"] * platform["direction"] * dt
                if rect.x <= platform["min_x"] or rect.x + rect.width >= platform["max_x"]:
                    platform["direction"] *= -1
                    rect.x = max(platform["min_x"], min(rect.x, platform["max_x"] - rect.width))

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

        previous_bottom = self.player.rect.bottom
        self.player.update(dt)

        if self.player.rect.bottom >= self.ground_y:
            self.player.rect.bottom = self.ground_y
            self.player.velocity.y = 0.0
            self.player.on_ground = True
            self.player.jump_count = 0
            if abs(self.player.velocity.x) > 0.1:
                self.player.state = Player.RUNNING
            else:
                self.player.state = Player.IDLE
        else:
            self.player.on_ground = False

        collision_boxes = self.platforms + [item["rect"] for item in self.moving_platforms]
        for platform in collision_boxes:
            if self.player.rect.colliderect(platform):
                if self.player.velocity.y >= 0 and previous_bottom <= platform.top + 24:
                    self.player.rect.bottom = platform.top
                    self.player.velocity.y = 0.0
                    self.player.on_ground = True
                    self.player.jump_count = 0
                    self.player.state = Player.RUNNING if abs(self.player.velocity.x) > 0.1 else Player.IDLE
                    break

        if self.player.rect.x < 0:
            self.player.rect.x = 0
        elif self.player.rect.x > self.world_width - self.player.rect.width:
            self.player.rect.x = self.world_width - self.player.rect.width

        for hazard in self.hazards:
            if self.player.rect.colliderect(hazard):
                self.trigger_death()
                break

        if self.player.rect.bottom > self.ground_y + 220 or self.player.rect.y > SCREEN_HEIGHT + 200:
            self.trigger_death()

        for item in self.collectibles:
            if not item["collected"] and self.player.rect.colliderect(item["rect"]):
                item["collected"] = True
                self.collected_count += 1
                if not self.double_jump_unlocked and self.collected_count >= self.double_jump_goal:
                    self.double_jump_unlocked = True
                    self.player.enable_double_jump()
                    self.collection_message = "Double Jump unlocked!"
                    self.message_timer = 2.0
                    if hasattr(self.game, "audio"):
                        self.game.audio.play_sfx("collect")
                else:
                    self.collection_message = "Mark collected!"
                    self.message_timer = 1.2
                self.collection_bursts.append({
                    "x": item["rect"].centerx,
                    "y": item["rect"].centery,
                    "age": 0.0,
                    "duration": 0.45,
                })
                if hasattr(self.game, "audio"):
                    self.game.audio.play_sfx("collect")

        for checkpoint in self.checkpoints:
            if not checkpoint["active"] and self.player.rect.colliderect(checkpoint["rect"]):
                checkpoint["active"] = True
                self.current_checkpoint = checkpoint["spawn"]
                if hasattr(self.game, "audio"):
                    self.game.audio.play_sfx("checkpoint")

        if self.player.rect.colliderect(self.goal_rect):
            self.level_complete = True
            if hasattr(self.game, "audio"):
                self.game.audio.play_sfx("goal")

        self.camera.update(self.player.rect.centerx)
        self.camera_x = self.camera.x

    def _draw_stadium_backdrop(self, surface: pygame.Surface) -> None:
        for y in range(0, 470, 4):
            blend = y / 470
            color = (int(112 + 105 * blend), int(177 + 30 * blend), int(235 - 48 * blend))
            pygame.draw.rect(surface, color, (0, y, SCREEN_WIDTH, 4))

        for index in range(-1, self.world_width // 700 + 2):
            x = int(index * 700 - self.camera_x * 0.12)
            if -180 < x < SCREEN_WIDTH + 180:
                height = 50 + (index % 3) * 22
                pygame.draw.rect(surface, (177, 195, 204), (x, 322 - height, 190, height))
                pygame.draw.rect(surface, (199, 211, 209), (x + 15, 335 - height, 160, 10))

        for index in range(-1, self.world_width // 1050 + 2):
            world_x = index * 1050 + 130
            x = int(world_x - self.camera_x * 0.42)
            if -380 < x < SCREEN_WIDTH + 380:
                pygame.draw.polygon(surface, (76, 103, 123), [(x - 55, 300), (x + 90, 205), (x + 620, 205), (x + 760, 300)])
                pygame.draw.polygon(surface, (224, 229, 217), [(x + 30, 240), (x + 125, 188), (x + 585, 188), (x + 680, 240)])
                pygame.draw.rect(surface, (233, 236, 224), (x - 28, 291, 720, 18))
                pygame.draw.rect(surface, (59, 83, 103), (x - 12, 309, 690, 144))
                for row in range(5):
                    row_y = 326 + row * 23
                    pygame.draw.line(surface, (110, 137, 151), (x + 5, row_y), (x + 655, row_y), 3)
                    for column in range(22):
                        person_x = x + 18 + column * 29
                        person_y = row_y - 5 + ((column + index + row) % 3) * 3
                        color = ((214, 115, 79), (238, 199, 104), (111, 184, 163))[(column + row) % 3]
                        pygame.draw.circle(surface, color, (person_x, person_y), 3)

        for world_x in (760, 2240, 3710, 5350, 6460):
            x = int(world_x - self.camera_x * 0.72)
            if -80 < x < SCREEN_WIDTH + 80:
                pygame.draw.rect(surface, (74, 91, 104), (x, 205, 14, 250))
                pygame.draw.rect(surface, (102, 120, 130), (x - 16, 198, 46, 14), border_radius=5)
                for light_x in range(x - 8, x + 25, 11):
                    pygame.draw.circle(surface, (255, 237, 176), (light_x, 205), 4)

        for world_x, text in ((2250, "TRAINING"), (4100, "CHALLENGE"), (5480, "FINAL SPRINT")):
            x = int(world_x - self.camera_x * 0.66)
            if -220 < x < SCREEN_WIDTH + 220:
                board = pygame.Rect(x, 278, 205, 64)
                pygame.draw.rect(surface, (34, 66, 83), board, border_radius=8)
                pygame.draw.rect(surface, (235, 205, 124), board, width=3, border_radius=8)
                text_surface = self.label_font.render(text, True, (250, 244, 216))
                surface.blit(text_surface, text_surface.get_rect(center=board.center))

    def _draw_track_and_entrance(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (177, 74, 76), (0, 490, SCREEN_WIDTH, self.ground_y - 490))
        pygame.draw.rect(surface, (197, 91, 83), (0, 500, SCREEN_WIDTH, 91))
        for lane_y in (516, 538, 560, 582, 604):
            pygame.draw.line(surface, (244, 218, 185), (0, lane_y), (SCREEN_WIDTH, lane_y), 2)
        for world_x in range(80, self.world_width, 180):
            x = int(world_x - self.camera_x)
            if -80 < x < SCREEN_WIDTH + 80:
                pygame.draw.line(surface, (247, 230, 201), (x, 522), (x, 601), 2)

        gate_x = int(28 - self.camera_x)
        if -440 < gate_x < SCREEN_WIDTH:
            pygame.draw.rect(surface, (237, 222, 185), (gate_x, 390, 28, 112), border_radius=5)
            pygame.draw.rect(surface, (237, 222, 185), (gate_x + 370, 390, 28, 112), border_radius=5)
            pygame.draw.rect(surface, (237, 222, 185), (gate_x + 14, 372, 370, 26), border_radius=8)
            pygame.draw.rect(surface, (44, 76, 91), (gate_x + 60, 405, 270, 48), border_radius=8)
            pygame.draw.rect(surface, (216, 112, 74), (gate_x + 60, 405, 270, 5), border_radius=2)
            gate_text = self.label_font.render("CAMPUS STADIUM", True, (250, 242, 217))
            surface.blit(gate_text, gate_text.get_rect(center=(gate_x + 195, 429)))
            for flag_x, flag_color in ((gate_x + 44, (234, 118, 77)), (gate_x + 345, (93, 177, 153))):
                pygame.draw.line(surface, (245, 239, 215), (flag_x, 340), (flag_x, 390), 3)
                pygame.draw.polygon(surface, flag_color, [(flag_x, 342), (flag_x + 33, 352), (flag_x, 364)])

        start_x = int(175 - self.camera_x)
        pygame.draw.line(surface, (255, 249, 222), (start_x, 504), (start_x, self.ground_y), 4)
        pygame.draw.rect(surface, (64, 78, 82), (start_x + 24, 593, 36, 9), border_radius=3)
        pygame.draw.rect(surface, (218, 170, 104), (start_x + 27, 587, 5, 8), border_radius=2)

        for world_x in (590, 1860, 3340, 4950, 6220):
            x = int(world_x - self.camera_x)
            if -130 < x < SCREEN_WIDTH + 130:
                pygame.draw.line(surface, (239, 231, 208), (x, 460), (x, 492), 3)
                pygame.draw.polygon(surface, (224, 133, 79), [(x, 461), (x + 40, 470), (x, 480)])

        for world_x in (700, 920, 2420, 2680, 3920, 4450, 5200, 5780):
            x = int(world_x - self.camera_x)
            if -40 < x < SCREEN_WIDTH + 40:
                pygame.draw.polygon(surface, (239, 155, 82), [(x - 12, 490), (x + 12, 490), (x, 466)])
                pygame.draw.ellipse(surface, (249, 219, 167), (x - 12, 487, 24, 7))

    def _draw_platforms_and_objects(self, surface: pygame.Surface) -> None:
        for platform in self.platforms:
            if platform.top >= self.ground_y:
                continue
            draw_rect = platform.move(-self.camera_x, 0)
            side = pygame.Rect(draw_rect.x, draw_rect.bottom - 5, draw_rect.width, 9)
            pygame.draw.rect(surface, (45, 75, 68), side, border_radius=5)
            pygame.draw.rect(surface, (61, 119, 91), draw_rect, border_radius=7)
            pygame.draw.rect(surface, (147, 181, 128), (draw_rect.x, draw_rect.y, draw_rect.width, 5), border_radius=3)

        for moving in self.moving_platforms:
            rect = moving["rect"].move(-self.camera_x, 0)
            pygame.draw.rect(surface, (52, 88, 102), rect.move(0, 4), border_radius=7)
            pygame.draw.rect(surface, (86, 151, 164), rect, border_radius=7)
            pygame.draw.rect(surface, (180, 222, 211), (rect.x + 8, rect.y + 3, rect.width - 16, 4), border_radius=2)

        for hazard in self.hazards:
            rect = hazard.move(-self.camera_x, 0)
            pygame.draw.rect(surface, (76, 61, 58), (rect.x - 3, rect.bottom - 4, rect.width + 6, 6), border_radius=2)
            pygame.draw.rect(surface, (228, 126, 74), rect, border_radius=5)
            pygame.draw.rect(surface, (255, 222, 158), (rect.x, rect.y, rect.width, 5), border_radius=2)
            for stripe_x in range(rect.x + 6, rect.right - 4, 14):
                pygame.draw.line(surface, (250, 222, 175), (stripe_x, rect.y + 8), (stripe_x + 7, rect.bottom - 4), 3)

        for checkpoint in self.checkpoints:
            marker = checkpoint["rect"].move(-self.camera_x, 0)
            color = (82, 224, 130) if checkpoint["active"] else (228, 220, 192)
            pygame.draw.rect(surface, (55, 67, 68), (marker.x + 8, marker.y, 8, marker.height))
            pygame.draw.polygon(surface, color, [(marker.x + 16, marker.y + 4), (marker.x + 58, marker.y + 18), (marker.x + 16, marker.y + 34)])

        for item in self.collectibles:
            if not item["collected"]:
                mark_rect = item["rect"].move(-self.camera_x, 0)
                pygame.draw.circle(surface, (151, 103, 48), mark_rect.center, 13)
                pygame.draw.circle(surface, (255, 214, 105), mark_rect.center, 10)
                pygame.draw.circle(surface, (255, 248, 207), mark_rect.center, 4)

    def _draw_finish(self, surface: pygame.Surface) -> None:
        goal_rect = self.goal_rect.move(-self.camera_x, 0)
        banner = pygame.Rect(goal_rect.x - 145, 380, 330, 46)
        pygame.draw.rect(surface, (44, 72, 88), banner, border_radius=6)
        pygame.draw.rect(surface, (245, 223, 172), banner, width=3, border_radius=6)
        finish_text = self.label_font.render("FINISH", True, (255, 244, 213))
        surface.blit(finish_text, finish_text.get_rect(center=banner.center))
        pygame.draw.rect(surface, (245, 240, 225), goal_rect)
        pygame.draw.rect(surface, (214, 96, 65), (goal_rect.x, goal_rect.y, 12, goal_rect.height))
        pygame.draw.rect(surface, (255, 255, 255), (goal_rect.x + 12, goal_rect.y, 12, goal_rect.height))
        pygame.draw.rect(surface, (39, 61, 70), (goal_rect.x - 30, goal_rect.y, 8, goal_rect.height))

        finish_line_x = int(goal_rect.x - 42)
        for row in range(4):
            for column in range(4):
                color = (247, 241, 220) if (row + column) % 2 == 0 else (49, 64, 68)
                pygame.draw.rect(surface, color, (finish_line_x + column * 10, self.ground_y - 24 + row * 6, 10, 6))

    def draw(self, surface: pygame.Surface) -> None:
        self.stadium_renderer.draw_background(surface, self.camera_x)
        self.stadium_renderer.draw_field_and_track(surface, self.camera_x, self.ground_y)
        self.stadium_renderer.draw_landmarks(surface, self.camera_x, self.visual_time)
        self.stadium_renderer.draw_gameplay_objects(
            surface,
            self.camera_x,
            self.ground_y,
            self.platforms,
            self.moving_platforms,
            self.hazards,
            self.checkpoints,
            self.collectibles,
            self.goal_rect,
            self.player.rect,
            self.visual_time,
            self.collection_bursts,
        )
        self.player.draw(surface, self.camera_x)

        panel = pygame.Rect(16, 14, 330, 72)
        pygame.draw.rect(surface, (31, 55, 71), panel, border_radius=8)
        pygame.draw.rect(surface, (218, 195, 151), panel, width=2, border_radius=8)
        label = self.label_font.render(f"{self.state.selected_character.upper()}  HERO", True, (250, 241, 215))
        marks = self.label_font.render(f"MARKS  {self.collected_count:02} / {self.total_collectibles:02}", True, (255, 215, 113))
        status = self.label_font.render(
            "DOUBLE JUMP" if self.double_jump_unlocked else f"NEEDS {max(0, self.double_jump_goal - self.collected_count)} MARKS",
            True,
            (162, 232, 176) if self.double_jump_unlocked else (232, 201, 143),
        )
        surface.blit(label, (28, 22))
        surface.blit(marks, (28, 46))
        surface.blit(status, (28, 58))

        if self.collection_message:
            collection_text = self.hint_font.render(self.collection_message, True, (255, 231, 164))
            text_rect = collection_text.get_rect(center=(SCREEN_WIDTH // 2, 112))
            backing = text_rect.inflate(30, 14)
            pygame.draw.rect(surface, (52, 74, 82), backing, border_radius=9)
            pygame.draw.rect(surface, (221, 183, 112), backing, width=2, border_radius=9)
            surface.blit(collection_text, text_rect)

        if self.level_complete:
            message = "LEVEL COMPLETE!"
        elif self.player_dead:
            message = "Respawning at checkpoint..."
        elif self.player.rect.x < 1200:
            message = "Run the track. Jump with Space."
        else:
            message = "CAMPUS TRACK  |  LEVEL 1"
        status = self.hint_font.render(message, True, (255, 246, 218))
        status_backing = status.get_rect(center=(SCREEN_WIDTH // 2, 34)).inflate(24, 12)
        pygame.draw.rect(surface, (31, 55, 71), status_backing, border_radius=7)
        pygame.draw.rect(surface, (204, 188, 152), status_backing, width=1, border_radius=7)
        surface.blit(status, status.get_rect(center=status_backing.center))

