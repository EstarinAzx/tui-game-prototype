---
type: code-map
project: karma-rush
updated: 2026-05-23
tags: [context, code-map]
---

# Code Map

Where each piece of logic lives. The codebase splits two ways — see [[decisions]]
D20 and `docs/adr/0001`: a pure **core** owns the rules, a **shell** owns the
terminal. Domain terms (Run, Tick, Phase, Intents…) are defined in `CONTEXT.md`.

**Layers** — [main.py](../main.py) boots [app.py](../karma_rush/app.py), the
phase machine, which drives:

- **core** — pure rules, `blessed`-free, dt-driven: [core.py](../karma_rush/core.py), [maze.py](../karma_rush/maze.py), [hunter.py](../karma_rush/hunter.py), [countdown.py](../karma_rush/countdown.py), [config.py](../karma_rush/config.py)
- **shell** — terminal + files: [render.py](../karma_rush/render.py), [screens.py](../karma_rush/screens.py), [input.py](../karma_rush/input.py), [highscore.py](../karma_rush/highscore.py)

## Entry

| File | What lives here |
|---|---|
| [main.py](../main.py) | UTF-8 stdout reconfigure, `blessed.Terminal()`, raw-mode context managers; calls [`app.run_session`](../karma_rush/app.py#L60). |

## Core — pure rules, no `blessed`

| File | What lives here |
|---|---|
| [core.py](../karma_rush/core.py) | `GameState` — all game rules; holds a `Maze` and one `Hunter`. [`tick`](../karma_rush/core.py#L182) advances one Tick: decay → Hunter advance → player move (Wall-blocked) → pickup (+ Bonus-time roll) → caught-check → end-check. [`new`](../karma_rush/core.py#L75) spawns the Hunter at [`_farthest_floor_cell`](../karma_rush/core.py#L94). [`_refill_items`](../karma_rush/core.py#L149) restocks Floor-only to `item_cap`; [`_roll_karma`](../karma_rush/core.py#L129) flips the 50/50 Karma, [`_roll_bonus`](../karma_rush/core.py#L139) rolls Bonus time on a good Pickup. `Pickup` event record at L31 (carries `bonus_seconds`). |
| [maze.py](../karma_rush/maze.py) | `Maze` — the braided Wall/Floor layout. [`generate`](../karma_rush/maze.py#L106) carves a perfect maze then braids out dead ends; [`path_step`](../karma_rush/maze.py#L77) is the BFS next-hop helper the Hunter chases along; [`is_floor`](../karma_rush/maze.py#L56) / [`floor_neighbours`](../karma_rush/maze.py#L66) / [`floor_cells`](../karma_rush/maze.py#L50) / [`origin`](../karma_rush/maze.py#L42) query it. RNG-injected, `blessed`-free. |
| [hunter.py](../karma_rush/hunter.py) | `Hunter` — the predator. Holds its cell and a dt accumulator; [`advance`](../karma_rush/hunter.py#L35) spends banked dt in whole BFS hops toward a target at ~75% player speed, catch-up capped at two steps per call. Pure-core, `blessed`-free. |
| [countdown.py](../karma_rush/countdown.py) | `Countdown` — dt-driven 3-2-1 timer; [`number`](../karma_rush/countdown.py#L31) is the on-screen digit. |
| [config.py](../karma_rush/config.py) | `Config` frozen dataclass — every tuning constant. `DEFAULT` preset at L92. The only place to rebalance. |

## Shell — terminal + files

| File | What lives here |
|---|---|
| [app.py](../karma_rush/app.py) | The phase machine. [`run_session`](../karma_rush/app.py#L60) drives TITLE→COUNTDOWN→PLAYING→GAMEOVER; [`next_phase`](../karma_rush/app.py#L49) is the transition table. Per-phase loops `_title` / `_countdown` / `_play_run` / `_game_over`; [`_wait_for_resize`](../karma_rush/app.py#L99) is the shared too-small-window handler. |
| [render.py](../karma_rush/render.py) | [`render_frame`](../karma_rush/render.py#L126) draws arena + HUD (karma flash + cyan Bonus-time flash); `is_terminal_too_small` / `required_terminal_size` gate window size. |
| [screens.py](../karma_rush/screens.py) | The three non-arena Screens — title, countdown, game-over. |
| [input.py](../karma_rush/input.py) | [`read_intents`](../karma_rush/input.py#L32) drains the keyboard into one `Intents` bundle. |
| [highscore.py](../karma_rush/highscore.py) | High-score JSON store — [`load_high_score`](../karma_rush/highscore.py#L23) / [`save_high_score`](../karma_rush/highscore.py#L35) (atomic `.tmp` + `os.replace`). |

## Glossary term → code

Where each [[CONTEXT]] term is represented. Most are concepts, not one symbol.

| Term | Lives as |
|---|---|
| Run | [`_play_run`](../karma_rush/app.py#L174) drives one; [`GameState`](../karma_rush/core.py#L32) holds its state; `run_seconds` / `run_over` |
| Session | [`run_session`](../karma_rush/app.py#L60) — the whole phase loop |
| Phase | `TITLE`/`COUNTDOWN`/`PLAYING`/`GAMEOVER` consts + [`next_phase`](../karma_rush/app.py#L49) |
| Tick | [`GameState.tick`](../karma_rush/core.py#L148), [`Countdown.tick`](../karma_rush/countdown.py#L25) |
| Frame | one [phase-loop iteration](../karma_rush/app.py#L187); `frame_hz` paces it |
| Sanity | `GameState.sanity` + [`_clamp_sanity`](../karma_rush/core.py#L139) |
| Karma | `Pickup.karma`, `karma_good`/`karma_bad`, [`_roll_karma`](../karma_rush/core.py#L129) |
| Bonus time | `Pickup.bonus_seconds`, `GameState.bonus_time_total`, `bonus_time_chance`/`bonus_time_amount`, [`_roll_bonus`](../karma_rush/core.py#L139); `_run_length` extends the clock |
| Item | `{cell: karma}` entries in `GameState.items` |
| Pickup | [`Pickup`](../karma_rush/core.py#L31) record, returned by `tick` |
| Score / High score | `GameState.score`; [`highscore.py`](../karma_rush/highscore.py) store |
| Arena | drawn by [`render_frame`](../karma_rush/render.py#L126); sized by `arena_width` / `arena_height` (122×45) |
| Maze | [`Maze`](../karma_rush/maze.py#L28) — generated by [`Maze.generate`](../karma_rush/maze.py#L106), held as `GameState.maze` |
| Hunter | [`Hunter`](../karma_rush/hunter.py#L19) — held as `GameState.hunter`, spawned in [`new`](../karma_rush/core.py#L75), advanced each [`tick`](../karma_rush/core.py#L182); BFS-chases via [`maze.path_step`](../karma_rush/maze.py#L77) |
| Wall / Floor | `Maze` cells — [`is_wall`](../karma_rush/maze.py#L60) / [`is_floor`](../karma_rush/maze.py#L56); the Floor set is `maze.floor_cells` |
| Player | `GameState.player` cell — starts on [`maze.origin`](../karma_rush/maze.py#L42) |
| Intents | [`Intents`](../karma_rush/input.py#L20) bundle from [`read_intents`](../karma_rush/input.py#L32) |
| Screen | [`screens.py`](../karma_rush/screens.py) — title / countdown / game-over |

## Quick "where do I look for…?"

| Question | Start at |
|---|---|
| "Why did sanity change?" | [core.py:190](../karma_rush/core.py#L190) — passive decay, then karma on pickup |
| "Why did the run end?" | [core.py:237](../karma_rush/core.py#L237) — end-check, priority sanity → caught → time |
| "Where is a Pickup resolved?" | [core.py:215](../karma_rush/core.py#L215) |
| "How is Bonus time granted?" | [core.py:222](../karma_rush/core.py#L222) — good-Karma `_roll_bonus`, banked in `bonus_time_total` |
| "How does an Item spawn?" | [core.py:149](../karma_rush/core.py#L149) — `_refill_items`, Floor cells only |
| "Why is a finished run frozen?" | [core.py:185](../karma_rush/core.py#L185) — `tick` no-ops once `run_over` |
| "How does the Hunter move / catch?" | [core.py:198](../karma_rush/core.py#L198) advances it, [core.py:230](../karma_rush/core.py#L230) is the caught-check; [`Hunter.advance`](../karma_rush/hunter.py#L35) |
| "How is the maze generated?" | [maze.py:106](../karma_rush/maze.py#L106) — `generate`: carve perfect maze, then [`_braid`](../karma_rush/maze.py#L151) |
| "Why can't the player move?" | [core.py:210](../karma_rush/core.py#L210) — per-axis `maze.is_floor` check |
| "How does a resize pause work?" | [app.py:99](../karma_rush/app.py#L99) — `_wait_for_resize`, called by every phase loop |
| "Where do keys map to moves?" | [input.py:44](../karma_rush/input.py#L44) |
| "Where do I rebalance the game?" | [config.py](../karma_rush/config.py) — all constants, nowhere else |

## Related

- [[overview]]
- [[CONTEXT]] — the domain glossary these terms are defined in
- [[decisions]] — D20 / ADR-0001, the core/shell split
- [[active-work]]
