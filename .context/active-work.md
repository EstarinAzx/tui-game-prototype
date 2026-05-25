---
type: active-work
project: karma-rush
updated: 2026-05-25
tags: [context, active-work]
---

# Active Work

_Last updated: 2026-05-25 by Opus 4.7 (auto)_
_At commit: 6e61c0e (uncommitted: Slice 3b smart Hunter — patrol + sight-range cap)_

## Current focus

KARMA RUSH **maze expansion**. Slice 3b (the smart Hunter, GitHub #6) is built
and green but **uncommitted**. Two HITL playtest tweaks layered on top of the
issue spec — patrol-toward-waypoint wander, and a sight-range cap — because the
literal spec (random wander, unlimited LOS) made the Hunter oscillate in
corridors yet still beelined from any open sight line. 121 tests green.

## State

- **In flight:** Uncommitted Slice 3b changes ready to commit:
  - `karma_rush/maze.py` — `has_line_of_sight(a, b, max_range=None)` (Bresenham +
    Chebyshev range gate); `_bresenham_cells` line-walk generator.
  - `karma_rush/hunter.py` — `Hunter(cell, step_seconds, rng, sight_range=None)`;
    `last_known` + `patrol_target` attrs; `advance(maze, player, dt)` (was
    `advance(maze, target, dt)`); three-state `_next_hop` (LOS chase / memory
    head / patrol-toward-waypoint).
  - `karma_rush/config.py` — `hunter_speed_factor` 0.75 → **0.5**; new
    `hunter_sight_range = 12`.
  - `karma_rush/core.py` — `GameState.new` wires the RNG and sight-range into
    Hunter; passes `player=` keyword to `advance`.
  - Tests: 8 new in `tests/test_hunter.py` (S1, S2, S3, S4, S5, S6, W1, W2, W3,
    W5, R2) and 4 new in `tests/test_core.py` (C7, C8, C9); 5 LOS tests in
    `tests/test_maze.py` (L1-L5, R1); H2-H6 repaired to new sig; existing
    C2-C6 gained `rng=…` on their hand-built Hunters.
- **Done this session:** built Slice 3b's smart Hunter via `/tdd`, 22 cycles
  across L1-L5, S1-S6, C7, W1-W3, W5, C8, C9, R1-R3. Patrol replaces the spec's
  random wander; sight cap defaults to 12 cells.
- **Blocked:** Nothing. Awaiting eyeball commit + push (was confirmed in
  conversation).

## Pick up here

**Commit Slice 3b** with a message that captures both the spec'd Smart Hunter
(LOS + memory + wander) and the two playtest-driven extensions (patrol
waypoint, sight-range cap). Suggested:
`feat: smart Hunter — LOS+memory+patrol, sight-range cap (maze expansion Slice 3b, #6)`.
Reference issue #6 in the message, push, close the issue.

After committing, **build issue #5 — Slice 4: Balance playtest** — the HITL
tuning slice. The four knobs ready for tuning are `hunter_speed_factor` (0.5),
`hunter_sight_range` (12), `bonus_time_chance` (0.25), `maze_braid_factor`
(1.0); decay (2.0 or 0.5, see open question) and `item_cap` (25) are also
in scope.

Run `python -m pytest` first — expect **121 green**.

## Skills for next session

- /verify — Slice 4 is HITL; launch the game, feel the Hunter and the clock.
- /tdd — only if playtest reveals a logic bug to chase down.

## Open questions

- `config.sanity_decay_per_second` reads **0.5** in `config.py` but the Slice 7
  ADR pinned it at **2.0**. Looks like a regression slipped in between sessions
  — confirm the intended value before Slice 4's playtest, or the balance will
  be a moving target.

## Recent context

- Issue #6's spec ("wander random corridors") was built first and felt dumb in
  playtest: 1-wide corridors gave the wander a 50% backtrack each step, so the
  Hunter oscillated near spawn. Replaced with patrol-toward-Floor-waypoint —
  same RNG-determinism property, but the Hunter sweeps the map.
- The first playtest of the patrol Hunter still felt omniscient because the
  spec set LOS as unlimited. Added a Chebyshev `hunter_sight_range` cap (12);
  spec itself flagged this as "a range cap can be a Slice 4 tuning knob".
- `Hunter.advance` signature flipped from `(maze, target, dt)` to
  `(maze, player, dt)` — targeting (LOS / memory / patrol) now lives inside the
  Hunter, not the caller. Old H tests with pre-set targets were repaired by
  pre-seeding `hunter.last_known` instead.
- `Hunter` constructor gained an injected `rng` (consistent with the rest of
  the core) — used for both patrol-target picks and any fallback wander.

## Related

- [[overview]]
- [[decisions]]
- [[code-map]]
- [[CONTEXT]]
