# --------------- highscore.py — persistent best-score store --------------- #
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

# The JSON key the best score is stored under.
_SCORE_KEY = "high_score"


# ----------------------------- Load / save ------------------------------- #

# Read the best score from path. A missing or unreadable file reads as 0, so a
# first launch — or a half-written file from a crash — never breaks the game.
def load_high_score(path):
    if not os.path.exists(path):
        return 0
    try:
        with open(path, encoding="utf-8") as f:
            return int(json.load(f)[_SCORE_KEY])
    except (OSError, ValueError, KeyError, TypeError):
        return 0


# Persist score only when it beats the stored best; return the resulting best.
# Safe to call after every run — a worse run is a cheap read and no write.
def save_high_score(path, score):
    best = load_high_score(path)
    if score <= best:
        return best
    with open(path, "w", encoding="utf-8") as f:
        json.dump({_SCORE_KEY: score}, f)
    return score
