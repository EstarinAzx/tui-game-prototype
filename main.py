# ============================================================================
# KARMA RUSH — Entry point
# ============================================================================
# This is the file you run: "python main.py". Its only job is to switch the
# terminal into game mode, hand control to the app loop, and — no matter what
# happens — switch the terminal back to normal before the program ends.


# "sys" lets us adjust how text is sent to the terminal.
import sys

# blessed builds the special terminal object the whole shell draws onto.
import blessed

from karma_rush import app, config


# ----------------------------------------------------------------------------
# main — set up the terminal, run the game, always clean up
# ----------------------------------------------------------------------------
def main():
    # The arena is drawn with Unicode box-drawing characters. Some Windows
    # consoles default to an older codepage that cannot print them and would
    # crash. Switching the output stream to UTF-8 makes those characters safe.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        # Older Python or an unusual stream: nothing to do, carry on.
        pass

    # Create the terminal handle blessed uses for drawing and key reading.
    term = blessed.Terminal()

    # Three "with" blocks put the terminal into game mode:
    #   fullscreen     - use a separate screen, restored on exit
    #   cbreak         - send keystrokes through instantly, no Enter needed
    #   hidden_cursor  - hide the blinking text cursor during play
    # The big win: when this "with" ends — even because of an error or a
    # crash — Python automatically undoes all three, so the player's shell
    # is left clean instead of garbled.
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        # Hand control to the game loop, using the Standard settings preset.
        app.run(term, config.DEFAULT)


# Only start the game when this file is run directly, not when imported.
if __name__ == "__main__":
    main()
