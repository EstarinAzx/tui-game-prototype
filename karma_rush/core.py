# ============================================================================
# KARMA RUSH — Core engine
# ============================================================================
# This is the brain of the game: all the rules and all the state live here.
# On purpose it imports NOTHING about the terminal — no "blessed", no screen,
# no keyboard, no clock, no files. That keeps it pure, so the tests can drive
# it without ever opening a real terminal window.
#
# Time arrives from the outside as "dt" (how many seconds passed). Randomness
# arrives from the outside as an injected RNG. Because of that, the exact same
# inputs always produce the exact same game — handy for tests.


# ----------------------------------------------------------------------------
# GameState — the whole game in one object
# ----------------------------------------------------------------------------
# GameState holds where the player is and how to advance the game one step.
class GameState:
    # Build a GameState from its pieces. Most code should use GameState.new(...)
    # below instead of calling this directly.
    def __init__(self, config, player):
        # Keep the settings bundle so tick() knows the arena size.
        self._config = config
        # The player's cell as an (x, y) pair: x is the column, y is the row.
        self.player = player

    # Make a brand-new game ready to play.
    # rng is the injected random source; config is the settings bundle.
    @classmethod
    def new(cls, rng, config):
        # The player starts in the middle of the arena.
        center = (config.arena_width // 2, config.arena_height // 2)
        # Hand the finished pieces to the constructor.
        return cls(config=config, player=center)

    # ------------------------------------------------------------------------
    # tick — advance the game by one frame
    # ------------------------------------------------------------------------
    # intents is the set of directions held this frame (any of "up", "down",
    # "left", "right"). dt is how many seconds passed since the last tick.
    # It returns a list of things that happened this frame (empty for now).
    def tick(self, intents, dt):
        # Copy the directions into a set so "in" checks are easy and safe.
        held = set(intents)
        # Work out the sideways step: +1 for right, -1 for left. Holding both
        # at once subtracts to 0, so opposing keys simply cancel out.
        dx = (1 if "right" in held else 0) - (1 if "left" in held else 0)
        # Work out the up/down step the same way. Rows count downward, so
        # "down" adds to y and "up" removes from y.
        dy = (1 if "down" in held else 0) - (1 if "up" in held else 0)
        # Move the player by that step, one cell per axis at most.
        x, y = self.player
        new_x = x + dx
        new_y = y + dy
        # Pin the new position inside the arena walls. Valid cells run from 0
        # up to one less than the arena size; anything outside is clamped back.
        new_x = max(0, min(self._config.arena_width - 1, new_x))
        new_y = max(0, min(self._config.arena_height - 1, new_y))
        self.player = (new_x, new_y)
        # No frame events exist yet in Slice 1, so report an empty list.
        return []
