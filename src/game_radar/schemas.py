"""Pydantic data models for Game Deal Radar."""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class WatchlistItem(BaseModel):
    """A game tracked by the user."""

    title: str = Field(..., min_length=1, description="遊戲名稱")
    target_price_usd: float = Field(default=0.0, ge=0.0, description="目標價格 (USD)")
    enabled: bool = Field(default=True, description="是否啟用追蹤")


class GameDealSnapshot(BaseModel):
    """Normalized price snapshot from CheapShark (Steam & Epic)."""

    query_title: str
    matched_title: str
    store: str  # "Steam" or "Epic Games"
    current_price_usd: float
    normal_price_usd: float
    historical_low_usd: Optional[float] = None
    discount_pct: int = 0
    deal_url: Optional[str] = None
    thumb_url: Optional[str] = None
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EpicFreeGame(BaseModel):
    """Free or upcoming free game from Epic Games Store."""

    title: str
    status: str  # "FREE_NOW" or "UPCOMING"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    store_url: Optional[str] = None
    thumb_url: Optional[str] = None
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
