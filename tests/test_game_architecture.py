import sqlite3
import sys
from types import SimpleNamespace

import pygame

from game.backend.database import DatabaseStore
from game.characters.jason import JasonCharacter
from game.characters.krrish import KrrishCharacter
from game.config.settings import SCREEN_WIDTH, SPORTS_WORLD_WIDTH
from game.core.camera import Camera, ParallaxLayer
from game.core.game_state import GameState
from game.core.scene_manager import SceneManager
from game.entities.player import Player
from game.scenes.character_select import CharacterSelectScene
from game.scenes.completion import CompletionScene
from game.scenes.map_select import MapSelectScene
from game.scenes.menu import MenuScene
from game.scenes.restaurant import RestaurantScene
from game.scenes.sports_prototype import SportsPrototypeScene


class DummyScene:
    def __init__(self, name: str) -> None:
        self.name = name
        self.entered = False

    def on_enter(self) -> None:
        self.entered = True

    def on_exit(self) -> None:
        pass

    def handle_event(self, event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface) -> None:
        pass


class PressedKeys:
    def __init__(self, *keys: int) -> None:
        self.keys = set(keys)

    def __getitem__(self, key: int) -> bool:
        return key in self.keys


def test_game_state_defaults() -> None:
    state = GameState()

    assert state.selected_character == "Krrish"
    assert state.current_scene == "menu"
    assert state.score == 0
    assert state.health == 100
    assert state.game_completed is False


def test_scene_manager_changes_scenes() -> None:
    game = type("Game", (), {"state": GameState()})()
    manager = SceneManager(game)
    menu_scene = DummyScene("menu")
    character_scene = DummyScene("character_select")

    manager.register("menu", menu_scene)
    manager.register("character_select", character_scene)
    manager.change_scene("menu")

    assert manager.current_scene_name == "menu"
    assert menu_scene.entered is True

    manager.change_scene("character_select")

    assert manager.current_scene_name == "character_select"
    assert character_scene.entered is True


def test_character_selection_continues_to_maps_then_starts_track() -> None:
    game = type("Game", (), {"state": GameState()})()
    manager = SceneManager(game)
    select_scene = CharacterSelectScene(game, manager)
    map_scene = MapSelectScene(game, manager)
    sports_scene = DummyScene("sports_prototype")

    manager.register("character_select", select_scene)
    manager.register("map_select", map_scene)
    manager.register("sports_prototype", sports_scene)
    manager.change_scene("character_select")

    select_scene.confirm_selection()

    assert game.state.selected_character == "Krrish"
    assert manager.current_scene_name == "map_select"
    map_scene.select_map(0)
    map_scene.start_game()
    assert game.state.current_map == "Campus Track"
    assert manager.current_scene_name == "sports_prototype"


def test_jason_selection_and_canteen_map_start_independently() -> None:
    game = type("Game", (), {"state": GameState()})()
    manager = SceneManager(game)
    select_scene = CharacterSelectScene(game, manager)
    map_scene = MapSelectScene(game, manager)
    canteen_scene = DummyScene("restaurant")

    manager.register("character_select", select_scene)
    manager.register("map_select", map_scene)
    manager.register("restaurant", canteen_scene)
    manager.change_scene("character_select")
    select_scene.selected_index = 0
    select_scene.confirm_selection()
    map_scene.select_map(1)
    map_scene.start_game()

    assert game.state.selected_character == "Jason"
    assert manager.current_scene_name == "restaurant"
    assert game.state.current_map == "Canteen"


def test_all_player_and_map_combinations_start_with_selected_player() -> None:
    game = type("Game", (), {"state": GameState()})()
    manager = SceneManager(game)
    map_scene = MapSelectScene(game, manager)
    manager.register("map_select", map_scene)
    manager.register("sports_prototype", SportsPrototypeScene(game, manager))
    manager.register("restaurant", RestaurantScene(game, manager))

    for character in ("Jason", "Krrish"):
        for map_index, (map_name, scene_name) in enumerate(
            (("Campus Track", "sports_prototype"), ("Canteen", "restaurant"))
        ):
            game.state.select_character(character)
            map_scene.select_map(map_index)
            map_scene.start_game()

            assert manager.current_scene_name == scene_name
            assert game.state.selected_character == character
            assert game.state.current_map == map_name
            assert manager.current_scene.player.character_name == character


def test_all_four_gameplay_runs_cover_movement_collision_checkpoint_respawn_and_goal(monkeypatch) -> None:
    keys = PressedKeys(pygame.K_d)
    monkeypatch.setattr(pygame.key, "get_pressed", lambda: keys)

    for character in ("Jason", "Krrish"):
        for map_name, scene_name in (("Campus Track", "sports_prototype"), ("Canteen", "restaurant")):
            game = type("Game", (), {"state": GameState(selected_character=character)})()
            manager = SceneManager(game)
            track = SportsPrototypeScene(game, manager)
            canteen = RestaurantScene(game, manager)
            completion = CompletionScene(game, manager)
            manager.register("sports_prototype", track)
            manager.register("restaurant", canteen)
            manager.register("completion", completion)
            manager.change_scene(scene_name)
            scene = manager.current_scene

            assert game.state.current_map == map_name
            assert scene.player.character_name == character
            keys = PressedKeys(pygame.K_d)
            start_x = scene.player.rect.x
            scene.update(0.05)
            assert scene.player.rect.x > start_x

            keys = PressedKeys()
            scene.player.rect.bottom = scene.ground_y - 3
            scene.player.velocity.y = 120
            scene.player.on_ground = False
            scene.update(0.05)
            assert scene.player.on_ground is True
            assert scene.player.rect.bottom == scene.ground_y

            keys = PressedKeys(pygame.K_SPACE)
            scene.update(1 / 60)
            assert scene.player.jump_count == 1
            assert scene.player.state == Player.JUMPING

            checkpoint = scene.checkpoints[0]
            scene.player.rect.topleft = (checkpoint["rect"].x, checkpoint["rect"].y + 10)
            scene.player.velocity.y = 0
            scene.player.on_ground = True
            scene.update(0.016)
            assert checkpoint["active"] is True
            assert scene.current_checkpoint == checkpoint["spawn"]
            scene.trigger_death()
            scene.respawn()
            assert scene.player.rect.topleft == checkpoint["spawn"]

            scene.player.rect.topleft = (scene.goal_rect.x, scene.goal_rect.y + 20)
            scene.player.on_ground = False
            scene.player.velocity.y = 0
            scene.update(0)
            assert manager.current_scene_name == "completion"
            assert game.state.game_completed is True


def test_jason_freeze_feedback_does_not_disable_movement() -> None:
    player = Player(100, 200)
    player.set_character(JasonCharacter())

    assert player.activate_ability() is True
    assert player.freeze_active is True
    assert player._get_animation_name() == "ability"
    player.handle_input(PressedKeys(pygame.K_RIGHT))
    assert player.velocity.x > 0


def test_home_navigation_has_four_options_without_guide() -> None:
    game = type("Game", (), {"state": GameState(), "quit": lambda self: None})()
    scene = MenuScene(game, SceneManager(game))

    assert [button.text for button in scene.buttons] == ["PLAY", "PLAYERS", "MAPS", "SETTINGS"]


def test_restaurant_preserves_finite_platforming_systems() -> None:
    game = type("Game", (), {"state": GameState()})()
    scene = RestaurantScene(game, SceneManager(game))

    assert len(scene.collectibles) == 12
    assert len(scene.checkpoints) == 2
    assert len(scene.moving_platforms) >= 1
    assert scene.goal_rect.right <= scene.world_width


def test_sports_map_initializes() -> None:
    pygame.init()
    game = type("Game", (), {"state": GameState()})()
    manager = SceneManager(game)
    scene = SportsPrototypeScene(game, manager)

    assert scene.world_width > SCREEN_WIDTH
    assert scene.goal_rect.x < scene.world_width
    assert scene.player.rect.width > 0
    assert scene.camera.world_width == SPORTS_WORLD_WIDTH
    assert len(scene.parallax_layers) >= 4
    assert len(scene.checkpoints) >= 1
    assert len(scene.collectibles) >= 1


def test_player_initializes() -> None:
    player = Player(100, 200)

    assert player.rect.x == 100
    assert player.rect.y == 200
    assert player.state == Player.IDLE
    assert player.facing == 1


def test_camera_clamps_to_level_boundaries() -> None:
    camera = Camera(world_width=2000, screen_width=1280)

    camera.update(10)
    assert camera.x == 0.0

    camera.update(3000)
    assert camera.x <= 720
    assert camera.x >= 0


def test_parallax_layer_initializes() -> None:
    layer = ParallaxLayer(0.25, (12, 34, 56), 100)

    assert layer.speed == 0.25
    assert layer.color == (12, 34, 56)
    assert layer.y == 100


def test_level_has_checkpoint_and_goal() -> None:
    game = type("Game", (), {"state": GameState()})()
    scene = SportsPrototypeScene(game, SceneManager(game))

    assert len(scene.checkpoints) >= 1
    assert scene.goal_rect.right <= scene.world_width
    assert scene.goal_rect.x > scene.checkpoints[-1]["rect"].x


def test_respawn_uses_latest_checkpoint() -> None:
    game = type("Game", (), {"state": GameState()})()
    scene = SportsPrototypeScene(game, SceneManager(game))
    checkpoint = scene.checkpoints[0]
    scene.current_checkpoint = checkpoint["spawn"]
    scene.player.rect.topleft = (checkpoint["spawn"][0], checkpoint["spawn"][1])

    scene.trigger_death()
    assert scene.player_dead is True

    scene.respawn()
    assert scene.player.rect.topleft == checkpoint["spawn"]
    assert scene.player_dead is False


def test_player_can_unlock_double_jump() -> None:
    player = Player(100, 200)
    player.set_character(KrrishCharacter())

    assert player.can_double_jump is False
    player.enable_double_jump()

    assert player.can_double_jump is True
    assert player.jump_count == 1


def test_krrish_starts_double_jump_locked_and_jason_never_unlocks_it() -> None:
    game = type("Game", (), {"state": GameState(selected_character="Krrish")})()
    scene = SportsPrototypeScene(game, SceneManager(game))
    scene.on_enter()

    assert scene.player.can_double_jump is False
    assert scene.double_jump_unlocked is False


def test_collectible_threshold_unlocks_double_jump_only_for_krrish_on_both_maps(monkeypatch) -> None:
    monkeypatch.setattr(pygame.key, "get_pressed", lambda: PressedKeys())

    for scene_type in (SportsPrototypeScene, RestaurantScene):
        for character in ("Jason", "Krrish"):
            game = type("Game", (), {"state": GameState(selected_character=character)})()
            scene = scene_type(game, SceneManager(game))
            scene.on_enter()

            for item in scene.collectibles[:scene.double_jump_goal]:
                scene.player.rect.topleft = (
                    item["rect"].x - scene.player.rect.width + 8,
                    item["rect"].y - scene.player.rect.height,
                )
                scene.player.on_ground = False
                scene.player.velocity.y = 0
                scene.update(0.1)

            if character == "Krrish":
                assert scene.double_jump_unlocked is True
                assert scene.player.can_double_jump is True
                scene.player.on_ground = True
                scene.player.handle_input(PressedKeys(pygame.K_SPACE))
                scene.player.handle_input(PressedKeys())
                scene.player.handle_input(PressedKeys(pygame.K_SPACE))
                assert scene.player.jump_count == 2
            else:
                assert scene.double_jump_unlocked is False
                assert scene.player.can_double_jump is False

    game.state.select_character("Jason")
    scene.on_enter()
    assert scene.player.can_double_jump is False
    assert scene.double_jump_unlocked is False


def test_jason_freeze_has_cooldown() -> None:
    character = JasonCharacter()

    assert character.ability_name == "freeze"
    assert character.cooldown == 5.0

    character.activate()
    assert character.is_active is True
    character.update(1.0)
    assert character.cooldown_remaining > 0.0


def test_progress_store_persists_local_data(tmp_path) -> None:
    database_path = tmp_path / "game-progress.sqlite3"
    store = DatabaseStore(str(database_path))
    created = store.save_progress(
        player_id="demo",
        character="Jason",
        map_name="Campus Track",
        score=1200,
        checkpoint=1,
        collected_count=5,
        collected_items=[0, 2, 7, 8, 11],
        completed=True,
    )
    store.close()

    reopened = DatabaseStore(str(database_path))
    recovered = reopened.get_progress(player_id="demo")

    assert created["character"] == "Jason"
    assert recovered["map_name"] == "Campus Track"
    assert recovered["score"] == 1200
    assert recovered["checkpoint"] == 1
    assert recovered["collected_count"] == 5
    assert recovered["collected_items"] == [0, 2, 7, 8, 11]
    assert recovered["completed"] == 1
    reopened.close()


def test_browser_progress_uses_local_storage(monkeypatch) -> None:
    from game.core import game as game_module

    class MemoryStorage:
        def __init__(self) -> None:
            self.values: dict[str, str] = {}

        def getItem(self, key: str) -> str | None:
            return self.values.get(key)

        def setItem(self, key: str, value: str) -> None:
            self.values[key] = value

    storage = MemoryStorage()
    monkeypatch.setattr(game_module.sys, "platform", "emscripten")
    monkeypatch.setitem(sys.modules, "platform", SimpleNamespace(window=SimpleNamespace(localStorage=storage)))

    browser_storage, initial = game_module._load_browser_progress()
    game = game_module.Game.__new__(game_module.Game)
    game.browser_storage = browser_storage
    game.progress_store = None
    game.saved_progress = initial
    game.state = GameState(selected_character="Krrish", current_map="Canteen")
    game.save_progress(checkpoint=1, collected_items=[0, 2, 5, 7])

    _, restored = game_module._load_browser_progress()
    assert restored["character"] == "Krrish"
    assert restored["map_name"] == "Canteen"
    assert restored["score"] == 400
    assert restored["checkpoint"] == 1
    assert restored["collected_items"] == [0, 2, 5, 7]


def test_progress_store_migrates_existing_schema(tmp_path) -> None:
    database_path = tmp_path / "legacy.sqlite3"
    connection = sqlite3.connect(database_path)
    connection.execute(
        "CREATE TABLE progress (player_id TEXT PRIMARY KEY, character TEXT NOT NULL, "
        "map_name TEXT NOT NULL, score INTEGER NOT NULL DEFAULT 0, "
        "updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
    )
    connection.execute(
        "INSERT INTO progress(player_id, character, map_name, score) VALUES(?, ?, ?, ?)",
        ("local", "Jason", "Canteen", 300),
    )
    connection.commit()
    connection.close()

    migrated = DatabaseStore(str(database_path))
    progress = migrated.get_progress(player_id="local")

    assert progress["character"] == "Jason"
    assert progress["map_name"] == "Canteen"
    assert progress["checkpoint"] == 0
    assert progress["collected_items"] == []
    assert progress["completed"] == 0
    migrated.close()


def test_gameplay_restores_checkpoint_and_collectibles_from_sqlite(tmp_path) -> None:
    from game.core.game import Game

    game = Game.__new__(Game)
    game.state = GameState(selected_character="Krrish")
    game.progress_store = DatabaseStore(str(tmp_path / "resume.sqlite3"))
    game.saved_progress = game.progress_store.save_progress(
        player_id="local",
        character="Krrish",
        map_name="Campus Track",
        score=400,
        checkpoint=1,
        collected_count=4,
        collected_items=[0, 1, 2, 3],
    )
    manager = SceneManager(game)
    track = SportsPrototypeScene(game, manager)
    manager.register("sports_prototype", track)

    manager.change_scene("sports_prototype")

    assert track.current_checkpoint == track.checkpoints[0]["spawn"]
    assert track.checkpoints[0]["active"] is True
    assert track.collected_count == 4
    assert [index for index, item in enumerate(track.collectibles) if item["collected"]] == [0, 1, 2, 3]
    assert track.double_jump_unlocked is True
    game.progress_store.close()


def test_goal_saves_completion_and_opens_completion_screen(monkeypatch) -> None:
    from game.core.game import Game

    monkeypatch.setattr(pygame.key, "get_pressed", lambda: PressedKeys())
    game = Game.__new__(Game)
    game.state = GameState(selected_character="Jason")
    game.progress_store = DatabaseStore(":memory:")
    game.saved_progress = game.progress_store.get_progress(player_id="local")
    manager = SceneManager(game)
    track = SportsPrototypeScene(game, manager)
    completion = CompletionScene(game, manager)
    manager.register("sports_prototype", track)
    manager.register("completion", completion)
    manager.change_scene("sports_prototype")
    track.player.rect.topleft = (track.goal_rect.x, track.goal_rect.y + 20)

    track.update(0)

    progress = game.progress_store.get_progress(player_id="local")
    assert manager.current_scene_name == "completion"
    assert game.state.game_completed is True
    assert progress["character"] == "Jason"
    assert progress["map_name"] == "Campus Track"
    assert progress["completed"] == 1
    game.progress_store.close()


def test_character_select_supports_jason_and_krrish() -> None:
    game = type("Game", (), {"state": GameState()})()
    scene = CharacterSelectScene(game, SceneManager(game))

    assert [item["name"] for item in scene.character_options] == ["Jason", "Krrish"]
    assert scene.character_options[0]["ability"] == "freeze"
    assert scene.character_options[1]["ability"] == "double_jump"
    assert all("map" not in item for item in scene.character_options)


def test_restaurant_level_has_distinct_layout() -> None:
    game = type("Game", (), {"state": GameState()})()
    scene = RestaurantScene(game, SceneManager(game))

    assert scene.level_name == "Canteen"
    assert len(scene.platforms) > 12
    assert scene.goal_rect.x > scene.checkpoints[-1]["spawn"][0]
    assert scene.platforms[0].x == 0


def test_campus_track_and_canteen_are_the_two_required_maps() -> None:
    game = type("Game", (), {"state": GameState()})()
    track = SportsPrototypeScene(game, SceneManager(game))
    canteen = RestaurantScene(game, SceneManager(game))

    assert track.level_name == "Campus Track"
    assert canteen.level_name == "Canteen"
