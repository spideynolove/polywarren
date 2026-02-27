import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL", "postgres://postgres:postgres@postgres:5432/polywarren")
GRPC_PORT = int(os.getenv("GRPC_PORT", "50051"))
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
MAX_LOSS_THRESHOLD = float(os.getenv("MAX_LOSS_THRESHOLD", "-100.0"))
MAX_ORDERS_PER_MINUTE_POLYMARKET = int(os.getenv("MAX_ORDERS_PER_MINUTE_POLYMARKET", "10"))
MAX_ORDERS_PER_MINUTE_KALSHI = int(os.getenv("MAX_ORDERS_PER_MINUTE_KALSHI", "10"))
POLYMARKET_KEY = os.getenv("POLYMARKET_KEY", "")
KALSHI_KEY = os.getenv("KALSHI_KEY", "")
