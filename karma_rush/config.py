# ------------------- config.py — tunable game constants ------------------- #
# Depends on:
#   - dataclasses (stdlib): frozen dataclass for the immutable Config bundle.
#
# Data shapes:
#   - Config: frozen dataclass holding every tuning constant in the game.
#   - DEFAULT: a ready-made Config using the PRD's Standard balance preset.
#
# All data, no game logic — rebalancing never means hunting through code.

from dataclasses import dataclass


# --------------------------- The Config bundle ---------------------------- #

# Single source of truth for every tuning constant. Frozen so values cannot be
# mutated by accident — make a fresh copy to rebalance.
@dataclass(frozen=True)
class Config:
    # --- The game loop ---
    # Frames per second — the shell loop rate. 20 means one frame every 0.05s.
    frame_hz: int = 20

    # --- The run ---
    # How long one full game lasts, in seconds.
    run_seconds: float = 180.0
    # How long the 3-2-1 countdown lasts before the timer starts, in seconds.
    countdown_seconds: float = 3.0

    # --- The arena ---
    # The size of the play area INSIDE the walls, measured in cells.
    # - Odd dimensions land cleanest: maze generation lays rooms on even
    #   coords, so an even side leaves its last column/row unreachable Wall.
    arena_width: int = 122
    arena_height: int = 45

    # --- The maze ---
    # Probability each dead-end room gets a second passage carved (braiding).
    # - 1.0: every dead end removed, so no corridor traps the Player.
    maze_braid_factor: float = 1.0

    # --- Items ---
    # How many items the floor is kept stocked with at all times.
    # - Scaled with arena area to hold item density ~constant.
    item_cap: int = 25

    # --- Sanity ---
    # Sanity is a number between these two limits; the player starts at the top.
    sanity_min: float = 0.0
    sanity_max: float = 100.0
    sanity_start: float = 100.0
    # How much sanity drains away on its own, every second.
    # - 2.0 (not 1.5): idling alone must lose, so collecting items is forced.
    sanity_decay_per_second: float = 0.5
    # How much a good item adds, and how much a bad item takes away.
    karma_good: float = 12.0
    karma_bad: float = -12.0
    # The chance (0 to 1) that a freshly rolled item turns out to be good karma.
    karma_good_chance: float = 0.5

    # --- The Hunter ---
    # The Hunter's speed as a fraction of Player speed. The Player crosses one
    # cell per frame; at 0.5 the Hunter covers one cell for every two of the
    # Player's — half-speed, leaving the Player room to break LOS and run.
    # - Starting value; slice #5's playtest sets the final balance.
    hunter_speed_factor: float = 0.5
    # The Hunter's sight reach, in Chebyshev cells. Capping it stops long open
    # corridors from giving the Hunter a free beeline on a Player it shouldn't
    # be able to spot yet — the Player must be close before the chase fires.
    # - Starting value; slice #5's playtest sets the final balance.
    hunter_sight_range: int = 12

    # --- Bonus time ---
    # A good-karma pickup may also grant Bonus time — extra Run seconds that
    # extend the Run past run_seconds, uncapped. The roll fires only on good
    # karma; a hit adds bonus_time_amount to the run-length accumulator.
    # - Starting values; slice #5's playtest sets the final balance.
    # The chance (0 to 1) a good-karma pickup also grants Bonus time.
    bonus_time_chance: float = 0.25
    # Seconds of Bonus time a winning roll adds to the Run.
    bonus_time_amount: float = 5.0

    # --- Feedback ---
    # How long the "+12 / -12" pickup flash stays on screen, in seconds.
    pickup_flash_seconds: float = 0.4
    # Sanity bar colors: above 60 is green, 30 to 60 is yellow, below 30 is red.
    sanity_green_above: float = 60.0
    sanity_yellow_above: float = 30.0

    # --- Files ---
    # The file name where the high score is saved between launches.
    highscore_path: str = "highscore.json"


# The Standard balance preset. Most of the game uses this; tests build their own.
DEFAULT = Config()
