import asyncio
import structlog
import grpc
from concurrent import futures
from execution.servicer import ExecutionServicer
from execution.config import GRPC_PORT, DRY_RUN
from shared.db import init_db, close_db

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

log = structlog.get_logger()


async def serve() -> None:
    from execution import trading_pb2_grpc

    await init_db()
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_send_message_length", 10 * 1024 * 1024),
            ("grpc.max_receive_message_length", 10 * 1024 * 1024),
        ],
    )
    trading_pb2_grpc.add_ExecutionServiceServicer_to_server(ExecutionServicer(), server)
    addr = f"[::]:{GRPC_PORT}"
    server.add_insecure_port(addr)
    await server.start()
    log.info("execution_engine_started", address=addr, dry_run=DRY_RUN)
    try:
        await server.wait_for_termination()
    finally:
        await server.stop(grace=5)
        await close_db()


if __name__ == "__main__":
    asyncio.run(serve())
