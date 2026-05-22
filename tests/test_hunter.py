# --------------------- test_hunter.py — Hunter AI tests ------------------- #
# Depends on:
#   - karma_rush.maze.Maze: the Wall/Floor layout the Hunter navigates.
#   - karma_rush.hunter.Hunter: the module under test.
#
# Tests check the Hunter through its public interface — construction and
# advance() — asserting observable movement, never internals.

from karma_rush.maze import Maze
from karma_rush.hunter import Hunter


# ------------------------------ Test helper ------------------------------- #

# An all-Floor maze of the given size — no Walls, so movement tests turn purely
# on the Hunter's step pacing and pathing, not on maze topology.
def open_maze(width, height):
    cells = {(x, y) for x in range(width) for y in range(height)}
    return Maze(width, height, cells)


# ---------------------------- Construction -------------------------------- #

# Cycle H1 — a Hunter holds the cell it was spawned on.
def test_hunter_holds_its_starting_cell():
    hunter = Hunter(cell=(3, 4), step_seconds=0.05)
    assert hunter.cell == (3, 4)


# ----------------------------- Movement ----------------------------------- #

# Cycle H2 — given a full step's worth of dt, the Hunter advances one cell along
# the BFS shortest path toward the target.
def test_advance_steps_one_cell_toward_the_target():
    maze = open_maze(6, 1)
    hunter = Hunter(cell=(0, 0), step_seconds=0.05)
    hunter.advance(maze, target=(5, 0), dt=0.05)
    assert hunter.cell == (1, 0)


# Cycle H3 — over N Ticks the Hunter covers ~75% of the ground the Player would:
# its step costs 4/3 of a Player Tick. The Player crosses one cell per Tick;
# the Hunter, three cells per four Ticks.
def test_hunter_moves_at_three_quarters_of_player_speed():
    maze = open_maze(40, 1)
    # Exact binary fractions: 0.046875 (Player Tick) / 0.0625 (Hunter step) is
    # exactly 0.75, and 16 dt additions carry zero rounding drift.
    player_tick = 0.046875
    hunter = Hunter(cell=(0, 0), step_seconds=0.0625)
    for _ in range(16):
        hunter.advance(maze, target=(39, 0), dt=player_tick)
    # 16 Ticks would carry the Player 16 cells; the Hunter covers 12 — three
    # quarters of the distance.
    assert hunter.cell == (12, 0)


# Cycle H4 — the Hunter follows the maze: every cell it lands on is Floor, even
# when a Wall blocks the straight line to the target.
def test_hunter_never_steps_onto_a_wall():
    # C-shaped corridor — a Wall at (0, 1) blocks the direct line from the
    # Hunter at (0, 0) down to the target at (0, 2).
    floor = {(0, 0), (1, 0), (2, 0), (2, 1), (0, 2), (1, 2), (2, 2)}
    maze = Maze(3, 3, floor)
    hunter = Hunter(cell=(0, 0), step_seconds=0.05)
    target = (0, 2)
    for _ in range(10):
        hunter.advance(maze, target, dt=0.05)
        assert maze.is_floor(hunter.cell)
    # It arrives — by the only route the maze allows.
    assert hunter.cell == target


# Cycle H5 — a dt smaller than one step's cost moves nothing, but the leftover
# is banked: enough small Ticks add up to a move.
def test_sub_step_dt_accumulates_until_it_buys_a_move():
    maze = open_maze(6, 1)
    hunter = Hunter(cell=(0, 0), step_seconds=0.10)
    # 0.04 < 0.10 — banked, no move.
    hunter.advance(maze, target=(5, 0), dt=0.04)
    assert hunter.cell == (0, 0)
    # 0.08 banked — still short of a step.
    hunter.advance(maze, target=(5, 0), dt=0.04)
    assert hunter.cell == (0, 0)
    # 0.12 banked — crosses 0.10, so one move is spent.
    hunter.advance(maze, target=(5, 0), dt=0.04)
    assert hunter.cell == (1, 0)


# Cycle H6 — a huge dt does not make the Hunter teleport. An OS suspend or a
# window-drag pause dumps its whole duration into one frame's dt; the Hunter
# must catch up only a step or two, not run a path_step BFS for hundreds of
# cells (which would stall the game on resume).
def test_a_dt_spike_does_not_make_the_hunter_teleport():
    maze = open_maze(500, 1)
    hunter = Hunter(cell=(0, 0), step_seconds=0.05)
    hunter.advance(maze, target=(499, 0), dt=10_000.0)
    assert hunter.cell[0] <= 2
