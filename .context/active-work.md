---
type: active-work
project: karma-rush
updated: 2026-05-21
tags: [context, active-work]
---

# Active Work

_Last updated: 2026-05-21 by Opus 4.7 (auto)_
_At commit: Slice 3 (this session — see git log for hash)_

## Current focus

KARMA RUSH **Slice 3 is built** — sanity decay, per-item karma, a color-coded
sanity bar, a pickup flash, and instant death at sanity 0, all with the
`blessed`-free core under `pytest`. The next agent builds **Slice 4** (timer,
game-over screen, restart loop).

## State

- **In flight:** Nothing — Slice 3 is complete and committed.
- **Done this session:** Built Slice 3 via `/tdd` (cycles 14–24). Core
  (`core.py`): `GameState` gained `sanity` (starts `config.sanity_start`) and
  a `run_over` flag; `tick` applies passive decay (`sanity_decay_per_second *
  dt`), a `_clamp_sanity` helper pins `[sanity_min, sanity_max]`. **`items`
  reshaped from a set of cells to a `dict {cell: karma}`** — each item's
  karma is rolled 50/50 at spawn by `_roll_karma`. Pickup applies the karma
  swing (clamped) and sets `run_over` when sanity ≤ 0. `Pickup` gained a
  `karma` field. Shell: `render.py` draws a color-coded sanity bar and a
  pickup flash; `app.py` consumes `tick`'s `Pickup` events for the flash and
  returns from `run()` on `run_over`. 49 core tests, all green.
- **Blocked:** Nothing.

## Pick up here

1. Start **Slice 4** in `ISSUES.md` (blocked by #3, now unblocked).
2. Extend the core (`karma_rush/core.py`):
   - Track elapsed run time: accumulate `dt` in `tick` (e.g. `self.elapsed`).
     End the run when `elapsed >= config.run_seconds` (60s).
   - **`run_over` is a bool today** — Slice 4 needs the *reason*. Add an
     end-reason field (`"time"` vs `"sanity"`) so the game-over screen can
     show `TIME UP` / `SANITY LOST`. Set it wherever `run_over` flips.
   - Decide whether `tick` should no-op once `run_over` is set — there is no
     guard today; `app.py` simply stops calling it. A test for "score
     freezes on death" may tick past the end and need that guard.
3. Write `tests/test_core.py` coverage (red-green): time-up fires at
   `elapsed >= 60s`, end reason is correct for each path, score frozen at
   death.
4. Shell: a 60s countdown in the HUD (`render.py` — HUD has 2 rows today,
   both used; the timer needs space — widen `HUD_ROWS` or share a row), a
   game-over screen showing reason + final score, and `app.py` state for
   game-over + `R` restart / `Q`-`Esc` quit. There is **no `screens.py`**
   yet though `overview.md` lists one — create it or fold into `app.py`.
5. Run `python -m pytest` — keep it green.

## Skills for next session

- `/tdd` — Slice 4 ships `pytest` core coverage (timer, end reason); fits
  red-green-refactor.

## Open questions

None.

## Recent context

- **`items` is now `dict {cell: karma}`** (was a set of cells in Slice 2).
  `render.py` iterates `for ix, iy in state.items` — dict iteration yields
  keys, so that line was unchanged. `test_core.py` stages items as dicts
  (`{(6,5): 12.0}`); cycles 10–13 were updated to the new shape.
- **`Pickup.karma`** carries the *nominal* swing (`±12`), not the clamped
  applied delta — the flash shows `+12`/`-12` regardless of clamping.
- **Death:** `tick` sets `run_over` when `sanity <= sanity_min`. `app.py`
  draws the final frame then `return`s from `run()` — there is no game-over
  screen yet (that is Slice 4).
- **Karma-isolation tests** pass `dt=0` so passive decay does not blur the
  `±12` swing under test; decay tests use a real `dt`.
- Could not run `python main.py` here (no interactive TTY) — verified by the
  49-test `pytest` suite plus a render smoke test (UTF-8 forced, non-TTY
  `blessed.Terminal`) that drew the sanity bar and both flash colors.

## Related

- [[overview]]
- [[decisions]]
