# polywarren Portfolio Design

## Context

polywarren needs to become an impressive portfolio project for a Senior Full Stack Developer role (JD.md) focused on high-performance trading on Polymarket and Kalshi. The approach is **Deep Backend + Minimal UI**: expert-level Python/gRPC/Postgres depth, thin but real Next.js frontend, and real AWS deployment. Goal: build fast (ASAP) while being genuine and production-quality.

## Architecture

```
Polymarket WS feed ──┐
                     ├──▶ Signal Engine ──▶ gRPC ──▶ Execution Engine
Kalshi WS feed ──────┘         │                           │
                          Redis cache                 Circuit breakers
                               │                      Latency logging
                          Postgres                         │
                               │                      Postgres (orders/PnL)
                          FastAPI (REST + SSE)
                               │
                     ┌─────────┴──────────┐
                 Next.js dashboard    Telegram bot
                  (SSE live odds)    (long-polling)

Ethereum/Polygon event watcher ──▶ Signal Engine
  (Polymarket resolution hints)
```

All services run on EC2 via Docker Compose. GitHub Actions deploys via SSH.

## Services

### signal/ — Signal Engine
- `aiohttp` WS consumers for both Polymarket and Kalshi
- Normalizes to internal `Tick` schema (venue-agnostic)
- Evaluates volatility threshold trigger
- Writes `Signal` rows to Postgres
- Publishes market state to Redis (batch reads, not per-symbol)

### execution/ — Execution Engine (gRPC server)
- Protobuf schema: `OrderRequest`, `OrderResponse`, `DryRunMode`
- Dry-run mode on by default (safe for portfolio demo)
- Routes to correct exchange based on `venue` field
- Circuit breakers: max-loss threshold halt, rate-limit per venue (N orders/min)
- Logs latency: `signal_received_at → order_sent_at → confirmation_at` via structlog

### api/ — FastAPI
- `GET /markets`, `GET /positions`, `GET /pnl`
- `GET /stream/ticks` — SSE push to frontend
- `/healthz` — checks Postgres + Redis + exchange ping
- `slowapi` rate limiting on all public endpoints
- `structlog` with `request_id`, `symbol`, `venue`, `latency_ms` on every request

### onchain/ — On-chain Event Watcher
- `web3.py` async subscriber to Polymarket resolution contract on Polygon
- On resolution event: writes to Postgres, signals Execution Engine to close positions
- Lightweight standalone service in Docker Compose

### bot/ — Telegram Bot
- `aiogram` long-polling (not Lambda — runs as Docker Compose service)
- Commands: `/status`, `/pnl`, `/buy <market> <side> <size>` (dry-run)

### frontend/ — Next.js 14
- Single `/` page: `MarketTable` (SSE live odds) + `PositionTable` + `PnLChart`
- TypeScript, Tailwind CSS, Recharts for PnL line chart
- No auth, no multi-page routing

## Data Models (TortoiseORM)

- `Market(id, symbol, venue, last_odds, updated_at)`
- `Signal(id, market_id, trigger_type, value, created_at)`
- `Order(id, signal_id, venue, side, size, status, sent_at, confirmed_at, latency_ms)`
- `Position(id, market_id, venue, side, size, entry_price, opened_at)`
- `PnLSnapshot(id, timestamp, value, venue)`

Indexes: `(timestamp, symbol)` on all time-series tables.
Migrations: Aerich.

## AWS Deployment

```
EC2 c5.large:
  Docker Compose services:
    - signal, execution, api, bot, onchain
    - postgres (or RDS t3.micro)
    - redis

GitHub Actions:
  1. pytest + ruff + mypy (fail fast)
  2. SSH to EC2 → git pull → docker compose up -d --build

Secrets Manager: POLYMARKET_KEY, KALSHI_KEY, POLYGON_RPC, DB_URL, TELEGRAM_TOKEN
CloudWatch: Docker log driver → log groups per service
```

## Portfolio README Highlights

- Architecture diagram (ASCII or Mermaid)
- Latency benchmark table (ms from signal to order, measured by structlog)
- GIF of Telegram alert firing on a live Polymarket event
- Link to `/healthz` endpoint (running on EC2)

## Files to Create

| Path | Description |
|---|---|
| `signal/` | Signal Engine service |
| `execution/` | gRPC Execution Engine |
| `api/` | FastAPI app |
| `onchain/` | Polygon event watcher |
| `bot/` | Telegram bot |
| `frontend/` | Next.js dashboard |
| `proto/` | Protobuf schema files |
| `docker-compose.yml` | All services |
| `.github/workflows/deploy.yml` | CI/CD pipeline |
| `aerich.ini` + `migrations/` | DB migrations |
| `docs/plans/2026-02-27-portfolio-design.md` | This design doc |

## Verification

- `docker compose up` — all services start, no errors
- `GET /healthz` → `{"status": "ok", "postgres": "ok", "redis": "ok", "polymarket": "ok", "kalshi": "ok"}`
- Trigger a mock signal → see `Order` row in Postgres with `latency_ms` populated
- Telegram `/status` command returns current positions
- Next.js dashboard shows live odds updating via SSE
- GitHub Actions pipeline runs green on push to main
