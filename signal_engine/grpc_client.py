import time
import grpc
import structlog
from signal_engine.config import EXECUTION_GRPC_ADDR

log = structlog.get_logger()

_channel = None
_stub = None


def get_stub():
    global _channel, _stub
    if _stub is None:
        from signal_engine import trading_pb2_grpc
        _channel = grpc.aio.insecure_channel(EXECUTION_GRPC_ADDR)
        _stub = trading_pb2_grpc.ExecutionServiceStub(_channel)
    return _stub


async def place_order_for_signal(
    signal_id: str,
    market_id: str,
    venue: str,
    side: str = "yes",
    size: float = 1.0,
    dry_run: bool = True,
) -> dict:
    from signal_engine import trading_pb2

    stub = get_stub()
    venue_val = trading_pb2.Venue.POLYMARKET if venue == "polymarket" else trading_pb2.Venue.KALSHI
    side_val = trading_pb2.Side.YES if side.lower() == "yes" else trading_pb2.Side.NO

    resp = await stub.PlaceOrder(trading_pb2.OrderRequest(
        signal_id=signal_id,
        market_id=market_id,
        venue=venue_val,
        side=side_val,
        size=size,
        dry_run=dry_run,
        signal_received_at=int(time.time() * 1000),
    ))
    log.info(
        "signal_order_placed",
        signal_id=signal_id,
        order_id=resp.order_id,
        status=resp.status,
        latency_ms=resp.latency_ms,
    )
    return {
        "order_id": resp.order_id,
        "status": resp.status,
        "message": resp.message,
        "latency_ms": resp.latency_ms,
    }
