import asyncio
import time
import grpc
import structlog
from web3 import AsyncWeb3
from web3.providers import WebSocketProvider
from onchain.config import POLYGON_RPC, POLYMARKET_CTF_ADDRESS, POLL_INTERVAL, EXECUTION_GRPC_ADDR
from shared.models import Market, Signal, Position, PnLSnapshot

log = structlog.get_logger()

CTF_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "conditionId", "type": "bytes32"},
            {"indexed": True, "name": "oracle", "type": "address"},
            {"indexed": True, "name": "questionId", "type": "bytes32"},
            {"indexed": False, "name": "outcomeSlotCount", "type": "uint256"},
        ],
        "name": "ConditionResolution",
        "type": "event",
    }
]

_channel = None
_stub = None


def _get_stub():
    global _channel, _stub
    if _stub is None:
        from onchain import trading_pb2_grpc
        _channel = grpc.aio.insecure_channel(EXECUTION_GRPC_ADDR)
        _stub = trading_pb2_grpc.ExecutionServiceStub(_channel)
    return _stub


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
        log.info("position_closed_onchain", market_id=str(market.id), side=pos.side, pnl=pnl)


async def handle_resolution(condition_id: str, question_id: str) -> None:
    cid = condition_id.hex() if isinstance(condition_id, bytes) else condition_id
    qid = question_id.hex() if isinstance(question_id, bytes) else question_id
    log.info("condition_resolved", condition_id=cid, question_id=qid)

    market = await Market.get_or_none(condition_id=cid)
    if not market:
        market = await Market.get_or_none(symbol=cid)
    if market:
        await Signal.create(
            market=market,
            trigger_type="resolution",
            value=1.0,
        )
        await _close_positions_for_market(market)
        log.info("resolution_signal_created", symbol=market.symbol, condition_id=cid)


async def watch_resolutions() -> None:
    while True:
        try:
            async with AsyncWeb3(WebSocketProvider(POLYGON_RPC)) as w3:
                contract = w3.eth.contract(
                    address=AsyncWeb3.to_checksum_address(POLYMARKET_CTF_ADDRESS),
                    abi=CTF_ABI,
                )
                log.info("onchain_watcher_connected", rpc=POLYGON_RPC)

                last_block = await w3.eth.block_number

                while True:
                    await asyncio.sleep(POLL_INTERVAL)
                    current_block = await w3.eth.block_number
                    if current_block <= last_block:
                        continue

                    events = await contract.events.ConditionResolution.get_logs(
                        fromBlock=last_block + 1,
                        toBlock=current_block,
                    )
                    for event in events:
                        await handle_resolution(
                            event["args"]["conditionId"],
                            event["args"]["questionId"],
                        )
                    last_block = current_block

        except Exception:
            log.exception("onchain_watcher_error", backoff=10)
            await asyncio.sleep(10)
