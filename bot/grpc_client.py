import grpc
import structlog
from bot.config import EXECUTION_GRPC_ADDR, DRY_RUN

log = structlog.get_logger()

_channel = None
_stub = None


def get_stub():
    global _channel, _stub
    if _stub is None:
        from bot import trading_pb2_grpc
        _channel = grpc.aio.insecure_channel(EXECUTION_GRPC_ADDR)
        _stub = trading_pb2_grpc.ExecutionServiceStub(_channel)
    return _stub


async def place_order(market_id: str, side: str, size: float) -> dict:
    from bot import trading_pb2
    stub = get_stub()
    side_val = trading_pb2.Side.YES if side.lower() == "yes" else trading_pb2.Side.NO
    resp = await stub.PlaceOrder(trading_pb2.OrderRequest(
        market_id=market_id,
        side=side_val,
        size=size,
        dry_run=DRY_RUN,
    ))
    return {
        "order_id": resp.order_id,
        "status": resp.status,
        "message": resp.message,
        "latency_ms": resp.latency_ms,
    }


async def get_pnl(venue: int = 0) -> dict:
    from bot import trading_pb2
    stub = get_stub()
    resp = await stub.GetPnL(trading_pb2.PnLRequest(venue=venue))
    return {"total_pnl": resp.total_pnl}
