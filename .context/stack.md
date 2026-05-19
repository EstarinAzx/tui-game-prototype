---
type: stack
project: karma-rush
updated: 2026-05-20
tags: [context, stack]
---

# Stack

## Languages & runtime

- Python: 3.11+

## Key libraries

- `blessed` — terminal control: rendering, color, box-drawing, non-blocking key input. The **only runtime dependency**. Chosen over `curses` (needs `windows-curses`, C-style API) and `textual` (widget/CSS model fights a per-cell game grid) — see [[decisions]] D1.
- `pytest` — test runner for the core engine. Dev dependency only.

## Project type

CLI / TUI game. One user-facing surface: the `python main.py` command. No HTTP, no service, no daemon.

## Persistence

- High score stored in a local JSON file (path defined in the config module). Missing file reads as 0. No database.

## Env vars

- None.

## Related

- [[overview]] — project shape
- [[decisions]] — why `blessed`, why the core/shell split
