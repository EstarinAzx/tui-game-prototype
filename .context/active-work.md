---
type: active-work
project: karma-rush
updated: 2026-05-23
tags: [context, active-work]
---

# Active Work

_Last updated: 2026-05-23 by Opus 4.7 (auto)_
_At commit: uncommitted — Slice 1 (#2) complete, about to commit_

## Current focus

KARMA RUSH **maze expansion**, Slice 1 of 4. The braided Maze is built: a
new pure-core maze module, the 81×25 Arena, Wall-blocked movement,
Floor-only item spawn, and Wall rendering. The empty Arena is gone — every
Run now threads a real maze. 81 tests green.

## State

- **In flight:** Nothing — Slice 1 done, uncommitted (about to commit).
- **Done this session:** Built GitHub issue #2 (Slice 1) via `/tdd`:
  - New `karma_rush/maze.py` — `Maze` class (`is_wall`/`is_floor`,
    `floor_neighbours`, `floor_cells`, `origin`) + `Maze.generate`:
    recursive-backtracker perfect maze, then a braid pass that removes
    every dead end. RNG-injected, `blessed`-free.
  - `config.py` — Arena 80×24 → 81×25 (odd), added `maze_braid_factor`.
  - `core.py` — `GameState` holds a `Maze`; `new` places the Player on
    `maze.origin`; `tick` Wall-blocks movement per-axis; `_refill_items`
    spawns on Floor cells only.
  - `render.py` — draws Wall cells dim; `required_terminal_size` is
    config-derived, now ~83×30.
  - New `tests/test_maze.py` (8 tests); `test_core.py` updated with an
    open-maze helper + 2 maze-behaviour tests. 71 → 81 tests green.
- **Blocked:** Nothing.

## Pick up here

**Build the remaining maze-expansion slices.** Read each with
`gh issue view <n> --repo EstarinAzx/tui-game-prototype`:
- **#3** — Bonus time (good-Karma Pickup may grant extra Run seconds).
- **#4** — Hunter (AI predator, BFS chase, CAUGHT end). The PRD folds BFS
  pathfinding into `maze.py` — it has no path helper yet.
- **#5** — HITL balance playtest (last; tunes the shipped constants).

#3 and #4 are independent pure-core additions and can run in parallel.
Run `python -m pytest` first — expect **81 green**.

## Skills for next session

- /tdd — #3 and #4 each ship tested pure-core logic; red-green-refactor fits.
- /to-parallel — if splitting #3 and #4 across two agents/worktrees.

## Open questions

None.

## Recent context

- `maze_braid_factor` defaults to **1.0** = every dead end removed (the hard
  no-dead-ends acceptance criterion). See [[decisions]].
- The Maze roughly halves open cells: 81×25 = 2025 cells, ~1118 Floor
  (~55%). `item_cap` is still 9 — effective Item density rose; flag for the
  #5 playtest.
- `make_state` (test helper) now injects an all-Floor "open maze" and
  re-centres the Player, so pre-maze movement/karma tests keep their old
  behaviour. Maze topology is tested only in `test_maze.py`.
- `GameState.new` gained an optional `maze=` param for test injection.

## Related

- [[overview]]
- [[decisions]]
- [[code-map]]
