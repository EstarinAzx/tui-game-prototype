# ------------------ core.py — game rules and state (pure core) ------------ #
# Depends on:
#   - dataclasses (stdlib): frozen dataclass for the Pickup event.
#
# Data shapes:
#   - Pickup: frozen (cell, karma) record — one collected item, returned by tick().
#   - GameState: mutable game state — player cell, items dict, score, sanity,
#     elapsed run time, and run_over / end_reason ("time" | "sanity").
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
        # Seconds of run time accumulated so far; the timer counts against this.
        self.elapsed = 0.0
        # Flips True the tick the run ends; the shell watches this.
        self.run_over = False
        # Why the run ended: "time" (clock hit 0) or "sanity" (hit the floor).
        self.end_reason = None

    # Make a brand-new game with the player centered and the floor stocked.
    @classmethod
    def new(cls, rng, config):
        center = (config.arena_width // 2, config.arena_height // 2)
        state = cls(config=config, player=center, rng=rng)
        state._refill_items()
        return state

    # ------------------ time_remaining — seconds left on the clock -------- #

    # Seconds left in the run, floored at 0 — the HUD countdown reads this.
    @property
    def time_remaining(self):
        return max(0.0, self._config.run_seconds - self.elapsed)

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
        need = cfg.item_cap - len(self.items)
        if need <= 0:
            return
        # Build the free-cell list once, not once per spawn — chosen cells are
        # dropped from it as we go. Same cells in the same order as the old
        # per-spawn rebuild, so a seeded RNG still picks an identical run.
        empty = [
            (x, y)
            for x in range(cfg.arena_width)
            for y in range(cfg.arena_height)
            if (x, y) != self.player and (x, y) not in self.items
        ]
        for _ in range(need):
            # No room left — stop rather than loop forever.
            if not empty:
                return
            cell = self._rng.choice(empty)
            empty.remove(cell)
            self.items[cell] = self._roll_karma()

    # ---------------- _clamp_sanity — pin sanity to its range ------------- #

    # Pin sanity inside [sanity_min, sanity_max]. Run after every sanity change.
    def _clamp_sanity(self):
        cfg = self._config
        self.sanity = max(cfg.sanity_min, min(cfg.sanity_max, self.sanity))

    # ------------------ tick — advance the game one frame ----------------- #

    # Advance one frame: decay sanity, move the player, collect any item.
    # directions is the set of held directions; dt is seconds since the last
    # tick. Returns the Pickup events from this frame.
    def tick(self, directions, dt):
        # Once the run is over, freeze everything — a late tick changes nothing,
        # so the game-over screen shows the score and clock at the end moment.
        if self.run_over:
            return []
        # dt is the run's real clock — accumulate it toward run_seconds.
        self.elapsed += dt
        # Passive decay scaled by dt.
        self.sanity -= self._config.sanity_decay_per_second * dt
        self._clamp_sanity()
        held = set(directions)
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
        # End the run: sanity loss takes priority over the clock when both
        # trip in the same tick — losing beats running out the timer.
        if self.sanity <= self._config.sanity_min:
            self.run_over = True
            self.end_reason = "sanity"
        elif self.elapsed >= self._config.run_seconds:
            self.run_over = True
            self.end_reason = "time"
        return events
