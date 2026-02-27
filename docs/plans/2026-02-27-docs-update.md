# Docs Update Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace job-prep notes with proper project documentation — a clean ADR and a minimal README.

**Architecture:** Delete `Techs.md`, create `docs/adr/tech-stack.md` as a single Architecture Decision Record covering all tech choices, and rewrite `README.md` as a minimal project description with stack summary.

**Tech Stack:** Markdown only — no code changes.

---

### Task 1: Create docs/adr directory and write tech-stack ADR

**Files:**
- Create: `docs/adr/tech-stack.md`
- Delete: `Techs.md`

**Step 1: Create `docs/adr/tech-stack.md`**

```markdown
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
```

**Step 2: Verify the file was created correctly**

Read `docs/adr/tech-stack.md` and confirm all 7 decision sections are present.

**Step 3: Delete `Techs.md`**

```bash
git rm Techs.md
```

Expected: `rm 'Techs.md'`

**Step 4: Commit**

```bash
git add docs/adr/tech-stack.md
git commit -m "docs: add tech stack ADR, remove job-prep notes"
```

---

### Task 2: Rewrite README.md

**Files:**
- Modify: `README.md`

**Step 1: Rewrite `README.md`**

```markdown
# polywarren

High-performance trading bot and dashboard for [Polymarket](https://polymarket.com) and [Kalshi](https://kalshi.com).
Streams live market data via WebSocket, triggers execution signals, routes orders, and delivers results to a Telegram bot and Next.js web dashboard.

## Stack

Python · FastAPI · PostgreSQL · TortoiseORM · Redis · gRPC · Next.js 14 · aiogram · AWS

---

See [CLAUDE.md](CLAUDE.md) for architecture and development commands.
See [docs/adr/tech-stack.md](docs/adr/tech-stack.md) for technology decisions.
```

**Step 2: Verify README looks correct**

Read `README.md` and confirm: description is 2 sentences, stack is one line, links to CLAUDE.md and ADR are present, no dev commands.

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: write minimal README with project description and stack"
```

---

### Task 3: Verify final state

**Step 1: Check file tree**

```bash
ls -la && ls docs/adr/
```

Expected: `Techs.md` is gone, `docs/adr/tech-stack.md` exists.

**Step 2: Verify git log**

```bash
git log --oneline -5
```

Expected: 2 new commits visible.
