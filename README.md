# KARMA RUSH

A 60-second top-down terminal arcade game. Hoard mysterious items — each one a
hidden 50/50 karma gamble that swings your sanity. Survive the minute and chase
the high score.

Every item looks the same: a yellow `?`. Picking it up flips a coin — good
karma (`+12` sanity) or bad (`−12`). Meanwhile sanity drains on its own. Grab
nothing and you die before the clock runs out; grab everything and bad luck
ends you early. Score is the number of items collected.

## Requirements

- Python 3.11+
- A Unicode-capable terminal at least **82 × 29** characters
  (Windows Terminal, iTerm2, most modern terminals). A smaller window shows a
  resize prompt instead of the game.

## Install

```
pip install -r requirements.txt
```

This installs `blessed`, the only dependency.

## Run

```
python main.py
```

## How to play

1. The title screen shows the controls — press any key.
2. A 3-2-1 countdown plays, then the 60-second run starts.
3. Move onto a `?` to collect it. Karma is revealed on pickup as a colored
   flash (`+12` green / `−12` red).
4. Watch the sanity bar: green is safe, yellow is warning, red is danger. At 0
   the run ends — `SANITY LOST`.
5. Survive to the timer hitting 0 — `TIME UP`.
6. The game-over screen shows your score and the best ever. Press `R` to play
   again, `Q` or `Esc` to quit.

### Controls

| Key | Action |
|---|---|
| Arrow keys / `WASD` | Move (hold to keep moving) |
| `R` | Restart (on the game-over screen) |
| `Q` / `Esc` | Quit |

The best score is saved to `highscore.json` between launches.

## Develop

The game core (`karma_rush/core.py`) is `blessed`-free, `dt`-driven, and
RNG-injected, so the rules are unit-testable without a terminal. All tuning
constants live in `karma_rush/config.py`.

Run the test suite:

```
python -m pytest
```
