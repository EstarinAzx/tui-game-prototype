---
type: active-work
project: karma-rush
updated: 2026-05-20
tags: [context, active-work]
---

# Active Work

_Last updated: 2026-05-20 by Opus 4.7 (auto)_
_At commit: uncommitted_

## Current focus

KARMA RUSH is fully specced via a `/grill-me` session, but **no code exists yet**. The next agent builds the game slice by slice from `ISSUES.md`, starting with Slice 1 (scaffold + arena + movable player).

## State

- **In flight:** Nothing in code. The spec is complete: `PRD.md`, `ISSUES.md`, and [[decisions]] are written.
- **Done this session:** Grilled 19 design decisions (+ the architecture call); wrote `PRD.md` and `ISSUES.md`; bootstrapped `.context/`.
- **Blocked:** Nothing.

## Pick up here

1. Read `PRD.md` (full spec) and `ISSUES.md` (7 vertical slices).
2. Read [[decisions]] — 20 settled decisions. Do not re-grill them.
3. Start **Slice 1** in `ISSUES.md`: scaffold the modular package and `requirements.txt` (`blessed`); add `main.py`; draw the bordered ~60×20 arena; render the cyan block player at center; wire arrow + WASD tick-poll movement at 20 Hz with wall clamping; add the terminal-too-small guard; make Q/Esc quit cleanly (terminal restored even on exception).
4. **Keep the game core free of `blessed` imports** from the first commit — `GameState.tick(intents, dt)`, `dt`-driven, RNG-injected. This is load-bearing for the Slice 2+ tests ([[decisions]] D17, D20).
5. Build slices in order: 1 → 2 → 3 → 4, then 5 and 6 (parallel), then 7 (HITL playtest + README).

## Skills for next session

- `/tdd` — Slices 2, 3, 4, and 6 each ship `pytest` coverage of the core; a red-green-refactor loop fits.

## Open questions

None — the grill resolved every design branch. The balance constants (Slice 7) are tunable by playtest, not an open question.

## Recent context

- The game core MUST stay free of `blessed` — it is the only unit-testable layer (pure, `dt`-driven, RNG-injected). See [[decisions]] D20.
- `to-prd` / `to-issues` normally create GitHub issues; the user explicitly wanted markdown files (`PRD.md` / `ISSUES.md`), and this repo has no GitHub remote — so the spec lives in files, not issues.
- The balance preset is "Standard" (decay 1.5/s, karma ±12) — a starting point to tune by feel in Slice 7, not a final number.

## Related

- [[overview]]
- [[decisions]]
