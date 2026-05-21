# ------------------ core.py — game rules and state (pure core) ------------ #
# Depends on:
#   - dataclasses (stdlib): frozen dataclass for the Pickup event.
#
# Data shapes:
#   - Pickup: frozen (cell, karma) record — one collected item, returned by tick().
#   - GameState: mutable game state — player cell, items dict, score, sanity,
#     run_over flag.
#
# This module imports nothing about the terminal (no blessed, screen, keyboard,
# clock, or files). Time and randomness are injected, so identical inputs always
# produce an identical game — which is what makes the core testable.

from dataclasses import dataclass


# ----------------------- Pickup — collected-item event -------------------- #

# One collected item, returned in tick()'s event list so the shell can react
# (flash, sound). Carries the cell and the revealed karma swing.
@dataclass(frozen=True)
class Pickup:
    # The (x, y) cell the collected item sat on.
    cell: tuple
    # The item's revealed karma: positive swing for good, negative for bad.
    karma: float


# ----------------------- GameState — rules and state ---------------------- #

# The whole game in one object: where things are, plus tick() to advance a frame.
class GameState:
    # Build a GameState from its pieces. Most code should use GameState.new().
    def __init__(self, config, player, rng):
        self._config = config
        self._rng = rng
        # Player cell as (x, y): x is the column, y is the row.
        self.player = player
        # Floor items: maps each item's (x, y) cell to its hidden karma swing.
        self.items = {}
        self.score = 0
        # The run's lifeline: drains every second, swings on every pickup.
        self.sanity = config.sanity_start
        # Flips True the tick sanity hits the floor; the shell watches this.
        self.run_over = False

    # Make a brand-new game with the player centered and the floor stocked.
    @classmethod
    def new(cls, rng, config):
        center = (config.arena_width // 2, config.arena_height // 2)
        state = cls(config=config, player=center, rng=rng)
        state._refill_items()
        return state

    # ----------------- _roll_karma — flip one item's hidden coin ---------- #

    # Roll the injected RNG once: good karma on a win, bad karma otherwise.
    # Hidden at spawn; the player only learns it on pickup.
    def _roll_karma(self):
        cfg = self._config
        if self._rng.random() < cfg.karma_good_chance:
            return cfg.karma_good
        return cfg.karma_bad

    # --------------- _refill_items — restock the floor to item_cap -------- #

    # Spawn items on random empty cells (no player, no other item) until the
    # floor holds item_cap.
    def _refill_items(self):
        cfg = self._config
        while len(self.items) < cfg.item_cap:
            empty = [
                (x, y)
                for x in range(cfg.arena_width)
                for y in range(cfg.arena_height)
                if (x, y) != self.player and (x, y) not in self.items
            ]
            # No room left — stop rather than loop forever.
            if not empty:
                return
            cell = self._rng.choice(empty)
            self.items[cell] = self._roll_karma()

    # ---------------- _clamp_sanity — pin sanity to its range ------------- #

    # Pin sanity inside [sanity_min, sanity_max]. Run after every sanity change.
    def _clamp_sanity(self):
        cfg = self._config
        self.sanity = max(cfg.sanity_min, min(cfg.sanity_max, self.sanity))

    # ------------------ tick — advance the game one frame ----------------- #

    # Advance one frame: decay sanity, move the player, collect any item.
    # intents is the set of held directions; dt is seconds since the last tick.
    # Returns the Pickup events from this frame.
    def tick(self, intents, dt):
        # Passive decay scaled by dt — this is the run's real clock.
        self.sanity -= self._config.sanity_decay_per_second * dt
        self._clamp_sanity()
        held = set(intents)
        # Opposing keys cancel: +1 and -1 sum to 0. Rows count downward, so
        # "down" adds to y and "up" subtracts.
        dx = (1 if "right" in held else 0) - (1 if "left" in held else 0)
        dy = (1 if "down" in held else 0) - (1 if "up" in held else 0)
        x, y = self.player
        new_x = x + dx
        new_y = y + dy
        # Clamp inside the walls: valid cells run 0 .. arena_size - 1.
        new_x = max(0, min(self._config.arena_width - 1, new_x))
        new_y = max(0, min(self._config.arena_height - 1, new_y))
        self.player = (new_x, new_y)
        events = []
        # Walking onto an item collects it: score, apply karma, report, restock.
        if self.player in self.items:
            karma = self.items.pop(self.player)
            self.score += 1
            self.sanity += karma
            self._clamp_sanity()
            events.append(Pickup(cell=self.player, karma=karma))
            self._refill_items()
        # Sanity bottoming out ends the run — decay or a bad pickup can trip it
        # in the same tick it happens.
        if self.sanity <= self._config.sanity_min:
            self.run_over = True
        return events
