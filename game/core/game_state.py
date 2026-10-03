from dataclasses import dataclass


@dataclass
class GameState:
    selected_character: str = "Krrish"
    current_scene: str = "menu"
    current_map: str = "none"
    score: int = 0
    health: int = 100
    sports_score: int = 0
    restaurant_score: int = 0
    active_powerup: str | None = None
    powerup_time_remaining: float = 0.0
    game_completed: bool = False

    def select_character(self, name: str) -> None:
        self.selected_character = name.strip().title()

    def select_map(self, map_name: str) -> None:
        self.current_map = map_name

    def reset_run(self) -> None:
        self.score = 0
        self.health = 100
        self.sports_score = 0
        self.restaurant_score = 0
        self.active_powerup = None
        self.powerup_time_remaining = 0.0
        self.game_completed = False
