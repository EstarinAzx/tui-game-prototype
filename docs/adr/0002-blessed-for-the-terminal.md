# `blessed` for terminal rendering and input

The terminal shell uses `blessed` as its single runtime dependency for raw-mode
control: rendering, color, box-drawing, and non-blocking key reads. We chose it
for cross-platform raw-terminal control with a simple manual game loop that
works on Windows with no extra package.

## Considered Options

- **`curses`** — rejected: needs `windows-curses` on Windows and exposes a
  C-style API.
- **`textual`** — rejected: its widget/CSS model fights a per-cell game grid.
- **`rich` Live** — rejected: no real input handling.

## Consequences

- All of `render.py`, `input.py`, and `screens.py` couple to the `blessed`
  terminal object. Swapping the library is a shell-wide rewrite — but the core
  (see ADR-0001) is untouched by it.
