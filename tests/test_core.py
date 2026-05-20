# ============================================================================
# KARMA RUSH — Core engine tests
# ============================================================================
# These tests check the game RULES only. They never open a terminal, so they
# run fast and the same way every time. They talk to the core through its
# public interface — GameState.new(...) and GameState.tick(...) — and check
# what an outside observer would see, not how the core does its job inside.

# random.Random gives us a seeded random-number source. A fixed seed means the
# "randomness" is the same on every run, so tests stay predictable.
import random

# pytest lets us run one test several times with different inputs.
import pytest

from karma_rush.config import Config
from karma_rush.core import GameState, Pickup


# ----------------------------------------------------------------------------
# A helper to build a game quickly
# ----------------------------------------------------------------------------
# Almost every test needs a fresh GameState. This wraps the two-step build so
# each test stays short. A custom arena size can be passed in when it matters.
def make_state(width=60, height=20):
    cfg = Config(arena_width=width, arena_height=height)
    return GameState.new(random.Random(0), cfg)


# ----------------------------------------------------------------------------
# Cycle 1 — a new game starts the player in the middle of the arena
# ----------------------------------------------------------------------------
# When a fresh game is created, the player square should sit at the center of
# the play area, not in a corner.
def test_new_game_places_player_at_arena_center():
    # Build a small, known arena so the expected center is easy to state.
    cfg = Config(arena_width=60, arena_height=20)
    # Create the game; the RNG is seeded so the result never changes.
    state = GameState.new(random.Random(0), cfg)
    # The center of a 60x20 arena is column 30, row 10.
    assert state.player == (30, 10)


# ----------------------------------------------------------------------------
# Cycle 2 — one tick with a held direction moves the player one cell
# ----------------------------------------------------------------------------
# Each of the four directions should nudge the player exactly one cell the
# right way: right adds to x, left removes from x, down adds to y (rows count
# downward), and up removes from y.
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
    # Start from the known center of a 60x20 arena.
    state = make_state()
    # Run a single tick with just that one direction held.
    state.tick({direction}, dt=0.05)
    # The player should have shifted exactly one cell.
    assert state.player == expected


# ----------------------------------------------------------------------------
# Cycle 3 — the arena walls stop the player
# ----------------------------------------------------------------------------
# Pushing toward a wall pins the player against it. The player can never walk
# off the edge into a negative cell or past the far side.
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
    # A tiny 3x3 arena: the center is (1, 1) and every wall is one step away.
    state = make_state(width=3, height=3)
    # Step to the wall, then keep shoving into it several more times.
    for _ in range(5):
        state.tick({direction}, dt=0.05)
    # The player should be pinned on the edge cell, never beyond it.
    assert state.player == wall_cell


# ----------------------------------------------------------------------------
# Cycle 4 — holding a direction keeps moving every tick
# ----------------------------------------------------------------------------
# A held key is not a one-time nudge: each tick it is still held moves the
# player another cell. Three ticks of "right" should travel three cells.
def test_holding_a_direction_moves_every_tick():
    # Start from the center of a 60x20 arena.
    state = make_state()
    # Run three ticks with "right" held the whole time.
    for _ in range(3):
        state.tick({"right"}, dt=0.05)
    # The player has travelled three cells right from column 30.
    assert state.player == (33, 10)


# ----------------------------------------------------------------------------
# Cycle 5 — two directions at once move the player diagonally
# ----------------------------------------------------------------------------
# Holding two non-opposing directions moves one cell on each axis in the same
# tick, so the player slides diagonally.
def test_two_directions_move_diagonally():
    # Start from the center of a 60x20 arena.
    state = make_state()
    # Hold "up" and "right" together for one tick.
    state.tick({"up", "right"}, dt=0.05)
    # x went up by one and y went down by one: a clean diagonal step.
    assert state.player == (31, 9)


# ----------------------------------------------------------------------------
# Cycle 6 — opposing directions cancel out
# ----------------------------------------------------------------------------
# Holding left and right at the same time should leave the player still on
# that axis, because the two steps cancel each other.
def test_opposing_directions_cancel_out():
    # Start from the center of a 60x20 arena.
    state = make_state()
    # Hold "left" and "right" at the same time for one tick.
    state.tick({"left", "right"}, dt=0.05)
    # The player has not moved at all.
    assert state.player == (30, 10)


# ----------------------------------------------------------------------------
# Cycle 7 — no keys held means the player stays put
# ----------------------------------------------------------------------------
# A tick with an empty set of directions must not move the player.
def test_empty_intents_does_not_move_player():
    # Start from the center of a 60x20 arena.
    state = make_state()
    # Tick with nothing held.
    state.tick(set(), dt=0.05)
    # The player is exactly where it started.
    assert state.player == (30, 10)


# ----------------------------------------------------------------------------
# Cycle 8 — a new game stocks the floor with item_cap items
# ----------------------------------------------------------------------------
# When a fresh game is created the floor should already be stocked: exactly
# item_cap items waiting to be collected.
def test_new_game_spawns_item_cap_items():
    # A config with a known item cap so the expected count is plain.
    cfg = Config(arena_width=60, arena_height=20, item_cap=6)
    state = GameState.new(random.Random(0), cfg)
    # The floor holds exactly the capped number of items.
    assert len(state.items) == 6


# ----------------------------------------------------------------------------
# Cycle 9 — a spawned item never lands on the player or another item
# ----------------------------------------------------------------------------
# Items must appear only on empty cells. Across many seeds, no spawn should
# ever sit on the player's cell, and no two items should share a cell.
@pytest.mark.parametrize("seed", range(20))
def test_spawned_items_never_overlap_player_or_each_other(seed):
    # A tight arena so the spawner is forced to fit items into few free cells.
    cfg = Config(arena_width=4, arena_height=3, item_cap=6)
    state = GameState.new(random.Random(seed), cfg)
    # No item shares the player's cell.
    assert state.player not in state.items
    # The items are a set, so the count proves none collided.
    assert len(state.items) == 6


# ----------------------------------------------------------------------------
# Cycle 10 — walking the player onto an item collects it
# ----------------------------------------------------------------------------
# Stepping onto an item's cell removes that item from the floor — no key
# press needed beyond the movement itself.
def test_walking_onto_an_item_collects_it():
    state = make_state()
    # Put the player next to one known item; ignore the auto-spawned ones.
    state.player = (5, 5)
    state.items = {(6, 5)}
    # Step right, onto the item's cell.
    state.tick({"right"}, dt=0.05)
    # The item the player stepped onto is gone from the floor.
    assert (6, 5) not in state.items


# ----------------------------------------------------------------------------
# Cycle 11 — collecting an item triggers a replacement spawn
# ----------------------------------------------------------------------------
# The floor is kept stocked: after a pickup the spawner tops it back up to the
# item cap, so the count is the same before and after.
def test_collecting_an_item_refills_to_the_cap():
    cfg = Config(arena_width=60, arena_height=20, item_cap=6)
    state = GameState.new(random.Random(0), cfg)
    # Sanity check: the floor starts full.
    assert len(state.items) == 6
    # Park the player beside one item and remove the rest so the step is known.
    state.player = (5, 5)
    state.items = {(6, 5)}
    # Step onto the item, collecting it.
    state.tick({"right"}, dt=0.05)
    # The pickup was replaced — the floor is back up to the cap.
    assert len(state.items) == 6


# ----------------------------------------------------------------------------
# Cycle 12 — the score rises by exactly 1 for each item collected
# ----------------------------------------------------------------------------
# Score starts at 0, climbs one per pickup, and a tick that collects nothing
# leaves it untouched.
def test_score_increments_by_one_per_pickup():
    state = make_state()
    # A fresh game starts with a score of zero.
    assert state.score == 0
    # Stage one known item beside the player and collect it.
    state.player = (5, 5)
    state.items = {(6, 5)}
    state.tick({"right"}, dt=0.05)
    # One pickup -> score of one.
    assert state.score == 1
    # A tick that walks onto no item must not change the score.
    state.items = set()
    state.tick({"right"}, dt=0.05)
    assert state.score == 1
    # Stage a second known item and collect it too.
    state.items = {(state.player[0] + 1, state.player[1])}
    state.tick({"right"}, dt=0.05)
    # Two pickups -> score of two.
    assert state.score == 2


# ----------------------------------------------------------------------------
# Cycle 13 — tick reports each collected item as a Pickup event
# ----------------------------------------------------------------------------
# The core tells the shell what happened: a tick that collects an item returns
# a Pickup carrying the cell it was collected from; a quiet tick returns none.
def test_tick_returns_a_pickup_event_for_each_collected_item():
    state = make_state()
    # A tick that walks onto no item reports nothing.
    state.player = (5, 5)
    state.items = set()
    assert state.tick({"right"}, dt=0.05) == []
    # Stage a known item and step onto it.
    state.player = (5, 5)
    state.items = {(6, 5)}
    events = state.tick({"right"}, dt=0.05)
    # Exactly one Pickup, carrying the cell the item was collected from.
    assert events == [Pickup(cell=(6, 5))]
