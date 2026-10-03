from __future__ import annotations

import json
import sqlite3
from typing import Any


class DatabaseStore:
    def __init__(self, db_path: str = "game_progress.db") -> None:
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS progress (
                player_id TEXT PRIMARY KEY,
                character TEXT NOT NULL,
                map_name TEXT NOT NULL,
                score INTEGER NOT NULL DEFAULT 0,
                checkpoint INTEGER NOT NULL DEFAULT 0,
                collected_count INTEGER NOT NULL DEFAULT 0,
                collected_items TEXT NOT NULL DEFAULT '[]',
                completed INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        existing_columns = {
            row["name"] for row in self.connection.execute("PRAGMA table_info(progress)")
        }
        for name, declaration in (
            ("checkpoint", "INTEGER NOT NULL DEFAULT 0"),
            ("collected_count", "INTEGER NOT NULL DEFAULT 0"),
            ("collected_items", "TEXT NOT NULL DEFAULT '[]'"),
            ("completed", "INTEGER NOT NULL DEFAULT 0"),
        ):
            if name not in existing_columns:
                self.connection.execute(f"ALTER TABLE progress ADD COLUMN {name} {declaration}")
        self.connection.commit()

    def save_progress(
        self,
        *,
        player_id: str,
        character: str,
        map_name: str,
        score: int,
        checkpoint: int = 0,
        collected_count: int = 0,
        collected_items: list[int] | None = None,
        completed: bool = False,
    ) -> dict[str, Any]:
        self.connection.execute(
            """
            INSERT INTO progress(player_id, character, map_name, score, checkpoint, collected_count, collected_items, completed)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(player_id)
            DO UPDATE SET
                character = excluded.character,
                map_name = excluded.map_name,
                score = excluded.score,
                checkpoint = excluded.checkpoint,
                collected_count = excluded.collected_count,
                collected_items = excluded.collected_items,
                completed = excluded.completed,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                player_id,
                character,
                map_name,
                score,
                checkpoint,
                collected_count,
                json.dumps(collected_items or []),
                int(completed),
            ),
        )
        self.connection.commit()
        return self.get_progress(player_id=player_id)

    def get_progress(self, *, player_id: str) -> dict[str, Any]:
        row = self.connection.execute(
            "SELECT player_id, character, map_name, score, checkpoint, collected_count, collected_items, completed, updated_at "
            "FROM progress WHERE player_id = ?",
            (player_id,),
        ).fetchone()
        if row is None:
            return {
                "player_id": player_id,
                "character": "",
                "map_name": "",
                "score": 0,
                "checkpoint": 0,
                "collected_count": 0,
                "collected_items": [],
                "completed": 0,
                "updated_at": None,
            }
        progress = dict(row)
        progress["collected_items"] = json.loads(progress["collected_items"])
        return progress

    def ping(self) -> dict[str, Any]:
        return {"status": "ok", "db_path": self.db_path, "backend": "sqlite"}

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "DatabaseStore":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
