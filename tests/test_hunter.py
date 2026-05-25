# --------------------- test_hunter.py — Hunter AI tests ------------------- #
# Depends on:
#   - random (stdlib): seeded Random for the Hunter's wander rolls in tests.
#   - karma_rush.maze.Maze: the Wall/Floor layout the Hunter navigates.
#   - karma_rush.hunter.Hunter: the module under test.
#
# Tests check the Hunter through its public interface — construction and
# advance() — asserting observable movement, never internals.

import random

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
    hunter = Hunter(cell=(3, 4), step_seconds=0.05, rng=random.Random(0))
    assert hunter.cell == (3, 4)


# Cycle S1 — a fresh Hunter has no memory of the Player: `last_known` is None
# until the Hunter first sees the Player.
def test_fresh_hunter_has_no_last_known_cell():
    hunter = Hunter(cell=(0, 0), step_seconds=0.05, rng=random.Random(0))
    assert hunter.last_known is None


# Cycle W1 — a fresh Hunter has no patrol waypoint either: `patrol_target` is
# None until the wander branch first fires and picks one.
def test_fresh_hunter_has_no_patrol_target():
    hunter = Hunter(cell=(0, 0), step_seconds=0.05, rng=random.Random(0))
    assert hunter.patrol_target is None


# Cycle S2 — with LOS, the Hunter chases the Player's real cell AND records it
# as last_known. The straight open corridor gives unobstructed sight, so the
# Hunter steps one cell toward the Player and starts remembering where it was.
def test_with_los_hunter_chases_player_and_records_last_known():
    maze = open_maze(6, 1)
    hunter = Hunter(cell=(0, 0), step_seconds=0.05, rng=random.Random(0))
    hunter.advance(maze, player=(5, 0), dt=0.05)
    assert hunter.cell == (1, 0)
    assert hunter.last_known == (5, 0)


# Cycle S3 — once LOS is broken, the Hunter heads to its memory of where the
# Player was, not the Player's real cell. last_known sits one direction;
# the Player sits the other — the Hunter steps toward the memory.
def test_no_los_with_last_known_hunter_heads_to_memory():
    # Plus-shaped corridor: a horizontal row and a vertical column meeting at
    # (3, 0). The vertical arm at (3, 1)/(3, 2) hides the Player from any cell
    # on the horizontal row whose column is not 3.
    floor = {(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (3, 1), (3, 2)}
    maze = Maze(6, 3, floor)
    hunter = Hunter(cell=(5, 0), step_seconds=0.05, rng=random.Random(0))
    # The Player is hidden down the vertical arm; pre-seed memory of an earlier
    # sighting at the far left of the row.
    hunter.last_known = (0, 0)
    hunter.advance(maze, player=(3, 2), dt=0.05)
    # Heads leftward toward memory (4, 0) — NOT down the vertical arm toward
    # the Player's real cell.
    assert hunter.cell == (4, 0)


# Cycle S4 — arriving on last_known with the Player still out of sight clears
# the memory: the trail has run cold, so the Hunter falls through to wander on
# its next step.
def test_reaching_last_known_with_no_los_clears_it():
    # Plus shape again — last_known is the row's left end; Hunter standing on it
    # cannot see the Player hidden in the vertical arm.
    floor = {(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (3, 1), (3, 2)}
    maze = Maze(6, 3, floor)
    hunter = Hunter(cell=(0, 0), step_seconds=0.05, rng=random.Random(0))
    hunter.last_known = (0, 0)
    hunter.advance(maze, player=(3, 2), dt=0.05)
    assert hunter.last_known is None


# Cycle W2 — with no LOS and no memory, the Hunter picks a Floor cell to
# patrol toward AND takes a real BFS hop toward it (not a stab at a random
# neighbour). Replaces a dumb oscillating wander with directed coverage.
def test_no_los_no_memory_picks_patrol_target_and_bfs_steps_toward_it():
    # Diagonal-walled 3x3 — LOS never recovers; pure wander branch fires.
    floor = {(0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (0, 2), (1, 2), (2, 2)}
    maze = Maze(3, 3, floor)
    hunter = Hunter(cell=(0, 0), step_seconds=0.05, rng=random.Random(0))
    hunter.advance(maze, player=(2, 2), dt=0.05)
    # A patrol target has been chosen — a Floor cell, not the Hunter's spawn.
    assert hunter.patrol_target is not None
    assert hunter.patrol_target in floor
    assert hunter.patrol_target != (0, 0)
    # The Hunter actually moved this step, onto a Floor cell neighbour of spawn.
    assert hunter.cell in {(1, 0), (0, 1)}


# Cycle W3 — once the Hunter reaches its patrol target, the next wander step
# picks a fresh one — the patrol is continuous, the Hunter never idles.
def test_reaching_patrol_target_picks_a_new_one():
    # Diagonal-walled 3x3 — LOS to the Player at (2, 2) never recovers from any
    # cell, so wander stays in charge and patrol-pick logic is exercised cleanly.
    floor = {(0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (0, 2), (1, 2), (2, 2)}
    maze = Maze(3, 3, floor)
    hunter = Hunter(cell=(0, 0), step_seconds=0.05, rng=random.Random(0))
    # Stage the Hunter already standing on its patrol target — the next wander
    # step must pick a new one and step off.
    hunter.patrol_target = (0, 0)
    hunter.advance(maze, player=(2, 2), dt=0.05)
    assert hunter.patrol_target is not None
    assert hunter.patrol_target != (0, 0)
    # And it took a step toward the new target — never stalls on the waypoint.
    assert hunter.cell != (0, 0)


# Cycle W5 — LOS overrides patrol: a stale patrol target left over from earlier
# wandering must not stop the Hunter from chasing the Player the moment sight
# returns.
def test_los_overrides_a_stale_patrol_target():
    # Open corridor — straight-line sight to the Player at (5, 0).
    maze = open_maze(6, 1)
    hunter = Hunter(cell=(0, 0), step_seconds=0.05, rng=random.Random(0))
    # A stale patrol target from earlier wandering points the other way.
    hunter.patrol_target = (0, 0)
    hunter.advance(maze, player=(5, 0), dt=0.05)
    # Chase fired — stepped toward the Player and recorded the sighting.
    assert hunter.cell == (1, 0)
    assert hunter.last_known == (5, 0)


# Cycle R2 — a sight_range cap gates the LOS-chase branch: a Player on a clear
# straight corridor BUT outside the Hunter's sight_range is NOT chased and
# leaves no last_known sighting — the Hunter falls through to patrol.
def test_sight_range_blocks_chase_when_player_is_too_far():
    # 20-cell straight corridor, Player at the far end well beyond range 5.
    maze = open_maze(20, 1)
    hunter = Hunter(
        cell=(0, 0), step_seconds=0.05, rng=random.Random(0), sight_range=5
    )
    hunter.advance(maze, player=(19, 0), dt=0.05)
    # No sighting recorded — chase branch did not fire.
    assert hunter.last_known is None
    # Patrol fired instead, so a patrol target now exists.
    assert hunter.patrol_target is not None


# Cycle S5 — with no LOS and no memory, the Hunter's patrol path is
# reproducible: same seed → same walk; different seeds → different walks (the
# RNG actually drives the patrol-target picks).
def test_wander_is_deterministic_under_a_seeded_rng():
    # 3x3 with the centre walled off — the diagonal from any corner to the
    # opposite corner crosses (1, 1), so LOS never recovers. Pure wander.
    floor = {(0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (0, 2), (1, 2), (2, 2)}
    maze = Maze(3, 3, floor)

    def walk(seed):
        hunter = Hunter(cell=(0, 0), step_seconds=0.05, rng=random.Random(seed))
        path = []
        for _ in range(8):
            hunter.advance(maze, player=(2, 2), dt=0.05)
            path.append(hunter.cell)
        return path

    assert walk(seed=7) == walk(seed=7)
    assert walk(seed=0) != walk(seed=1)


# Cycle S6 — across every targeting state, the Hunter only ever lands on Floor.
# The pure-core invariant: a step picked by chase / memory / wander is a Floor
# cell, never the blocking Wall on the diagonal.
def test_hunter_never_enters_a_wall_across_all_states():
    # Same diagonal-walled 3x3: forces LOS off, exercises memory and wander.
    floor = {(0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (0, 2), (1, 2), (2, 2)}
    maze = Maze(3, 3, floor)
    hunter = Hunter(cell=(0, 0), step_seconds=0.05, rng=random.Random(0))
    for _ in range(30):
        hunter.advance(maze, player=(2, 2), dt=0.05)
        assert maze.is_floor(hunter.cell)


# ----------------------------- Movement ----------------------------------- #

# Cycle H2 — given a full step's worth of dt, the Hunter advances one cell along
# the BFS shortest path toward the target.
def test_advance_steps_one_cell_toward_the_target():
    maze = open_maze(6, 1)
    hunter = Hunter(cell=(0, 0), step_seconds=0.05, rng=random.Random(0))
    hunter.advance(maze, player=(5, 0), dt=0.05)
    assert hunter.cell == (1, 0)


# Cycle H3 — over N Ticks the Hunter covers half the ground the Player would:
# its step costs 2x a Player Tick. The Player crosses one cell per Tick; the
# Hunter, one cell per two. Pure pacing — independent of any Config.
def test_hunter_moves_at_half_of_player_speed():
    maze = open_maze(40, 1)
    # Exact binary fractions: 0.05 (Player Tick) / 0.10 (Hunter step) is exactly
    # 0.5, and 16 dt additions carry zero rounding drift.
    player_tick = 0.05
    hunter = Hunter(cell=(0, 0), step_seconds=0.10, rng=random.Random(0))
    for _ in range(16):
        hunter.advance(maze, player=(39, 0), dt=player_tick)
    # 16 Ticks would carry the Player 16 cells; the Hunter covers 8 — half.
    assert hunter.cell == (8, 0)


# Cycle H4 — the Hunter follows the maze: every cell it lands on is Floor, even
# when a Wall blocks the straight line to the target.
def test_hunter_never_steps_onto_a_wall():
    # C-shaped corridor — a Wall at (0, 1) blocks the direct line from the
    # Hunter at (0, 0) down to the target at (0, 2).
    floor = {(0, 0), (1, 0), (2, 0), (2, 1), (0, 2), (1, 2), (2, 2)}
    maze = Maze(3, 3, floor)
    hunter = Hunter(cell=(0, 0), step_seconds=0.05, rng=random.Random(0))
    # No LOS from (0, 0) to (0, 2) — the Wall at (0, 1) blocks the ray. Pre-seed
    # last_known so the Hunter heads to memory via BFS instead of wandering.
    hunter.last_known = (0, 2)
    for _ in range(10):
        hunter.advance(maze, player=(0, 2), dt=0.05)
        assert maze.is_floor(hunter.cell)
    # It arrives — by the only route the maze allows.
    assert hunter.cell == (0, 2)


# Cycle H5 — a dt smaller than one step's cost moves nothing, but the leftover
# is banked: enough small Ticks add up to a move.
def test_sub_step_dt_accumulates_until_it_buys_a_move():
    maze = open_maze(6, 1)
    hunter = Hunter(cell=(0, 0), step_seconds=0.10, rng=random.Random(0))
    # 0.04 < 0.10 — banked, no move.
    hunter.advance(maze, player=(5, 0), dt=0.04)
    assert hunter.cell == (0, 0)
    # 0.08 banked — still short of a step.
    hunter.advance(maze, player=(5, 0), dt=0.04)
    assert hunter.cell == (0, 0)
    # 0.12 banked — crosses 0.10, so one move is spent.
    hunter.advance(maze, player=(5, 0), dt=0.04)
    assert hunter.cell == (1, 0)


# Cycle H6 — a huge dt does not make the Hunter teleport. An OS suspend or a
# window-drag pause dumps its whole duration into one frame's dt; the Hunter
# must catch up only a step or two, not run a path_step BFS for hundreds of
# cells (which would stall the game on resume).
def test_a_dt_spike_does_not_make_the_hunter_teleport():
    maze = open_maze(500, 1)
    hunter = Hunter(cell=(0, 0), step_seconds=0.05, rng=random.Random(0))
    hunter.advance(maze, player=(499, 0), dt=10_000.0)
    assert hunter.cell[0] <= 2
