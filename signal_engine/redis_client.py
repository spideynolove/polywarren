import json
from typing import Any
import redis.asyncio as aioredis
from signal_engine.config import REDIS_URL, REDIS_MARKET_TTL


_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis


async def publish_market_batch(ticks: list[dict[str, Any]]) -> None:
    r = await get_redis()
    pipe = r.pipeline()
    for tick in ticks:
        key = f"market:{tick['venue']}:{tick['symbol']}"
        pipe.setex(key, REDIS_MARKET_TTL, json.dumps(tick))
    await pipe.execute()


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None
