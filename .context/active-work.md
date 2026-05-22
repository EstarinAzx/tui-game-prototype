---
type: active-work
project: karma-rush
updated: 2026-05-23
tags: [context, active-work]
---

# Active Work

_Last updated: 2026-05-23 by Opus 4.7 (auto)_
_At commit: 0ea4f23 — Slice 3 (#4) committed_

## Current focus

KARMA RUSH **maze expansion**. Slice 3 — the Hunter (GitHub #4) — is built,
tested, and committed. A playtest of the shipped Hunter rejected its omniscient
chase, so a follow-up issue **#6 (Slice 3b: Smart Hunter)** redesigns the
targeting model. 101 tests green.

## State

- **In flight:** Nothing — Slice 3 committed at `0ea4f23`.
- **Done this session:** Built GitHub issue #4 (Slice 3, the Hunter) via
  `/tdd`, 14 red-green cycles:
  - `maze.py` — BFS `path_step` (next hop on a shortest Floor path).
  - `hunter.py` — new pure-core module: `Hunter` holds a cell + dt accumulator,
    steps at 75% player speed via the BFS first hop.
  - `config.py` — `hunter_speed_factor` (0.75).
  - `core.py` — `GameState` owns one Hunter, spawned at the BFS-farthest Floor
    cell; `tick` advances it; caught (shared cell or head-on swap) ends the run
    with `end_reason "caught"`; end priority sanity → caught → time.
  - `render.py` / `screens.py` — red `◆` Hunter glyph, CAUGHT headline, title
    mentions the Hunter.
  - `advance()` caps dt catch-up at two steps — a dt-spike robustness fix.
  - Cycle 27 rewritten to drop Hunter coupling — the only existing test changed.
- **Blocked:** Nothing.

## Pick up here

**Build issue #6 — Slice 3b: Smart Hunter.** Read it with
`gh issue view 6 --repo EstarinAzx/tui-game-prototype`. It replaces the
Hunter's omniscient targeting with line of sight + last-known-position memory +
random-corridor wander, and lowers `hunter_speed_factor` to 0.5. Pure-core,
TDD-able. After #6, **#5 (Slice 4: Balance playtest)** remains — #5 tunes the
final Hunter, so #6 must land first.

Run `python -m pytest` first — expect **101 green**.

## Skills for next session

- /tdd — #6 is tested pure-core logic (LOS, memory, wander); red-green-refactor.

## Open questions

None — #6's design calls (wander when no target, speed 0.5, unlimited LOS
range) are settled in the issue body.

## Recent context

- Issue #4 specified an *omniscient* Hunter ("BFS to the player's current
  cell", "active from t=0"). It was built to spec and committed; the playtest
  then judged omniscience unfair. #6 is the agreed redesign — #4's commit is
  kept as the tested BFS-pathing / catch / spawn foundation #6 extends.
- A perceived "freeze at GET READY 2" during the playtest is **not** a Slice 3
  regression — Slice 3 touches no countdown code, and `tick` benchmarks at
  ~1.5 ms. Most likely Windows console QuickEdit Mode (a click pauses output).
- Benchmarks (122×45 default config): `GameState.new` 8.6 ms, `path_step`
  ~2 ms, `tick` ~1.5 ms. A 60 s dt-spike once cost 366 ms in `advance()`; the
  two-step cap cut it to 3.4 ms.

## Related

- [[overview]]
- [[decisions]]
- [[code-map]]
- [[CONTEXT]]
