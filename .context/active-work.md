---
type: active-work
project: karma-rush
updated: 2026-05-21
tags: [context, active-work]
---

# Active Work

_Last updated: 2026-05-21 by Opus 4.7 (auto)_
_At commit: 08f744c (Slice 1)_

## Current focus

KARMA RUSH **Slice 1 is built** — the project scaffold, the bordered arena, and
a wall-clamped movable player, with the `blessed`-free core under `pytest`. The
next agent builds **Slice 2** (items: spawn, walk-over collect, score).

## State

- **In flight:** Nothing — Slice 1 is complete and committed.
- **Done this session:** Built Slice 1 via `/tdd` — `config.py`, `core.py`
  (`GameState.new` + `tick`), `render.py`, `input.py`, `app.py`, `main.py`,
  `requirements.txt`, `pytest.ini`. 13 core tests, all green.
- **Blocked:** Nothing.

## Pick up here

1. Start **Slice 2** in `ISSUES.md` (blocked by #1, now unblocked).
2. Extend the core (`karma_rush/core.py`): add an item list to `GameState`,
   a steady-cap spawner (6 items) using the injected RNG, walk-over collect in
   `tick`, and a score counter. `tick` should return pickup events.
3. Write `tests/test_core.py` coverage first (red-green): spawner keeps the
   cap, a spawn never lands on the player or another item, score +1 per pickup.
4. Render items as yellow `?` and add a score readout to the HUD region
   (`render.py` reserves `HUD_ROWS = 2` under the arena already).
5. Run `python -m pytest` — keep it green.

## Skills for next session

- `/tdd` — Slice 2 ships `pytest` core coverage; red-green-refactor fits.

## Open questions

None.

## Recent context

- **Core/shell split holds:** `core.py` imports nothing terminal — verified.
  `tick(intents, dt)` takes `intents` as a plain set of direction strings
  (`"up"/"down"/"left"/"right"`); the shell's `Intents` dataclass (in
  `input.py`) carries `directions` + `quit` and is unpacked before `tick`.
- **Movement is dt-independent in Slice 1** — tick-poll moves one cell per
  axis per tick; `dt` is threaded through `tick` but unused until Slice 3
  (decay) needs it. Keep the signature.
- **Config is injectable** — `GameState.new(rng, config)` takes a `Config`
  dataclass; tests build tiny arenas (e.g. 3×3) to exercise wall clamping.
- **Windows gotcha:** `main.py` forces `sys.stdout` to UTF-8 — legacy Windows
  codepages (cp1252) crash on the box-drawing glyphs otherwise.
- Could not run `python main.py` here (no interactive TTY); verified by
  import + render smoke test and the `pytest` suite.

## Related

- [[overview]]
- [[decisions]]
