from datetime import datetime, timezone
from typing import Any
from shared.schemas import Tick


def normalize_polymarket(raw: dict[str, Any]) -> Tick | None:
    try:
        asset_id = raw.get("asset_id", "")
        yes_price = float(raw.get("price", 0))
        return Tick(
            symbol=asset_id,
            venue="polymarket",
            yes_price=yes_price,
            no_price=round(1.0 - yes_price, 6),
            timestamp=datetime.fromtimestamp(
                float(raw.get("timestamp", 0)) / 1e9, tz=timezone.utc
            ) if raw.get("timestamp") else datetime.now(tz=timezone.utc),
            volume=float(raw.get("size", 0)) if raw.get("size") else None,
            condition_id=raw.get("condition_id"),
        )
    except (KeyError, ValueError, TypeError):
        return None


def normalize_kalshi(raw: dict[str, Any]) -> Tick | None:
    try:
        ticker = raw.get("market_ticker", "")
        yes_price = float(raw.get("yes_price", 0)) / 100.0
        return Tick(
            symbol=ticker,
            venue="kalshi",
            yes_price=yes_price,
            no_price=round(1.0 - yes_price, 6),
            timestamp=datetime.now(tz=timezone.utc),
            volume=float(raw.get("volume", 0)) if raw.get("volume") else None,
        )
    except (KeyError, ValueError, TypeError):
        return None
