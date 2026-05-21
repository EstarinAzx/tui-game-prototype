---
type: active-work
project: karma-rush
updated: 2026-05-21
tags: [context, active-work]
---

# Active Work

_Last updated: 2026-05-21 by Opus 4.7 (auto)_
_At commit: Slice 7 (this session — see git log for hash)_

## Current focus

KARMA RUSH **Slice 7 is built — the project is complete.** All 7 tracer-bullet
slices are done. Slice 7 was the HITL playtest + balance pass: a human played
runs, reported the Standard preset as trivially survivable and the arena as too
small; the balance constants were tuned, a README written, and the final
constants recorded in [[decisions]].

## State

- **In flight:** Nothing — Slice 7 is complete.
- **Done this session:** HITL playtest of Slice 7. Human feedback: runs
  *trivially survivable*, arena *too small*. Tuned `config.py`:
  `sanity_decay_per_second` 1.5 → **2.0** (idle now dies ~50s in, so
  collecting items is forced), `arena_width` 60 → **80**, `arena_height`
  20 → **24**, `item_cap` 6 → **9** (holds item density ≈ constant in the
  bigger arena). Karma `±12` and `run_seconds` 60 unchanged. Wrote **README.md**
  (install / run / play / controls / develop). Recorded final constants in
  `decisions.md` (entry supersedes D19). Fixed
  `test_run_ends_with_time_reason_when_clock_runs_out` — it was coupled to the
  old soft decay; rewritten to run with `sanity_decay_per_second=0.0` so it
  tests the timer path independent of the preset. **71 tests, all green.**
- **Blocked:** Nothing.

## Pick up here

**No active work — the game is feature-complete.** All PRD slices shipped.

Optional follow-up if desired:
- **Re-playtest at the new balance.** Decay 2.0 / arena 80×24 / item_cap 9
  are an informed tune, but a human has not felt the *new* values. Run
  `python main.py` (needs a real TTY ≥ 82×29) and confirm runs feel tense, not
  unfairly punishing. Re-tune `config.py` only if needed; update [[decisions]].
- Anything else is a new feature beyond the PRD.

After any change: run `python -m pytest` — keep it green.

## Skills for next session

- None required. A re-playtest is hand-tuning, not a `/tdd` slice.

## Open questions

None.

## Recent context

- **Decay 2.0 is the load-bearing fix.** At 1.5/s a 60s run drained only 90 of
  100 sanity — idling (zero karma risk) won the game. At 2.0/s a full run
  drains 120, so doing nothing kills you; the 50/50 item gamble is now forced.
- **`item_cap` was bumped *because* the arena grew**, not as a separate balance
  call — 6 items in the 80×24 arena would be too sparse. 9 keeps ~210
  cells/item, close to the original density.
- **The bigger arena raises the terminal floor to 82×29** (was 62×25) —
  `render.required_terminal_size` = arena + border + 3 HUD rows. Smaller
  windows get the resize prompt.
- **One test was balance-coupled and broke on the decay change** — it assumed a
  full idle run survives. Fixed by pinning that test to decay 0; it tests the
  timer path, not the preset.
- Could not run `python main.py` here (no interactive TTY); the human ran the
  playtest. AFK verification was the 71-test `pytest` suite.

## Related

- [[overview]]
- [[decisions]]
