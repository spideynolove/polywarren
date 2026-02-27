import asyncio
import structlog
from shared.db import init_db, close_db
from signal_engine.redis_client import close_redis
from signal_engine.consumers import consume_polymarket, consume_kalshi

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

log = structlog.get_logger()


async def main() -> None:
    log.info("signal_engine_starting")
    await init_db()
    try:
        await asyncio.gather(
            consume_polymarket(),
            consume_kalshi(),
        )
    finally:
        await close_db()
        await close_redis()


if __name__ == "__main__":
    asyncio.run(main())
