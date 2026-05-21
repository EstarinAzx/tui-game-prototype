# ------------------ test_app.py — app state-machine tests ----------------- #
# Depends on:
#   - pytest: parametrize and the test runner.
#   - karma_rush.app: the phase constants and next_phase transition table.
#
# Tests only the pure state-machine transitions — next_phase((phase, outcome))
# -> phase. The loop, screens, and key reads are shell and stay untested.

import pytest

from karma_rush import app


# ---------------------- State-machine transitions ------------------------- #

# Cycle 36 — a key press on the title screen moves to the countdown.
def test_title_advances_to_countdown_on_start():
    assert app.next_phase(app.TITLE, "start") == app.COUNTDOWN


# Cycle 37 — a finished countdown moves into the run.
def test_countdown_advances_to_playing_when_done():
    assert app.next_phase(app.COUNTDOWN, "play") == app.PLAYING


# Cycle 38 — a run that ends on its own moves to the game-over screen.
def test_playing_advances_to_gameover_when_the_run_ends():
    assert app.next_phase(app.PLAYING, "ended") == app.GAMEOVER


# Cycle 39 — R on the game-over screen loops back through the countdown, not
# straight into a run — the player gets the 3-2-1 again.
def test_gameover_restart_loops_back_to_countdown():
    assert app.next_phase(app.GAMEOVER, "restart") == app.COUNTDOWN


# Cycle 40 — a quit outcome ends the machine (returns None) from any phase.
@pytest.mark.parametrize(
    "phase", [app.TITLE, app.COUNTDOWN, app.PLAYING, app.GAMEOVER]
)
def test_quit_ends_the_machine_from_any_phase(phase):
    assert app.next_phase(phase, "quit") is None
