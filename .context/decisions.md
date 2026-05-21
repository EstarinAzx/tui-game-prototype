---
type: decisions
project: karma-rush
updated: 2026-05-21
tags: [context, decisions]
---

# Decisions

Settled questions. Append-only; each entry dated. The block below came from a `/grill-me` session — **do not re-litigate without a reason.** Each entry records the *why* and the rejected alternatives so a future agent can judge edge cases instead of guessing.

## Related

- [[overview]]

---

## 2026-05-20 — Design grill (KARMA RUSH, 19 decisions + architecture)

### D1 — TUI library: `blessed`
Render and read input with `blessed`. **Why:** cross-platform raw-terminal control, simple manual game loop, non-blocking key reads (`inkey`); one pip dependency, works on Windows with no extra package. **Rejected:** `curses` (needs `windows-curses`, C-style API), `textual` (widget/CSS model fights a per-cell grid), `rich` Live (no real input handling).

### D2 — Movement: tick-poll, hold-to-move
Fixed 20 Hz tick loop. Each tick drains the input buffer and moves the player at most one cell per axis toward the latest direction(s) held; key release stops movement. **Why:** responsive, easy to aim at items, and a constant speed regardless of OS key-repeat rate or buffer depth. **Rejected:** snake-style auto-move heading (hard to grab items precisely), step-per-press (too calm for a 60s twitch game).

### D3 — Arena: fixed bordered box, empty
Fixed ~60×20-cell rectangle with a drawn wall border; no interior obstacles. **Why:** simplest, matches scope — tension comes from sanity, not layout. **Rejected:** interior obstacles (collision + spawn-avoidance code), fit-to-terminal (min-size checks + dynamic spawn math).

### D4 — Spawning: steady cap, respawn on pickup
Keep ~6 items on the floor at all times; collecting one spawns a replacement. No timed despawn. **Why:** always targets to chase, pure hoarding race, no empty-floor risk. **Rejected:** interval spawn + timed despawn (more tuning, empty-floor risk), accumulate-with-no-cap (floor crowds late-game).

### D5 — Mystery: fully hidden, identical glyph
Every item is the same glyph (`?`); good/bad karma is revealed only on pickup. **Why:** this *is* the "mysterious" core — every pickup is a genuine gamble. **Rejected:** rare visual tells (more design + code), distinguishable-on-sight (removes the mystery entirely).

### D6 — Karma odds: 50 / 50
Each item is an even good/bad coin-flip. **Why:** cleanest gamble — hoarding everything is genuinely risky. **Rejected:** 60/40 good (too safe, grabbing everything is fine), 40/60 bad (fights the stated hoard-hard goal).

### D7 — Sanity: start 100, slow passive decay
Sanity is 0–100, starts at 100, and drains slowly every second. **Why:** "helps *maintain* it" implies something to maintain against — decay forces hoarding and makes good karma valuable even at 50/50 odds. **Rejected:** start 50 no decay (survival is pure luck), start 100 no decay (weak "maintain" pressure).

### D8 — Win/lose: score chase, sanity-0 = death
Goal: collect the most items in 60s. Score = items collected. Sanity hitting 0 ends the run instantly (death), score frozen; surviving to 60s completes the run. **Why:** scope says "keep hoarding" → score is item count, and sanity is the constraint/lose-gate; a high-score arcade loop. **Rejected:** threshold win/lose at 60s (binary, score secondary), survival-only (no score chase).

### D9 — Collection: walk-over auto-collect
Moving the square onto an item's cell collects it instantly — no key press. **Why:** frantic, fits tick-poll movement and the hoarding goal. **Rejected:** press-key-to-grab (slows the hoard, adds nothing for a 60s game).

### D10 — Difficulty: flat
All tuning constants are fixed for the whole run. **Why:** simplest to build and balance, matches scope — tension comes from current sanity, not escalation. **Rejected:** ramping decay / ramping spawn or odds (more code and balancing; not in scope).

### D11 — Pickup feedback: HUD flash + sanity-bar reaction
On pickup, a transient colored text flash (`+12` green / `−12` red) plus a color-coded sanity bar that visibly jumps (green high / yellow mid / red low). **Why:** clear and readable in a terminal. **Rejected:** cell-flash-only, and HUD-flash + cell-flash together (more rendering code for marginal gain).

### D12 — Run-end: restart + persistent high score
End screen shows this run's score and the best-ever; R replays, Q quits; the best score is saved to a local file across launches. **Why:** a full arcade replay loop with a long-term target. **Rejected:** restart without persistence (best resets on exit), single-run-then-exit (no loop).

### D13 — Start flow: title → countdown → play
Launch shows a title screen (name, controls, "press any key"), then a 3-2-1 countdown, then the timer starts. **Why:** the player reads controls before the clock runs. **Rejected:** countdown-only (controls never shown up front), instant start (disorienting first seconds).

### D14 — Controls: arrows + WASD, Q/Esc quit, R restart
Both arrow keys and WASD move; Q or Esc quits mid-run; R restarts on the end screen. **Why:** most accommodating — either movement scheme works. **Rejected:** arrows-only or WASD-only (each excludes a player habit).

### D15 — Visuals: block player, color, box-drawing walls
Player = solid block (cyan), items = `?` (yellow), arena = box-drawing border (dim), color-coded sanity bar. **Why:** the "square" is literal, and color carries the karma feedback from D11. Needs a Unicode-capable terminal — fine on Windows Terminal. **Rejected:** pure ASCII (compatibility we do not need), monochrome (kills the green/red feedback).

### D16 — Structure: modular package + requirements.txt
A modular Python package (config, core, render, input, screens, highscore, app), `requirements.txt` pinning `blessed`, Python 3.11+, run via `python main.py`. **Why:** modules map cleanly onto the issue slices; `requirements.txt` is enough for a small game. **Rejected:** single file (hard to slice into issues, gets messy), `pyproject.toml` package (setup overhead not worth it).

### D17 — Testing: pytest on a blessed-free core
Keep all game rules in a `blessed`-free core module; `pytest` covers sanity clamping, karma resolution, spawn placement, score, and end conditions. Rendering and input stay untested. **Why:** a pure core is testable without a TTY; high value for modest effort. **Rejected:** no tests (logic regressions slip silently), full coverage including rendering (brittle, slow).

### D18 — Name: KARMA RUSH
The game is called KARMA RUSH. **Why:** short, arcade-y, captures the 60-second frenzy and the karma mechanic.

### D19 — Balance: "Standard" preset
Starting values: passive decay 1.5/sec, good karma `+12`, bad karma `−12`, item cap 6. **Why:** with 50/50 odds the average item swing is zero, so decay is the real clock — you usually survive most of the minute and bad-luck streaks end runs early. These live in the config module and are a starting point; final values are set by the Slice 7 playtest. **Rejected:** Forgiving (most runs trivially reach 60s), Harsh (many runs die before 60s).

### D20 — Architecture: pure core + thin terminal shell
The game splits into a pure **core engine** and a thin **terminal shell**. The core (`GameState.tick(intents, dt)`) imports no `blessed`, reads no real clock, and touches no files — time arrives as `dt`, randomness as an injected RNG; the shell does all rendering, input, and I/O. **Why:** this is the consequence of D16 + D17 — it is the only thing that makes the rules unit-testable, and `dt`-driving keeps frame hitches from changing game speed. Load-bearing: keep `blessed` out of the core from the first commit.

---

## 2026-05-21 — Items carry karma as a dict `{cell: karma}`

**Decision:** Slice 3 reshaped `GameState.items` from a `set` of `(x, y)` cells to a `dict` mapping each cell to its hidden karma swing (`+12` / `-12`), rolled 50/50 at spawn.
**Why:** Each item needs a per-item karma. A dict keeps cell lookup O(1) (collection still does `player in items`), karma reads as `items[cell]`, and `render.py` iterating `for ix, iy in state.items` works unchanged because dict iteration yields keys. **Rejected:** a set of frozen `Item` objects — would force `render.py` and every Slice-2 test off plain cells for no gain.
**Reversibility:** hard — `core.py`, `render.py`, and `test_core.py` all read the shape.

---

## 2026-05-21 — Slice 4: `tick` no-ops after `run_over`; sanity loss outranks the clock

**Decision:** Once `GameState.run_over` is set, `tick()` returns `[]` immediately and mutates nothing — score, sanity, `elapsed`, and player all freeze. When a single tick both drains sanity to 0 and runs the clock out, `end_reason` is `"sanity"` (sanity is checked before the clock). `end_reason` is `"time"` | `"sanity"`, `None` while the run is live.
**Why:** The game-over screen must show the score frozen at the end moment — without the guard a late tick from the shell (or Slice 5's state machine) would keep mutating a finished run. `active-work.md` had flagged "should `tick` no-op once over?" as open; this closes it. Sanity-first priority so a death reads as `SANITY LOST`, not `TIME UP`.
**Reversibility:** easy — both behaviors are localized to `tick()`.

---

## 2026-05-21 — Slice 7: final balance constants (supersedes D19)

**Decision:** The Slice 7 HITL playtest replaces the D19 "Standard" starting
values. Final tuned constants in `karma_rush/config.py`:

| Constant | D19 start | Final | 
|---|---|---|
| `sanity_decay_per_second` | 1.5 | **2.0** |
| `arena_width` | 60 | **80** |
| `arena_height` | 20 | **24** |
| `item_cap` | 6 | **9** |
| `karma_good` / `karma_bad` | `+12` / `−12` | unchanged |
| `run_seconds` | 60 | unchanged |

**Why:** The playtest found the D19 preset **trivially survivable** and the
arena **too small**.
- *Decay 1.5 → 2.0:* at 1.5/s a 60s run drains only 90 of 100 sanity, so
  idling — collecting nothing, taking zero karma risk — wins. At 2.0/s a full
  run drains 120, so doing nothing kills you ~50s in. Collecting items (the
  50/50 gamble of D5/D6) is now forced, not optional. This restores D7's
  intent — sanity is something you must *maintain against*.
- *Arena 60×20 → 80×24:* play area felt cramped; `80×24` is ~60% more cells.
- *`item_cap` 6 → 9:* the bigger arena would otherwise scatter 6 items too
  thinly (1200→1920 cells). 9 holds item density ≈ constant (~210 cells/item),
  so the bigger arena is not also a punishing-sparse one.
- *Karma `±12` kept:* not flagged in playtest; the EV-0 coin-flip is the core
  gamble (D6) and changing it is out of scope.

**Cost:** the larger arena raises the required terminal from 62×25 to **82×29**
(`render.required_terminal_size` = `arena + border + 3 HUD rows`).

**Test impact:** `test_run_ends_with_time_reason_when_clock_runs_out` was
coupled to the old soft decay (it ticked a full 60s assuming sanity survived).
Rewritten to run with `sanity_decay_per_second=0.0` so it tests the timer-end
path independent of the balance preset. 71 tests green.

**Reversibility:** trivial — all values are constants in `config.py`. A
re-playtest at 2.0 decay is recommended to confirm runs now feel tense rather
than swinging to unfairly punishing.
