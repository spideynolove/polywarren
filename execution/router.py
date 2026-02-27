import structlog
import httpx
from execution.config import POLYMARKET_KEY, KALSHI_KEY

log = structlog.get_logger()


async def route_polymarket(market_id: str, side: str, size: float, limit_price: float) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://clob.polymarket.com/order",
            headers={"Authorization": f"Bearer {POLYMARKET_KEY}"},
            json={
                "tokenID": market_id,
                "side": side.upper(),
                "price": limit_price,
                "size": size,
                "orderType": "GTC",
            },
            timeout=5.0,
        )
        resp.raise_for_status()
        return resp.json()


async def route_kalshi(market_id: str, side: str, size: float, limit_price: float) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://trading-api.kalshi.com/trade-api/v2/portfolio/orders",
            headers={"Authorization": f"Bearer {KALSHI_KEY}"},
            json={
                "ticker": market_id,
                "side": side.lower(),
                "count": int(size),
                "yes_price": int(limit_price * 100) if side.lower() == "yes" else None,
                "no_price": int(limit_price * 100) if side.lower() == "no" else None,
                "type": "limit",
            },
            timeout=5.0,
        )
        resp.raise_for_status()
        return resp.json()
