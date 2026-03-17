import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL", "postgres://postgres:postgres@postgres:5432/polywarren")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
POLYMARKET_WS_URL = os.getenv("POLYMARKET_WS_URL", "wss://ws-subscriptions-clob.polymarket.com/ws/market")
KALSHI_WS_URL = os.getenv("KALSHI_WS_URL", "wss://trading-api.kalshi.com/trade-api/ws/v2")
KALSHI_API_KEY = os.getenv("KALSHI_KEY", "")
VOLATILITY_THRESHOLD = float(os.getenv("VOLATILITY_THRESHOLD", "0.05"))
REDIS_MARKET_TTL = int(os.getenv("REDIS_MARKET_TTL", "60"))
EXECUTION_GRPC_ADDR = os.getenv("EXECUTION_GRPC_ADDR", "execution:50051")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
