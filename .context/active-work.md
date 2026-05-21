---
type: active-work
project: karma-rush
updated: 2026-05-21
tags: [context, active-work]
---

# Active Work

_Last updated: 2026-05-21 by Opus 4.7 (auto)_
_At commit: Slice 5 (this session — see git log for hash)_

## Current focus

KARMA RUSH **Slice 5 is built** — a title screen, a 3-2-1 countdown, and a
formal app state machine (TITLE → COUNTDOWN → PLAYING → GAMEOVER, `R` loops
GAMEOVER → COUNTDOWN), all on top of the `blessed`-free, `pytest`-covered core.
The next agent builds **Slice 6** (persistent high score) — still unblocked —
then **Slice 7** (playtest + balance, HITL — needs a human).

## State

- **In flight:** Nothing — Slice 5 is complete and committed.
- **Done this session:** Built Slice 5 via `/tdd` (cycles 32–40). New
  **`countdown.py`**: a `Countdown` class — dt-driven, `blessed`-free like the
  core (`tick(dt)`, `number` = digit on screen, `done`). New phase machine in
  **`app.py`**: phase constants `TITLE`/`COUNTDOWN`/`PLAYING`/`GAMEOVER`, a
  `_TRANSITIONS` table, and a pure `next_phase(phase, outcome)` (`"quit"` →
  `None` from any phase). `app.run` is now a state-machine dispatcher;
  `_title` and `_countdown` are new phase loops; `_play_run` / `_game_over`
  kept as phase handlers. **`screens.py`** gained `render_title` and
  `render_countdown`, and the centering code was extracted to a shared
  `_draw_centered` helper (game-over uses it too). **`input.py`** `Intents`
  gained an `any_key` flag (true when any key was pressed — the title waits on
  it). Tests: `test_countdown.py` (4) + `test_app.py` (8, transitions only).
  **68 tests, all green.**
- **Blocked:** Nothing.

## Pick up here

**Slice 6 — Persistent high score** (`ISSUES.md`):
1. There is **no `highscore.py`** yet — create it. `config.highscore_path`
   (`"highscore.json"`) is already defined.
2. Load best score at launch (missing file → 0), save when beaten, show it in
   the HUD (`render.py`) and on the game-over screen (`screens.py`).
3. `/tdd` it — `ISSUES.md` Slice 6 wants `pytest` on the store (missing-file
   reads 0, save/load round-trips, a lower score does not overwrite a higher
   best). The store is pure I/O — fits red-green cleanly.

**Slice 7 — Playtest and balance pass** (`ISSUES.md`, **HITL**): a human plays
full runs and tunes the `config.py` constants; also write a short README.
Blocked on a human — do not attempt AFK.

After Slice 6: run `python -m pytest` — keep it green.

## Skills for next session

- `/tdd` — Slice 6's high-score store is pure file I/O, ideal for
  red-green-refactor.

## Open questions

None.

## Recent context

- **`next_phase` is pure and tested:** the state machine's transition table
  lives in `app.py` but `next_phase(phase, outcome)` is a pure function — the
  8 `test_app.py` tests drive it directly. The phase *loops* (`_title`,
  `_countdown`, `run`) stay untested shell, verified by a non-TTY smoke run.
- **`Countdown` mirrors the core's contract:** dt-injected, no real clock, no
  `blessed` — so it unit-tests like `GameState`. `number` is `ceil` of time
  left, floored at 0; `done` flips at `elapsed >= seconds`.
- **Restart now replays the countdown:** `R` on game-over goes GAMEOVER →
  COUNTDOWN → PLAYING, so the player gets a fresh 3-2-1 (Slice 4's `R` jumped
  straight into a run). This is the Slice 5 spec / decision D13.
- **`_countdown` returns `"play"` before painting "0":** it checks
  `countdown.done` after `tick` and returns immediately, so no "0" frame ever
  shows — the digits read 3-2-1 then the run starts.
- **Title/countdown screens skip the resize check** (`_play_run` still has
  it). Their text is short and `_draw_centered` clamps to column/row 0, so a
  small terminal degrades gracefully instead of drawing a broken arena.
- Could not run `python main.py` here (no interactive TTY) — verified by the
  68-test `pytest` suite plus a non-TTY smoke test (title/countdown/game-over
  screens render, `_title` returns start/quit, `_countdown` returns play/quit,
  the full TITLE→…→restart→COUNTDOWN cycle resolves).

## Related

- [[overview]]
- [[decisions]]
