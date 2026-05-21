# ------------------------- app.py — the game loop ------------------------- #
# Depends on:
#   - time (stdlib): steady clock for measuring frame time and pacing the loop.
#   - random (stdlib): the RNG handed to the core — injected here so test runs
#     stay deterministic; the core never makes its own randomness.
#   - karma_rush.core.GameState: the game rules and state this loop advances.
#   - karma_rush.countdown.Countdown: the pre-run 3-2-1 timer.
#   - karma_rush.input: reads the keyboard into Intents.
#   - karma_rush.render: draws each frame and the resize prompt.
#   - karma_rush.screens: draws the title, countdown, and game-over screens.
#
# Owns the app state machine — TITLE -> COUNTDOWN -> PLAYING -> GAMEOVER, with
# R looping GAMEOVER -> COUNTDOWN — and the per-phase loops, but holds no game
# rules: those all live in the core.

import time
import random

from karma_rush.core import GameState
from karma_rush.countdown import Countdown
from karma_rush import input as game_input
from karma_rush import render
from karma_rush import screens


# ------------------------- The app state machine ------------------------- #

# The four phases the app moves through. TITLE waits for a key, COUNTDOWN runs
# the 3-2-1, PLAYING is one run, GAMEOVER is the end screen.
TITLE = "title"
COUNTDOWN = "countdown"
PLAYING = "playing"
GAMEOVER = "gameover"

# Transition table: (phase, outcome) -> next phase. The outcome is whatever the
# phase's handler returned. Quit is handled separately — it ends from anywhere.
_TRANSITIONS = {
    (TITLE, "start"): COUNTDOWN,
    (COUNTDOWN, "play"): PLAYING,
    (PLAYING, "ended"): GAMEOVER,
    (GAMEOVER, "restart"): COUNTDOWN,
}


# Given the phase just finished and its outcome, return the next phase — or
# None to quit, which any phase can yield.
def next_phase(phase, outcome):
    # Quit short-circuits the table — every phase can bail out the same way.
    if outcome == "quit":
        return None
    return _TRANSITIONS[(phase, outcome)]


# ----------------------- run — drive the state machine ------------------- #

# Run the app: step through phases until one yields a quit. term is the blessed
# terminal (already in raw mode); config is the settings bundle.
def run(term, config):
    phase = TITLE
    # The finished GameState, carried from PLAYING into GAMEOVER.
    state = None

    while phase is not None:
        if phase == TITLE:
            outcome = _title(term, config)
        elif phase == COUNTDOWN:
            outcome = _countdown(term, config)
        elif phase == PLAYING:
            state = _play_run(term, config)
            # _play_run returns None on a mid-run quit, else the finished run.
            outcome = "quit" if state is None else "ended"
        else:  # GAMEOVER
            outcome = "restart" if _game_over(term, config, state) else "quit"

        phase = next_phase(phase, outcome)


# ------------------------- _title — the title screen --------------------- #

# Show the title screen and wait. Returns "start" on any key, "quit" on Q/Esc.
def _title(term, config):
    screens.render_title(term)
    frame_seconds = 1.0 / config.tick_hz

    while True:
        intents = game_input.read_intents(term)
        # Q/Esc checked before any_key so quitting beats starting on that key.
        if intents.quit:
            return "quit"
        if intents.any_key:
            return "start"
        # Idle at the frame rate so the wait does not spin the CPU.
        time.sleep(frame_seconds)


# --------------------- _countdown — the 3-2-1 countdown ------------------ #

# Play the 3-2-1 countdown before a run. Returns "play" when it finishes, or
# "quit" if the player bails out with Q/Esc.
def _countdown(term, config):
    countdown = Countdown(config.countdown_seconds)
    frame_seconds = 1.0 / config.tick_hz
    last_time = time.monotonic()

    while True:
        frame_start = time.monotonic()
        dt = frame_start - last_time
        last_time = frame_start

        intents = game_input.read_intents(term)
        if intents.quit:
            return "quit"

        countdown.tick(dt)
        # Finished — start the run without ever painting a "0" frame.
        if countdown.done:
            return "play"
        screens.render_countdown(term, countdown.number)

        # Pace the loop: sleep off whatever is left in the frame budget.
        leftover = frame_seconds - (time.monotonic() - frame_start)
        if leftover > 0:
            time.sleep(leftover)


# ----------------------- _play_run — one full run ------------------------- #

# Play one run start to finish. Returns the finished GameState when the run
# ends (clock or sanity), or None if the player quit mid-run.
def _play_run(term, config):
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
                return None
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
            return None

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

        # The run ended (clock or sanity) — the final frame is drawn above;
        # hand the frozen state back for the game-over screen.
        if state.run_over:
            return state

        # Pace the loop: sleep off whatever is left in the frame budget.
        elapsed = time.monotonic() - frame_start
        leftover = frame_seconds - elapsed
        if leftover > 0:
            time.sleep(leftover)


# ---------------------- _game_over — the end-of-run wait ------------------ #

# Show the game-over screen and wait for the player's choice. Returns True to
# play again (R) or False to quit (Q/Esc). state is the finished GameState.
def _game_over(term, config, state):
    screens.render_game_over(term, state)
    frame_seconds = 1.0 / config.tick_hz

    while True:
        intents = game_input.read_intents(term)
        if intents.quit:
            return False
        if intents.restart:
            return True
        # Idle at the frame rate so the wait does not spin the CPU.
        time.sleep(frame_seconds)
