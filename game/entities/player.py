from __future__ import annotations

import pygame

from game.characters import get_character_definition
from game.config.settings import (
    GRAVITY,
    JUMP_STRENGTH,
    MAX_FALL_SPEED,
    PLAYER_COLOR,
    PLAYER_HEIGHT,
    PLAYER_SPEED,
    PLAYER_WIDTH,
)
from game.graphics import SpriteSheetLoader


class Player:
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    JUMPING = "JUMPING"
    FALLING = "FALLING"

    def __init__(self, x: float, y: float) -> None:
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.velocity = pygame.Vector2(0.0, 0.0)
        self.facing = 1
        self.on_ground = False
        self.state = self.IDLE
        self.color = PLAYER_COLOR
        self.ground_y = 0
        self.character_name = "Krrish"
        self.character = get_character_definition(self.character_name)
        self.can_double_jump = self.character.name == "Krrish"
        self.jump_count = 0
        self.jump_held = False
        self.audio = None
        self.freeze_timer = 0.0
        self.freeze_cooldown = 0.0
        self.freeze_active = False
        self.sprite_loader = SpriteSheetLoader()
        self.animations = (
            self.sprite_loader.load_character(self.character_name)
            if pygame.display.get_init() and pygame.display.get_surface() is not None
            else {}
        )
        self.animation_index = 0
        self.animation_timer = 0.0

    def _get_animation_name(self) -> str:
        if self.freeze_active:
            return "ability"
        if self.state == self.RUNNING:
            return "run"
        if self.state == self.JUMPING:
            return "jump"
        if self.state == self.FALLING:
            return "fall"
        return "idle"

    def set_character(self, character) -> None:
        self.character = character
        self.character_name = getattr(character, "name", "Krrish")
        self.can_double_jump = self.character_name == "Krrish"
        self.jump_count = 0
        self.freeze_timer = 0.0
        self.freeze_cooldown = 0.0
        self.freeze_active = False
        self.animations = (
            self.sprite_loader.load_character(self.character_name)
            if pygame.display.get_init() and pygame.display.get_surface() is not None
            else {}
        )
        self.animation_index = 0
        self.animation_timer = 0.0
        if self.character_name == "Jason":
            self.color = (104, 166, 255)
        else:
            self.color = PLAYER_COLOR

    def set_ground(self, ground_y: float) -> None:
        self.ground_y = ground_y

    def enable_double_jump(self) -> None:
        self.can_double_jump = True
        self.jump_count = 1

    def reset_jump_state(self) -> None:
        self.jump_count = 0
        self.jump_held = False

    def _trigger_jump(self, *, is_double: bool = False) -> None:
        if is_double:
            self.velocity.y = -JUMP_STRENGTH * 0.9
            self.jump_count = 2
        else:
            self.velocity.y = -JUMP_STRENGTH
            self.jump_count = 1
        self.on_ground = False
        self.state = self.JUMPING
        if self.audio is not None and hasattr(self.audio, "play_sfx"):
            self.audio.play_sfx("jump")

    def activate_ability(self) -> bool:
        if self.character_name == "Jason":
            if self.freeze_cooldown > 0.0 or self.freeze_active:
                return False
            self.freeze_timer = getattr(self.character, "freeze_duration", 2.5)
            self.freeze_cooldown = getattr(self.character, "cooldown", 5.0)
            self.freeze_active = True
            if self.audio is not None and hasattr(self.audio, "play_sfx"):
                self.audio.play_sfx("freeze")
            return True
        return False

    def handle_input(self, pressed_keys) -> None:
        move_x = 0.0

        if pressed_keys[pygame.K_a] or pressed_keys[pygame.K_LEFT]:
            move_x -= 1.0
        if pressed_keys[pygame.K_d] or pressed_keys[pygame.K_RIGHT]:
            move_x += 1.0

        if move_x < 0:
            self.facing = -1
        elif move_x > 0:
            self.facing = 1

        self.velocity.x = move_x * PLAYER_SPEED

        jump_requested = bool(
            pressed_keys[pygame.K_SPACE]
            or pressed_keys[pygame.K_w]
            or pressed_keys[pygame.K_UP]
        )

        if jump_requested and not self.jump_held:
            if self.on_ground:
                self._trigger_jump(is_double=False)
            elif self.can_double_jump and self.jump_count < 2:
                self._trigger_jump(is_double=True)

        if pressed_keys[pygame.K_f] and not self.freeze_active:
            self.activate_ability()

        self.jump_held = jump_requested

    def update(self, dt: float) -> None:
        if self.freeze_cooldown > 0.0:
            self.freeze_cooldown = max(0.0, self.freeze_cooldown - dt)
        if self.freeze_timer > 0.0:
            self.freeze_timer = max(0.0, self.freeze_timer - dt)
            if self.freeze_timer == 0.0:
                self.freeze_active = False

        if not self.on_ground:
            self.velocity.y = min(self.velocity.y + GRAVITY * dt, MAX_FALL_SPEED)
        else:
            self.velocity.y = 0.0

        if self.on_ground and abs(self.velocity.x) > 0.1:
            self.state = self.RUNNING
        elif self.on_ground:
            self.state = self.IDLE
        elif self.velocity.y < 0:
            self.state = self.JUMPING
        else:
            self.state = self.FALLING

        self.animation_timer += dt
        animation_name = self._get_animation_name()
        frames = self.animations.get(animation_name, [])
        if frames:
            frame_rate = 0.12 if animation_name == "run" else 0.2
            if self.animation_timer >= frame_rate:
                self.animation_timer = 0.0
                self.animation_index = (self.animation_index + 1) % len(frames)

        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt

    def draw(self, surface: pygame.Surface, camera_x: float = 0.0) -> None:
        animation_name = self._get_animation_name()
        frames = self.animations.get(animation_name, [])
        if frames:
            frame = frames[self.animation_index % len(frames)]
            if self.facing < 0:
                frame = pygame.transform.flip(frame, True, False)
            sprite_rect = frame.get_rect()
            sprite_rect.midbottom = (self.rect.centerx - camera_x, self.rect.bottom)
            if self.freeze_active:
                glow = pygame.Surface((self.rect.width + 18, self.rect.height + 18), pygame.SRCALPHA)
                pygame.draw.ellipse(glow, (110, 200, 255, 110), (0, 0, glow.get_width(), glow.get_height()))
                surface.blit(glow, (self.rect.x - camera_x - 9, self.rect.y - 9))
            surface.blit(frame, sprite_rect)
            return

        body = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(body, self.color, (0, 8, self.rect.width, self.rect.height - 8), border_radius=10)
        pygame.draw.circle(body, (245, 230, 210), (self.rect.width // 2, 12), 12)

        if self.freeze_active:
            glow = pygame.Surface((self.rect.width + 18, self.rect.height + 18), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (110, 200, 255, 110), (0, 0, glow.get_width(), glow.get_height()))
            surface.blit(glow, (self.rect.x - camera_x - 9, self.rect.y - 9))

        if self.facing < 0:
            body = pygame.transform.flip(body, True, False)

        screen_rect = self.rect.move(-camera_x, 0)
        surface.blit(body, screen_rect)
