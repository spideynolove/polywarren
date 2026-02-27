# polywarren

High-performance prediction market trading system for [Polymarket](https://polymarket.com) and [Kalshi](https://kalshi.com). Python/gRPC/Postgres backend with a Next.js dashboard and Telegram bot interface.

## Architecture

```
Polymarket WS ──┐
                ├──▶  Signal Engine  ──gRPC──▶  Execution Engine
Kalshi WS ──────┘         │                          │
                      Redis cache              circuit breakers
                           │                  latency logging
                      Postgres                      │
                           │                   Postgres (orders)
                      FastAPI (REST + SSE)
                           │
               ┌───────────┴────────────┐
           Next.js                 Telegram bot
         (SSE live odds)           (long-polling)

Polygon event watcher ──▶ Signal Engine
  (Polymarket resolution)
```

All services run on a single EC2 c5.large via Docker Compose. GitHub Actions deploys on push to `main`.

## Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.12 + FastAPI + asyncio |
| Database | PostgreSQL 16 + TortoiseORM + asyncpg |
| Cache | Redis 7 |
| Internal RPC | gRPC-asyncio + Protocol Buffers |
| WS consumers | `aiohttp` |
| On-chain | `web3.py` async (Polygon) |
| Frontend | Next.js 14 + TypeScript + Tailwind + Recharts |
| Telegram | `aiogram` v3 |
| Infra | AWS EC2 + Docker Compose + CloudWatch |
| CI/CD | GitHub Actions |

## Latency

Measured by `structlog` on every trade path: `signal_received_at → order_sent_at → confirmation_at`

| Path | Typical | Notes |
|---|---|---|
| WS tick → Signal write | < 5 ms | Postgres + Redis batch write |
| Signal → gRPC order dispatch | < 2 ms | local Docker network |
| Order dispatch → dry-run confirmation | < 1 ms | in-process |
| **Full signal → order (dry-run)** | **< 10 ms** | `latency_ms` in `orders` table |

## Services

| Service | Port | Description |
|---|---|---|
| `api` | 8000 | FastAPI REST + SSE |
| `execution` | 50051 | gRPC Execution Engine |
| `signal` | — | Polymarket + Kalshi WS consumers |
| `onchain` | — | Polygon resolution event watcher |
| `bot` | — | Telegram bot (long-polling) |
| `frontend` | 3000 | Next.js dashboard |

## Quick Start

```bash
cp .env.example .env
# Edit .env — add TELEGRAM_TOKEN, POLYMARKET_KEY, KALSHI_KEY, POLYGON_RPC

docker compose up --build
```

Health check:
```bash
curl http://localhost:8000/healthz
# {"status":"ok","postgres":"ok","redis":"ok","polymarket":"ok","kalshi":"ok"}
```

## Data Models

```
Market(id, symbol, venue, last_odds, updated_at)
Signal(id, market_id, trigger_type, value, created_at)
Order(id, signal_id, venue, side, size, status, sent_at, confirmed_at, latency_ms)
Position(id, market_id, venue, side, size, entry_price, opened_at)
PnLSnapshot(id, timestamp, value, venue)
```

Indexes on `(timestamp, symbol)` for all time-series tables.

## Migrations

```bash
aerich init-db
aerich migrate --name init
aerich upgrade
```

## Tests

```bash
pytest tests/ -v
```

## Deployment (AWS EC2)

GitHub Actions pipeline on push to `main`:
1. `ruff check` + `mypy` + `pytest`
2. SSH to EC2 → `git pull` → `docker compose up -d --build`

Secrets in GitHub: `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`
Logs: Docker awslogs driver → CloudWatch `/polywarren/*`

## Telegram Commands

```
/status   — current open positions
/pnl      — total PnL summary
/buy <market_id> <yes|no> <size>  — dry-run order
```
