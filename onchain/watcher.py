import asyncio
import structlog
from web3 import AsyncWeb3
from web3.providers import WebSocketProvider
from onchain.config import POLYGON_RPC, POLYMARKET_CTF_ADDRESS, POLL_INTERVAL
from shared.models import Market, Signal

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


async def handle_resolution(condition_id: str, question_id: str) -> None:
    cid = condition_id.hex() if isinstance(condition_id, bytes) else condition_id
    qid = question_id.hex() if isinstance(question_id, bytes) else question_id
    log.info("condition_resolved", condition_id=cid, question_id=qid)

    market = await Market.get_or_none(symbol=cid)
    if market:
        await Signal.create(
            market=market,
            trigger_type="resolution",
            value=1.0,
        )
        log.info("resolution_signal_created", symbol=cid)


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
