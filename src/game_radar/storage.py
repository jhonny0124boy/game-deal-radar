"""DuckDB storage layer for historical game price snapshots and Epic free games."""

from pathlib import Path
from typing import Iterable

import duckdb

from src.game_radar.schemas import EpicFreeGame, GameDealSnapshot


class DealRepository:
    """Persist and query game deals and Epic free games in DuckDB."""

    def __init__(self, db_path: str | Path = "data/game_radar.duckdb") -> None:
        self.db_path = str(db_path)
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = duckdb.connect(self.db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS price_snapshots (
                query_title VARCHAR NOT NULL,
                matched_title VARCHAR NOT NULL,
                store VARCHAR NOT NULL,
                current_price_usd DOUBLE NOT NULL,
                normal_price_usd DOUBLE NOT NULL,
                historical_low_usd DOUBLE,
                discount_pct INTEGER NOT NULL,
                deal_url VARCHAR,
                thumb_url VARCHAR,
                fetched_at TIMESTAMPTZ NOT NULL
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS epic_free_games (
                title VARCHAR PRIMARY KEY,
                status VARCHAR NOT NULL,
                start_date VARCHAR,
                end_date VARCHAR,
                store_url VARCHAR,
                thumb_url VARCHAR,
                fetched_at TIMESTAMPTZ NOT NULL
            )
            """
        )

    def insert_price_snapshots(self, snapshots: Iterable[GameDealSnapshot]) -> int:
        count = 0
        for snap in snapshots:
            self.conn.execute(
                """
                INSERT INTO price_snapshots VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    snap.query_title,
                    snap.matched_title,
                    snap.store,
                    snap.current_price_usd,
                    snap.normal_price_usd,
                    snap.historical_low_usd,
                    snap.discount_pct,
                    snap.deal_url,
                    snap.thumb_url,
                    snap.fetched_at,
                ],
            )
            count += 1
        return count

    def replace_epic_free_games(self, games: Iterable[EpicFreeGame]) -> int:
        self.conn.execute("DELETE FROM epic_free_games")
        count = 0
        for game in games:
            self.conn.execute(
                """
                INSERT INTO epic_free_games VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (title) DO UPDATE SET
                    status = EXCLUDED.status,
                    start_date = EXCLUDED.start_date,
                    end_date = EXCLUDED.end_date,
                    store_url = EXCLUDED.store_url,
                    thumb_url = EXCLUDED.thumb_url,
                    fetched_at = EXCLUDED.fetched_at
                """,
                [
                    game.title,
                    game.status,
                    game.start_date,
                    game.end_date,
                    game.store_url,
                    game.thumb_url,
                    game.fetched_at,
                ],
            )
            count += 1
        return count

    def get_latest_deals(self) -> list[dict]:
        """Return the latest price snapshot for each (query_title, store) pair."""
        rows = self.conn.execute(
            """
            SELECT
                query_title, matched_title, store,
                current_price_usd, normal_price_usd, historical_low_usd,
                discount_pct, deal_url, thumb_url, fetched_at
            FROM (
                SELECT *,
                    ROW_NUMBER() OVER (
                        PARTITION BY query_title, store
                        ORDER BY fetched_at DESC
                    ) AS rn
                FROM price_snapshots
            )
            WHERE rn = 1
            ORDER BY query_title, current_price_usd ASC
            """
        ).fetchall()
        cols = [
            "query_title",
            "matched_title",
            "store",
            "current_price_usd",
            "normal_price_usd",
            "historical_low_usd",
            "discount_pct",
            "deal_url",
            "thumb_url",
            "fetched_at",
        ]
        return [dict(zip(cols, r)) for r in rows]

    def get_epic_free_games(self) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT title, status, start_date, end_date, store_url, thumb_url, fetched_at
            FROM epic_free_games
            ORDER BY CASE WHEN status = 'FREE_NOW' THEN 0 ELSE 1 END, title
            """
        ).fetchall()
        cols = ["title", "status", "start_date", "end_date", "store_url", "thumb_url", "fetched_at"]
        return [dict(zip(cols, r)) for r in rows]

    def get_price_history(self, query_title: str, store: str) -> list[dict]:
        """Return chronological price snapshots for a specific game and store."""
        rows = self.conn.execute(
            """
            SELECT fetched_at, current_price_usd, normal_price_usd, discount_pct
            FROM price_snapshots
            WHERE query_title = ? AND store = ?
            ORDER BY fetched_at ASC
            """,
            [query_title, store],
        ).fetchall()
        cols = ["fetched_at", "current_price_usd", "normal_price_usd", "discount_pct"]
        return [dict(zip(cols, r)) for r in rows]

    def delete_game(self, query_title: str) -> None:
        """Delete all price snapshots for a game."""
        self.conn.execute("DELETE FROM price_snapshots WHERE query_title = ?", [query_title])

    def get_last_sync_time(self):
        """Return the latest fetched_at timestamp across price_snapshots and epic_free_games."""
        row = self.conn.execute(
            """
            SELECT MAX(ts) FROM (
                SELECT MAX(fetched_at) AS ts FROM price_snapshots
                UNION ALL
                SELECT MAX(fetched_at) AS ts FROM epic_free_games
            )
            """
        ).fetchone()
        return row[0] if row else None

    def close(self) -> None:
        self.conn.close()
