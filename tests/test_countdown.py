# ----------------- test_countdown.py — countdown timer tests -------------- #
# Depends on:
#   - pytest: approx and the test runner.
#   - karma_rush.countdown.Countdown: the pre-run 3-2-1 timer under test.
#
# Tests the countdown's observable behavior — the digit it shows and when it
# reports done — through its public interface, with no terminal involved.

from karma_rush.countdown import Countdown


# --------------------------- Countdown behavior --------------------------- #

# Cycle 32 — a fresh countdown shows its starting digit before any tick.
def test_new_countdown_shows_the_starting_number():
    countdown = Countdown(3.0)
    assert countdown.number == 3


# Cycle 33 — feeding the countdown dt counts the digit down.
def test_ticking_counts_the_number_down():
    countdown = Countdown(3.0)
    countdown.tick(1.0)
    assert countdown.number == 2
    countdown.tick(1.0)
    assert countdown.number == 1


# Cycle 34 — the countdown reports done only once its full length has elapsed.
def test_countdown_finishes_once_its_length_elapses():
    countdown = Countdown(3.0)
    assert countdown.done is False
    countdown.tick(2.99)
    assert countdown.done is False
    countdown.tick(0.01)
    assert countdown.done is True


# Cycle 35 — a tick past the end leaves the digit at 0, never negative.
def test_the_number_never_drops_below_zero():
    countdown = Countdown(3.0)
    countdown.tick(10.0)
    assert countdown.number == 0
