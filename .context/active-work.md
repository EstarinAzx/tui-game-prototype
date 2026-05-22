---
type: active-work
project: karma-rush
updated: 2026-05-23
tags: [context, active-work]
---

# Active Work

_Last updated: 2026-05-23 by Opus 4.7 (auto)_
_At commit: uncommitted — Slice 2 (#3) complete, about to commit_

## Current focus

KARMA RUSH **maze expansion**, Slice 2 of 4. Bonus time is built: a good-Karma
Pickup may roll a chance to also grant extra Run seconds, extending the Run past
its nominal length with no cap. 86 tests green.

## State

- **In flight:** Nothing — Slice 2 done, uncommitted (about to commit).
- **Done this session:** Built GitHub issue #3 (Slice 2) via `/tdd`, 5
  red-green cycles:
  - `config.py` — added `bonus_time_chance` (0.25) and `bonus_time_amount`
    (5.0). Starting values; slice #5 tunes.
  - `core.py` — `Pickup` gained a `bonus_seconds` field; `GameState` gained a
    `bonus_time_total` accumulator and a `_roll_bonus` roll; `tick` rolls bonus
    on a good-Karma Pickup only; new `_run_length` property
    (`run_seconds + bonus_time_total`) backs both `time_remaining` and the
    `"time"` end-check.
  - `render.py` / `app.py` — a cyan Bonus-time HUD flash (e.g. `+5s`) trails
    the karma flash, sharing its fade countdown.
  - `tests/test_core.py` — `make_state` gained a `bonus_time_chance` param
    (default 0.0); 5 new bonus-time tests. 81 → 86 green.
- **Blocked:** Nothing.

## Pick up here

**Build the remaining maze-expansion slices.** Read each with
`gh issue view <n> --repo EstarinAzx/tui-game-prototype`:
- **#4** — Hunter (AI predator, BFS chase, CAUGHT end). The PRD folds BFS
  pathfinding into `maze.py` — it has no path helper yet, build it. New
  `hunter.py` pure-core module.
- **#5** — HITL balance playtest (last; tunes the shipped constants, including
  the new `bonus_time_chance` / `bonus_time_amount`).

Run `python -m pytest` first — expect **86 green**.

## Skills for next session

- /tdd — #4 ships tested pure-core logic (Hunter + BFS); red-green-refactor fits.

## Open questions

None.

## Recent context

- The Bonus-time roll fires only on good Karma (`karma > 0`) — bad Karma never
  consumes the RNG. Tests force it on with `bonus_time_chance=1.0`, off with
  `0.0`, so they are deterministic without seed fiddling.
- `make_state` defaults `bonus_time_chance=0.0` so every pre-bonus core test
  stays deterministic — the same isolation trick as Cycle 27's `decay=0.0`.
- The HUD timer already rendered values > 60 (`run_seconds` is 180); the
  Bonus-time flash was the only real render change.
- `item_cap` 9 and the new bonus constants are all unplayed — flag for the #5
  playtest.

## Related

- [[overview]]
- [[decisions]]
- [[code-map]]
- [[CONTEXT]]
