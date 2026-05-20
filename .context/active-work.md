---
type: active-work
project: karma-rush
updated: 2026-05-21
tags: [context, active-work]
---

# Active Work

_Last updated: 2026-05-21 by Opus 4.7 (auto)_
_At commit: Slice 2 (this session — see git log for hash)_

## Current focus

KARMA RUSH **Slice 2 is built** — items spawn, walk-over collect, and a score
counter, with the `blessed`-free core under `pytest`. The next agent builds
**Slice 3** (sanity: decay, karma, bar, death).

## State

- **In flight:** Nothing — Slice 2 is complete and committed.
- **Done this session:** Built Slice 2 via `/tdd` (cycles 8–13). Core
  (`core.py`): `GameState` gained `items` (set of `(x,y)` cells), `score`,
  an injected `rng`, a steady-cap spawner `_refill_items`, walk-over collect
  in `tick`, and a `Pickup` event dataclass. `tick` returns a list of
  `Pickup`s. Shell (`render.py`): items draw as yellow `?`, HUD shows
  `SCORE n` in the reserved rows under the arena. 38 core tests, all green.
- **Blocked:** Nothing.

## Pick up here

1. Start **Slice 3** in `ISSUES.md` (blocked by #2, now unblocked).
2. Extend the core (`karma_rush/core.py`):
   - Add `sanity` to `GameState` (starts at `config.sanity_start` = 100).
   - Passive decay in `tick`: subtract `sanity_decay_per_second * dt`,
     clamped to `[sanity_min, sanity_max]`. **`dt` becomes meaningful here**
     — Slices 1–2 threaded it through `tick` unused.
   - Each item carries a hidden karma rolled 50/50 at spawn time
     (`rng` + `karma_good_chance`). **This changes the `items` data shape** —
     today `items` is a plain `set` of `(x,y)` cells; Slice 3 needs a karma
     per cell, so make it a `dict {cell: karma}` (or a set of small item
     objects). `render.py` and `test_core.py` both read `state.items` as a
     set of cells — update both.
   - On pickup, apply `+12`/`-12` (`karma_good`/`karma_bad`) clamped to
     `[0, 100]`. Extend the `Pickup` dataclass to carry the swing so the
     shell can flash it.
   - End the run immediately when sanity hits 0 (add a run-over flag/field).
3. Write `tests/test_core.py` coverage first (red-green): decay equals
   `rate * dt`, karma applies exactly `±12` and clamps at both ends, run ends
   at sanity ≤ 0.
4. Shell: color-coded sanity bar in the HUD (green >60, yellow 30–60,
   red <30 — see `config.sanity_green_above` / `sanity_yellow_above`), and a
   pickup flash (`+12` green / `-12` red) for ~`pickup_flash_seconds` (0.4s).
   `app.py` must now consume `tick`'s returned `Pickup` events for the flash
   and stop the loop on death.
5. Run `python -m pytest` — keep it green.

## Skills for next session

- `/tdd` — Slice 3 ships `pytest` core coverage; red-green-refactor fits.

## Open questions

None.

## Recent context

- **Core/shell split holds:** `core.py` still imports nothing terminal —
  only `dataclasses`. Verified by import smoke test.
- **`items` is a set of `(x,y)` cells** in Slice 2. Slice 3 must reshape it
  to carry per-item karma — flagged in "Pick up here" step 2.
- **`Pickup` event** (`core.py`) currently carries only `cell`. `tick`
  returns `list[Pickup]`; `app.py` ignores it for now. Slice 3 extends it
  with the karma swing and `app.py` starts consuming it.
- **Spawner `_refill_items`** builds the empty-cell list by comprehension
  (x-major order) and picks with `rng.choice` — deterministic under a seeded
  RNG. It stops early if the arena has no room (small-arena tests rely on
  this). Karma roll gets added here at spawn.
- **`dt` is still unused by game logic** after Slice 2 — `tick` threads it
  but movement and collection don't read it. Slice 3's decay is the first
  real consumer. Keep the `tick(intents, dt)` signature.
- **Tests** drive collection by setting `state.player` and `state.items`
  directly (public attributes), then ticking a direction — keeps pickups
  deterministic without depending on spawn placement.
- Could not run `python main.py` here (no interactive TTY); verified by
  import + render smoke test (UTF-8 forced) and the `pytest` suite.

## Related

- [[overview]]
- [[decisions]]
