# PRD — KARMA RUSH

> A 60-second top-down terminal arcade game. Hoard mysterious items; each is a hidden karma gamble that swings your sanity. Survive the minute, chase the high score.

_Status: spec ready for build · Created 2026-05-20 · Source: `/grill-me` session (19 design decisions)_

## Problem Statement

A player wants a quick, self-contained game that runs in a plain terminal — no GUI, no install ceremony, no long session. They want a tight loop they can finish in one minute, a simple but real decision to make every few seconds, and a score that makes "one more run" tempting. Nothing like this exists yet; it must be built from scratch.

## Solution

KARMA RUSH is a top-down TUI arcade game played entirely in a CLI terminal.

The player controls a single square inside a fixed bordered arena. Mysterious items (`?`) keep appearing on the floor. Walking over one collects it — but every item is a hidden 50/50 gamble: good karma raises sanity, bad karma lowers it. Sanity also decays slowly on its own, so the player must keep hoarding to stay alive.

A run lasts 60 seconds. Score is the number of items collected. If sanity hits 0 the run ends early (death); otherwise it ends when the timer expires. The best score persists between launches, making the game an endless high-score chase.

The core tension: the goal is to hoard as many items as possible, but every pickup might be the bad-karma one that ends the run.

## User Stories

1. As a player, I want to launch the game with a single command, so that I can start playing without setup.
2. As a player, I want a title screen showing the game name and controls, so that I know how to play before the timer starts.
3. As a player, I want a 3-2-1 countdown before the run begins, so that I am ready when the clock starts.
4. As a player, I want to move my square with the arrow keys, so that I can navigate comfortably.
5. As a player, I want to move my square with WASD as well, so that I can use whichever keys I prefer.
6. As a player, I want to hold a direction key to keep moving, so that traversal feels continuous and not stuttery.
7. As a player, I want my square stopped by the arena walls, so that I stay inside the play area.
8. As a player, I want mysterious items to appear on the floor, so that I always have something to chase.
9. As a player, I want the floor kept stocked with items, so that the run never stalls waiting for a spawn.
10. As a player, I want to collect an item just by walking onto it, so that hoarding feels fast and frantic.
11. As a player, I want every item to look identical, so that each pickup is a genuine gamble.
12. As a player, I want a collected item's karma revealed instantly, so that I learn the outcome of my gamble.
13. As a player, I want good karma to raise my sanity, so that lucky pickups keep me alive.
14. As a player, I want bad karma to lower my sanity, so that unlucky pickups carry real risk.
15. As a player, I want my sanity to decay slowly on its own, so that standing still is not a safe strategy.
16. As a player, I want a sanity bar that changes color as it drains, so that I can read my danger at a glance.
17. As a player, I want a pickup flash showing the karma swing (`+12` / `−12`), so that feedback is immediate and clear.
18. As a player, I want the run to end the instant my sanity hits 0, so that bad luck has a real consequence.
19. As a player, I want a visible 60-second countdown, so that I can pace my hoarding.
20. As a player, I want my score to be the count of items collected, so that the goal is simple: hoard more.
21. As a player, I want a game-over screen showing why the run ended and my final score, so that I can see how I did.
22. As a player, I want to press R to play again immediately, so that I can chase a better score without friction.
23. As a player, I want to press Q or Esc to quit at any time, so that I am never trapped in the game.
24. As a player, I want my best score saved between launches, so that I have a long-term target.
25. As a player, I want the best score shown during and after a run, so that I always know the bar to beat.
26. As a player, I want the terminal restored cleanly when I quit or the game crashes, so that my shell is not left garbled.
27. As a player on a too-small terminal, I want a clear "resize" message, so that I know why the game will not start.
28. As a developer, I want the game logic isolated from the terminal layer, so that I can unit-test the rules without a TTY.
29. As a developer, I want all tuning constants in one place, so that I can rebalance the game without hunting through code.

## Implementation Decisions

### Architecture — core/shell split

The game splits into a pure **core engine** and a thin **terminal shell**. The core holds all rules and state and imports nothing terminal-related. The shell (rendering, input, screens, orchestration) is the only part that touches `blessed`. This makes the rules unit-testable without a TTY and is the central architectural decision — see Testing Decisions.

### Modules

- **Config** — every tuning constant: tick rate, run length, arena size, item cap, decay rate, karma magnitudes, color thresholds, file paths. One source of truth for balance.
- **Core engine** — the deep module. Owns `GameState`: player position, the list of items (each carrying a hidden karma), sanity, score, elapsed time, run status. Exposes `GameState.new(rng, config)` and `GameState.tick(intents, dt)`. `tick` advances one frame: applies movement intents, resolves walk-over pickups, applies karma and passive decay, advances the timer, checks end conditions, and returns a list of frame events (notably pickup events carrying the karma sign). It imports no `blessed`, reads no real clock, touches no files — time arrives as `dt`, randomness as an injected RNG.
- **High-score store** — loads the persisted best score and saves a new best. A simple interface hiding the file format and the missing-file case.
- **Rendering** — translates a `GameState` plus the frame's events into terminal output: arena border, player, items, HUD (timer, sanity bar, score, best), and the transient pickup flash.
- **Input** — maps `blessed` keystrokes to core intents: movement directions, quit, restart, "any key".
- **Screens** — the title screen, the 3-2-1 countdown, and the game-over screen.
- **App / orchestration** — the run-level state machine (TITLE → COUNTDOWN → PLAYING → GAMEOVER, with R looping GAMEOVER → COUNTDOWN). Owns the fixed-timestep frame loop, measures real `dt` from a monotonic clock, and wires input → core → rendering.
- **Entry point** — sets up and tears down raw terminal mode (restoring the terminal even on exception) and launches the app.

### Key mechanic decisions

- Fixed **20 Hz** tick loop; the core is driven by `dt` so frame hitches do not change game speed.
- Movement is **tick-poll**: each tick the input buffer is drained and the player moves at most one cell per axis toward the latest direction(s) held — a constant rate regardless of OS key-repeat speed or buffer depth. Walls clamp the player inside the arena.
- The arena is a **fixed bordered box** (~60×20 interior). No interior obstacles.
- The floor is kept stocked at **6 items** (steady cap); collecting one triggers a replacement spawn at a random empty cell that is never the player's cell or another item's cell. Items never despawn on a timer.
- Every item looks **identical** (`?`); its karma (good/bad, 50/50) is hidden, rolled with the injected RNG, and revealed only on pickup.
- **Sanity** is a float in `[0, 100]`, starts at 100, decays at 1.5/sec, and is clamped on every change. Good karma is `+12`, bad karma is `−12`. Overflow above 100 is wasted.
- A run is **60 seconds**. It ends immediately when sanity reaches 0 (`SANITY LOST`) or when the timer expires (`TIME UP`). Score is the count of items collected and freezes at the end moment.
- The **best score persists** across launches in a local file.

### Balance

Starting preset "Standard": decay 1.5/sec, good `+12`, bad `−12`, item cap 6. With 50/50 odds the average item swing is zero, so passive decay is the real clock and bad-luck streaks end runs early. All values live in the config module and are meant to be tuned by playtest.

## Testing Decisions

- A good test exercises the **external behavior of the core engine**, not its internals: construct a `GameState` with a seeded RNG, drive it with `tick(intents, dt)` calls, and assert on observable state — sanity, score, item count, run status, end reason. Do not assert on private fields or call order.
- **Core engine** tests cover: sanity clamps to `[0, 100]`; good/bad karma applies exactly `±12` on pickup; passive decay equals `rate × dt`; the item floor stays at the cap and a spawn never lands on the player or another item; score increments by exactly 1 per pickup; the run ends at sanity ≤ 0; the run ends at elapsed ≥ 60s; a fixed RNG seed yields a deterministic run.
- **High-score store** tests cover: a missing file loads as 0; save-then-load round-trips; saving a lower score does not overwrite a higher best.
- **Not unit-tested:** rendering, input, screens, and the app loop — they are terminal-coupled and verified by manual playtest (see Slice 7 in ISSUES.md).
- **Prior art:** none — this is a greenfield project. The pattern to establish: a pure, `dt`-driven, RNG-injected core plus a `pytest` suite.

## Out of Scope

- Multiplayer, networking, online leaderboards.
- Audio / sound effects.
- Interior walls or obstacles in the arena.
- Difficulty ramping or escalation over the 60 seconds (flat by decision).
- Multiple item types or visually distinguishable item glyphs.
- Mouse input.
- A settings/options menu, a pause feature, or run replays.
- Multiple arenas or levels.
- Packaging/distribution beyond `requirements.txt` (no `pyproject.toml`, no installable console script).
- Adapting the arena to terminal size — the arena is fixed; oversized terminals letterbox, undersized terminals show a resize prompt.

## Further Notes

**Tuning constants (Standard preset):**

| Constant | Value | Meaning |
|---|---|---|
| Tick rate | 20 Hz | fixed game-loop frequency |
| Run length | 60 s | one run |
| Arena interior | ~60 × 20 cells | play area inside the border |
| Item cap | 6 | items kept on the floor |
| Sanity range / start | 0–100 / 100 | clamped each change |
| Passive decay | 1.5 / s | sanity lost per second |
| Good karma | +12 sanity | per good item |
| Bad karma | −12 sanity | per bad item |
| Good : bad odds | 50 : 50 | per item |
| Pickup flash | ~0.4 s | HUD karma flash duration |
| Countdown | 3 s | before the timer starts |
| Sanity bar colors | >60 green · 30–60 yellow · <30 red | danger read |

- **Minimum terminal size:** roughly 62 columns × 24 rows (arena border + HUD line). Below this the game shows a resize prompt and will not start.
- **Tech:** Python 3.11+, single runtime dependency `blessed`. Run with `python main.py`.
- The full design rationale for each decision is recorded in `.context/decisions.md` — 19 decisions from the grill session. Do not re-litigate them without a reason.
