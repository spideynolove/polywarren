import asyncio
import httpx
import structlog
from fastapi import APIRouter
from tortoise import connections
import redis.asyncio as aioredis
from api.config import REDIS_URL, POLYMARKET_API_URL, KALSHI_API_URL

router = APIRouter()
log = structlog.get_logger()


async def _check_postgres() -> str:
    try:
        conn = connections.get("default")
        await conn.execute_query("SELECT 1")
        return "ok"
    except Exception as exc:
        log.error("healthz_postgres_fail", error=str(exc))
        return "error"


async def _check_redis() -> str:
    try:
        r = aioredis.from_url(REDIS_URL, socket_connect_timeout=2)
        await r.ping()
        await r.aclose()
        return "ok"
    except Exception as exc:
        log.error("healthz_redis_fail", error=str(exc))
        return "error"


async def _check_exchange(name: str, url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(url)
            return "ok" if resp.status_code < 500 else "error"
    except Exception as exc:
        log.error("healthz_exchange_fail", exchange=name, error=str(exc))
        return "error"


@router.get("/healthz")
async def healthz() -> dict:
    postgres, redis_status, polymarket, kalshi = await asyncio.gather(
        _check_postgres(),
        _check_redis(),
        _check_exchange("polymarket", POLYMARKET_API_URL),
        _check_exchange("kalshi", KALSHI_API_URL),
    )
    overall = "ok" if all(s == "ok" for s in [postgres, redis_status, polymarket, kalshi]) else "degraded"
    return {
        "status": overall,
        "postgres": postgres,
        "redis": redis_status,
        "polymarket": polymarket,
        "kalshi": kalshi,
    }
