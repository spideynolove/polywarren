import asyncio
import json
import structlog
import aiohttp
from signal_engine.normalizer import normalize_polymarket, normalize_kalshi
from signal_engine.detector import evaluate_signal
from signal_engine.redis_client import publish_market_batch
from signal_engine.config import POLYMARKET_WS_URL, KALSHI_WS_URL, KALSHI_API_KEY

log = structlog.get_logger()

POLYMARKET_SUBSCRIBE = {
    "type": "subscribe",
    "channel": "price_change",
}

KALSHI_SUBSCRIBE = {
    "id": 1,
    "cmd": "subscribe",
    "params": {"channels": ["ticker"]},
}


async def consume_polymarket() -> None:
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect(POLYMARKET_WS_URL) as ws:
                    await ws.send_json(POLYMARKET_SUBSCRIBE)
                    log.info("polymarket_ws_connected")
                    batch: list[dict] = []
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            events = data if isinstance(data, list) else [data]
                            for event in events:
                                tick = normalize_polymarket(event)
                                if tick:
                                    batch.append(tick.model_dump(mode="json"))
                                    await evaluate_signal(tick)
                            if batch:
                                await publish_market_batch(batch)
                                batch.clear()
                        elif msg.type in (aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSED):
                            break
        except Exception:
            log.exception("polymarket_ws_error", backoff=5)
            await asyncio.sleep(5)


async def consume_kalshi() -> None:
    headers = {}
    if KALSHI_API_KEY:
        headers["Authorization"] = f"Bearer {KALSHI_API_KEY}"

    while True:
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.ws_connect(KALSHI_WS_URL) as ws:
                    await ws.send_json(KALSHI_SUBSCRIBE)
                    log.info("kalshi_ws_connected")
                    batch: list[dict] = []
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            markets = data.get("msg", {}).get("markets", [])
                            for m in markets:
                                tick = normalize_kalshi(m)
                                if tick:
                                    batch.append(tick.model_dump(mode="json"))
                                    await evaluate_signal(tick)
                            if batch:
                                await publish_market_batch(batch)
                                batch.clear()
                        elif msg.type in (aiohttp.WSMsgType.ERROR, aiohttp.WSMsgType.CLOSED):
                            break
        except Exception:
            log.exception("kalshi_ws_error", backoff=5)
            await asyncio.sleep(5)
