# ============================================================================
# KARMA RUSH — Config
# ============================================================================
# This file is a tidy box of settings. Every number you can tune to change how
# the game feels lives here, and nowhere else. None of this is game logic — it
# is just data — so rebalancing the game never means hunting through code.

# A "dataclass" is a short, tidy way to bundle named values together.
from dataclasses import dataclass


# ----------------------------------------------------------------------------
# The Config bundle
# ----------------------------------------------------------------------------
# Config is the single source of truth for every tuning constant in the game.
# It is "frozen", which means once a Config is built its values cannot be
# changed by accident — you make a fresh copy to get different numbers.
@dataclass(frozen=True)
class Config:
    # --- The game loop ---
    # How many times per second the game updates. 20 means one tick every 0.05s.
    tick_hz: int = 20

    # --- The run ---
    # How long one full game lasts, in seconds.
    run_seconds: float = 60.0
    # How long the 3-2-1 countdown lasts before the timer starts, in seconds.
    countdown_seconds: float = 3.0

    # --- The arena ---
    # The size of the play area INSIDE the walls, measured in cells.
    arena_width: int = 60
    arena_height: int = 20

    # --- Items ---
    # How many items the floor is kept stocked with at all times.
    item_cap: int = 6

    # --- Sanity ---
    # Sanity is a number between these two limits; the player starts at the top.
    sanity_min: float = 0.0
    sanity_max: float = 100.0
    sanity_start: float = 100.0
    # How much sanity drains away on its own, every second.
    sanity_decay_per_second: float = 1.5
    # How much a good item adds, and how much a bad item takes away.
    karma_good: float = 12.0
    karma_bad: float = -12.0
    # The chance (0 to 1) that a freshly rolled item turns out to be good karma.
    karma_good_chance: float = 0.5

    # --- Feedback ---
    # How long the "+12 / -12" pickup flash stays on screen, in seconds.
    pickup_flash_seconds: float = 0.4
    # Sanity bar colors: above 60 is green, 30 to 60 is yellow, below 30 is red.
    sanity_green_above: float = 60.0
    sanity_yellow_above: float = 30.0

    # --- Files ---
    # The file name where the best-ever score is saved between launches.
    highscore_path: str = "highscore.json"


# A ready-made Config that uses the "Standard" balance preset from the PRD.
# Most of the game uses this one; tests can build their own smaller Config.
DEFAULT = Config()
