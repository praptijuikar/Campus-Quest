import asyncio

from game.config.settings import FPS
from game.core.game import Game


async def main() -> None:
    game = Game()
    try:
        while game.running:
            dt = game.clock.tick(FPS) / 1000.0
            game.handle_events()
            game.update(dt)
            game.draw()
            await asyncio.sleep(0)
    finally:
        if game.progress_store is not None:
            game.progress_store.close()


if __name__ == "__main__":
    asyncio.run(main())
