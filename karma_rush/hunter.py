# ------------------ hunter.py — the Hunter predator (pure core) ----------- #
# Depends on:
#   - karma_rush.maze.Maze: queried (never mutated) for line-of-sight and the
#     BFS hop along a chosen target via has_line_of_sight / path_step.
#
# Data shapes:
#   - Hunter: mutable predator state — current cell, a dt accumulator that
#     paces it to a fraction of Player speed, and last_known (the Player cell
#     last seen, or None until the first sighting).
#
# This module imports nothing about the terminal (no blessed) and reads no real
# clock. Time arrives as dt, the maze as a queryable object, randomness as an
# injected RNG — so a seeded Run moves the Hunter identically every time, which
# is what makes the three-state targeting (chase / memory / wander) testable.


# ----------------------------- Hunter — the predator ---------------------- #

# One AI predator that hunts the Player through the Maze. Built once per Run
# by GameState and advanced every Tick. The targeting is a three-state machine
# resolved per step inside advance: with line of sight the Hunter chases the
# Player and remembers them; without sight but with a memory it heads to that
# last-known cell; with neither it wanders random Floor neighbours until it
# regains sight.
class Hunter:
    # Build a Hunter on a starting cell. step_seconds is the run-time budget one
    # move costs — larger than the Player's per-Tick budget, so the Hunter moves
    # slower than the Player. rng is injected so wander rolls reproduce under a
    # seeded Run. sight_range caps LOS to N Chebyshev cells (None = unlimited):
    # bounding sight to a finite radius is what stops the Hunter from beelining
    # to any Player visible at the far end of a long straight corridor.
    def __init__(self, cell, step_seconds, rng, sight_range=None):
        self.cell = cell
        self._step_seconds = step_seconds
        self._rng = rng
        self._sight_range = sight_range
        # The Player cell the Hunter last saw — None until first sighting; the
        # memory it falls back to when it loses LOS.
        self.last_known = None
        # The far Floor cell the Hunter is patrolling toward when it has no
        # sight and no memory — None until the wander branch first picks one.
        self.patrol_target = None
        # dt banked toward the next move; a move is spent each time it crosses
        # step_seconds, so fractional Ticks accumulate into whole steps.
        self._budget = 0.0

    # ------------------- advance — hunt the Player this Tick -------------- #

    # Bank this Tick's dt and spend it in whole moves. Each move picks a target
    # per the three-state machine — LOS → chase Player and remember; no LOS but
    # memory → head to last_known; neither → wander a random Floor neighbour —
    # then takes one BFS hop toward it.
    def advance(self, maze, player, dt):
        # Cap the bank at two steps' worth. A dt spike — an OS suspend, a
        # window-drag pause, a console QuickEdit pause — otherwise dumps its
        # whole duration into one dt, and the loop below would run a path_step
        # BFS for every backlogged cell, stalling the game on resume. Two
        # steps of catch-up is plenty; the rest of the backlog is dropped.
        self._budget = min(self._budget + dt, 2.0 * self._step_seconds)
        while self._budget >= self._step_seconds:
            self._budget -= self._step_seconds
            hop = self._next_hop(maze, player)
            if hop is None:
                break
            self.cell = hop

    # -------------- _next_hop — pick this step's destination cell --------- #

    # Resolve one step of the three-state targeting machine and return the
    # Floor cell to move to, or None when the Hunter has nowhere meaningful to
    # go (e.g. no Floor neighbours at all — a maze invariant says this never
    # fires, but the guard keeps the loop honest).
    def _next_hop(self, maze, player):
        # Sight: chase the Player's real cell and refresh memory. The
        # range-capped LOS keeps a long open corridor from giving the Hunter
        # a free beeline on a Player it shouldn't be able to spot yet.
        if maze.has_line_of_sight(self.cell, player, max_range=self._sight_range):
            self.last_known = player
            return maze.path_step(self.cell, player)
        # Memory: head to where the Player was last seen. Reaching it with no
        # LOS clears the memory — the trail has run cold — and the next branch
        # picks up to wander.
        if self.last_known is not None:
            if self.cell == self.last_known:
                self.last_known = None
            else:
                return maze.path_step(self.cell, self.last_known)
        # Wander as patrol: pick a far Floor waypoint and BFS toward it; pick a
        # new one once it's reached. Beats pure random wander, which oscillates
        # in 1-wide corridors (50% backtrack every step) — the Hunter sweeps
        # the map instead of bumbling.
        if self.patrol_target is None or self.patrol_target == self.cell:
            self.patrol_target = self._pick_patrol_target(maze)
        if self.patrol_target is None:
            return None
        return maze.path_step(self.cell, self.patrol_target)

    # ------------ _pick_patrol_target — choose a new waypoint ------------- #

    # Choose any Floor cell other than the Hunter's current one. Sorted so the
    # pick reproduces under a seeded RNG regardless of the maze's Floor-set
    # iteration order.
    def _pick_patrol_target(self, maze):
        candidates = sorted(cell for cell in maze.floor_cells if cell != self.cell)
        if not candidates:
            return None
        return self._rng.choice(candidates)
