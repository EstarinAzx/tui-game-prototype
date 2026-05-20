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

# How many rows under the arena are kept clear for the HUD (added in Slice 2).
# It counts toward the minimum terminal size so the layout never jumps later.
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
# render_frame — draw one frame of the running game
# ----------------------------------------------------------------------------
# Draws the bordered arena and the cyan player block. The whole arena is
# redrawn every frame, so the player's old position is painted over and no
# trail is left behind. The arena is centered, so big windows just letterbox.
def render_frame(term, state, config):
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
        # By default the whole floor row is empty space.
        if row == py:
            # On the player's row, drop the cyan block at the player's column.
            interior = (
                " " * px
                + term.cyan(PLAYER_GLYPH)
                + " " * (width - px - 1)
            )
        else:
            # Every other row is just blank floor.
            interior = " " * width
        # Move to the row's start and draw wall + floor + wall.
        out.append(
            term.move_xy(origin_x, origin_y + 1 + row)
            + term.dim(VERTICAL)
            + interior
            + term.dim(VERTICAL)
        )

    # The bottom border line, drawn the same way as the top.
    bottom = BOTTOM_LEFT + HORIZONTAL * width + BOTTOM_RIGHT
    out.append(term.move_xy(origin_x, origin_y + box_h - 1) + term.dim(bottom))

    # Send the whole frame to the terminal in a single write.
    print("".join(out), end="", flush=True)
