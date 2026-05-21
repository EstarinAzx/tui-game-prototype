---
type: code-map
project: karma-rush
updated: 2026-05-21
tags: [context, code-map]
---

# Code Map

Where each piece of logic lives. The codebase splits two ways — see [[decisions]]
D20 and `docs/adr/0001`: a pure **core** owns the rules, a **shell** owns the
terminal. Domain terms (Run, Tick, Phase, Intents…) are defined in `CONTEXT.md`.

**Layers** — [main.py](../main.py) boots [app.py](../karma_rush/app.py), the
phase machine, which drives:

- **core** — pure rules, `blessed`-free, dt-driven: [core.py](../karma_rush/core.py), [countdown.py](../karma_rush/countdown.py), [config.py](../karma_rush/config.py)
- **shell** — terminal + files: [render.py](../karma_rush/render.py), [screens.py](../karma_rush/screens.py), [input.py](../karma_rush/input.py), [highscore.py](../karma_rush/highscore.py)

## Entry

| File | What lives here |
|---|---|
| [main.py](../main.py) | UTF-8 stdout reconfigure, `blessed.Terminal()`, raw-mode context managers; calls [`app.run_session`](../karma_rush/app.py#L60). |

## Core — pure rules, no `blessed`

| File | What lives here |
|---|---|
| [core.py](../karma_rush/core.py) | `GameState` — all game rules. [`tick`](../karma_rush/core.py#L114) advances one Tick: decay → move → pickup → end-check. [`_refill_items`](../karma_rush/core.py#L80) restocks to `item_cap`; [`_roll_karma`](../karma_rush/core.py#L70) flips the 50/50. `Pickup` event record at L22. |
| [countdown.py](../karma_rush/countdown.py) | `Countdown` — dt-driven 3-2-1 timer; [`number`](../karma_rush/countdown.py#L31) is the on-screen digit. |
| [config.py](../karma_rush/config.py) | `Config` frozen dataclass — every tuning constant. `DEFAULT` preset at L67. The only place to rebalance. |

## Shell — terminal + files

| File | What lives here |
|---|---|
| [app.py](../karma_rush/app.py) | The phase machine. [`run_session`](../karma_rush/app.py#L60) drives TITLE→COUNTDOWN→PLAYING→GAMEOVER; [`next_phase`](../karma_rush/app.py#L49) is the transition table. Per-phase loops `_title` / `_countdown` / `_play_run` / `_game_over`; [`_wait_for_resize`](../karma_rush/app.py#L99) is the shared too-small-window handler. |
| [render.py](../karma_rush/render.py) | [`render_frame`](../karma_rush/render.py#L91) draws arena + HUD; [`is_terminal_too_small`](../karma_rush/render.py#L55) / `required_terminal_size` gate window size. |
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
| Tick | [`GameState.tick`](../karma_rush/core.py#L114), [`Countdown.tick`](../karma_rush/countdown.py#L25) |
| Frame | one [phase-loop iteration](../karma_rush/app.py#L187); `frame_hz` paces it |
| Sanity | `GameState.sanity` + [`_clamp_sanity`](../karma_rush/core.py#L105) |
| Karma | [`Pickup.karma`](../karma_rush/core.py#L22), `karma_good`/`karma_bad`, [`_roll_karma`](../karma_rush/core.py#L70) |
| Item | `{cell: karma}` entries in `GameState.items` |
| Pickup | [`Pickup`](../karma_rush/core.py#L22) record, returned by `tick` |
| Score / High score | `GameState.score`; [`highscore.py`](../karma_rush/highscore.py) store |
| Arena | drawn by [`render_frame`](../karma_rush/render.py#L91); sized by `arena_width` / `arena_height` |
| Player | `GameState.player` cell |
| Intents | [`Intents`](../karma_rush/input.py#L20) bundle from [`read_intents`](../karma_rush/input.py#L32) |
| Screen | [`screens.py`](../karma_rush/screens.py) — title / countdown / game-over |

## Quick "where do I look for…?"

| Question | Start at |
|---|---|
| "Why did sanity change?" | [core.py:122](../karma_rush/core.py#L122) — passive decay, then karma on pickup |
| "Why did the run end?" | [core.py:147](../karma_rush/core.py#L147) — sanity-first end-check |
| "Where is a Pickup resolved?" | [core.py:138](../karma_rush/core.py#L138) |
| "How does an Item spawn?" | [core.py:80](../karma_rush/core.py#L80) — `_refill_items` |
| "Why is a finished run frozen?" | [core.py:117](../karma_rush/core.py#L117) — `tick` no-ops once `run_over` |
| "How does a resize pause work?" | [app.py:99](../karma_rush/app.py#L99) — `_wait_for_resize`, called by every phase loop |
| "Where do keys map to moves?" | [input.py:44](../karma_rush/input.py#L44) |
| "Where do I rebalance the game?" | [config.py](../karma_rush/config.py) — all constants, nowhere else |

## Related

- [[overview]]
- [[CONTEXT]] — the domain glossary these terms are defined in
- [[decisions]] — D20 / ADR-0001, the core/shell split
- [[active-work]]
