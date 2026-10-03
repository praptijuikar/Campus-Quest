from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets" / "characters"
FRAME_WIDTH = 64
FRAME_HEIGHT = 64
COLUMNS = 6
ROWS = 7


CHARACTER_PALETTES = {
    "jason": {
        "shirt": (45, 119, 207, 255),
        "pants": (29, 43, 81, 255),
        "skin": (230, 199, 166, 255),
        "hair": (42, 29, 20, 255),
        "shoes": (21, 22, 29, 255),
        "accent": (149, 217, 255, 255),
        "outline": (64, 47, 35, 255),
    },
    "krrish": {
        "shirt": (114, 187, 118, 255),
        "pants": (52, 64, 78, 255),
        "skin": (228, 198, 169, 255),
        "hair": (43, 29, 20, 255),
        "shoes": (73, 55, 39, 255),
        "accent": (243, 211, 113, 255),
        "outline": (66, 47, 35, 255),
    },
}


def draw_shadow(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    draw.ellipse((12, height - 8, width - 12, height - 2), fill=(0, 0, 0, 40))


def draw_human(frame: Image.Image, palette: dict[str, tuple[int, int, int, int]], pose: str, variant: str) -> None:
    draw = ImageDraw.Draw(frame)
    width, height = frame.size
    draw_shadow(draw, width, height)

    cx = width // 2
    cy = height // 2 - 2
    skin = palette["skin"]
    shirt = palette["shirt"]
    pants = palette["pants"]
    accent = palette["accent"]
    shoes = palette["shoes"]
    hair = palette["hair"]
    outline = palette["outline"]

    if pose == "run":
        arm_shift = 5 if (cx % 2) == 0 else -5
    elif pose == "jump":
        arm_shift = -8
    elif pose == "fall":
        arm_shift = 8
    else:
        arm_shift = 0

    draw.ellipse((cx - 10, 2, cx + 10, 22), fill=skin)
    draw.ellipse((cx - 9, 0, cx + 9, 14), fill=hair)
    draw.arc((cx - 5, 9, cx + 5, 15), 220, 320, fill=outline, width=2)
    draw.ellipse((cx - 3, 9, cx - 1, 12), fill=(0, 0, 0, 180))
    draw.ellipse((cx + 1, 9, cx + 3, 12), fill=(0, 0, 0, 180))

    draw.rounded_rectangle((cx - 12, 20, cx + 12, 39), radius=7, fill=shirt)
    draw.line((cx, 20, cx + arm_shift, 32), fill=accent, width=3)

    draw.rounded_rectangle((cx - 9, 39, cx - 3, 53), radius=3, fill=pants)
    draw.rounded_rectangle((cx + 3, 39, cx + 9, 53), radius=3, fill=pants)

    draw.rounded_rectangle((cx - 13, 24, cx - 7, 36), radius=3, fill=skin)
    draw.rounded_rectangle((cx + 7, 24, cx + 13, 36), radius=3, fill=skin)

    if variant == "jason":
        draw.rounded_rectangle((cx - 9, 30, cx + 9, 36), radius=3, fill=accent)
    else:
        draw.rounded_rectangle((cx - 14, 18, cx - 11, 35), radius=2, fill=palette["accent"])

    if pose in {"run", "jump", "fall"}:
        draw.rounded_rectangle((cx - 16, 39, cx - 8, 53), radius=3, fill=shoes)
        draw.rounded_rectangle((cx + 8, 39, cx + 16, 53), radius=3, fill=shoes)
        if pose == "run":
            if (cx % 3) == 0:
                draw.rounded_rectangle((cx - 14, 35, cx - 8, 45), radius=3, fill=skin)
                draw.rounded_rectangle((cx + 8, 35, cx + 14, 45), radius=3, fill=skin)
            else:
                draw.rounded_rectangle((cx - 8, 35, cx - 2, 45), radius=3, fill=skin)
                draw.rounded_rectangle((cx + 2, 35, cx + 8, 45), radius=3, fill=skin)
        elif pose == "jump":
            draw.rounded_rectangle((cx - 14, 38, cx - 8, 47), radius=3, fill=skin)
            draw.rounded_rectangle((cx + 8, 41, cx + 14, 50), radius=3, fill=skin)
        elif pose == "fall":
            draw.rounded_rectangle((cx - 14, 42, cx - 8, 51), radius=3, fill=skin)
            draw.rounded_rectangle((cx + 8, 36, cx + 14, 45), radius=3, fill=skin)
    else:
        draw.rounded_rectangle((cx - 14, 44, cx - 8, 54), radius=3, fill=shoes)
        draw.rounded_rectangle((cx + 8, 44, cx + 14, 54), radius=3, fill=shoes)

    if pose == "ability":
        if variant == "jason":
            for ring in range(1, 6):
                radius = 12 + ring * 4
                alpha = 60 - ring * 8
                draw.ellipse((cx - radius, 17 - radius, cx + radius, 17 + radius), outline=(120, 200, 255, alpha), width=2)
        else:
            for offset in range(6):
                px = cx + (offset - 2) * 7
                py = 12 + (offset % 2) * 7
                draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill=(138, 232, 128, 160))

    if pose == "hurt":
        draw.line((cx - 8, 4, cx - 12, 12), fill=outline, width=2)
        draw.line((cx + 8, 4, cx + 12, 12), fill=outline, width=2)

    if pose == "death":
        draw.line((cx - 12, 20, cx - 18, 30), fill=outline, width=2)
        draw.line((cx + 12, 20, cx + 18, 30), fill=outline, width=2)


def create_sprite_sheet(character_name: str) -> tuple[Path, dict[str, object]]:
    palette = CHARACTER_PALETTES[character_name]
    folder = ASSETS_DIR / character_name
    folder.mkdir(parents=True, exist_ok=True)
    sheet_path = folder / f"{character_name}_spritesheet.png"
    metadata_path = folder / f"{character_name}.json"

    sheet = Image.new("RGBA", (COLUMNS * FRAME_WIDTH, ROWS * FRAME_HEIGHT), (0, 0, 0, 0))
    animation_ranges = {
        "idle": (0, 5),
        "run": (6, 11),
        "jump": (12, 17),
        "fall": (18, 23),
        "ability": (24, 29),
        "hurt": (30, 35),
        "death": (36, 41),
    }

    metadata: dict[str, object] = {
        "columns": COLUMNS,
        "rows": ROWS,
        "frame_width": FRAME_WIDTH,
        "frame_height": FRAME_HEIGHT,
        "animations": {},
    }

    for row_index, (animation_name, (start, end)) in enumerate(animation_ranges.items()):
        metadata["animations"][animation_name] = {"start_frame": start, "end_frame": end}
        for frame_number in range(start, end + 1):
            row = frame_number // COLUMNS
            col = frame_number % COLUMNS
            x = col * FRAME_WIDTH
            y = row_index * FRAME_HEIGHT
            frame = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
            pose = animation_name
            draw_human(frame, palette, pose, character_name)
            sheet.paste(frame, (x, y), frame)

    sheet.save(sheet_path)
    with metadata_path.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)

    return sheet_path, metadata


if __name__ == "__main__":
    created: list[str] = []
    for name in ("jason", "krrish"):
        path, _ = create_sprite_sheet(name)
        created.append(str(path))
    for path in created:
        print(f"Created {path}")
