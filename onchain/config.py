import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL", "postgres://postgres:postgres@postgres:5432/polywarren")
POLYGON_RPC = os.getenv("POLYGON_RPC", "wss://polygon-bor-rpc.publicnode.com")
POLYMARKET_CTF_ADDRESS = os.getenv(
    "POLYMARKET_CTF_ADDRESS",
    "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045",
)
POLL_INTERVAL = int(os.getenv("ONCHAIN_POLL_INTERVAL", "12"))
