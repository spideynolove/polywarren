import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL", "postgres://postgres:postgres@postgres:5432/polywarren")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
POLYMARKET_API_URL = os.getenv("POLYMARKET_API_URL", "https://clob.polymarket.com")
KALSHI_API_URL = os.getenv("KALSHI_API_URL", "https://trading-api.kalshi.com")
