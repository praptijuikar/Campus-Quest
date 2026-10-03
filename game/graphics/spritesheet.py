from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pygame


class SpriteSheetLoader:
    _cache: dict[str, dict[str, list[pygame.Surface]]] = {}
    _json_cache: dict[str, dict[str, Any]] = {}

    def __init__(self, root_dir: str | Path | None = None) -> None:
        self.root_dir = Path(root_dir) if root_dir is not None else Path(__file__).resolve().parents[1]
        self.assets_dir = self.root_dir.parent / "assets" / "characters"

    def load_character(self, character_name: str) -> dict[str, list[pygame.Surface]]:
        key = character_name.lower()
        if key in self._cache:
            return self._cache[key]

        if not pygame.get_init():
            pygame.init()
        if not pygame.display.get_init() or pygame.display.get_surface() is None:
            return {}

        metadata_path = self.assets_dir / character_name.lower() / f"{character_name.lower()}.json"
        png_path = self.assets_dir / character_name.lower() / f"{character_name.lower()}_spritesheet.png"

        if not metadata_path.exists() or not png_path.exists():
            return {}

        with metadata_path.open("r", encoding="utf-8") as handle:
            metadata = json.load(handle)

        sheet = pygame.image.load(str(png_path)).convert_alpha()
        frame_width = int(metadata["frame_width"])
        frame_height = int(metadata["frame_height"])
        animations: dict[str, list[pygame.Surface]] = {}

        for name, info in metadata.get("animations", {}).items():
            frames: list[pygame.Surface] = []
            for frame_index in range(info["start_frame"], info["end_frame"] + 1):
                col = frame_index % metadata["columns"]
                row = frame_index // metadata["columns"]
                rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), rect)
                frames.append(frame)
            animations[name] = frames

        self._cache[key] = animations
        self._json_cache[key] = metadata
        return animations

    def get_animation(self, character_name: str, animation_name: str) -> list[pygame.Surface]:
        animations = self.load_character(character_name)
        return animations.get(animation_name, [])
