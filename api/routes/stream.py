import asyncio
import json
from typing import AsyncGenerator
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import redis.asyncio as aioredis
from api.config import REDIS_URL

router = APIRouter()


async def tick_generator(redis_url: str) -> AsyncGenerator[str, None]:
    r = aioredis.from_url(redis_url, decode_responses=True)
    try:
        while True:
            keys = await r.keys("market:*")
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
        tick_generator(REDIS_URL),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
