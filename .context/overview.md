---
type: overview
project: karma-rush
updated: 2026-05-21
tags: [context, overview]
---

# Overview

**Project:** KARMA RUSH
**One-liner:** A 60-second top-down TUI arcade game — hoard mysterious items, each a hidden 50/50 karma gamble that swings your sanity; survive the minute and chase the high score.

_Status: **Complete — all 7 slices built.** Scaffold, arena, movable player, items (spawn, walk-over collect, score), sanity (decay, per-item karma, color-coded bar, pickup flash, death at 0), the 60s run loop (`TIME UP` / `SANITY LOST` end, game-over screen, `R` restart), the front end — title screen, 3-2-1 countdown, and a formal app state machine (TITLE → COUNTDOWN → PLAYING → GAMEOVER) — and a persistent high score (`BEST` in the HUD and on game-over) all exist with a tested `blessed`-free core. Slice 7 (HITL playtest) tuned the balance constants and added the README. 71 tests green — see [[active-work]]._

## Layout

- `main.py` — entry point; sets up/tears down raw terminal mode, launches the app loop.
- `karma_rush/` — the game package: config, core engine, countdown timer, rendering, input, screens, high-score store, app/orchestration.
- `tests/` — `pytest` suite for the `blessed`-free core.
- `requirements.txt` — pins `blessed`.
- `README.md` — install, run, and play instructions.
- `PRD.md` — the full build spec.
- `ISSUES.md` — the work, broken into 7 tracer-bullet vertical slices.

## How to run

- Install deps: `pip install -r requirements.txt`
- Play: `python main.py`
- Test: `pytest`

## Where to look first

- **Build spec:** `PRD.md` (problem, solution, modules, mechanics, tests).
- **Work breakdown:** `ISSUES.md` — all 7 slices done.
- **Settled design:** [[decisions]] — 19 grilled decisions, the architecture call, and the Slice 7 balance tune. Do not re-litigate.
- **Handoff state:** [[active-work]] — current focus and where to pick up.
- **Built:** All 7 slices (`karma_rush/`, `main.py`, `tests/`, `README.md`). The game is feature-complete.

## Conventions

- The game **core is `blessed`-free** — all rules live behind `GameState.tick(intents, dt)` so they unit-test without a TTY. Keep terminal code out of it.
- The core is **`dt`-driven** (no real clock) and **RNG-injected** (no global `random`) so runs are deterministic under test.
- All tuning constants live in **one config module** — rebalance there, never inline.

## Map

- [[stack]] — language, libraries, how it runs
- [[active-work]] — current handoff state
- [[decisions]] — the settled design decisions
