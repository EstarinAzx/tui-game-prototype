# ------------------ hunter.py — the Hunter predator (pure core) ----------- #
# Depends on:
#   - karma_rush.maze.Maze: queried (never mutated) for the BFS hop toward the
#     Player via Maze.path_step.
#
# Data shapes:
#   - Hunter: mutable predator state — its current cell and a dt accumulator
#     that paces it to a fraction of Player speed.
#
# This module imports nothing about the terminal (no blessed) and reads no real
# clock. Time arrives as dt, the maze as a queryable object — so a seeded Run
# moves the Hunter identically every time, which is what makes it testable.


# ----------------------------- Hunter — the predator ---------------------- #

# One AI predator that chases the Player through the Maze. Built once per Run
# by GameState and advanced every Tick.
class Hunter:
    # Build a Hunter on a starting cell. step_seconds is the run-time budget one
    # move costs — larger than the Player's per-Tick budget, so the Hunter moves
    # slower than the Player.
    def __init__(self, cell, step_seconds):
        self.cell = cell
        self._step_seconds = step_seconds
        # dt banked toward the next move; a move is spent each time it crosses
        # step_seconds, so fractional Ticks accumulate into whole steps.
        self._budget = 0.0

    # ------------------- advance — chase the target this Tick ------------- #

    # Bank this Tick's dt and spend it in whole moves: each move is one BFS hop
    # along the shortest Floor path toward `target`. A dt below one step's cost
    # buys no move and just accumulates.
    def advance(self, maze, target, dt):
        # Cap the bank at two steps' worth. A dt spike — an OS suspend, a
        # window-drag pause, a console QuickEdit pause — otherwise dumps its
        # whole duration into one dt, and the loop below would run a path_step
        # BFS for every backlogged cell, stalling the game on resume. Two
        # steps of catch-up is plenty; the rest of the backlog is dropped.
        self._budget = min(self._budget + dt, 2.0 * self._step_seconds)
        while self._budget >= self._step_seconds:
            self._budget -= self._step_seconds
            hop = maze.path_step(self.cell, target)
            # No hop means the Hunter already sits on the target — stop rather
            # than burn the rest of the budget going nowhere.
            if hop is None:
                break
            self.cell = hop
