# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

**polywarren** is a high-performance Polymarket/Kalshi trading system with a Telegram bot interface and Next.js web dashboard. Core goal: minimum-latency execution from signal to order.

## Planned Architecture

### Service Boundaries

- **Execution Engine** — isolated trade routing, dry-run mode, slippage control. Communicates internally via gRPC.
- **Signal Engine** — market data ingestion, volatility triggers, precomputed signals.
- **Telegram Bot** — `aiogram` (async). Commands: `/buy`, `/status`, `/pnl`. Stateless; deployed as AWS Lambda + webhook.
- **REST/WebSocket API** — FastAPI + uvicorn. Exposes market data, order status, PnL to frontend.
- **Next.js Dashboard** — real-time odds/positions via WebSocket or SSE.

### Data Flow

```
Polymarket/Kalshi WS feed → Signal Engine → Execution Engine (gRPC) → Postgres (TortoiseORM)
                                           ↓
                                     Telegram alert / WebSocket push → Next.js UI
```

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | Python + FastAPI + asyncio |
| Database | PostgreSQL + TortoiseORM + asyncpg (connection pooling) |
| HTTP client | `httpx` or `aiohttp` (non-blocking) |
| Cache | Redis (`aioredis`) for market data |
| Internal RPC | gRPC-asyncio + Protocol Buffers |
| Frontend | TypeScript + Next.js 14 App Router + Tailwind CSS |
| Telegram | `aiogram` |
| Infra | AWS EC2 (c5/c6i), ECS/Fargate, Lambda, CloudWatch |
| CI/CD | GitHub Actions |

## Development Environment

### Python Backend

```bash
source /home/hung/env/.venv/bin/activate
uv pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database

```bash
# Run migrations with TortoiseORM
python -m aerich upgrade
```

### Tests

```bash
# Backend
pytest tests/ -v
pytest tests/test_execution.py::test_name -v  # single test

# Frontend
npm run test
```

### Linting

```bash
# Python
ruff check . && mypy .

# TypeScript
npm run lint
```

## Key Patterns

- **Async everywhere** — all DB calls, HTTP calls, and WebSocket handlers must be `async/await`. No blocking I/O in the hot path.
- **Structured logging** — use `structlog` with request_id and symbol context. Never `print()`.
- **Health checks** — every service exposes `/healthz` checking DB + exchange connectivity.
- **Secrets** — AWS Secrets Manager in prod. Local `.env` via `python-dotenv` for dev only; never commit `.env`.
- **Rate limiting** — `slowapi` middleware on all public endpoints.
- **Latency measurement** — log round-trip time (UI input → order confirmation) on every trade path.

## Performance Notes

- Index Postgres on `(timestamp, symbol)` for all order/tick tables.
- Batch Redis reads for market data; avoid per-symbol round trips.
- Profile hot paths with `py-spy` before optimizing.
- Execution Engine and Signal Engine should run on compute-optimized instances close to exchange API endpoints.
