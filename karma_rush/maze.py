# ------------------ maze.py — braided maze generation (pure core) --------- #
# Depends on:
#   - karma_rush.config.Config: supplies arena dimensions and the braid factor.
#
# Data shapes:
#   - Maze: an immutable Wall/Floor layout filling the Arena interior. Queryable
#     for Wall vs Floor, a cell's Floor neighbours, the full Floor-cell set, and
#     the canonical Player-start cell (the origin).
#
# This module imports nothing about the terminal (no blessed) and reads no real
# clock. Randomness is injected as an RNG, so a seeded Run reproduces an
# identical Maze — which is what makes generation testable.

from collections import deque


# ------------------------- Adjacency step vectors ------------------------- #

# The four orthogonal directions, as (dx, dy). Two-cell steps reach the next
# room; the cell halfway between is the connector carved to link them.
_STEPS = ((2, 0), (-2, 0), (0, 2), (0, -2))


# ----------------------------- Maze — the layout -------------------------- #

# A generated braided maze: corridors loop, no dead ends. Built once by
# Maze.generate and never mutated afterwards.
class Maze:
    # Build a Maze from its dimensions and the set of Floor cells. Most code
    # should use Maze.generate(); the plain constructor exists for tests that
    # need a hand-built layout.
    def __init__(self, width, height, floor_cells):
        self.width = width
        self.height = height
        self._floor = frozenset(floor_cells)

    # ------------------ origin — the canonical Player start --------------- #

    # The Maze origin: corner (0, 0). Even coords, so generation always carves
    # it as a room — a guaranteed Floor cell for the Player to start on.
    @property
    def origin(self):
        return (0, 0)

    # ------------------ floor_cells — the full Floor set ------------------ #

    # Every Floor cell of the Maze. Movement, spawning, and pathfinding all
    # read this one source of truth.
    @property
    def floor_cells(self):
        return self._floor

    # --------------------- is_floor / is_wall — queries ------------------- #

    # True when the cell is an open, enterable Floor cell.
    def is_floor(self, cell):
        return cell in self._floor

    # True when the cell is blocked — a Wall, or outside the Maze entirely.
    def is_wall(self, cell):
        return cell not in self._floor

    # ---------------- floor_neighbours — adjacent Floor cells ------------- #

    # The orthogonally adjacent cells of `cell` that are Floor.
    def floor_neighbours(self, cell):
        x, y = cell
        adjacent = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
        return [n for n in adjacent if n in self._floor]

    # -------------------- path_step — one BFS hop toward a goal ----------- #

    # The next cell on a shortest Floor path from `start` toward `goal` — the
    # single hop the Hunter takes each move. Returns None when already on the
    # goal, or when no Floor path connects the two (a Wall goal included, since
    # BFS only ever crosses Floor).
    def path_step(self, start, goal):
        if start == goal:
            return None
        # BFS out from start; came_from records each cell's predecessor so the
        # shortest path can be walked back once goal is reached.
        frontier = deque([start])
        came_from = {start: None}
        while frontier:
            cell = frontier.popleft()
            if cell == goal:
                break
            for nbr in self.floor_neighbours(cell):
                if nbr not in came_from:
                    came_from[nbr] = cell
                    frontier.append(nbr)
        if goal not in came_from:
            return None
        # Walk the predecessor chain back from goal; the cell whose predecessor
        # is start is the first hop.
        cell = goal
        while came_from[cell] != start:
            cell = came_from[cell]
        return cell

    # ----------------------- generate — build a Maze ---------------------- #

    # Generate a fresh braided Maze sized to the config, using only the
    # injected RNG. Two passes: carve a perfect maze, then braid out dead ends.
    @classmethod
    def generate(cls, rng, config):
        width = config.arena_width
        height = config.arena_height
        floor = cls._carve_perfect_maze(rng, width, height)
        cls._braid(rng, floor, width, height, config.maze_braid_factor)
        return cls(width, height, floor)

    # ------------------ _carve_perfect_maze — DFS pass -------------------- #

    # Randomized depth-first search (recursive backtracker): rooms sit on
    # even coords; carve the connector between a room and a random unvisited
    # neighbour room. Produces a perfect maze — exactly one path between any
    # two cells. Returns the set of Floor cells.
    @staticmethod
    def _carve_perfect_maze(rng, width, height):
        floor = {(0, 0)}
        visited = {(0, 0)}
        stack = [(0, 0)]
        while stack:
            cx, cy = stack[-1]
            unvisited = [
                (cx + sx, cy + sy, sx, sy)
                for sx, sy in _STEPS
                if 0 <= cx + sx < width
                and 0 <= cy + sy < height
                and (cx + sx, cy + sy) not in visited
            ]
            if not unvisited:
                stack.pop()
                continue
            nx, ny, sx, sy = rng.choice(unvisited)
            # Carve the connector cell and the destination room.
            floor.add((cx + sx // 2, cy + sy // 2))
            floor.add((nx, ny))
            visited.add((nx, ny))
            stack.append((nx, ny))
        return floor

    # ------------------------- _braid — loop pass ------------------------- #

    # Remove dead ends: a perfect maze has rooms with a single passage, which
    # would trap the Player against a chasing Hunter. For each dead-end room,
    # carve one more connector so every Floor cell has at least two neighbours.
    # Mutates `floor` in place.
    @staticmethod
    def _braid(rng, floor, width, height, braid_factor):
        # Only rooms (even, even) can dead-end; connectors link two rooms by
        # construction, so they always have two Floor neighbours.
        for cx, cy in sorted(floor):
            if cx % 2 or cy % 2:
                continue
            neighbours = [
                (cx + sx // 2, cy + sy // 2)
                for sx, sy in _STEPS
                if (cx + sx // 2, cy + sy // 2) in floor
            ]
            if len(neighbours) > 1:
                continue
            if rng.random() >= braid_factor:
                continue
            # Closed connectors leading to an in-bounds room — carving one
            # gives this dead end a second passage.
            closed = [
                (cx + sx // 2, cy + sy // 2)
                for sx, sy in _STEPS
                if 0 <= cx + sx < width
                and 0 <= cy + sy < height
                and (cx + sx // 2, cy + sy // 2) not in floor
            ]
            if closed:
                floor.add(rng.choice(closed))
