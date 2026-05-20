# ============================================================================
# KARMA RUSH — App / orchestration
# ============================================================================
# This file is part of the terminal "shell". It owns the game loop: the
# repeating cycle of "read keys -> advance the game -> draw the screen".
# It wires the three layers together — input, core, render — but holds no
# game rules itself. The rules all live in the core.


# "time" gives us a steady clock for measuring how long each frame took and
# for pausing so the loop runs at a fixed speed.
import time
# "random" is the random source we hand to the core. The core never makes its
# own randomness — we inject it here so test runs can stay predictable.
import random

from karma_rush.core import GameState
from karma_rush import input as game_input
from karma_rush import render


# ----------------------------------------------------------------------------
# run — the main game loop
# ----------------------------------------------------------------------------
# Keeps looping until the player asks to quit. "term" is the blessed terminal,
# already set to raw mode by the entry point. "config" is the settings bundle.
def run(term, config):
    # Build a fresh game. The core gets its randomness from this RNG.
    state = GameState.new(random.Random(), config)

    # How long one frame should last. 20 ticks per second -> 0.05s each.
    frame_seconds = 1.0 / config.tick_hz

    # Remember the clock reading from the previous frame, to measure "dt".
    last_time = time.monotonic()

    # Remember whether last frame showed the "resize" message, so we can wipe
    # the screen once when switching back to the arena (and avoid flicker
    # during normal play by NOT clearing every frame).
    was_too_small = False

    # Pickup flash state: the transient "+12 / -12" feedback shown for a short
    # while after a collection. `flash` is a (text, is_good) pair or None;
    # `flash_remaining` counts down the seconds it stays on screen.
    flash = None
    flash_remaining = 0.0

    # The loop runs forever until a "return" below ends it.
    while True:
        # --- Case 1: the window is too small to fit the arena ---
        if render.is_terminal_too_small(term, config):
            # Show the resize message instead of a broken arena.
            render.render_resize_prompt(term, config)
            was_too_small = True
            # The player can still quit while the message is up.
            intents = game_input.read_intents(term)
            if intents.quit:
                return
            # Wait out the frame, then check the window size again.
            time.sleep(frame_seconds)
            continue

        # --- Coming back from the resize message ---
        # The message left text on screen; wipe it once before drawing again.
        if was_too_small:
            print(term.home + term.clear, end="", flush=True)
            was_too_small = False

        # --- Case 2: a normal frame of the running game ---
        # Mark when this frame started, for pacing at the end.
        frame_start = time.monotonic()
        # Measure how many real seconds passed since the last frame ("dt").
        dt = frame_start - last_time
        last_time = frame_start

        # Read the keyboard for this frame.
        intents = game_input.read_intents(term)
        # Quitting (Q or Esc) ends the loop right away.
        if intents.quit:
            return

        # Advance the game one tick, passing the held directions and dt.
        # tick reports back any items collected this frame.
        events = state.tick(intents.directions, dt)

        # Age a flash already on screen; drop it once its time runs out.
        if flash is not None:
            flash_remaining -= dt
            if flash_remaining <= 0:
                flash = None

        # A pickup this frame starts a fresh flash showing the karma swing.
        # tick collects at most one item per frame; read the last to be safe.
        if events:
            karma = events[-1].karma
            flash = (f"{int(karma):+d}", karma > 0)
            flash_remaining = config.pickup_flash_seconds

        # Draw the new picture, including any active pickup flash.
        render.render_frame(term, state, config, flash)

        # Sanity hitting zero ends the run immediately: the final frame is
        # already drawn above, so stop the loop now.
        if state.run_over:
            return

        # --- Pace the loop so it runs at a steady 20 ticks per second ---
        # Sleep off whatever time is left in this frame's budget.
        elapsed = time.monotonic() - frame_start
        leftover = frame_seconds - elapsed
        if leftover > 0:
            time.sleep(leftover)
