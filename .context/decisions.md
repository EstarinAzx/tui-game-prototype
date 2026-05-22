---
type: decisions
project: karma-rush
updated: 2026-05-23
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

---

## 2026-05-21 — Resize handling: every phase guards size; clocks reset after a pause

**Decision:** A `/reviewer` audit fixed two resize defects in `app.py`.
(1) `_play_run` reset `last_time` only on a normal frame, so time spent on the
resize prompt leaked into the next `dt` — the first post-resize tick decayed
sanity and burned the timer for seconds the run never played, sometimes ending
it instantly. (2) Only the PLAYING phase checked terminal size at all. Both are
fixed with a shared helper `app._wait_for_resize`, which blocks on the resize
prompt until the window fits (or the player quits). Every phase loop — title,
countdown, playing, game-over — now calls it, and every `dt`-driven phase
(`_countdown`, `_play_run`) resets its frame clock immediately after it returns.
**Why:** The resize prompt is a PRD requirement (story 27), but recovering from
it corrupted the run, and three of four phases never showed it. Rule going
forward: any new phase loop must call `_wait_for_resize`, and any `dt`-driven
loop must reset `last_time` after any pause so paused time is never dumped into
a `dt`.
**Reversibility:** easy — localized to `app.py`.

---

## 2026-05-21 — Domain glossary + ADRs; code aligned to glossary terms

**Decision:** A `/grill-with-docs` session made `CONTEXT.md` the owner of the
project's ubiquitous language (13 terms; 7 overloads resolved) and promoted
three load-bearing decisions to `docs/adr/` — `0001` core/shell split, `0002`
`blessed` over curses/textual, `0003` items as a `{cell: karma}` dict. Code
identifiers were renamed to the settled terms (commit `ca172bc`): `tick_hz` →
`frame_hz`, `best` → `high_score` family, `app.run` → `run_session`, core
`tick(intents)` → `tick(directions)`, "app state machine" → "phase machine".
**Why:** Terms were overloaded across docs and code — one name per concept,
enforced in code, stops drift. ADRs give the architectural decisions a permanent
home independent of this rolling `.context/`; D1, D16, D20 and the items-dict
entry above are the source rationale.
**Reversibility:** easy — the renames are mechanical and the 71 tests stay
green; the ADR'd decisions are as reversible as their subjects (see each ADR).

---

## 2026-05-23 — KARMA RUSH maze expansion: design pass (12 decisions)

**Decision:** A `/grill-with-docs` → `/to-prd` → `/to-issues` session specced
an expansion that **replaces** the empty-arena game with a maze game. Three
features: a procedurally generated braided maze, one Hunter enemy AI, and bonus
time granted by good karma. Full spec is PRD GitHub issue #1; domain terms are
in `CONTEXT.md`. Settled design:
- *Maze:* braided (looping corridors, no dead ends), fresh per Run; arena bumped
  to 81×25 odd, 1-cell corridors. See `docs/adr/0004-braided-maze.md`.
- *Hunter:* instant-death on contact (`end_reason "caught"`), ~75% player speed,
  BFS shortest-path chase, spawns at the BFS-farthest floor cell, active from
  t=0. One Hunter; end-priority sanity → caught → time.
- *Bonus time:* a separate roll on a good-karma Pickup only; extends the Run
  past 60s, uncapped; `Pickup` gains a `bonus_seconds` field. Item shape stays
  `{cell: karma}` — ADR-0003 preserved.
- *Build:* 2 new pure-core modules (`maze` incl. BFS, `hunter`); 4 tracer-bullet
  slices = GitHub issues #2–#5; #5 is an HITL balance playtest.

**Why:** The empty arena was one-dimensional once the rhythm was learned.
Braided (not perfect) maze so a slower chaser stays fair — escape loops, no
dead-end death traps. Bonus time rolled at pickup, not pre-stored, to keep
ADR-0003's item dict intact. Replace, not a mode, to avoid maintaining two code
paths. All new logic stays in the pure core (ADR-0001) so it unit-tests.

**Reversibility:** hard — supersedes D3 (empty arena); the braided topology, the
Hunter, and the 81×25 arena are load-bearing across core/render/tests. The
shipped balance constants (tuned in slice #5) are trivially reversible.

---

## 2026-05-23 — Slice 1 (#2): `maze_braid_factor` defaults to 1.0 — no dead ends

**Decision:** `config.maze_braid_factor` (default **1.0**) is the probability
each dead-end room gets a second passage carved. `Maze.generate` always runs two
passes: a recursive-backtracker perfect maze, then a braid pass. At factor 1.0
every dead end is removed, satisfying the slice's hard acceptance criterion
"every Floor cell has ≥2 Floor neighbours". Only rooms (even,even cells) can
dead-end; connectors link two rooms by construction, so they always have two
Floor neighbours.
**Why:** The acceptance criterion forbids dead ends outright, yet
`maze_braid_factor` had to exist as a config knob (PRD story 28). Resolved by
making it a real probability with the shipped default pinned at 1.0 — the
shipped Maze never has a dead end, but slice #5's playtest *could* lower it.
This closes the "what does the braid factor do / why 1.0" question.
**Reversibility:** easy — one constant in `config.py`; lowering it is a balance
choice deferred to slice #5.

---

## 2026-05-23 — Slice 1 (#2): test mazes injected, not generated

**Decision:** `GameState.new(rng, config, maze=None)` gained an optional `maze`
parameter. Production passes nothing (a fresh Maze is generated); tests inject
a hand-built `Maze` — an all-Floor "open maze" for movement/karma/sanity tests
(via the `make_state` helper, which also re-centres the Player), or a tiny
hand-carved maze for Wall-blocking tests.
**Why:** Pre-maze core tests stage the Player and Items on arbitrary cells; on a
real braided maze those cells are often Walls, so the tests would break against
maze topology rather than the behaviour they cover. Injecting an open maze keeps
each test pinned to one behaviour. Maze generation itself is covered separately
in `tests/test_maze.py`.
**Reversibility:** easy — the parameter is optional and additive.

---

## 2026-05-23 — Slice 2 (#3): Bonus time — Pickup roll, accumulator, test isolation

**Decision:** Bonus time is a second roll resolved inside `tick` on a *good*-Karma
Pickup only (`karma > 0`); a hit adds `config.bonus_time_amount` to a
`GameState.bonus_time_total` accumulator and is reported on `Pickup.bonus_seconds`
(0 otherwise). `time_remaining` and the `"time"` end-check both read one
`GameState._run_length` property (`run_seconds + bonus_time_total`). Starting
constants: `bonus_time_chance` 0.25, `bonus_time_amount` 5.0. The `make_state`
test helper defaults `bonus_time_chance=0.0`.
**Why:** The maze-expansion design pass already settled *that* bonus time rolls
at Pickup and never touches the Item dict (ADR-0003); this records the build
choices. The roll is good-Karma-only so bad Karma never consumes the RNG. One
`_run_length` value because the HUD clock and the end-check are the same boundary
— naming it once stops a future edit from desyncing them. `make_state` defaults
the chance off so all 81 pre-bonus core tests stay deterministic (a good-Karma
Pickup would otherwise roll and shift the seeded RNG) — the same isolation trick
as Cycle 27's `sanity_decay_per_second=0.0`. Bonus tests force the roll with
chance 1.0 / 0.0, needing no seed control.
**Reversibility:** easy — `bonus_time_chance` / `bonus_time_amount` are constants
in `config.py`, retuned by slice #5; the rest is additive.

---

## 2026-05-23 — Slice 3 (#4): Hunter shipped omniscient, then redesigned — smart Hunter is #6

**Decision:** Slice 3 built issue #4's Hunter exactly as specced — an omniscient
BFS chaser that targets the player's *current* cell every step and is active
from t=0 (committed `0ea4f23`, 101 tests green). A playtest judged the
omniscience unfair: there is no way to break the chase. The targeting model is
being redesigned in a new issue **#6 (Slice 3b: Smart Hunter)** — line of sight
+ last-known-position memory + random-corridor wander when it has no target,
and `hunter_speed_factor` 0.75 → 0.5. Separately, `Hunter.advance` caps its
banked dt at two steps (`min(budget + dt, 2 * step_seconds)`).

**Why:** This supersedes the targeting half of the 2026-05-23 maze-expansion
design pass ("BFS shortest-path chase ... active from t=0"). #4's omniscient
Hunter is kept committed, not reverted: its BFS `path_step`, BFS-farthest spawn,
catch detection (shared cell / head-on swap), and end-priority (sanity → caught
→ time) are all unchanged by #6 — #6 only gates *targeting* with LOS + memory.
Shipping #4 first keeps a clean tested slice boundary and a foundation #6
extends. The `advance` dt-cap exists because a dt spike (OS suspend, window
drag, console QuickEdit pause) otherwise dumps its whole duration into one `dt`
and runs a `path_step` BFS per backlogged cell — a measured 60 s spike cost
366 ms; the cap cut it to 3.4 ms. A chaser gains nothing from teleporting to
make up lost time, so dropping the backlog is correct.

**Reversibility:** medium — #6 changes how the Hunter picks its target; the
pathing, spawn, and catch machinery underneath is stable. The dt-cap is one
line, trivially reversible.
