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

# A dataclass bundles a few named values into one tidy object.
from dataclasses import dataclass


# ----------------------------------------------------------------------------
# Pickup — a thing that happened: the player collected an item
# ----------------------------------------------------------------------------
# tick() returns a list of these so the shell can react (flash, sound, ...).
# For now it just carries the cell the item was collected from.
@dataclass(frozen=True)
class Pickup:
    # The (x, y) cell the collected item sat on.
    cell: tuple


# ----------------------------------------------------------------------------
# GameState — the whole game in one object
# ----------------------------------------------------------------------------
# GameState holds where the player is and how to advance the game one step.
class GameState:
    # Build a GameState from its pieces. Most code should use GameState.new(...)
    # below instead of calling this directly.
    def __init__(self, config, player, rng):
        # Keep the settings bundle so tick() knows the arena size.
        self._config = config
        # Keep the injected RNG so the spawner can pick empty cells later.
        self._rng = rng
        # The player's cell as an (x, y) pair: x is the column, y is the row.
        self.player = player
        # The set of item cells currently on the floor.
        self.items = set()
        # How many items the player has collected this run.
        self.score = 0

    # Make a brand-new game ready to play.
    # rng is the injected random source; config is the settings bundle.
    @classmethod
    def new(cls, rng, config):
        # The player starts in the middle of the arena.
        center = (config.arena_width // 2, config.arena_height // 2)
        # Build the game, then stock the floor up to the item cap.
        state = cls(config=config, player=center, rng=rng)
        state._refill_items()
        return state

    # ------------------------------------------------------------------------
    # _refill_items — top the floor back up to the item cap
    # ------------------------------------------------------------------------
    # Spawns items at random empty cells until the floor holds item_cap of
    # them. An empty cell is one with neither the player nor another item on
    # it. If the arena has no room left, it simply stops early.
    def _refill_items(self):
        cfg = self._config
        while len(self.items) < cfg.item_cap:
            # Every floor cell that is free to take a new item.
            empty = [
                (x, y)
                for x in range(cfg.arena_width)
                for y in range(cfg.arena_height)
                if (x, y) != self.player and (x, y) not in self.items
            ]
            # No room left — stop rather than loop forever.
            if not empty:
                return
            # Pick one free cell with the injected RNG and place an item.
            self.items.add(self._rng.choice(empty))

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
        # Things that happened this frame, reported back to the shell.
        events = []
        # If the player landed on an item, collect it: take it off the floor,
        # score the pickup, and spawn a replacement to keep the floor stocked.
        if self.player in self.items:
            self.items.discard(self.player)
            self.score += 1
            events.append(Pickup(cell=self.player))
            self._refill_items()
        return events
