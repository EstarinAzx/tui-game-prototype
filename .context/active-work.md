---
type: active-work
project: karma-rush
updated: 2026-05-23
tags: [context, active-work]
---

# Active Work

_Last updated: 2026-05-23 by Opus 4.7 (auto)_
_At commit: 4797b64 (planning docs committed — clean tree)_

## Current focus

KARMA RUSH **maze expansion** is fully planned and ticketed. A grill →
PRD → issues pass this session turned three new features — a procedural
maze, a Hunter enemy AI, and bonus time from good karma — into GitHub
issue #1 (PRD) and four build slices (#2–#5). No code written yet.

## State

- **In flight:** Nothing — planning complete, build not started.
- **Done this session:**
  - `/grill-with-docs` — resolved 12 design decisions. Updated
    `CONTEXT.md` (5 new terms: Maze, Wall, Floor, Hunter, Bonus time;
    Arena/Player/Item/Pickup/Run/Karma redefined). Wrote
    `docs/adr/0004-braided-maze.md` (supersedes D3).
  - `/to-prd` — PRD submitted as GitHub issue #1.
  - `/to-issues` — 4 tracer-bullet slices: #2 Maze, #3 Bonus time,
    #4 Hunter, #5 balance playtest (HITL).
- **Blocked:** Nothing.

## Pick up here

**Start GitHub issue #2 — "Slice 1: The Maze".** Read issue #2 and
parent #1 (the PRD) for full context. Build the braided-maze module +
81×25 arena + wall-blocked movement + floor-only item spawn + wall
render. #3 and #4 can then run in parallel; #5 (HITL playtest) is last.

Run `python -m pytest` first to confirm the suite is green (71 tests)
before building.

## Skills for next session

- /tdd — slices #2–#4 each ship a tested pure-core module; red-green-refactor fits.

## Open questions

None.

## Recent context

- The expansion **replaces** the empty-arena game — no Classic mode.
- Hunter: instant-death on contact (`end_reason "caught"`), ~75% player
  speed, BFS pathing, spawns at the BFS-farthest floor cell, active t=0.
- Bonus time: rolled at pickup on good karma only, extends the run past
  60s uncapped; keeps the `{cell: karma}` item shape (ADR-0003).
- Maze gen, Hunter, and BFS all stay in the pure core (ADR-0001).
- Shipped balance constants are starting values — slice #5 tunes them.

## Related

- [[overview]]
- [[decisions]]
- [[code-map]]
