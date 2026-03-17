import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from shared.db import init_db, close_db
from api.config import CORS_ORIGINS, REDIS_URL
from api.limiter import limiter
from api.middleware import RequestContextMiddleware
from api.routes import markets, positions, pnl, stream, health

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    stream.init_redis_pool(REDIS_URL)
    yield
    await stream.close_redis_pool()
    await close_db()


app = FastAPI(title="polywarren API", version="0.1.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(markets.router)
app.include_router(positions.router)
app.include_router(pnl.router)
app.include_router(stream.router)
app.include_router(health.router)
