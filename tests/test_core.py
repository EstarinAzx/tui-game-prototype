# --------------------- test_core.py — core engine tests ------------------- #
# Depends on:
#   - random (stdlib): seeded Random for deterministic "randomness" in tests.
#   - pytest: parametrize, approx, and the test runner.
#   - karma_rush.config.Config: builds custom-sized arenas for tests.
#   - karma_rush.core.GameState, Pickup: the core under test.
#
# Tests check game RULES only — no terminal — through the public interface
# (GameState.new / GameState.tick), asserting observable behavior, not internals.

import random

import pytest

from karma_rush.config import Config
from karma_rush.core import GameState, Pickup
from karma_rush.maze import Maze
from karma_rush.hunter import Hunter


# ------------------------------ Test helper ------------------------------- #

# An all-Floor maze of the given size — no Walls anywhere.
def open_maze(width, height):
    cells = {(x, y) for x in range(width) for y in range(height)}
    return Maze(width, height, cells)


# Build a fresh GameState on an open (Wall-free) maze with the player centred.
# Movement, karma, and sanity tests use this so they behave as the pre-maze
# empty Arena did — maze-specific behaviour is covered by its own tests.
# Bonus time defaults off (chance 0) so pre-bonus tests stay deterministic;
# bonus-time tests pass their own chance.
def make_state(width=60, height=20, item_cap=9, bonus_time_chance=0.0):
    cfg = Config(
        arena_width=width,
        arena_height=height,
        item_cap=item_cap,
        bonus_time_chance=bonus_time_chance,
    )
    state = GameState(
        config=cfg,
        player=(width // 2, height // 2),
        rng=random.Random(0),
        maze=open_maze(width, height),
    )
    state._refill_items()
    return state


# --------------------------- Movement and walls --------------------------- #

# Cycle 1 — a new game places the player on the maze origin Floor cell.
def test_new_game_places_player_at_maze_origin():
    state = GameState.new(random.Random(0), Config())
    assert state.player == state.maze.origin
    # The origin must be enterable — the player can never start inside a Wall.
    assert state.maze.is_floor(state.player)


# Cycle 2 — one tick with a held direction moves the player exactly one cell.
@pytest.mark.parametrize(
    "direction, expected",
    [
        ("right", (31, 10)),
        ("left", (29, 10)),
        ("down", (30, 11)),
        ("up", (30, 9)),
    ],
)
def test_tick_moves_player_one_cell_per_direction(direction, expected):
    state = make_state()
    state.tick({direction}, dt=0.05)
    assert state.player == expected


# Cycle 3 — the arena walls pin the player; it cannot walk off the edge.
@pytest.mark.parametrize(
    "direction, wall_cell",
    [
        ("left", (0, 1)),
        ("right", (2, 1)),
        ("up", (1, 0)),
        ("down", (1, 2)),
    ],
)
def test_player_cannot_move_through_arena_walls(direction, wall_cell):
    # A 3x3 arena: center (1, 1), every wall one step away.
    state = make_state(width=3, height=3)
    # Shove into the wall well past reaching it.
    for _ in range(5):
        state.tick({direction}, dt=0.05)
    assert state.player == wall_cell


# Cycle 4 — a held direction keeps moving the player every tick.
def test_holding_a_direction_moves_every_tick():
    state = make_state()
    for _ in range(3):
        state.tick({"right"}, dt=0.05)
    # Three ticks of "right" travel three cells from column 30.
    assert state.player == (33, 10)


# Cycle 5 — two non-opposing directions move the player diagonally.
def test_two_directions_move_diagonally():
    state = make_state()
    state.tick({"up", "right"}, dt=0.05)
    assert state.player == (31, 9)


# Cycle 6 — opposing directions cancel; the player stays put on that axis.
def test_opposing_directions_cancel_out():
    state = make_state()
    state.tick({"left", "right"}, dt=0.05)
    assert state.player == (30, 10)


# Cycle 7 — no keys held leaves the player where it is.
def test_empty_intents_does_not_move_player():
    state = make_state()
    state.tick(set(), dt=0.05)
    assert state.player == (30, 10)


# Cycle 3b — a Wall cell stops the player, just like the arena border.
def test_walls_block_the_player():
    # A 1-row arena with a Wall at the middle cell: . # .
    cfg = Config(arena_width=3, arena_height=1, item_cap=0)
    maze = Maze(3, 1, {(0, 0), (2, 0)})
    state = GameState.new(random.Random(0), cfg, maze=maze)
    state.tick({"right"}, dt=0.05)
    # The player started on the origin and cannot enter the Wall at (1, 0).
    assert state.player == (0, 0)


# --------------------- Item spawning and collection ----------------------- #

# Cycle 8 — a new game stocks the floor with item_cap items.
def test_new_game_spawns_item_cap_items():
    cfg = Config(arena_width=60, arena_height=20, item_cap=6)
    state = GameState.new(random.Random(0), cfg)
    assert len(state.items) == 6


# Cycle 8b — items only ever spawn on Floor cells of the maze.
def test_items_spawn_only_on_floor_cells():
    # A real generated maze, so the floor is a true subset of the arena.
    state = GameState.new(random.Random(0), Config())
    assert state.items
    for cell in state.items:
        assert state.maze.is_floor(cell)


# Cycle 9 — a spawned item never lands on the player or another item.
@pytest.mark.parametrize("seed", range(20))
def test_spawned_items_never_overlap_player_or_each_other(seed):
    # A tight arena forces the spawner to fit items into few free cells.
    cfg = Config(arena_width=4, arena_height=3, item_cap=6)
    state = GameState.new(random.Random(seed), cfg)
    assert state.player not in state.items
    # items is a dict keyed by cell — a full count proves no two collided.
    assert len(state.items) == 6


# Cycle 10 — walking the player onto an item collects it.
def test_walking_onto_an_item_collects_it():
    state = make_state()
    # Stage one known item; ignore the auto-spawned ones.
    state.player = (5, 5)
    state.items = {(6, 5): 12.0}
    state.tick({"right"}, dt=0.05)
    assert (6, 5) not in state.items


# Cycle 11 — collecting an item triggers a replacement spawn to the cap.
def test_collecting_an_item_refills_to_the_cap():
    state = make_state(item_cap=6)
    assert len(state.items) == 6
    # Stage a single known item so the step is deterministic.
    state.player = (5, 5)
    state.items = {(6, 5): 12.0}
    state.tick({"right"}, dt=0.05)
    assert len(state.items) == 6


# Cycle 12 — the score rises by exactly 1 for each item collected.
def test_score_increments_by_one_per_pickup():
    state = make_state()
    assert state.score == 0
    state.player = (5, 5)
    state.items = {(6, 5): 12.0}
    state.tick({"right"}, dt=0.05)
    assert state.score == 1
    # A tick that collects nothing must not change the score.
    state.items = {}
    state.tick({"right"}, dt=0.05)
    assert state.score == 1
    state.items = {(state.player[0] + 1, state.player[1]): 12.0}
    state.tick({"right"}, dt=0.05)
    assert state.score == 2


# Cycle 13 — tick reports each collected item as a Pickup event.
def test_tick_returns_a_pickup_event_for_each_collected_item():
    state = make_state()
    # A quiet tick reports nothing.
    state.player = (5, 5)
    state.items = {}
    assert state.tick({"right"}, dt=0.05) == []
    # A collecting tick reports one Pickup carrying the cell and karma.
    state.player = (5, 5)
    state.items = {(6, 5): 12.0}
    events = state.tick({"right"}, dt=0.05)
    assert events == [Pickup(cell=(6, 5), karma=12.0)]


# ----------------------- Sanity, karma, and run end ----------------------- #

# Cycle 14 — a new game starts with full sanity.
def test_new_game_starts_with_full_sanity():
    cfg = Config(arena_width=60, arena_height=20)
    state = GameState.new(random.Random(0), cfg)
    assert state.sanity == cfg.sanity_start


# Cycle 15 — sanity decays passively by rate x dt every tick.
def test_sanity_decays_by_rate_times_dt():
    state = make_state()
    start = state.sanity
    state.tick(set(), dt=0.05)
    rate = Config(arena_width=60, arena_height=20).sanity_decay_per_second
    assert state.sanity == pytest.approx(start - rate * 0.05)


# Cycle 16 — decay never drives sanity below the minimum.
def test_decay_clamps_sanity_at_minimum():
    state = make_state()
    cfg = Config(arena_width=60, arena_height=20)
    # A huge dt so unclamped decay would overshoot well past zero.
    state.tick(set(), dt=1000.0)
    assert state.sanity == cfg.sanity_min


# Cycle 17 — every item carries a hidden karma swing, rolled 50/50.
def test_items_carry_karma_rolled_good_or_bad():
    cfg = Config(arena_width=60, arena_height=20, item_cap=6)
    seen = set()
    for seed in range(20):
        state = GameState.new(random.Random(seed), cfg)
        for karma in state.items.values():
            assert karma in (cfg.karma_good, cfg.karma_bad)
            seen.add(karma)
    # Both outcomes appear across the seeds — a true 50/50 roll.
    assert seen == {cfg.karma_good, cfg.karma_bad}


# Cycle 18 — collecting a good item raises sanity by its karma.
def test_collecting_a_good_item_raises_sanity():
    state = make_state()
    cfg = Config(arena_width=60, arena_height=20)
    state.sanity = 50.0
    state.player = (5, 5)
    state.items = {(6, 5): cfg.karma_good}
    # dt=0 isolates the karma swing from passive decay.
    state.tick({"right"}, dt=0.0)
    assert state.sanity == 50.0 + cfg.karma_good


# Cycle 19 — collecting a bad item lowers sanity by its karma.
def test_collecting_a_bad_item_lowers_sanity():
    state = make_state()
    cfg = Config(arena_width=60, arena_height=20)
    state.sanity = 50.0
    state.player = (5, 5)
    state.items = {(6, 5): cfg.karma_bad}
    # dt=0 isolates the karma swing from passive decay.
    state.tick({"right"}, dt=0.0)
    assert state.sanity == 50.0 + cfg.karma_bad


# Cycle 20 — a good swing never pushes sanity past the maximum.
def test_good_karma_clamps_sanity_at_maximum():
    state = make_state()
    cfg = Config(arena_width=60, arena_height=20)
    # Sit close to the ceiling so a full good swing would overshoot it.
    state.sanity = cfg.sanity_max - 5.0
    state.player = (5, 5)
    state.items = {(6, 5): cfg.karma_good}
    state.tick({"right"}, dt=0.0)
    assert state.sanity == cfg.sanity_max


# Cycle 21 — a bad swing never pushes sanity below the minimum.
def test_bad_karma_clamps_sanity_at_minimum():
    state = make_state()
    cfg = Config(arena_width=60, arena_height=20)
    # Sit just above the floor so a full bad swing would overshoot it.
    state.sanity = 5.0
    state.player = (5, 5)
    state.items = {(6, 5): cfg.karma_bad}
    state.tick({"right"}, dt=0.0)
    assert state.sanity == cfg.sanity_min


# Cycle 22 — the Pickup event carries the karma swing the shell flashes.
def test_pickup_event_carries_the_karma_swing():
    state = make_state()
    state.player = (5, 5)
    # A bad item, so the reported karma is plainly distinct from a good one.
    state.items = {(6, 5): -12.0}
    events = state.tick({"right"}, dt=0.0)
    assert events == [Pickup(cell=(6, 5), karma=-12.0)]


# Cycle 23 — the run ends the moment sanity reaches zero.
def test_run_ends_when_sanity_reaches_zero():
    state = make_state()
    assert state.run_over is False
    # One point above the floor; a large decay tick drives sanity to zero
    # regardless of the configured decay rate, and stays under the clock.
    state.sanity = 1.0
    state.tick(set(), dt=100.0)
    assert state.sanity == 0.0
    assert state.run_over is True


# Cycle 24 — the run stays alive while sanity is still positive.
def test_run_stays_alive_while_sanity_positive():
    state = make_state()
    state.tick(set(), dt=0.05)
    assert state.sanity > 0
    assert state.run_over is False


# ------------------------ Timer and the run's end ------------------------- #

# Cycle 25 — a new game starts with no time elapsed and no end reason.
def test_new_game_starts_with_zero_elapsed_and_no_end_reason():
    state = make_state()
    assert state.elapsed == 0.0
    assert state.end_reason is None


# Cycle 26 — each tick adds its dt to the elapsed run time.
def test_tick_accumulates_elapsed_by_dt():
    state = make_state()
    state.tick(set(), dt=0.05)
    state.tick(set(), dt=0.05)
    state.tick(set(), dt=0.10)
    assert state.elapsed == pytest.approx(0.20)


# Cycle 27 — the run ends with reason "time" once elapsed reaches run_seconds.
def test_run_ends_with_time_reason_when_clock_runs_out():
    # - Decay off AND no Hunter (built directly, not via GameState.new), so the
    #   clock alone ends this run — pins the test to the timer path, isolated
    #   from both the balance preset's decay and the Hunter's catch.
    cfg = Config(
        arena_width=60,
        arena_height=20,
        item_cap=0,
        sanity_decay_per_second=0.0,
    )
    state = GameState(
        config=cfg,
        player=(5, 5),
        rng=random.Random(0),
        maze=open_maze(60, 20),
    )
    state.tick(set(), dt=cfg.run_seconds)
    assert state.run_over is True
    assert state.end_reason == "time"
    assert state.sanity > 0


# Cycle 28 — the run ends with reason "sanity" when sanity reaches zero.
def test_run_ends_with_sanity_reason_when_sanity_hits_zero():
    state = make_state()
    state.sanity = 1.0
    # A large tick drains sanity to the floor, still well before the clock
    # runs out — decoupled from the configured decay rate.
    state.tick(set(), dt=100.0)
    assert state.run_over is True
    assert state.end_reason == "sanity"


# Cycle 29 — once the run is over, tick freezes everything (score at death).
def test_tick_is_a_no_op_once_the_run_is_over():
    state = make_state()
    # End the run on the clock.
    state.tick(set(), dt=Config().run_seconds)
    frozen = (state.score, state.elapsed, state.sanity, state.player)
    # Stage an item one step right and try to walk onto it after the end.
    nx, ny = state.player[0] + 1, state.player[1]
    state.items = {(nx, ny): 12.0}
    events = state.tick({"right"}, dt=1.0)
    assert events == []
    assert (state.score, state.elapsed, state.sanity, state.player) == frozen


# Cycle 30 — when one tick drains sanity AND runs the clock out, sanity wins.
def test_sanity_loss_beats_the_clock_when_both_end_the_run():
    state = make_state()
    state.sanity = 1.0
    # dt of a full run length: clock runs out and decay drags sanity to zero.
    state.tick(set(), dt=Config().run_seconds)
    assert state.run_over is True
    assert state.end_reason == "sanity"


# Cycle 31 — time_remaining counts down with the run and never goes negative.
def test_time_remaining_counts_down_and_floors_at_zero():
    state = make_state()
    full = Config().run_seconds
    assert state.time_remaining == full
    state.tick(set(), dt=10.0)
    assert state.time_remaining == pytest.approx(full - 10.0)
    # Ticking past the end leaves the clock at zero, never negative.
    state.tick(set(), dt=full)
    assert state.time_remaining == 0.0


# ------------------------------ Bonus time -------------------------------- #

# Cycle 32 — a good-Karma Pickup that hits the bonus roll extends the clock.
def test_good_karma_pickup_hitting_the_roll_grants_bonus_time():
    # bonus_time_chance=1.0 forces every roll to hit.
    state = make_state(bonus_time_chance=1.0)
    full = Config().run_seconds
    state.player = (5, 5)
    state.items = {(6, 5): Config().karma_good}
    # dt=0.0 so only the Bonus-time grant moves the clock, not elapsed time.
    state.tick({"right"}, dt=0.0)
    assert state.time_remaining > full


# Cycle 33 — a bad-Karma Pickup never grants Bonus time, even at chance 1.0.
def test_bad_karma_pickup_grants_no_bonus_time():
    # chance 1.0 would hit any roll — bad karma must not roll at all.
    state = make_state(bonus_time_chance=1.0)
    full = Config().run_seconds
    state.player = (5, 5)
    state.items = {(6, 5): Config().karma_bad}
    state.tick({"right"}, dt=0.0)
    assert state.time_remaining == full


# Cycle 34 — a good-Karma Pickup that misses the roll grants no Bonus time.
def test_good_karma_pickup_missing_the_roll_grants_no_bonus_time():
    # bonus_time_chance=0.0 forces every roll to miss.
    state = make_state(bonus_time_chance=0.0)
    full = Config().run_seconds
    state.player = (5, 5)
    state.items = {(6, 5): Config().karma_good}
    state.tick({"right"}, dt=0.0)
    assert state.time_remaining == full


# Cycle 35 — the Pickup record carries the Bonus time the pickup granted.
def test_pickup_event_carries_the_bonus_seconds_granted():
    state = make_state(bonus_time_chance=1.0)
    cfg = Config()
    state.player = (5, 5)
    state.items = {(6, 5): cfg.karma_good}
    events = state.tick({"right"}, dt=0.0)
    assert events == [
        Pickup(cell=(6, 5), karma=cfg.karma_good, bonus_seconds=cfg.bonus_time_amount)
    ]


# Cycle 36 — banked Bonus time keeps the Run alive past run_seconds, and the
# clock ends it only once elapsed reaches the extended total.
def test_banked_bonus_time_extends_the_run_past_run_seconds():
    # Decay off so sanity never ends the run — the clock is the only end path.
    cfg = Config(
        arena_width=60,
        arena_height=20,
        item_cap=0,
        bonus_time_chance=1.0,
        sanity_decay_per_second=0.0,
    )
    state = GameState(
        config=cfg,
        player=(5, 5),
        rng=random.Random(0),
        maze=open_maze(60, 20),
    )
    # Bank one Bonus-time grant by collecting a good item.
    state.items = {(6, 5): cfg.karma_good}
    state.tick({"right"}, dt=0.0)
    # Ticking exactly to run_seconds would end a no-bonus run — not this one.
    state.tick(set(), dt=cfg.run_seconds)
    assert state.run_over is False
    assert state.end_reason is None
    # Past the extended total, the clock finally ends the run.
    state.tick(set(), dt=cfg.bonus_time_amount)
    assert state.run_over is True
    assert state.end_reason == "time"


# ------------------------------ The Hunter -------------------------------- #

# Cycle C1 — a new game spawns one Hunter on the Floor cell with the greatest
# BFS distance from the Player start, so the chase begins as far away as the
# maze allows.
def test_new_game_spawns_hunter_at_the_farthest_floor_cell():
    cfg = Config(arena_width=10, arena_height=6, item_cap=0)
    state = GameState.new(random.Random(0), cfg, maze=open_maze(10, 6))
    # The Player starts on the maze origin (0, 0); on an open 10x6 maze the
    # BFS-farthest Floor cell is the opposite corner.
    assert state.hunter.cell == (9, 5)


# Cycle C2 — each tick advances the Hunter one BFS hop toward the Player; the
# Hunter hunts from the very first Tick.
def test_tick_advances_the_hunter_toward_the_player():
    cfg = Config(arena_width=20, arena_height=1, item_cap=0)
    state = GameState(
        config=cfg,
        player=(0, 0),
        rng=random.Random(0),
        maze=open_maze(20, 1),
        hunter=Hunter(cell=(10, 0), step_seconds=0.05, rng=random.Random(0)),
    )
    state.tick(set(), dt=0.05)
    assert state.hunter.cell == (9, 0)


# Cycle C3 — the run ends the moment the Hunter lands on the Player's cell, with
# end_reason "caught".
def test_run_ends_caught_when_the_hunter_reaches_the_player():
    cfg = Config(arena_width=10, arena_height=1, item_cap=0)
    state = GameState(
        config=cfg,
        player=(0, 0),
        rng=random.Random(0),
        maze=open_maze(10, 1),
        hunter=Hunter(cell=(1, 0), step_seconds=0.05, rng=random.Random(0)),
    )
    # The Hunter, one cell away, steps onto the stationary Player.
    state.tick(set(), dt=0.05)
    assert state.run_over is True
    assert state.end_reason == "caught"


# Cycle C4 — a head-on pass counts: when the Player and Hunter swap cells in one
# Tick they have collided, so the run ends "caught" even though neither ends on
# the other's final cell.
def test_a_cell_swap_with_the_hunter_counts_as_caught():
    cfg = Config(arena_width=10, arena_height=1, item_cap=0)
    state = GameState(
        config=cfg,
        player=(0, 0),
        rng=random.Random(0),
        maze=open_maze(10, 1),
        hunter=Hunter(cell=(1, 0), step_seconds=0.05, rng=random.Random(0)),
    )
    # The Player steps right as the Hunter steps left — they pass through each
    # other, ending on each other's start cells.
    state.tick({"right"}, dt=0.05)
    assert state.run_over is True
    assert state.end_reason == "caught"


# Cycle C5 — end priority: when one Tick both drains sanity to zero and lets the
# Hunter reach the Player, sanity loss outranks the catch.
def test_sanity_loss_beats_caught_when_both_end_the_run():
    cfg = Config(arena_width=10, arena_height=1, item_cap=0)
    state = GameState(
        config=cfg,
        player=(0, 0),
        rng=random.Random(0),
        maze=open_maze(10, 1),
        hunter=Hunter(cell=(1, 0), step_seconds=0.05, rng=random.Random(0)),
    )
    state.sanity = 1.0
    # A big dt drains sanity past zero and carries the Hunter onto the Player.
    state.tick(set(), dt=100.0)
    assert state.run_over is True
    assert state.end_reason == "sanity"


# Cycle C6 — end priority: when one Tick both runs the clock out and lets the
# Hunter reach the Player, the catch outranks the timer.
def test_caught_beats_the_clock_when_both_end_the_run():
    cfg = Config(
        arena_width=10,
        arena_height=1,
        item_cap=0,
        sanity_decay_per_second=0.0,
    )
    state = GameState(
        config=cfg,
        player=(0, 0),
        rng=random.Random(0),
        maze=open_maze(10, 1),
        hunter=Hunter(cell=(1, 0), step_seconds=0.05, rng=random.Random(0)),
    )
    # A full run's dt: the clock runs out and the Hunter reaches the Player in
    # the same Tick. Decay is off, so sanity never competes.
    state.tick(set(), dt=cfg.run_seconds)
    assert state.run_over is True
    assert state.end_reason == "caught"


# Cycle C7 — at spawn the Hunter sits at the BFS-farthest cell, which on a real
# braided maze has no LOS to the Player at the origin. So the first Tick must
# NOT register a sighting — last_known stays None and the Hunter wanders rather
# than beelining, giving the Player an opening.
def test_at_spawn_with_no_los_the_hunter_does_not_beeline():
    # A real generated maze — the empty open_maze has no Walls, so it can't
    # exercise the "no LOS at spawn" case the smart Hunter is designed for.
    cfg = Config(arena_width=21, arena_height=21, item_cap=0)
    state = GameState.new(random.Random(0), cfg)
    # Precondition: the spawn really has no LOS to the Player. If a generation
    # accident put them in sight, the test below would be meaningless.
    assert not state.maze.has_line_of_sight(state.hunter.cell, state.player)
    # One Tick at a step's budget: the Hunter takes one wander step. Since LOS
    # never fired this Tick, it cannot have recorded a last_known.
    state.tick(set(), dt=1.0 / cfg.frame_hz / cfg.hunter_speed_factor)
    assert state.hunter.last_known is None


# Cycle C8 — the patrol-based wander actually sweeps the map: over a stretch of
# Ticks with no LOS to the Player, the Hunter visits many distinct cells, not
# oscillating between two neighbours of its spawn.
def test_patrol_wander_covers_many_unique_cells_on_a_real_maze():
    cfg = Config(arena_width=21, arena_height=21, item_cap=0)
    state = GameState.new(random.Random(0), cfg)
    # The Player stays put at the origin; the Hunter wanders far across the
    # generated maze, well out of LOS, so the test pins patrol coverage.
    step_dt = 1.0 / cfg.frame_hz / cfg.hunter_speed_factor
    visited = set()
    for _ in range(200):
        state.tick(set(), dt=step_dt)
        visited.add(state.hunter.cell)
    # A pure oscillating wander would land on ~2-3 cells; the patrol-led wander
    # should cover an order of magnitude more.
    assert len(visited) >= 30


# Cycle C9 — GameState.new wires config.hunter_sight_range into the spawned
# Hunter so the playtest-tunable range cap actually reaches the predator.
def test_game_state_new_passes_sight_range_to_hunter():
    cfg = Config(arena_width=10, arena_height=6, item_cap=0, hunter_sight_range=7)
    state = GameState.new(random.Random(0), cfg, maze=open_maze(10, 6))
    assert state.hunter._sight_range == 7
