# ------------- countdown.py — the pre-run 3-2-1 countdown timer ----------- #
# Depends on:
#   - math (stdlib): rounds the remaining time up to the digit on screen.
#
# Data shapes:
#   - Countdown: a dt-driven timer — holds its length and elapsed time, reports
#     the digit to show and whether it has finished.
#
# Like the core, this is time-injected (no real clock) so it stays testable:
# the shell feeds it dt every frame.

import math


# --------------------------- Countdown timer ------------------------------ #

# A countdown of a fixed length. tick(dt) advances it; number is the digit to
# show (3, 2, 1); done flips True once the full length has elapsed.
class Countdown:
    def __init__(self, seconds):
        self._seconds = seconds
        self.elapsed = 0.0

    # Advance the countdown by dt real seconds.
    def tick(self, dt):
        self.elapsed += dt

    # Digit on screen: time left rounded up, so "1" shows through its whole
    # second and only reads 0 at the true end. Floored so an overshoot frame
    # (dt landing past the end) never paints a negative digit.
    @property
    def number(self):
        return max(0, math.ceil(self._seconds - self.elapsed))

    # True once the full length has elapsed — the shell then starts the run.
    @property
    def done(self):
        return self.elapsed >= self._seconds
