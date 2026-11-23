"""Free public API fetchers for Steam/Epic prices (CheapShark) and Epic weekly free games."""

from typing import Any

import httpx

from src.game_radar.schemas import EpicFreeGame, GameDealSnapshot

CHEAPSHARK_GAMES_URL = "https://www.cheapshark.com/api/1.0/games"
CHEAPSHARK_DEALS_URL = "https://www.cheapshark.com/api/1.0/deals"
EPIC_FREE_GAMES_URL = (
    "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    "?locale=zh-Hant&country=TW&allowCountries=TW"
)

# CheapShark Store IDs: 1 = Steam, 25 = Epic Games Store
STORE_ID_MAP = {
    "1": "Steam",
    "25": "Epic Games",
}


def parse_epic_free_payload(payload: dict[str, Any]) -> list[EpicFreeGame]:
    """Parse Epic Games Store freeGamesPromotions JSON payload."""
    elements = (
        payload.get("data", {})
        .get("Catalog", {})
        .get("searchStore", {})
        .get("elements", [])
    )
    results: list[EpicFreeGame] = []
    for item in elements:
        promotions = item.get("promotions") or {}
        current_promos = promotions.get("promotionalOffers") or []
        upcoming_promos = promotions.get("upcomingPromotionalOffers") or []

        status = None
        start_date = None
        end_date = None

        if current_promos:
            for group in current_promos:
                for offer in group.get("promotionalOffers") or []:
                    pct = offer.get("discountSetting", {}).get("discountPercentage")
                    discount_price = item.get("price", {}).get("totalPrice", {}).get("discountPrice")
                    if pct == 0 or discount_price == 0:
                        status = "FREE_NOW"
                        start_date = offer.get("startDate")
                        end_date = offer.get("endDate")
                        break
                if status:
                    break

        if not status and upcoming_promos:
            for group in upcoming_promos:
                for offer in group.get("promotionalOffers") or []:
                    pct = offer.get("discountSetting", {}).get("discountPercentage")
                    if pct == 0:
                        status = "UPCOMING"
                        start_date = offer.get("startDate")
                        end_date = offer.get("endDate")
                        break
                if status:
                    break

        if not status:
            continue

        slug = item.get("productSlug") or item.get("urlSlug") or ""
        if not slug:
            mappings = item.get("catalogNs", {}).get("mappings") or item.get("offerMappings") or []
            if mappings and mappings[0].get("pageSlug"):
                slug = mappings[0]["pageSlug"]
        store_url = f"https://store.epicgames.com/zh-Hant/p/{slug}" if slug else "https://store.epicgames.com/zh-Hant/free-games"
        thumb_url = None
        for img in item.get("keyImages") or []:
            if img.get("url"):
                thumb_url = img["url"]
                break

        results.append(
            EpicFreeGame(
                title=item.get("title", "Unknown"),
                status=status,
                start_date=start_date,
                end_date=end_date,
                store_url=store_url,
                thumb_url=thumb_url,
            )
        )
    return results


DEFAULT_HEADERS = {
    "User-Agent": "GameDealRadar/1.0 (+https://github.com/game-deal-radar)",
    "Accept": "application/json",
}

FX_RATE_URL = "https://open.er-api.com/v6/latest/USD"
STEAM_FEATURED_URL = "https://store.steampowered.com/api/featuredcategories?cc=tw&l=tchinese"
STEAM_SEARCH_URL = "https://store.steampowered.com/api/storesearch/"
STEAM_CHART_SEARCH_URL = "https://store.steampowered.com/search/results/"


def search_steam_game_zh(query: str, timeout: float = 10.0) -> dict[str, Any] | None:
    """Search Steam Taiwan store in Traditional Chinese or English and return top match."""
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True, headers=DEFAULT_HEADERS) as client:
            resp = client.get(
                STEAM_SEARCH_URL,
                params={"term": query, "l": "tchinese", "cc": "tw"},
            )
            if resp.status_code == 200:
                items = resp.json().get("items") or []
                if items:
                    return items[0]
    except Exception:
        pass
    return None


def fetch_steam_charts(limit: int = 30, timeout: float = 15.0) -> dict[str, list[dict[str, Any]]]:
    """Fetch official Steam Taiwan Top Sellers and Specials (up to `limit` items each)."""
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=DEFAULT_HEADERS) as client:
        resp = client.get(STEAM_FEATURED_URL)
        resp.raise_for_status()
        data = resp.json()

    def _parse_featured(raw_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        parsed: list[dict[str, Any]] = []
        seen: set[int] = set()
        for item in raw_items:
            app_id = item.get("id")
            if app_id in seen:
                continue
            if app_id:
                seen.add(app_id)
            final_price = (item.get("final_price") or 0) / 100
            orig_price = (item.get("original_price") or 0) / 100
            parsed.append(
                {
                    "id": app_id,
                    "name": item.get("name", "Unknown"),
                    "discount_pct": int(item.get("discount_percent") or 0),
                    "final_price_twd": round(final_price),
                    "original_price_twd": round(orig_price),
                    "image": item.get("large_capsule_image") or item.get("small_capsule_image"),
                    "url": f"https://store.steampowered.com/app/{app_id}" if app_id else None,
                }
            )
        return parsed[:limit]

    top_sellers = _parse_featured(data.get("top_sellers", {}).get("items", []))
    specials = _parse_featured(data.get("specials", {}).get("items", []))
    new_releases = _parse_featured(data.get("new_releases", {}).get("items", []))
    coming_soon = _parse_featured(data.get("coming_soon", {}).get("items", []))

    # Extend top_sellers & specials with additional featured items if fewer than limit
    seen_top = {x["id"] for x in top_sellers}
    for extra in new_releases + specials:
        if len(top_sellers) >= limit:
            break
        if extra["id"] not in seen_top:
            top_sellers.append(extra)
            seen_top.add(extra["id"])

    seen_spec = {x["id"] for x in specials}
    for extra in top_sellers + coming_soon:
        if len(specials) >= limit:
            break
        if extra["discount_pct"] > 0 and extra["id"] not in seen_spec:
            specials.append(extra)
            seen_spec.add(extra["id"])

    return {
        "top_sellers": top_sellers,
        "specials": specials,
    }


def fetch_usd_to_twd_rate(default: float = 32.5, timeout: float = 8.0) -> float:
    """Fetch live USD -> TWD exchange rate (falls back to default if unavailable)."""
    try:
        with httpx.Client(timeout=timeout, headers=DEFAULT_HEADERS) as client:
            resp = client.get(FX_RATE_URL)
            if resp.status_code == 200:
                rate = resp.json().get("rates", {}).get("TWD")
                if rate:
                    return float(rate)
    except Exception:
        pass
    return default


def fetch_epic_free_games(timeout: float = 15.0) -> list[EpicFreeGame]:
    """Fetch current and upcoming free games from Epic Games Store."""
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=DEFAULT_HEADERS) as client:
        resp = client.get(EPIC_FREE_GAMES_URL)
        resp.raise_for_status()
        return parse_epic_free_payload(resp.json())


def parse_cheapshark_deals(
    query_title: str,
    deals_payload: list[dict[str, Any]],
    historical_low: float | None = None,
) -> list[GameDealSnapshot]:
    """Parse CheapShark deals response filtered to Steam and Epic Games."""
    seen_stores: set[str] = set()
    snapshots: list[GameDealSnapshot] = []

    for deal in deals_payload:
        store_id = str(deal.get("storeID", ""))
        if store_id not in STORE_ID_MAP or store_id in seen_stores:
            continue
        seen_stores.add(store_id)

        sale_price = float(deal.get("salePrice", 0.0))
        normal_price = float(deal.get("normalPrice", sale_price))
        savings = round(float(deal.get("savings", 0.0)))
        deal_id = deal.get("dealID")

        snapshots.append(
            GameDealSnapshot(
                query_title=query_title,
                matched_title=deal.get("title", query_title),
                store=STORE_ID_MAP[store_id],
                current_price_usd=sale_price,
                normal_price_usd=normal_price,
                historical_low_usd=historical_low,
                discount_pct=savings,
                deal_url=f"https://www.cheapshark.com/redirect?dealID={deal_id}" if deal_id else None,
                thumb_url=deal.get("thumb"),
            )
        )
    return snapshots


def fetch_deals_for_game(title: str, timeout: float = 15.0) -> list[GameDealSnapshot]:
    """Fetch Steam & Epic current prices and historical low for a game (supports Chinese & English)."""
    steam_match = search_steam_game_zh(title, timeout=timeout)
    steam_app_id = str(steam_match["id"]) if steam_match and steam_match.get("id") else None
    display_name = steam_match.get("name") if steam_match else title

    with httpx.Client(timeout=timeout, follow_redirects=True, headers=DEFAULT_HEADERS) as client:
        # 1. Fetch active deals on Steam (1) and Epic Games (25)
        params: dict[str, Any] = {"storeID": "1,25"}
        if steam_app_id:
            params["steamAppID"] = steam_app_id
        else:
            params["title"] = title

        deals_resp = client.get(CHEAPSHARK_DEALS_URL, params=params)
        deals_resp.raise_for_status()
        deals_payload = deals_resp.json()

        # Fallback to title search if steamAppID returned no deals
        if not deals_payload and steam_app_id:
            deals_resp = client.get(CHEAPSHARK_DEALS_URL, params={"title": title, "storeID": "1,25"})
            if deals_resp.status_code == 200:
                deals_payload = deals_resp.json()

        # 2. Lookup historical low via games endpoint (best-effort)
        historical_low: float | None = None
        try:
            game_id = deals_payload[0].get("gameID") if deals_payload else None
            if game_id:
                detail_resp = client.get(CHEAPSHARK_GAMES_URL, params={"id": game_id})
                if detail_resp.status_code == 200:
                    cheapest = detail_resp.json().get("cheapestPriceEver", {}).get("price")
                    if cheapest is not None:
                        historical_low = float(cheapest)
        except httpx.HTTPError:
            historical_low = None

        snapshots = parse_cheapshark_deals(title, deals_payload, historical_low=historical_low)

        # 3. Fallback to official Steam Store Search result (covers Software like Wallpaper Engine & new releases)
        if not snapshots and steam_match and steam_app_id:
            price_info = steam_match.get("price") or {}
            final_twd = (price_info.get("final") or 0) / 100
            initial_twd = (price_info.get("initial") or final_twd * 100) / 100
            fx_rate = fetch_usd_to_twd_rate()
            discount_pct = (
                round((1 - final_twd / initial_twd) * 100)
                if initial_twd > 0 and final_twd < initial_twd
                else 0
            )
            snapshots.append(
                GameDealSnapshot(
                    query_title=title,
                    matched_title=display_name or title,
                    store="Steam",
                    current_price_usd=round(final_twd / fx_rate, 2),
                    normal_price_usd=round(initial_twd / fx_rate, 2),
                    historical_low_usd=None,
                    discount_pct=discount_pct,
                    deal_url=f"https://store.steampowered.com/app/{steam_app_id}",
                    thumb_url=steam_match.get("tiny_image"),
                )
            )
            return snapshots

        # Preserve Chinese display name if user searched in Chinese
        if display_name and any("\u4e00" <= ch <= "\u9fff" for ch in title):
            for snap in snapshots:
                snap.matched_title = display_name
        return snapshots
