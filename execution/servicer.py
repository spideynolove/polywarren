import time
import uuid
import structlog
from datetime import datetime, timezone

from execution.circuit_breaker import circuit_breaker
from execution.router import route_polymarket, route_kalshi
from execution.config import DRY_RUN
from shared.models import Market, Order, Position, PnLSnapshot

log = structlog.get_logger()

VENUE_MAP = {1: "polymarket", 2: "kalshi"}
SIDE_MAP = {1: "yes", 2: "no"}
STATUS_DRY_RUN = 1
STATUS_PENDING = 2
STATUS_FILLED = 3
STATUS_REJECTED = 4
STATUS_HALTED = 5


async def _check_max_loss(venue: str):
    from execution import trading_pb2

    snapshots = await PnLSnapshot.filter(venue=venue).order_by("-timestamp").limit(1)
    current_pnl = snapshots[0].value if snapshots else 0.0
    if not circuit_breaker.check_loss_threshold(current_pnl):
        return trading_pb2.OrderResponse(
            order_id=str(uuid.uuid4()),
            status=STATUS_HALTED,
            message=f"max-loss circuit breaker: pnl={current_pnl}",
            order_sent_at=int(time.time() * 1000),
            latency_ms=0,
        )
    return None


async def _update_position(market_id: str, venue: str, side: str, size: float, price: float) -> None:
    market = await Market.get_or_none(symbol=market_id, venue=venue)
    if not market:
        market = await Market.get_or_none(id=market_id)
    if not market:
        return

    existing = await Position.filter(market=market, venue=venue, side=side).first()
    if existing:
        new_size = existing.size + size
        avg_price = (existing.entry_price * existing.size + price * size) / new_size
        existing.size = new_size
        existing.entry_price = avg_price
        await existing.save()
    else:
        await Position.create(
            market=market,
            venue=venue,
            side=side,
            size=size,
            entry_price=price,
        )


async def _create_pnl_snapshot(venue: str, market_id: str, side: str, size: float) -> None:
    market = await Market.get_or_none(symbol=market_id, venue=venue)
    if not market:
        market = await Market.get_or_none(id=market_id)

    current_price = market.last_odds if market and market.last_odds else 0.5

    positions = await Position.filter(venue=venue)
    total_pnl = 0.0
    for pos in positions:
        pos_market = await Market.get_or_none(id=pos.market_id)
        pos_price = pos_market.last_odds if pos_market and pos_market.last_odds else 0.5
        if pos.side == "yes":
            total_pnl += (pos_price - pos.entry_price) * pos.size
        else:
            total_pnl += (pos.entry_price - pos_price) * pos.size

    await PnLSnapshot.create(venue=venue, value=total_pnl)


async def _close_positions_for_market(market: Market) -> None:
    positions = await Position.filter(market=market)
    for pos in positions:
        price = market.last_odds if market.last_odds else 1.0
        if pos.side == "yes":
            pnl = (price - pos.entry_price) * pos.size
        else:
            pnl = (pos.entry_price - price) * pos.size
        await PnLSnapshot.create(venue=pos.venue, value=pnl)
        await pos.delete()
        log.info("position_closed", market_id=str(market.id), side=pos.side, pnl=pnl)


class ExecutionServicer:
    async def PlaceOrder(self, request, context):
        from execution import trading_pb2

        signal_received_at = request.signal_received_at or int(time.time() * 1000)
        venue = VENUE_MAP.get(request.venue, "polymarket")
        side = SIDE_MAP.get(request.side, "yes")
        dry_run = request.dry_run or DRY_RUN

        log.info(
            "order_received",
            signal_id=request.signal_id,
            market_id=request.market_id,
            venue=venue,
            side=side,
            size=request.size,
            dry_run=dry_run,
        )

        if circuit_breaker.halted:
            return trading_pb2.OrderResponse(
                order_id=str(uuid.uuid4()),
                status=STATUS_HALTED,
                message="circuit breaker active",
                order_sent_at=int(time.time() * 1000),
                latency_ms=0,
            )

        if not await circuit_breaker.check_rate_limit(venue):
            return trading_pb2.OrderResponse(
                order_id=str(uuid.uuid4()),
                status=STATUS_REJECTED,
                message="rate limit exceeded",
                order_sent_at=int(time.time() * 1000),
                latency_ms=0,
            )

        halt_resp = await _check_max_loss(venue)
        if halt_resp:
            return halt_resp

        order_sent_at = int(time.time() * 1000)

        if dry_run:
            confirmation_at = int(time.time() * 1000)
            latency_ms = confirmation_at - signal_received_at
            order = await Order.create(
                venue=venue,
                side=side,
                size=request.size,
                status="dry_run",
                sent_at=datetime.fromtimestamp(order_sent_at / 1000, tz=timezone.utc),
                confirmed_at=datetime.fromtimestamp(confirmation_at / 1000, tz=timezone.utc),
                latency_ms=latency_ms,
            )

            market = await Market.get_or_none(symbol=request.market_id, venue=venue)
            price = market.last_odds if market and market.last_odds else 0.5
            await _update_position(request.market_id, venue, side, request.size, price)
            await _create_pnl_snapshot(venue, request.market_id, side, request.size)

            log.info(
                "dry_run_order",
                order_id=str(order.id),
                latency_ms=latency_ms,
                venue=venue,
                symbol=request.market_id,
            )
            return trading_pb2.OrderResponse(
                order_id=str(order.id),
                status=STATUS_DRY_RUN,
                message="dry run — no real order placed",
                order_sent_at=order_sent_at,
                confirmation_at=confirmation_at,
                latency_ms=latency_ms,
            )

        try:
            if venue == "polymarket":
                result = await route_polymarket(request.market_id, side, request.size, request.limit_price)
            else:
                result = await route_kalshi(request.market_id, side, request.size, request.limit_price)

            confirmation_at = int(time.time() * 1000)
            latency_ms = confirmation_at - signal_received_at
            order = await Order.create(
                venue=venue,
                side=side,
                size=request.size,
                status="filled",
                sent_at=datetime.fromtimestamp(order_sent_at / 1000, tz=timezone.utc),
                confirmed_at=datetime.fromtimestamp(confirmation_at / 1000, tz=timezone.utc),
                latency_ms=latency_ms,
            )

            market = await Market.get_or_none(symbol=request.market_id, venue=venue)
            price = market.last_odds if market and market.last_odds else request.limit_price or 0.5
            await _update_position(request.market_id, venue, side, request.size, price)
            await _create_pnl_snapshot(venue, request.market_id, side, request.size)

            log.info(
                "order_filled",
                order_id=str(order.id),
                latency_ms=latency_ms,
                venue=venue,
                symbol=request.market_id,
                result=result,
            )
            return trading_pb2.OrderResponse(
                order_id=str(order.id),
                status=STATUS_FILLED,
                message="order filled",
                order_sent_at=order_sent_at,
                confirmation_at=confirmation_at,
                latency_ms=latency_ms,
            )
        except Exception as exc:
            log.exception("order_failed", venue=venue, market_id=request.market_id, error=str(exc))
            return trading_pb2.OrderResponse(
                order_id=str(uuid.uuid4()),
                status=STATUS_REJECTED,
                message=str(exc),
                order_sent_at=order_sent_at,
                latency_ms=int(time.time() * 1000) - signal_received_at,
            )

    async def GetPosition(self, request, context):
        from execution import trading_pb2

        venue = VENUE_MAP.get(request.venue, "polymarket")
        market = await Market.get_or_none(symbol=request.market_id, venue=venue)
        if not market:
            return trading_pb2.PositionResponse()
        pos = await Position.filter(market=market, venue=venue).first()
        if not pos:
            return trading_pb2.PositionResponse()
        return trading_pb2.PositionResponse(
            market_id=str(market.id),
            venue=request.venue,
            side=1 if pos.side == "yes" else 2,
            size=pos.size,
            entry_price=pos.entry_price,
        )

    async def GetPnL(self, request, context):
        from execution import trading_pb2

        venue = VENUE_MAP.get(request.venue, "polymarket")
        snapshots = await PnLSnapshot.filter(venue=venue).order_by("-timestamp").limit(1)
        total = snapshots[0].value if snapshots else 0.0
        return trading_pb2.PnLResponse(total_pnl=total)

    async def Health(self, request, context):
        from execution import trading_pb2

        return trading_pb2.HealthResponse(ok=True, message="ok")
