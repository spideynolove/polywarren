import structlog
from shared.models import Market, Signal
from shared.schemas import Tick
from signal_engine.config import VOLATILITY_THRESHOLD, DRY_RUN
from signal_engine.grpc_client import place_order_for_signal

log = structlog.get_logger()


async def evaluate_signal(tick: Tick) -> Signal | None:
    market = await Market.get_or_none(symbol=tick.symbol, venue=tick.venue)
    if market is None:
        market = await Market.create(
            symbol=tick.symbol,
            venue=tick.venue,
            last_odds=tick.yes_price,
            condition_id=tick.condition_id,
        )
        return None

    if tick.condition_id and not market.condition_id:
        market.condition_id = tick.condition_id
        await market.save()

    if market.last_odds is None:
        await market.update_from_dict({"last_odds": tick.yes_price})
        await market.save()
        return None

    delta = abs(tick.yes_price - market.last_odds)
    await market.update_from_dict({"last_odds": tick.yes_price})
    await market.save()

    if delta >= VOLATILITY_THRESHOLD:
        signal = await Signal.create(
            market=market,
            trigger_type="volatility",
            value=delta,
        )
        log.info(
            "signal_triggered",
            symbol=tick.symbol,
            venue=tick.venue,
            delta=delta,
            threshold=VOLATILITY_THRESHOLD,
            signal_id=str(signal.id),
        )

        side = "yes" if tick.yes_price > (market.last_odds or 0.5) else "no"
        try:
            await place_order_for_signal(
                signal_id=str(signal.id),
                market_id=tick.symbol,
                venue=tick.venue,
                side=side,
                size=1.0,
                dry_run=DRY_RUN,
            )
        except Exception:
            log.exception("signal_order_failed", signal_id=str(signal.id))

        return signal

    return None
