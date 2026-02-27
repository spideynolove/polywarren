import asyncio
import structlog
from aiogram import Bot, Dispatcher
from bot.config import TELEGRAM_TOKEN
from bot.handlers import router

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

log = structlog.get_logger()


async def main() -> None:
    if not TELEGRAM_TOKEN:
        log.error("telegram_token_missing")
        return

    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    log.info("telegram_bot_starting")
    await dp.start_polling(bot, allowed_updates=["message"])


if __name__ == "__main__":
    asyncio.run(main())
