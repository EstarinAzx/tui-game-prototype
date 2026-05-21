# --------------- screens.py — full-screen between-run overlays ------------ #
# Depends on:
#   - blessed: the terminal object (term) passed in — supplies colors, cursor
#     moves, and screen size. This module never imports blessed itself.
#   - karma_rush.core.GameState: the finished state read to show the result.
#
# Data shapes:
#   - No types of its own; END_REASON_TEXT maps a core end_reason to its label.
#   - A "screen" is a list of (text, style) lines — style is a term color
#     callable or None — drawn centered by _draw_centered.
#
# The non-arena screens — title, countdown, game-over — kept apart from
# render.py's per-frame arena draw.


# --------------------------- End-reason labels ---------------------------- #

# Maps the core's end_reason flag to the headline shown on the game-over screen.
END_REASON_TEXT = {
    "time": "TIME UP",
    "sanity": "SANITY LOST",
}


# --------------------------- Centered drawing ----------------------------- #

# Draw a block of (text, style) lines centered both ways, in one screen write.
def _draw_centered(term, lines):
    out = [term.home + term.clear]
    # Stack the block vertically centered; each line is centered by its visible
    # text length, so color escapes never throw the horizontal centering off.
    top = max(0, term.height // 2 - len(lines) // 2)
    for offset, (text, style) in enumerate(lines):
        col = max(0, (term.width - len(text)) // 2)
        painted = style(text) if style is not None else text
        out.append(term.move_xy(col, top + offset) + painted)
    # One write so the whole screen appears at once.
    print("".join(out), end="", flush=True)


# ------------------------------ Title screen ------------------------------ #

# Draw the title screen: the game name, the controls, and the "press any key"
# prompt — the player reads the controls before the clock ever runs.
def render_title(term):
    lines = [
        ("KARMA RUSH", term.bold),
        ("", None),
        ("Hoard mysterious items. Survive 60 seconds.", None),
        ("", None),
        ("Move    WASD / Arrow keys", term.dim),
        ("Quit    Q / Esc", term.dim),
        ("", None),
        ("PRESS ANY KEY TO START", term.bold),
    ]
    _draw_centered(term, lines)


# ---------------------------- Countdown screen ---------------------------- #

# Draw one frame of the 3-2-1 countdown: a big digit under a "GET READY" label.
# number is the current Countdown digit.
def render_countdown(term, number):
    lines = [
        ("GET READY", term.dim),
        ("", None),
        (str(number), term.bold),
    ]
    _draw_centered(term, lines)


# ---------------------------- Game-over screen ---------------------------- #

# Draw the game-over screen: why the run ended, the final (frozen) score, and
# the keys to play again or quit. state is the finished GameState.
def render_game_over(term, state):
    headline = END_REASON_TEXT.get(state.end_reason, "GAME OVER")
    # Red headline for a sanity loss, yellow for a clean time-out.
    headline_color = term.red if state.end_reason == "sanity" else term.yellow

    lines = [
        ("GAME OVER", term.bold),
        (headline, headline_color),
        ("", None),
        (f"FINAL SCORE {state.score}", term.bold),
        ("", None),
        ("[R] play again     [Q] quit", term.dim),
    ]
    _draw_centered(term, lines)
