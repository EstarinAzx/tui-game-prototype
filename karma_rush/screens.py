# --------------- screens.py — full-screen between-run overlays ------------ #
# Depends on:
#   - blessed: the terminal object (term) passed in — supplies colors, cursor
#     moves, and screen size. This module never imports blessed itself.
#   - karma_rush.core.GameState: the finished state read to show the result.
#
# Data shapes:
#   - No types of its own; END_REASON_TEXT maps a core end_reason to its label.
#
# Between-run screens, kept apart from render.py's per-frame arena draw. Slice
# 5's title and countdown screens will land here too.


# --------------------------- End-reason labels ---------------------------- #

# Maps the core's end_reason flag to the headline shown on the game-over screen.
END_REASON_TEXT = {
    "time": "TIME UP",
    "sanity": "SANITY LOST",
}


# ---------------------------- Game-over screen ---------------------------- #

# Draw the game-over screen: why the run ended, the final (frozen) score, and
# the keys to play again or quit. state is the finished GameState.
def render_game_over(term, state):
    headline = END_REASON_TEXT.get(state.end_reason, "GAME OVER")
    # Red headline for a sanity loss, yellow for a clean time-out.
    headline_color = term.red if state.end_reason == "sanity" else term.yellow

    # Each line is (text, style) — style is a term color callable, or None.
    lines = [
        ("GAME OVER", term.bold),
        (headline, headline_color),
        ("", None),
        (f"FINAL SCORE {state.score}", term.bold),
        ("", None),
        ("[R] play again     [Q] quit", term.dim),
    ]

    out = [term.home + term.clear]
    # Stack the block centered both ways; col is centered by visible text
    # length, so color escapes never throw the centering off.
    top = max(0, term.height // 2 - len(lines) // 2)
    for offset, (text, style) in enumerate(lines):
        col = max(0, (term.width - len(text)) // 2)
        painted = style(text) if style is not None else text
        out.append(term.move_xy(col, top + offset) + painted)

    # One write so the whole screen appears at once.
    print("".join(out), end="", flush=True)
