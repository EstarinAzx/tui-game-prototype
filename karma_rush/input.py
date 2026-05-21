# ----------------- input.py — keyboard reading: keys -> Intents ----------- #
# Depends on:
#   - dataclasses (stdlib): frozen dataclass for the Intents result.
#   - blessed: the terminal object (term) passed in — the only input code that
#     touches blessed; the core never sees a key.
#
# Data shapes:
#   - Intents: frozen (directions frozenset, quit bool, restart bool, any_key
#     bool) — the per-frame request.

from dataclasses import dataclass, field


# --------------------- Intents — the per-frame request -------------------- #

# What the player asked for this frame: the directions held, a quit flag, a
# restart flag (R, used only on the game-over screen), and any_key — true when
# at least one key was pressed, which the title screen waits on.
@dataclass(frozen=True)
class Intents:
    directions: frozenset = field(default_factory=frozenset)
    quit: bool = False
    restart: bool = False
    any_key: bool = False


# --------------- read_intents — drain the keyboard buffer ----------------- #

# Drain every keystroke waiting this tick (non-blocking) into one Intents.
# A held key keeps repeating in the buffer, so "seen this tick" == "held this
# tick" — movement stays at a steady speed regardless of key-repeat rate.
def read_intents(term):
    directions = set()
    quit_requested = False
    restart_requested = False
    # Any key at all this tick — set the moment the drain loop runs once.
    any_key_pressed = False

    # timeout=0 means "do not wait" — pull keys until the buffer is empty.
    key = term.inkey(timeout=0)
    while key:
        any_key_pressed = True
        # blessed may report Esc by name or as the raw char.
        if key.name == "KEY_ESCAPE" or key == "\x1b":
            quit_requested = True
        else:
            # Lower-case so caps lock does not matter.
            ch = str(key).lower()
            if ch == "q":
                quit_requested = True
            elif ch == "r":
                restart_requested = True
            elif key.name == "KEY_UP" or ch == "w":
                directions.add("up")
            elif key.name == "KEY_DOWN" or ch == "s":
                directions.add("down")
            elif key.name == "KEY_LEFT" or ch == "a":
                directions.add("left")
            elif key.name == "KEY_RIGHT" or ch == "d":
                directions.add("right")

        key = term.inkey(timeout=0)

    return Intents(
        directions=frozenset(directions),
        quit=quit_requested,
        restart=restart_requested,
        any_key=any_key_pressed,
    )
