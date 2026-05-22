---
type: overview
project: karma-rush
updated: 2026-05-23
tags: [context, overview]
---

# Overview

**Project:** KARMA RUSH
**One-liner:** A 60-second top-down TUI arcade game — hoard mysterious items, each a hidden 50/50 karma gamble that swings your sanity; survive the minute and chase the high score.

_Status: **v1 complete (all 7 slices, 71 tests green); v2 maze expansion planned, not built.** v1: scaffold, arena, movable player, items (spawn, walk-over collect, score), sanity (decay, per-item karma, color-coded bar, pickup flash, death at 0), the 60s run loop (`TIME UP` / `SANITY LOST` end, game-over screen, `R` restart), the front end — title screen, 3-2-1 countdown, and a formal phase machine (TITLE → COUNTDOWN → PLAYING → GAMEOVER) — and a persistent high score, all on a tested `blessed`-free core. **v2 — the maze expansion** (procedural braided maze, Hunter enemy AI, bonus time) is specced as PRD GitHub issue #1 and broken into build slices #2–#5; no v2 code written yet. See [[active-work]]._

## Layout

- `main.py` — entry point; sets up/tears down raw terminal mode, launches the app loop.
- `karma_rush/` — the game package: config, core engine, countdown timer, rendering, input, screens, high-score store, app/orchestration.
- `tests/` — `pytest` suite for the `blessed`-free core.
- `requirements.txt` — pins `blessed`.
- `README.md` — install, run, and play instructions.
- `CONTEXT.md` — the domain glossary (owns the project's ubiquitous language).
- `docs/adr/` — architecture decision records (0001–0004).
- `docs/old spec/` — archived v1 build spec (`PRD.md`, `ISSUES.md`); v2 work now lives as GitHub issues.

## How to run

- Install deps: `pip install -r requirements.txt`
- Play: `python main.py`
- Test: `pytest`

## Where to look first

- **Domain language:** `CONTEXT.md` — the glossary; use its terms in code and docs.
- **Architecture:** `docs/adr/` — 0001 core/shell split, 0002 `blessed`, 0003 items-dict, 0004 braided maze.
- **v2 build spec:** PRD GitHub issue #1; build slices = issues #2–#5.
- **v1 spec (archived):** `docs/old spec/PRD.md` + `ISSUES.md` — all 7 v1 slices done.
- **Settled design:** [[decisions]] — the v1 grill (19 decisions + architecture + Slice 7 tune) and the v2 maze-expansion design pass. Do not re-litigate.
- **Code layout:** [[code-map]] — where each piece of logic lives.
- **Handoff state:** [[active-work]] — current focus and where to pick up.
- **Built:** v1 only — all 7 slices (`karma_rush/`, `main.py`, `tests/`, `README.md`). v2 maze expansion is specced, not built.

## Conventions

- The game **core is `blessed`-free** — all rules live behind `GameState.tick(directions, dt)` so they unit-test without a TTY. Keep terminal code out of it.
- The core is **`dt`-driven** (no real clock) and **RNG-injected** (no global `random`) so runs are deterministic under test.
- All tuning constants live in **one config module** — rebalance there, never inline.

## Map

- [[stack]] — language, libraries, how it runs
- [[code-map]] — where each piece of logic lives
- [[active-work]] — current handoff state
- [[decisions]] — the settled design decisions
