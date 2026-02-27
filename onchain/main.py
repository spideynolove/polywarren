import asyncio
import structlog
from shared.db import init_db, close_db
from onchain.watcher import watch_resolutions

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

log = structlog.get_logger()


async def main() -> None:
    log.info("onchain_watcher_starting")
    await init_db()
    try:
        await watch_resolutions()
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
