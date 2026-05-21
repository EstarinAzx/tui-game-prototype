---
type: active-work
project: karma-rush
updated: 2026-05-21
tags: [context, active-work]
---

# Active Work

_Last updated: 2026-05-21 by Opus 4.7 (auto)_
_At commit: Slice 6 (this session — see git log for hash)_

## Current focus

KARMA RUSH **Slice 6 is built** — a persistent high-score store, loaded once
at launch and re-saved whenever a run beats it, shown as `BEST` in the HUD and
on the game-over screen. Built `/tdd` on the `pytest`-covered, `blessed`-free
contract. The next agent runs **Slice 7** — the final slice: a playtest +
balance pass. Slice 7 is **HITL** — it needs a human to play and judge feel.

## State

- **In flight:** Nothing — Slice 6 is complete and committed.
- **Done this session:** Built Slice 6 via `/tdd` (cycles 41–43). New
  **`highscore.py`**: a 2-function store — `load_high_score(path)` (missing or
  unreadable file → 0) and `save_high_score(path, score)` (writes only when
  the score beats the stored best, returns the resulting best). Wired into the
  shell: **`app.py`** loads the best once at launch, re-saves after every
  finished run, and threads `best` / `is_new_best` through the phase loop;
  **`render.py`** `render_frame` gained a `best` param and a `BEST n` HUD field
  beside `SCORE`; **`screens.py`** `render_game_over` gained `best` /
  `is_new_best` and shows `NEW HIGH SCORE!` (green) or `BEST n` (dim). Tests:
  `test_highscore.py` (3 — missing-file, save/load round-trip, lower score
  does not overwrite). **71 tests, all green.**
- **Blocked:** Nothing for Slice 6. Slice 7 is blocked on a human (HITL).

## Pick up here

**Slice 7 — Playtest and balance pass** (`ISSUES.md`, **HITL** — the last
slice):
1. A human plays several full runs end-to-end, reaching both `SANITY LOST`
   and `TIME UP` — run `python main.py` (needs a real TTY).
2. Tune the balance constants in **`config.py`** only — decay rate, karma
   magnitudes, item cap, arena size — if runs feel trivially survivable or
   unfairly punishing. No new mechanics.
3. Record the final tuned constants in [[decisions]].
4. Write a short **README** — how to install, run, and play.

Do not attempt Slice 7 AFK — it needs a human to feel the balance.

After any change: run `python -m pytest` — keep it green.

## Skills for next session

- None required. Slice 7 is hand-tuning + a README, not a `/tdd` slice.

## Open questions

None.

## Recent context

- **`highscore.py` is a deep 2-function module:** the JSON encoding, the
  "only write if it beats the best" comparison, and corruption handling all
  live behind `load_high_score` / `save_high_score`. `save` is safe to call
  after *every* run — a worse run is a cheap read and no write.
- **`load_high_score` swallows a broad set of errors → 0:** missing file,
  bad JSON, missing key, wrong type all read as 0. A half-written file from a
  crash mid-save therefore never breaks the next launch.
- **`is_new_best` is computed before the save:** `app.run` records
  `state.score > best` *before* calling `save_high_score`, so the game-over
  screen can flair a new record even though `save` has since raised `best`.
- **`highscore.json` is already in `.gitignore`** ("Game data" section) — the
  runtime score file is never committed.
- **Slice 6 was parallel with Slice 5** in the dependency graph (both blocked
  only by Slice 4); Slice 5 was built first last session, Slice 6 this one.
- Could not run `python main.py` here (no interactive TTY) — verified by the
  71-test `pytest` suite plus a non-TTY smoke test (store round-trips through
  a real temp file; `render_frame` and `render_game_over` draw with the new
  `best` / `is_new_best` params against a fake terminal).

## Related

- [[overview]]
- [[decisions]]
