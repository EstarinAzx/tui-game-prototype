# ------------------ core.py — game rules and state (pure core) ------------ #
# Depends on:
#   - dataclasses (stdlib): frozen dataclass for the Pickup event.
#   - collections.deque (stdlib): BFS queue for the Hunter's spawn search.
#   - karma_rush.maze.Maze: the Wall/Floor layout the run plays on.
#   - karma_rush.hunter.Hunter: the predator GameState owns and advances.
#
# Data shapes:
#   - Pickup: frozen (cell, karma, bonus_seconds) record — one collected item,
#     returned by tick().
#   - GameState: mutable game state — maze, player cell, items dict, the Hunter,
#     score, sanity, elapsed run time, banked bonus time, and run_over /
#     end_reason ("time" | "sanity" | "caught").
#
# This module imports nothing about the terminal (no blessed, screen, keyboard,
# clock, or files). Time and randomness are injected, so identical inputs always
# produce an identical game — which is what makes the core testable.

from collections import deque
from dataclasses import dataclass

from karma_rush.maze import Maze
from karma_rush.hunter import Hunter


# ----------------------- Pickup — collected-item event -------------------- #

# One collected item, returned in tick()'s event list so the shell can react
# (flash, sound). Carries the cell and the revealed karma swing.
@dataclass(frozen=True)
class Pickup:
    # The (x, y) cell the collected item sat on.
    cell: tuple
    # The item's revealed karma: positive swing for good, negative for bad.
    karma: float
    # Bonus time this pickup granted: extra Run seconds, 0 when none.
    bonus_seconds: float = 0.0


# ----------------------- GameState — rules and state ---------------------- #

# The whole game in one object: where things are, plus tick() to advance a frame.
class GameState:
    # Build a GameState from its pieces. Most code should use GameState.new();
    # the hunter is optional so pre-Hunter tests can build a hunterless state.
    def __init__(self, config, player, rng, maze, hunter=None):
        self._config = config
        self._rng = rng
        # The braided maze this run plays on: the Wall/Floor source of truth.
        self.maze = maze
        # Player cell as (x, y): x is the column, y is the row.
        self.player = player
        # The Hunter predator chasing the player; None for a hunterless run.
        self.hunter = hunter
        # Floor items: maps each item's (x, y) cell to its hidden karma swing.
        self.items = {}
        self.score = 0
        # The run's lifeline: drains every second, swings on every pickup.
        self.sanity = config.sanity_start
        # Seconds of run time accumulated so far; the timer counts against this.
        self.elapsed = 0.0
        # Bonus time banked from good-karma pickups; extends the run past
        # run_seconds, uncapped.
        self.bonus_time_total = 0.0
        # Flips True the tick the run ends; the shell watches this.
        self.run_over = False
        # Why the run ended: "time" (clock hit 0) or "sanity" (hit the floor).
        self.end_reason = None

    # Make a brand-new game: generate a fresh maze, place the player on its
    # origin Floor cell, stock the floor with items, and spawn the Hunter as far
    # from the player as the maze allows. Tests may inject their own maze;
    # otherwise one is generated from the same RNG.
    @classmethod
    def new(cls, rng, config, maze=None):
        if maze is None:
            maze = Maze.generate(rng, config)
        state = cls(config=config, player=maze.origin, rng=rng, maze=maze)
        state._refill_items()
        # The Player crosses one cell per frame; the Hunter's step costs more,
        # so it moves at hunter_speed_factor of that pace.
        step_seconds = (1.0 / config.frame_hz) / config.hunter_speed_factor
        spawn = cls._farthest_floor_cell(maze, maze.origin)
        state.hunter = Hunter(
            spawn, step_seconds, rng=rng, sight_range=config.hunter_sight_range
        )
        return state

    # --------------- _farthest_floor_cell — the Hunter's spawn ------------ #

    # The Floor cell at the greatest BFS distance from `start`. A breadth-first
    # flood dequeues cells in non-decreasing distance order, so the last one out
    # is a farthest cell — where the Hunter spawns, as far from the player as
    # the maze allows.
    @staticmethod
    def _farthest_floor_cell(maze, start):
        frontier = deque([start])
        seen = {start}
        farthest = start
        while frontier:
            farthest = frontier.popleft()
            # Sorted so the farthest tie-breaks identically regardless of the
            # neighbour-list order — a deterministic spawn.
            for nbr in sorted(maze.floor_neighbours(farthest)):
                if nbr not in seen:
                    seen.add(nbr)
                    frontier.append(nbr)
        return farthest

    # ------------------ _run_length — total run seconds incl. bonus ------- #

    # The run's full length: the nominal run plus all banked bonus time. The
    # HUD clock and the time-end check both measure against this one value, so
    # they can never disagree on when the run is out of time.
    @property
    def _run_length(self):
        return self._config.run_seconds + self.bonus_time_total

    # ------------------ time_remaining — seconds left on the clock -------- #

    # Seconds left in the run, floored at 0 — the HUD countdown reads this.
    # Banked bonus time extends the total, so this can start a tick above 60.
    @property
    def time_remaining(self):
        return max(0.0, self._run_length - self.elapsed)

    # ----------------- _roll_karma — flip one item's hidden coin ---------- #

    # Roll the injected RNG once: good karma on a win, bad karma otherwise.
    # Hidden at spawn; the player only learns it on pickup.
    def _roll_karma(self):
        cfg = self._config
        if self._rng.random() < cfg.karma_good_chance:
            return cfg.karma_good
        return cfg.karma_bad

    # ----------------- _roll_bonus — roll a good pickup for Bonus time ---- #

    # Roll the injected RNG once: a win grants bonus_time_amount seconds, a miss
    # grants none. Caller rolls this only for a good-karma pickup.
    def _roll_bonus(self):
        cfg = self._config
        if self._rng.random() < cfg.bonus_time_chance:
            return cfg.bonus_time_amount
        return 0.0

    # --------------- _refill_items — restock the floor to item_cap -------- #

    # Spawn items on random empty Floor cells (no player, no other item, no
    # Wall) until the floor holds item_cap.
    def _refill_items(self):
        cfg = self._config
        need = cfg.item_cap - len(self.items)
        if need <= 0:
            return
        # Build the free-cell list once, not once per spawn — chosen cells are
        # dropped from it as we go. Sorted so a seeded RNG picks an identical
        # run regardless of the maze's Floor-set iteration order.
        empty = sorted(
            cell
            for cell in self.maze.floor_cells
            if cell != self.player and cell not in self.items
        )
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
        # The Hunter chases the Player's cell as of the start of this Tick —
        # it advances before the Player moves, so a head-on pass swaps the two
        # cells, which still counts as a catch.
        hunter_old = None
        if self.hunter is not None:
            hunter_old = self.hunter.cell
            self.hunter.advance(self.maze, player=self.player, dt=dt)
        # The Player's cell before this Tick's move — needed to spot a swap.
        player_old = self.player
        held = set(directions)
        # Opposing keys cancel: +1 and -1 sum to 0. Rows count downward, so
        # "down" adds to y and "up" subtracts.
        dx = (1 if "right" in held else 0) - (1 if "left" in held else 0)
        dy = (1 if "down" in held else 0) - (1 if "up" in held else 0)
        x, y = player_old
        # Resolve each axis against Wall cells independently, so the player
        # slides along a wall instead of stopping dead on a blocked diagonal.
        # is_floor is False off-grid too, so this also enforces the arena border.
        new_x = x + dx if dx and self.maze.is_floor((x + dx, y)) else x
        new_y = y + dy if dy and self.maze.is_floor((new_x, y + dy)) else y
        self.player = (new_x, new_y)
        events = []
        # Walking onto an item collects it: score, apply karma, report, restock.
        if self.player in self.items:
            karma = self.items.pop(self.player)
            self.score += 1
            self.sanity += karma
            self._clamp_sanity()
            # Good karma alone rolls for Bonus time; a hit banks extra run
            # seconds and is reported on the Pickup.
            bonus = self._roll_bonus() if karma > 0 else 0.0
            self.bonus_time_total += bonus
            events.append(
                Pickup(cell=self.player, karma=karma, bonus_seconds=bonus)
            )
            self._refill_items()
        # The Hunter catches the Player by landing on the same cell, or by the
        # two swapping cells in one Tick — a head-on pass through each other.
        caught = self.hunter is not None and (
            self.hunter.cell == self.player
            or (hunter_old == self.player and self.hunter.cell == player_old)
        )
        # End the run, in strict priority when more than one trips on a tick:
        # sanity loss, then the Hunter's catch, then the clock — a death always
        # outranks merely running out of time.
        if self.sanity <= self._config.sanity_min:
            self.run_over = True
            self.end_reason = "sanity"
        elif caught:
            self.run_over = True
            self.end_reason = "caught"
        elif self.elapsed >= self._run_length:
            self.run_over = True
            self.end_reason = "time"
        return events
