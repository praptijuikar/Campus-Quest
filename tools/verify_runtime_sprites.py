import os

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame

from game.characters import get_character_definition
from game.core.game import Game
from game.entities.player import Player

game = Game()
surface = pygame.Surface((400, 240))

for name in ["Jason", "Krrish"]:
    player = Player(100, 100)
    player.set_character(get_character_definition(name))
    player.draw(surface, 0)
    print(f"{name} sprite-ok")

game.draw()
game.quit()
pygame.quit()
print("game-start-ok")
