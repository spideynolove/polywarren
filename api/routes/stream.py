import asyncio
import json
from typing import AsyncGenerator
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import redis.asyncio as aioredis

router = APIRouter()
_SCAN_COUNT = 100

_pool: aioredis.ConnectionPool | None = None


def init_redis_pool(redis_url: str) -> None:
    global _pool
    _pool = aioredis.ConnectionPool.from_url(redis_url, decode_responses=True)


async def close_redis_pool() -> None:
    global _pool
    if _pool:
        await _pool.aclose()
        _pool = None


async def tick_generator() -> AsyncGenerator[str, None]:
    r = aioredis.Redis(connection_pool=_pool)
    try:
        while True:
            keys: list[str] = []
            cursor = 0
            while True:
                cursor, batch = await r.scan(cursor, match="market:*", count=_SCAN_COUNT)
                keys.extend(batch)
                if cursor == 0:
                    break
                if len(keys) >= 50:
                    break
            if keys:
                pipe = r.pipeline()
                for key in keys[:50]:
                    pipe.get(key)
                values = await pipe.execute()
                ticks = [json.loads(v) for v in values if v]
                yield f"data: {json.dumps(ticks)}\n\n"
            await asyncio.sleep(1)
    finally:
        await r.aclose()


@router.get("/stream/ticks")
async def stream_ticks(request: Request) -> StreamingResponse:
    return StreamingResponse(
        tick_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
