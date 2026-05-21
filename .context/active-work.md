---
type: active-work
project: karma-rush
updated: 2026-05-21
tags: [context, active-work]
---

# Active Work

_Last updated: 2026-05-21 by Opus 4.7 (auto)_
_At commit: post-review fix pass (this session — see git log for hash)_

## Current focus

KARMA RUSH **is feature-complete and has now had a review pass.** A `/reviewer`
audit of the finished codebase found 1 blocker + 1 important + 2 nits; all four
were fixed this session. 71 tests still green.

## State

- **In flight:** Nothing.
- **Done this session:** `/reviewer` audit of the whole codebase, then fixes:
  - **Blocker — `app._play_run` resize `dt` leak.** `last_time` was reset only
    on normal frames, so time on the resize prompt (the too-small `continue`
    path) leaked into the next `dt`. The first frame after a resize got a giant
    `dt` → mass sanity decay + timer burn; a long resize could end the run
    instantly. Fixed.
  - **Important — only PLAYING guarded terminal size.** Title, countdown, and
    game-over drew unconditionally — a small window showed a garbled screen,
    not the resize prompt (PRD story 27). Now all four phases guard size.
  - Both fixed via a new shared helper `app._wait_for_resize` (blocks on the
    prompt until the window fits or the player quits); `dt`-driven phases reset
    their frame clock after it returns. See [[decisions]].
  - **Nit — `highscore.save_high_score`** now writes a `.tmp` file then
    `os.replace`s it: a crash mid-write keeps the old file instead of a
    truncated one `load` reads back as score 0.
  - **Nit — `core._refill_items`** builds the free-cell list once instead of
    rebuilding it per spawn. Verified RNG-identical (same cells, same order at
    each `choice`) — seeded runs are unchanged.
  - Player-color commit `a1072d4` (cyan → white) was reviewed and **kept** —
    deliberate, documented in its commit message.
- **Blocked:** Nothing.

## Pick up here

**No active work — the game is feature-complete and reviewed.**

Optional follow-ups, in priority order:
- **Manual resize check.** The shell loop is untested by PRD design (D17).
  Launch `python main.py` in a terminal smaller than 82×29, resize it mid-run,
  and confirm the run resumes with a fresh clock — full sanity, 60s — not a
  corrupted one. This is exactly the path the blocker fix touched.
- **Re-playtest at the current balance.** Decay 2.0 / arena 80×24 / item_cap 9
  is an informed tune but has not been felt by a human at the *new* values.
- Anything else is a new feature beyond the PRD.

After any change: run `python -m pytest` — keep it green.

## Skills for next session

- None required. Both follow-ups are hand-testing, not a `/tdd` slice.

## Open questions

None.

## Recent context

- **Resize handling is now uniform.** Every phase loop routes a too-small
  window through `_wait_for_resize`; any new phase must do the same, and any
  `dt`-driven loop must reset `last_time` after a pause. See [[decisions]].
- **Balance is decay 2.0 / arena 80×24 / item_cap 9** (Slice 7 tune). The
  required terminal is 82×29. A human has not re-felt the new values.
- Could not run `python main.py` here (no interactive TTY); AFK verification
  was the 71-test `pytest` suite.

## Related

- [[overview]]
- [[decisions]]
