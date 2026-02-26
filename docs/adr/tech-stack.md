# Tech Stack ADR

## Context

polywarren is a high-performance trading system for Polymarket and Kalshi. Requirements:
- Sub-millisecond execution path from signal to order
- 99.9% uptime
- Real-time market data streaming
- Telegram bot interface + web dashboard
- Internal microservice communication

## Decisions

### Backend: Python + FastAPI + asyncio

Python's async ecosystem (asyncio, uvicorn, httpx) matches the non-blocking I/O requirements of a trading system. FastAPI provides automatic OpenAPI docs and native WebSocket support with minimal overhead.

### Database: PostgreSQL + TortoiseORM + asyncpg

PostgreSQL handles structured trading data (orders, positions, PnL) reliably. TortoiseORM is specified by the project requirements and integrates cleanly with asyncio. asyncpg provides a high-performance async driver with connection pooling.

### Cache: Redis (aioredis)

Market data is read far more than written. Redis with aioredis provides sub-millisecond cache reads for frequently accessed market state, avoiding redundant exchange API calls.

### Internal RPC: gRPC-asyncio + Protocol Buffers

Lower latency than REST for internal microservice calls (e.g., signal engine → execution engine). Protobuf serialization is faster than JSON for high-frequency internal traffic.

### Frontend: TypeScript + Next.js 14 App Router + Tailwind CSS

Next.js App Router enables SSR for fast initial load. TypeScript prevents type errors at the boundaries between trading data structures. Tailwind CSS allows rapid UI iteration without context-switching to a stylesheet.

### Telegram Bot: aiogram

aiogram is the most actively maintained async Python Telegram bot framework. It supports long-polling and webhooks, fits naturally into the asyncio event loop, and avoids the overhead of a separate thread pool.

### Infrastructure: AWS EC2 (c5/c6i) + ECS/Fargate + Lambda

c5/c6i instances are compute-optimized — reduces CPU bottlenecks in the execution path. ECS/Fargate containerizes services for reproducible deployment and horizontal scaling. Lambda handles stateless webhook events (Telegram bot) without maintaining a persistent instance.
