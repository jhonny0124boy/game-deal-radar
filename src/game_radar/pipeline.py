"""Sync pipeline for Steam/Epic watchlist deals and Epic weekly free games."""

import json
from pathlib import Path

from src.game_radar.fetchers import fetch_deals_for_game, fetch_epic_free_games
from src.game_radar.schemas import WatchlistItem
from src.game_radar.storage import DealRepository


def load_watchlist(path: Path) -> list[WatchlistItem]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [WatchlistItem.model_validate(item) for item in raw]


def save_watchlist(path: Path, items: list[WatchlistItem]) -> None:
    payload = [item.model_dump() for item in items]
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def run_sync(
    watchlist_path: Path = Path("watchlist.json"),
    db_path: Path = Path("data/game_radar.duckdb"),
) -> dict[str, int]:
    """Fetch Epic free games and watchlist deals, then persist into DuckDB."""
    watchlist = load_watchlist(watchlist_path)
    all_snapshots = []
    for item in watchlist:
        if not item.enabled:
            continue
        all_snapshots.extend(fetch_deals_for_game(item.title))

    epic_free = fetch_epic_free_games()

    repo = DealRepository(db_path=db_path)
    try:
        saved_deals = repo.insert_price_snapshots(all_snapshots)
        saved_free = repo.replace_epic_free_games(epic_free)
    finally:
        repo.close()

    return {"deals_saved": saved_deals, "epic_free_saved": saved_free}


if __name__ == "__main__":
    summary = run_sync()
    print(
        f"同步完成！已寫入 {summary['deals_saved']} 筆價格快照、"
        f"{summary['epic_free_saved']} 筆 Epic 限免資訊。"
    )
