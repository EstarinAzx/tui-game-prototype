# ----------------- render.py — draw GameState to the terminal ------------- #
# Depends on:
#   - blessed: the terminal object (term) passed in — supplies colors, cursor
#     moves, and screen size. This module never imports blessed itself.
#   - karma_rush.core.GameState: the state read (never mutated) to draw a frame.
#
# Data shapes:
#   - No types of its own; module-level constants hold the box glyphs and the
#     HUD / sanity-bar layout sizes.
#
# Drawing only — never changes the game; the core owns the rules.


# ----------------------- Box glyphs and layout sizes ---------------------- #

# The four corners and two lines used to draw the arena border.
TOP_LEFT = "┌"
TOP_RIGHT = "┐"
BOTTOM_LEFT = "└"
BOTTOM_RIGHT = "┘"
HORIZONTAL = "─"
VERTICAL = "│"

# The player glyph: a solid filled block.
PLAYER_GLYPH = "█"

# The item glyph: a mysterious question mark (its karma is hidden).
ITEM_GLYPH = "?"

# The sanity bar: a fixed-width HUD gauge. Filled cells show sanity remaining,
# empty cells show how much has drained away.
SANITY_BAR_WIDTH = 20
SANITY_BAR_FILLED = "█"
SANITY_BAR_EMPTY = "░"

# Rows kept clear under the arena for the HUD (score line + sanity bar). Counts
# toward the minimum terminal size so the layout never jumps later.
HUD_ROWS = 2


# ----------------- Terminal-size checks and resize prompt ----------------- #

# The window size the game needs: arena interior + border + HUD rows.
# Returns (columns, rows).
def required_terminal_size(config):
    cols = config.arena_width + 2
    rows = config.arena_height + 2 + HUD_ROWS
    return cols, rows


# True when the terminal is narrower or shorter than the game needs.
def is_terminal_too_small(term, config):
    need_cols, need_rows = required_terminal_size(config)
    return term.width < need_cols or term.height < need_rows


# Show a resize instruction instead of a broken, half-drawn arena.
def render_resize_prompt(term, config):
    need_cols, need_rows = required_terminal_size(config)
    line1 = "Terminal too small for KARMA RUSH."
    line2 = f"Please resize to at least {need_cols} x {need_rows} and restart."
    out = [term.home + term.clear]
    # Center both lines roughly in the middle of the window.
    mid_row = max(0, term.height // 2 - 1)
    for offset, text in enumerate((line1, line2)):
        col = max(0, (term.width - len(text)) // 2)
        out.append(term.move_xy(col, mid_row + offset) + text)
    # One write so it all appears at once.
    print("".join(out), end="", flush=True)


# --------------------------- Frame rendering ------------------------------ #

# Pick the HUD color for the current sanity: green high, yellow mid, red low.
def _sanity_color(term, sanity, config):
    if sanity > config.sanity_green_above:
        return term.green
    if sanity >= config.sanity_yellow_above:
        return term.yellow
    return term.red


# Draw one frame: bordered arena, item glyphs, player block, and the HUD
# (score + optional pickup flash, color-coded sanity bar). The whole frame is
# redrawn every tick, so old positions paint over and no trail is left.
# flash, when given, is a (text, is_good) pair — None for no flash.
def render_frame(term, state, config, flash=None):
    width = config.arena_width
    height = config.arena_height
    box_w = width + 2
    box_h = height + 2
    # Center the box; big windows just letterbox.
    origin_x = max(0, (term.width - box_w) // 2)
    origin_y = max(0, (term.height - box_h) // 2)

    px, py = state.player

    # Build the screen as a list of pieces, then write it all at once.
    out = []

    top = TOP_LEFT + HORIZONTAL * width + TOP_RIGHT
    out.append(term.move_xy(origin_x, origin_y) + term.dim(top))

    for row in range(height):
        cells = [" "] * width
        for ix, iy in state.items:
            if iy == row:
                cells[ix] = term.yellow(ITEM_GLYPH)
        # Player drawn last so it sits on top of anything else.
        if row == py:
            cells[px] = term.cyan(PLAYER_GLYPH)
        out.append(
            term.move_xy(origin_x, origin_y + 1 + row)
            + term.dim(VERTICAL)
            + "".join(cells)
            + term.dim(VERTICAL)
        )

    bottom = BOTTOM_LEFT + HORIZONTAL * width + BOTTOM_RIGHT
    out.append(term.move_xy(origin_x, origin_y + box_h - 1) + term.dim(bottom))

    # HUD row 0: the score, with an optional pickup flash beside it.
    row0 = f"SCORE {state.score}"
    if flash is not None:
        flash_text, flash_good = flash
        flash_color = term.green if flash_good else term.red
        row0 += "   " + flash_color(flash_text)
    # Pad by visible length — term.length ignores invisible color escape bytes.
    pad0 = " " * max(0, width - term.length(row0))
    out.append(term.move_xy(origin_x, origin_y + box_h) + row0 + pad0)

    # HUD row 1: the sanity bar, filled in proportion to sanity and colored by
    # danger level, followed by the rounded sanity number.
    fraction = max(0.0, min(1.0, state.sanity / config.sanity_max))
    filled = round(fraction * SANITY_BAR_WIDTH)
    bar = SANITY_BAR_FILLED * filled + SANITY_BAR_EMPTY * (SANITY_BAR_WIDTH - filled)
    color = _sanity_color(term, state.sanity, config)
    row1 = f"SANITY {color(bar)} {round(state.sanity):3d}"
    pad1 = " " * max(0, width - term.length(row1))
    out.append(term.move_xy(origin_x, origin_y + box_h + 1) + row1 + pad1)

    # Send the whole frame to the terminal in a single write.
    print("".join(out), end="", flush=True)
