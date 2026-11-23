"""Offline unit tests for Game Deal Radar."""

from src.game_radar.fetchers import parse_cheapshark_deals, parse_epic_free_payload
from src.game_radar.storage import DealRepository


def test_parse_epic_free_payload() -> None:
    fake_payload = {
        "data": {
            "Catalog": {
                "searchStore": {
                    "elements": [
                        {
                            "title": "Demo Free Game",
                            "productSlug": "demo-free-game",
                            "keyImages": [{"url": "https://example.com/img.jpg"}],
                            "promotions": {
                                "promotionalOffers": [
                                    {
                                        "promotionalOffers": [
                                            {
                                                "startDate": "2026-11-20T16:00:00.000Z",
                                                "endDate": "2026-11-27T16:00:00.000Z",
                                                "discountSetting": {"discountPercentage": 0},
                                            }
                                        ]
                                    }
                                ]
                            },
                        }
                    ]
                }
            }
        }
    }
    games = parse_epic_free_payload(fake_payload)
    assert len(games) == 1
    assert games[0].title == "Demo Free Game"
    assert games[0].status == "FREE_NOW"


def test_parse_cheapshark_and_storage() -> None:
    fake_deals = [
        {
            "storeID": "1",
            "title": "Hollow Knight",
            "salePrice": "7.49",
            "normalPrice": "14.99",
            "savings": "50.03",
            "dealID": "abc123",
        },
        {
            "storeID": "25",
            "title": "Hollow Knight",
            "salePrice": "14.99",
            "normalPrice": "14.99",
            "savings": "0.0",
            "dealID": "xyz789",
        },
    ]
    snaps = parse_cheapshark_deals("Hollow Knight", fake_deals, historical_low=7.49)
    assert len(snaps) == 2

    repo = DealRepository(":memory:")
    try:
        assert repo.insert_price_snapshots(snaps) == 2
        latest = repo.get_latest_deals()
        assert len(latest) == 2
        assert latest[0]["store"] == "Steam"
        assert latest[0]["current_price_usd"] == 7.49
    finally:
        repo.close()
