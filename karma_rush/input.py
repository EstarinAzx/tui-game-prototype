# ============================================================================
# KARMA RUSH — Input
# ============================================================================
# This file is part of the terminal "shell". Its one job is to read the
# keyboard and turn raw keystrokes into plain instructions the game can use.
# It is the ONLY input code that touches "blessed"; the core never sees a key.

# A dataclass bundles the read-out result into one tidy object.
from dataclasses import dataclass, field


# ----------------------------------------------------------------------------
# Intents — what the player asked for this frame
# ----------------------------------------------------------------------------
# "directions" is the set of movement directions held this frame (any of
# "up", "down", "left", "right"). "quit" is True if the player wants to leave.
@dataclass(frozen=True)
class Intents:
    directions: frozenset = field(default_factory=frozenset)
    quit: bool = False


# ----------------------------------------------------------------------------
# read_intents — drain the keyboard buffer and decide what was pressed
# ----------------------------------------------------------------------------
# Each tick we grab every keystroke waiting in the buffer (without blocking).
# While a key is held the terminal keeps repeating it, so a key showing up
# this tick counts as "held this tick"; when it stops repeating, movement
# stops. This keeps the player at a steady speed no matter the key-repeat rate.
def read_intents(term):
    # Collect the directions seen during this buffer drain.
    directions = set()
    # Track whether the player asked to quit.
    quit_requested = False

    # Pull the first waiting keystroke. timeout=0 means "do not wait".
    key = term.inkey(timeout=0)
    # Keep pulling until the buffer is empty (an empty keystroke is falsy).
    while key:
        # Esc asks to quit. blessed may report it by name or as the raw char.
        if key.name == "KEY_ESCAPE" or key == "\x1b":
            quit_requested = True
        else:
            # For normal letters, compare in lower case so caps lock is fine.
            ch = str(key).lower()
            # Q also quits.
            if ch == "q":
                quit_requested = True
            # Up: the up arrow or the W key.
            elif key.name == "KEY_UP" or ch == "w":
                directions.add("up")
            # Down: the down arrow or the S key.
            elif key.name == "KEY_DOWN" or ch == "s":
                directions.add("down")
            # Left: the left arrow or the A key.
            elif key.name == "KEY_LEFT" or ch == "a":
                directions.add("left")
            # Right: the right arrow or the D key.
            elif key.name == "KEY_RIGHT" or ch == "d":
                directions.add("right")

        # Grab the next waiting keystroke for the loop.
        key = term.inkey(timeout=0)

    # Hand back one tidy bundle of what the player wants.
    return Intents(directions=frozenset(directions), quit=quit_requested)
