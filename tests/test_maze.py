# --------------------- test_maze.py — maze generator tests --------------- #
# Depends on:
#   - random (stdlib): seeded Random for deterministic generation in tests.
#   - pytest: the test runner.
#   - karma_rush.config.Config: supplies arena size and braid factor.
#   - karma_rush.maze.Maze: the module under test.
#
# Tests check the generated Maze through its public interface — dimensions,
# Wall/Floor queries, connectivity, no dead ends, determinism — never internals.

import random

from karma_rush.config import Config
from karma_rush.maze import Maze


# ------------------------------ Test helper ------------------------------- #

# Generate a Maze from a seeded RNG; arena size and braid factor overridable.
def make_maze(seed=0, **overrides):
    cfg = Config(**overrides)
    return Maze.generate(random.Random(seed), cfg)


# ------------------------- Dimensions and origin -------------------------- #

# Cycle M1 — a generated maze matches the configured arena dimensions.
def test_generated_maze_matches_arena_dimensions():
    cfg = Config(arena_width=81, arena_height=25)
    maze = Maze.generate(random.Random(0), cfg)
    assert (maze.width, maze.height) == (81, 25)


# Cycle M2 — interior pillar cells (odd, odd) are always Wall — this is what
# makes the layout a maze and not an open room.
def test_interior_pillars_are_walls():
    maze = make_maze()
    for x in (1, 3, 5):
        for y in (1, 3, 5):
            assert maze.is_wall((x, y))


# ----------------------- Wall / Floor queryability ------------------------ #

# Cycle M3 — the origin is a Floor cell, so the Player always has a valid start.
def test_origin_is_a_floor_cell():
    maze = make_maze()
    assert maze.origin == (0, 0)
    assert maze.is_floor(maze.origin)


# Cycle M4 — is_floor and is_wall partition every in-bounds cell exactly, and
# agree with the floor_cells set.
def test_is_floor_and_is_wall_partition_every_cell():
    maze = make_maze(arena_width=21, arena_height=15)
    for x in range(maze.width):
        for y in range(maze.height):
            cell = (x, y)
            assert maze.is_floor(cell) != maze.is_wall(cell)
            assert maze.is_floor(cell) == (cell in maze.floor_cells)
    # A maze has both Walls and Floor — neither set is empty.
    assert maze.floor_cells
    assert len(maze.floor_cells) < maze.width * maze.height


# Cycle M5 — floor_neighbours returns exactly the adjacent Floor cells.
def test_floor_neighbours_returns_adjacent_floor_cells():
    # A hand-built plus shape: centre (1, 1) with four Floor arms.
    maze = Maze(3, 3, {(1, 1), (0, 1), (2, 1), (1, 0), (1, 2)})
    assert set(maze.floor_neighbours((1, 1))) == {(0, 1), (2, 1), (1, 0), (1, 2)}
    # A corner arm touches only the centre.
    assert maze.floor_neighbours((0, 1)) == [(1, 1)]


# --------------------- Braided structure: no dead ends -------------------- #

# Cycle M6 — a braided maze has no dead ends: every Floor cell has at least two
# Floor neighbours, so no corridor terminates.
def test_braided_maze_has_no_dead_ends():
    maze = make_maze()
    for cell in maze.floor_cells:
        assert len(maze.floor_neighbours(cell)) >= 2


# ----------------------------- Connectivity ------------------------------- #

# Cycle M7 — every Floor cell is reachable from every other: a flood fill from
# the origin reaches the whole Floor-cell set.
def test_every_floor_cell_is_reachable_from_the_origin():
    maze = make_maze()
    reached = {maze.origin}
    frontier = [maze.origin]
    while frontier:
        cell = frontier.pop()
        for nbr in maze.floor_neighbours(cell):
            if nbr not in reached:
                reached.add(nbr)
                frontier.append(nbr)
    assert reached == set(maze.floor_cells)


# ------------------------------ Determinism ------------------------------- #

# Cycle M8 — generation uses only the injected RNG: the same seed reproduces an
# identical Maze, and different seeds produce different Mazes.
def test_generation_is_deterministic_under_a_seeded_rng():
    assert make_maze(seed=7).floor_cells == make_maze(seed=7).floor_cells
    assert make_maze(seed=1).floor_cells != make_maze(seed=2).floor_cells


# ---------------------------- BFS pathfinding ----------------------------- #

# Cycle M9 — path_step returns the first hop on a shortest Floor path from
# start toward goal: the Hunter takes one step of this each move.
def test_path_step_returns_first_hop_toward_the_goal():
    # A straight 4-cell corridor: . . . .
    maze = Maze(4, 1, {(0, 0), (1, 0), (2, 0), (3, 0)})
    assert maze.path_step((0, 0), (3, 0)) == (1, 0)


# Cycle M10 — path_step returns None when start already equals goal: a Hunter
# standing on the Player has nowhere to step.
def test_path_step_returns_none_when_already_on_the_goal():
    maze = Maze(4, 1, {(0, 0), (1, 0), (2, 0), (3, 0)})
    assert maze.path_step((2, 0), (2, 0)) is None


# Cycle M11 — path_step follows the maze, not the compass: when a Wall blocks
# the direct line, the first hop is a Floor cell that may point away from the
# goal, and it is never a Wall.
def test_path_step_routes_around_walls_not_toward_the_goal_blindly():
    # goal sits straight below start, but the cell between them is a Wall, so
    # the only route loops right and down. Floor is a C-shaped corridor.
    #   y=0:  S . .        y=1:  # # .        y=2:  G . .
    floor = {(0, 0), (1, 0), (2, 0), (2, 1), (0, 2), (1, 2), (2, 2)}
    maze = Maze(3, 3, floor)
    step = maze.path_step((0, 0), (0, 2))
    # The first hop is (1, 0) — rightward, away from the goal's column — and a
    # real Floor cell, never the blocking Wall at (0, 1).
    assert step == (1, 0)
    assert maze.is_floor(step)
