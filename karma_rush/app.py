# ------------------------- app.py — the game loop ------------------------- #
# Depends on:
#   - time (stdlib): steady clock for measuring frame time and pacing the loop.
#   - random (stdlib): the RNG handed to the core — injected here so test runs
#     stay deterministic; the core never makes its own randomness.
#   - karma_rush.core.GameState: the game rules and state this loop advances.
#   - karma_rush.input: reads the keyboard into Intents.
#   - karma_rush.render: draws each frame and the resize prompt.
#
# Owns the game loop (read keys -> advance -> draw) but holds no game rules —
# those all live in the core.

import time
import random

from karma_rush.core import GameState
from karma_rush import input as game_input
from karma_rush import render


# ------------------------- run — the main game loop ----------------------- #

# Run the game loop until the player quits or the run ends. term is the blessed
# terminal (already in raw mode); config is the settings bundle.
def run(term, config):
    state = GameState.new(random.Random(), config)

    # One frame's budget. 20 ticks/sec -> 0.05s each.
    frame_seconds = 1.0 / config.tick_hz

    last_time = time.monotonic()

    # Tracks the resize-message state so the screen is wiped once on return —
    # the arena is NOT cleared every frame, which would flicker.
    was_too_small = False

    # Pickup flash: transient "+12 / -12" feedback. flash is a (text, is_good)
    # pair or None; flash_remaining counts down its seconds on screen.
    flash = None
    flash_remaining = 0.0

    while True:
        # Case 1: window too small — show the resize prompt instead of a
        # broken arena. The player can still quit.
        if render.is_terminal_too_small(term, config):
            render.render_resize_prompt(term, config)
            was_too_small = True
            intents = game_input.read_intents(term)
            if intents.quit:
                return
            time.sleep(frame_seconds)
            continue

        # Coming back from the resize message — wipe its leftover text once.
        if was_too_small:
            print(term.home + term.clear, end="", flush=True)
            was_too_small = False

        # Case 2: a normal frame. Measure dt — real seconds since last frame.
        frame_start = time.monotonic()
        dt = frame_start - last_time
        last_time = frame_start

        intents = game_input.read_intents(term)
        if intents.quit:
            return

        # Advance one tick; tick reports any items collected this frame.
        events = state.tick(intents.directions, dt)

        # Age an on-screen flash; drop it once its time runs out.
        if flash is not None:
            flash_remaining -= dt
            if flash_remaining <= 0:
                flash = None

        # A pickup starts a fresh flash showing the karma swing. tick collects
        # at most one item per frame; read the last to be safe.
        if events:
            karma = events[-1].karma
            flash = (f"{int(karma):+d}", karma > 0)
            flash_remaining = config.pickup_flash_seconds

        render.render_frame(term, state, config, flash)

        # Sanity at zero ends the run — the final frame is already drawn above.
        if state.run_over:
            return

        # Pace the loop: sleep off whatever is left in the frame budget.
        elapsed = time.monotonic() - frame_start
        leftover = frame_seconds - elapsed
        if leftover > 0:
            time.sleep(leftover)
