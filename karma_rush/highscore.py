# --------------- highscore.py — persistent high-score store --------------- #
# Depends on:
#   - json (stdlib): the on-disk score file is a small JSON object.
#   - os (stdlib): checks whether the score file exists yet.
#
# Data shapes:
#   - The score file is JSON: {"high_score": <int>}.
#
# Pure file I/O — no game rules, no terminal. The shell calls load once at
# launch and save once per finished run.

import json
import os

# The JSON key the high score is stored under.
_SCORE_KEY = "high_score"


# ----------------------------- Load / save ------------------------------- #

# Read the high score from path. A missing or unreadable file reads as 0, so a
# first launch — or a half-written file from a crash — never breaks the game.
def load_high_score(path):
    if not os.path.exists(path):
        return 0
    try:
        with open(path, encoding="utf-8") as f:
            return int(json.load(f)[_SCORE_KEY])
    except (OSError, ValueError, KeyError, TypeError):
        return 0


# Persist score only when it beats the stored value; return the resulting high
# score. Safe to call after every run — a worse run is a cheap read, no write.
def save_high_score(path, score):
    high_score = load_high_score(path)
    if score <= high_score:
        return high_score
    # Write to a temp file, then atomically swap it in: a crash mid-write
    # leaves the old file intact instead of a truncated one load reads as 0.
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump({_SCORE_KEY: score}, f)
    os.replace(tmp_path, path)
    return score
