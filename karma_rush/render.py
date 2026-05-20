# ============================================================================
# KARMA RUSH — Render
# ============================================================================
# This file is part of the terminal "shell". Its job is to take a GameState
# and paint it onto the screen: the arena walls and the player block. It also
# shows a "resize" message when the terminal window is too small to fit.
# This is drawing only — it never changes the game; the core owns the rules.


# ----------------------------------------------------------------------------
# Box-drawing pieces and layout sizes
# ----------------------------------------------------------------------------
# The four corners and two lines used to draw the arena border.
TOP_LEFT = "┌"
TOP_RIGHT = "┐"
BOTTOM_LEFT = "└"
BOTTOM_RIGHT = "┘"
HORIZONTAL = "─"
VERTICAL = "│"

# The character used for the player: a solid filled block.
PLAYER_GLYPH = "█"

# The character used for an item: a mysterious question mark.
ITEM_GLYPH = "?"

# The sanity bar: a fixed-width gauge drawn in the HUD. Filled cells show the
# sanity that remains; empty cells show how much has drained away.
SANITY_BAR_WIDTH = 20
SANITY_BAR_FILLED = "█"
SANITY_BAR_EMPTY = "░"

# How many rows under the arena are kept clear for the HUD. Row 0 holds the
# score and the pickup flash; row 1 holds the sanity bar. It counts toward the
# minimum terminal size so the layout never jumps later.
HUD_ROWS = 2


# ----------------------------------------------------------------------------
# required_terminal_size — how big the window must be
# ----------------------------------------------------------------------------
# The arena box is the interior plus a one-cell border on every side, and the
# HUD needs a couple of rows under it. Returns (columns, rows) needed.
def required_terminal_size(config):
    cols = config.arena_width + 2
    rows = config.arena_height + 2 + HUD_ROWS
    return cols, rows


# ----------------------------------------------------------------------------
# is_terminal_too_small — does the window fit the game?
# ----------------------------------------------------------------------------
# Returns True when the terminal is narrower or shorter than the game needs.
def is_terminal_too_small(term, config):
    need_cols, need_rows = required_terminal_size(config)
    return term.width < need_cols or term.height < need_rows


# ----------------------------------------------------------------------------
# render_resize_prompt — ask the player to make the window bigger
# ----------------------------------------------------------------------------
# Shown instead of the arena when the window is too small, so the player sees
# a clear instruction rather than a broken, half-drawn arena.
def render_resize_prompt(term, config):
    need_cols, need_rows = required_terminal_size(config)
    # Two short lines of text to show.
    line1 = "Terminal too small for KARMA RUSH."
    line2 = f"Please resize to at least {need_cols} x {need_rows} and restart."
    # Start from a fully blank screen.
    out = [term.home + term.clear]
    # Put each line roughly in the vertical middle, centered left-to-right.
    mid_row = max(0, term.height // 2 - 1)
    for offset, text in enumerate((line1, line2)):
        col = max(0, (term.width - len(text)) // 2)
        out.append(term.move_xy(col, mid_row + offset) + text)
    # Paint it all in one write so it appears at once.
    print("".join(out), end="", flush=True)


# ----------------------------------------------------------------------------
# _sanity_color — pick the HUD color for the current sanity level
# ----------------------------------------------------------------------------
# The sanity bar is a danger gauge: green when comfortably high, yellow in the
# middle, red when sanity is low enough to threaten the run. Returns a blessed
# color callable that wraps text in the right color.
def _sanity_color(term, sanity, config):
    if sanity > config.sanity_green_above:
        return term.green
    if sanity >= config.sanity_yellow_above:
        return term.yellow
    return term.red


# ----------------------------------------------------------------------------
# render_frame — draw one frame of the running game
# ----------------------------------------------------------------------------
# Draws the bordered arena, the yellow item glyphs, the cyan player block, and
# the HUD under the arena: a score line with an optional pickup flash, and a
# color-coded sanity bar. The whole frame is redrawn every tick, so old
# positions are painted over and no trail is left. The arena is centered, so
# big windows just letterbox.
#
# flash, when given, is a (text, is_good) pair — the "+12" / "-12" pickup
# feedback; is_good picks green vs red. Pass None for no flash.
def render_frame(term, state, config, flash=None):
    width = config.arena_width
    height = config.arena_height
    # The box is the interior plus one border cell on each side.
    box_w = width + 2
    box_h = height + 2
    # Find the top-left corner that centers the box in the window.
    origin_x = max(0, (term.width - box_w) // 2)
    origin_y = max(0, (term.height - box_h) // 2)

    # The player's cell, as a column and a row inside the arena.
    px, py = state.player

    # Build the screen as a list of pieces, then write it all at once.
    out = []

    # The top border line: a left corner, a run of dashes, a right corner.
    top = TOP_LEFT + HORIZONTAL * width + TOP_RIGHT
    out.append(term.move_xy(origin_x, origin_y) + term.dim(top))

    # Each interior row: a side wall, the floor, then a side wall.
    for row in range(height):
        # Start the row as bare floor, one cell per column.
        cells = [" "] * width
        # Drop a yellow "?" on every item that sits on this row.
        for ix, iy in state.items:
            if iy == row:
                cells[ix] = term.yellow(ITEM_GLYPH)
        # The player draws last so it sits on top of anything else.
        if row == py:
            cells[px] = term.cyan(PLAYER_GLYPH)
        # Move to the row's start and draw wall + floor + wall.
        out.append(
            term.move_xy(origin_x, origin_y + 1 + row)
            + term.dim(VERTICAL)
            + "".join(cells)
            + term.dim(VERTICAL)
        )

    # The bottom border line, drawn the same way as the top.
    bottom = BOTTOM_LEFT + HORIZONTAL * width + BOTTOM_RIGHT
    out.append(term.move_xy(origin_x, origin_y + box_h - 1) + term.dim(bottom))

    # --- HUD row 0: the score, with an optional pickup flash beside it ---
    # The flash carries color codes, so pad by visible length (term.length)
    # to clear the rest of the row without counting invisible escape bytes.
    row0 = f"SCORE {state.score}"
    if flash is not None:
        flash_text, flash_good = flash
        flash_color = term.green if flash_good else term.red
        row0 += "   " + flash_color(flash_text)
    pad0 = " " * max(0, width - term.length(row0))
    out.append(term.move_xy(origin_x, origin_y + box_h) + row0 + pad0)

    # --- HUD row 1: the color-coded sanity bar ---
    # The bar is filled in proportion to sanity, colored by danger level, and
    # followed by the rounded sanity number.
    fraction = max(0.0, min(1.0, state.sanity / config.sanity_max))
    filled = round(fraction * SANITY_BAR_WIDTH)
    bar = SANITY_BAR_FILLED * filled + SANITY_BAR_EMPTY * (SANITY_BAR_WIDTH - filled)
    color = _sanity_color(term, state.sanity, config)
    row1 = f"SANITY {color(bar)} {round(state.sanity):3d}"
    pad1 = " " * max(0, width - term.length(row1))
    out.append(term.move_xy(origin_x, origin_y + box_h + 1) + row1 + pad1)

    # Send the whole frame to the terminal in a single write.
    print("".join(out), end="", flush=True)
