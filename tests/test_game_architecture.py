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


def test_character_select_starts_sports_prototype() -> None:
    game = type("Game", (), {"state": GameState()})()
    manager = SceneManager(game)
    select_scene = CharacterSelectScene(game, manager)
    sports_scene = DummyScene("sports_prototype")

    manager.register("character_select", select_scene)
    manager.register("sports_prototype", sports_scene)
    manager.change_scene("character_select")

    select_scene.confirm_selection()

    assert game.state.selected_character == "Krrish"
    assert game.state.current_map == "Campus Track"
    assert manager.current_scene_name == "sports_prototype"


def test_character_select_starts_restaurant_map() -> None:
    game = type("Game", (), {"state": GameState()})()
    manager = SceneManager(game)
    select_scene = CharacterSelectScene(game, manager)
    restaurant_scene = RestaurantScene(game, manager)

    manager.register("character_select", select_scene)
    manager.register("restaurant", restaurant_scene)
    manager.change_scene("character_select")
    select_scene.start_restaurant()

    assert manager.current_scene_name == "restaurant"
    assert game.state.current_map == "Canteen"


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

    player.enable_double_jump()

    assert player.can_double_jump is True
    assert player.jump_count == 1


def test_jason_freeze_has_cooldown() -> None:
    character = JasonCharacter()

    assert character.ability_name == "freeze"
    assert character.cooldown == 5.0

    character.activate()
    assert character.is_active is True
    character.update(1.0)
    assert character.cooldown_remaining > 0.0


def test_progress_store_persists_local_data() -> None:
    store = DatabaseStore(":memory:")
    created = store.save_progress(player_id="demo", character="Jason", map_name="Campus Track", score=1200)

    assert created["character"] == "Jason"
    assert store.get_progress(player_id="demo")["map_name"] == "Campus Track"


def test_character_select_supports_jason_and_krrish() -> None:
    game = type("Game", (), {"state": GameState()})()
    scene = CharacterSelectScene(game, SceneManager(game))

    assert [item["name"] for item in scene.character_options] == ["Jason", "Krrish"]
    assert scene.character_options[0]["ability"] == "freeze"
    assert scene.character_options[1]["ability"] == "double_jump"


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
