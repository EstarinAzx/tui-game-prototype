---
type: active-work
project: karma-rush
updated: 2026-05-21
tags: [context, active-work]
---

# Active Work

_Last updated: 2026-05-21 by Opus 4.7 (auto)_
_At commit: Slice 4 (this session — see git log for hash)_

## Current focus

KARMA RUSH **Slice 4 is built** — a 60-second countdown, a `TIME UP` /
`SANITY LOST` end reason, a game-over screen, and an `R` restart / `Q`-`Esc`
quit loop, all with the `blessed`-free core under `pytest`. The next agent
builds **Slice 5** (title screen + 3-2-1 countdown, formal state machine) and
can build **Slice 6** (persistent high score) in parallel — both unblocked.

## State

- **In flight:** Nothing — Slice 4 is complete and committed.
- **Done this session:** Built Slice 4 via `/tdd` (cycles 25–31). Core
  (`core.py`): `GameState` gained `elapsed` (accumulates `dt` in `tick`) and
  `end_reason` (`"time"` | `"sanity"`, `None` mid-run). `tick` now **no-ops
  once `run_over`** — returns `[]` and mutates nothing, so score/sanity/clock
  freeze at the end moment. End conditions: `elapsed >= run_seconds` →
  `"time"`; `sanity <= sanity_min` → `"sanity"`, **sanity checked first** so a
  tick that trips both ends as `"sanity"`. New `time_remaining` property
  (`max(0, run_seconds - elapsed)`). Shell: `render.py` HUD widened to 3 rows
  (`HUD_ROWS = 3`) with a `TIME` countdown row (`math.ceil` of
  `time_remaining`); new **`screens.py`** with `render_game_over`; `input.py`
  `Intents` gained a `restart` flag (`R` key); `app.py` restructured into
  `run` (restart cycle) → `_play_run` (one run, returns finished state or
  `None` on quit) → `_game_over` (waits for `R`/`Q`). 56 core tests, all green.
- **Blocked:** Nothing.

## Pick up here

Two slices are now unblocked and independent — do either order, or both.

**Slice 5 — Title screen and countdown** (`ISSUES.md`):
1. Add a title screen + a 3-2-1 countdown to `screens.py` (it already holds
   `render_game_over`; `END_REASON_TEXT` lives there too).
2. Formalize the app state machine in `app.py`: TITLE → COUNTDOWN → PLAYING →
   GAMEOVER, with `R` looping GAMEOVER → COUNTDOWN. `config.countdown_seconds`
   (3.0) already exists for the countdown length.
3. `app.py` is currently `run` / `_play_run` / `_game_over` — the state
   machine likely replaces or wraps these.

**Slice 6 — Persistent high score** (`ISSUES.md`, parallel with #5):
1. There is **no `highscore.py`** yet — create it. `config.highscore_path`
   (`"highscore.json"`) is already defined.
2. Load best score at launch (missing file → 0), save when beaten, show it in
   the HUD (`render.py`) and on the game-over screen (`screens.py`).
3. `/tdd` it — `ISSUES.md` Slice 6 wants `pytest` on the store (missing-file
   reads 0, save/load round-trips, a lower score does not overwrite).

After either: run `python -m pytest` — keep it green.

## Skills for next session

- `/tdd` — Slice 6's high-score store fits red-green-refactor cleanly (pure,
  testable). Slice 5 is mostly shell (state machine + screens), less TDD-shaped.

## Open questions

None.

## Recent context

- **`tick` no-op guard:** the very first thing `tick` does is
  `if self.run_over: return []`. Any new caller (Slice 5's state machine) can
  safely tick a finished state — it changes nothing.
- **`end_reason` priority:** sanity-loss is checked before the clock, so the
  game-over screen reads `SANITY LOST` whenever sanity hit 0, even on the tick
  the timer also expired. `screens.END_REASON_TEXT` maps the flag to the label.
- **HUD is 3 rows now** (`HUD_ROWS = 3`): row 0 score + flash, row 1 `TIME`,
  row 2 sanity bar. `required_terminal_size` grew by one row (now 62 × 25 for
  the Standard preset) — the min-size check picks this up automatically.
- **`screens.py` exists** — `overview.md` always listed it; Slice 4 created it
  with `render_game_over`. Slice 5's title/countdown screens belong there too.
- Could not run `python main.py` here (no interactive TTY) — verified by the
  56-test `pytest` suite plus a non-TTY render/screens smoke test (3-row HUD
  shows `TIME`, both game-over reasons render, required size is 62 × 25).

## Related

- [[overview]]
- [[decisions]]
