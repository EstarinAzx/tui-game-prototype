---
type: active-work
project: karma-rush
updated: 2026-05-21
tags: [context, active-work]
---

# Active Work

_Last updated: 2026-05-21 18:40 by Opus 4.7 (auto)_
_At commit: 74921db (grill-with-docs + PRD note); this context-update commits on top._

## Current focus

KARMA RUSH is **feature-complete, reviewed, and now documented.** A
`/grill-with-docs` session this session built the domain glossary, promoted the
load-bearing decisions to ADRs, and renamed code identifiers to match. No code
work is outstanding.

## State

- **In flight:** Nothing.
- **Done this session:**
  - `/grill-with-docs` — resolved 7 overloaded terms, created `CONTEXT.md`
    (13-term glossary) and `docs/adr/0001-0003`.
  - Renamed code to the settled terms across 6 files: `tick_hz`→`frame_hz`,
    `best`→`high_score` family, `app.run`→`run_session`, core
    `tick(intents)`→`tick(directions)`, "app state machine"→"phase machine".
    Committed `ca172bc`. 71 tests green.
  - Added a Slice-7 supersession note to `PRD.md` (stale balance numbers).
    Committed `74921db`.
  - Eyeball test: the user ran `python main.py` and screenshotted a live run —
    render correct (9 items, white player, HUD, letterboxed arena); live sanity
    decay matched the math (87 shown vs 88 predicted at 6s elapsed).
  - AFK balance math pass — no defect found, `config.py` left untouched.
  - Added `.context/code-map.md`.
- **Blocked:** Nothing.

## Pick up here

**No active work — pick a new task.**

Two optional playtests remain, both needing a human at a live terminal:
- **Resize check.** The eyeball test ran in a large terminal — it did *not*
  exercise resize. Launch `python main.py`, shrink the window below 82×29
  mid-run, confirm the resize prompt shows and the run resumes with a fresh
  clock (full sanity, 60s), not a corrupted one.
- **Full-run feel.** One screenshot can't show "tense vs unfairly punishing".
  Play a full 60s (or a death) at decay 2.0 / arena 80×24 / item_cap 9. If it
  feels unfair, say what felt wrong and `config.py` can be tuned to it.

After any `config.py` change: run `python -m pytest` — keep it green.

## Skills for next session

- None required. Both follow-ups are hand-testing, not a coding slice.

## Open questions

None.

## Recent context

- `CONTEXT.md` now owns the ubiquitous language — use its terms (Run, Session,
  Tick, Frame, Phase, Screen, Intents, Karma, High score…) in code and docs.
- `docs/adr/` is the durable home for architectural decisions; `.context/` is
  rolling handoff only. ADR-0001 = core/shell split, 0002 = `blessed`, 0003 =
  items-as-`{cell: karma}`-dict.
- Balance is decay 2.0 / arena 80×24 / item_cap 9; required terminal 82×29. The
  math is internally consistent and matches design intent — feel is unverified.

## Related

- [[overview]]
- [[decisions]]
- [[code-map]]
