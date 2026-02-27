import structlog
import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from bot.config import API_BASE_URL
from bot.grpc_client import place_order, get_pnl

log = structlog.get_logger()
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "polywarren bot\n\n"
        "/status — current positions\n"
        "/pnl — PnL summary\n"
        "/buy <market> <yes|no> <size> — place dry-run order"
    )


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{API_BASE_URL}/positions")
            resp.raise_for_status()
            positions = resp.json()
        if not positions:
            await message.answer("No open positions.")
            return
        lines = ["*Open Positions*\n"]
        for p in positions[:10]:
            lines.append(
                f"• `{p['market_id'][:8]}...` {p['venue']} {p['side'].upper()} "
                f"{p['size']} @ {p['entry_price']:.3f}"
            )
        await message.answer("\n".join(lines), parse_mode="Markdown")
    except Exception as exc:
        log.exception("status_command_error", error=str(exc))
        await message.answer("Error fetching positions.")


@router.message(Command("pnl"))
async def cmd_pnl(message: Message) -> None:
    try:
        result = await get_pnl()
        pnl_val = result.get("total_pnl", 0.0)
        sign = "+" if pnl_val >= 0 else ""
        await message.answer(f"*Total PnL:* `{sign}{pnl_val:.4f}`", parse_mode="Markdown")
    except Exception as exc:
        log.exception("pnl_command_error", error=str(exc))
        await message.answer("Error fetching PnL.")


@router.message(Command("buy"))
async def cmd_buy(message: Message) -> None:
    if not message.text:
        await message.answer("Usage: /buy <market_id> <yes|no> <size>")
        return

    parts = message.text.split()
    if len(parts) != 4:
        await message.answer("Usage: /buy <market_id> <yes|no> <size>")
        return

    _, market_id, side, size_str = parts
    if side.lower() not in ("yes", "no"):
        await message.answer("Side must be yes or no.")
        return

    try:
        size = float(size_str)
    except ValueError:
        await message.answer("Size must be a number.")
        return

    try:
        result = await place_order(market_id, side, size)
        await message.answer(
            f"*Dry-run order submitted*\n"
            f"ID: `{result['order_id']}`\n"
            f"Status: {result['message']}\n"
            f"Latency: {result['latency_ms']}ms",
            parse_mode="Markdown",
        )
    except Exception as exc:
        log.exception("buy_command_error", error=str(exc))
        await message.answer("Error placing order.")
