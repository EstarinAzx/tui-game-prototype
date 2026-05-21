# ---------------- test_highscore.py — high-score store tests -------------- #
# Depends on:
#   - pytest: tmp_path fixture for a throwaway score file, and the test runner.
#   - karma_rush.highscore: the persistent high-score store under test.
#
# Tests the store's observable behavior — what load returns and what save
# persists — through its public functions, against a real temp file.

from karma_rush.highscore import load_high_score, save_high_score


# --------------------------- High-score store ----------------------------- #

# Cycle 41 — a missing score file reads as a score of 0.
def test_missing_file_reads_zero(tmp_path):
    path = str(tmp_path / "highscore.json")
    assert load_high_score(path) == 0


# Cycle 42 — a saved score round-trips: load reads back what save wrote, and
# save reports the resulting high score.
def test_save_then_load_round_trips(tmp_path):
    path = str(tmp_path / "highscore.json")
    assert save_high_score(path, 100) == 100
    assert load_high_score(path) == 100


# Cycle 43 — saving a score below the stored high score leaves it untouched,
# and save still reports the (unchanged) high score.
def test_lower_score_does_not_overwrite_higher_best(tmp_path):
    path = str(tmp_path / "highscore.json")
    save_high_score(path, 100)
    assert save_high_score(path, 50) == 100
    assert load_high_score(path) == 100
