# --------------------------- main.py — entry point ------------------------ #
# Depends on:
#   - sys (stdlib): reconfigure stdout to UTF-8 for the box-drawing glyphs.
#   - blessed: builds the terminal object the whole shell draws onto.
#   - karma_rush.app: the game loop control is handed to.
#   - karma_rush.config: supplies the DEFAULT settings preset.
#
# Run with "python main.py". Switches the terminal into game mode, runs the
# loop, and always restores the terminal before the program ends.

import sys

import blessed

from karma_rush import app, config


# ------------------- main — set up the terminal, run, clean up ------------ #

# Put the terminal into game mode, run the game, and always restore it after.
def main():
    # The arena uses Unicode box-drawing glyphs; some Windows consoles default
    # to an older codepage that cannot print them. UTF-8 makes them safe.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        # Older Python or an unusual stream — nothing to do, carry on.
        pass

    term = blessed.Terminal()

    # The three context managers (fullscreen, cbreak, hidden_cursor) put the
    # terminal into game mode and — even on a crash — undo all three on exit,
    # leaving the player's shell clean instead of garbled.
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        app.run(term, config.DEFAULT)


# Only start the game when this file is run directly, not when imported.
if __name__ == "__main__":
    main()
