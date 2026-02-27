# Design: Update Techs.md and README.md

**Date:** 2026-02-27
**Status:** Approved

## Context

The repository currently has:
- `README.md` — empty (just a heading)
- `Techs.md` — detailed tech stack doc written as personal job-prep notes (informal framing, advisory tone)
- `CLAUDE.md` — just created; captures architecture, commands, and patterns

`Techs.md` contains valuable technology decisions but is framed as advice to a job candidate rather than project documentation. `README.md` has no useful content. Both need to serve the project going forward.

## Decisions

### Techs.md → docs/adr/tech-stack.md

Rename and rewrite `Techs.md` as `docs/adr/tech-stack.md` — a single Architecture Decision Record.

**Structure:**
```
# Tech Stack ADR

## Context
## Decisions
  ### Backend: Python + FastAPI + asyncio
  ### Database: PostgreSQL + TortoiseORM + asyncpg
  ### Cache: Redis (aioredis)
  ### Internal RPC: gRPC-asyncio + Protobuf
  ### Frontend: TypeScript + Next.js 14 App Router + Tailwind CSS
  ### Telegram Bot: aiogram
  ### Infrastructure: AWS EC2 (c5/c6i) + ECS/Fargate + Lambda
```

Each decision section contains 1-3 sentences of rationale only — the "why", not "how to use". No setup instructions (those live in CLAUDE.md).

### README.md — minimal description + stack

Replace with a minimal README: 2-sentence project description, one-line stack summary, and links to CLAUDE.md and the ADR. No dev commands (those are in CLAUDE.md).

**Structure:**
```
# polywarren

[description]

## Stack
[one-liner]

> Early-stage. See CLAUDE.md and docs/adr/tech-stack.md.
```

## Files Changed

| File | Action |
|---|---|
| `Techs.md` | Delete (content moved) |
| `docs/adr/tech-stack.md` | Create new |
| `README.md` | Rewrite |
