# KARMA RUSH — Build Issues

Tracer-bullet vertical slices for building KARMA RUSH. Source spec: [PRD.md](PRD.md).

Each slice cuts **end-to-end** (state → core logic → render → input → tests) and is verifiable on its own. Build in dependency order. Every slice is **AFK** (implement and merge without human interaction) except Slice 7, which is **HITL** (needs a human to feel the balance).

```
Slice 1 ─→ 2 ─→ 3 ─→ 4 ─┬─→ 5 ─┐
                         └─→ 6 ─┴─→ 7
```

---

## Slice 1 — Scaffold, arena, movable player

**Type:** AFK
**Blocked by:** None — can start immediately.
**User stories:** 1, 4, 5, 6, 7, 26, 27, 28, 29

### What to build

Stand up the project and a controllable square. `python main.py` opens a `blessed` terminal, draws a fixed bordered arena, and renders a cyan block at the center that the player moves with arrow keys or WASD inside a 20 Hz tick loop. This slice establishes the **core/shell split**: a `blessed`-free core module exposing `GameState.tick(intents, dt)`, called by a thin shell loop. No items, sanity, score, or timer yet.

### Acceptance criteria

- [ ] `python main.py` launches the game and exits cleanly — terminal fully restored — on Q or Esc, including on exception.
- [ ] Project is a modular Python package with a `requirements.txt` pinning `blessed`; runs on Python 3.11+.
- [ ] A fixed bordered arena (~60×20 interior) is drawn with box-drawing characters.
- [ ] A cyan block player renders at the arena center.
- [ ] Arrow keys and WASD move the player; holding a key moves continuously via the tick loop.
- [ ] The player cannot move through or past the arena walls.
- [ ] Launching in a terminal smaller than the required size shows a clear resize message instead of a broken arena.
- [ ] All game state and movement logic lives in a `blessed`-free core module driven by `GameState.tick(intents, dt)`.

---

## Slice 2 — Items: spawn, walk-over collect, score

**Type:** AFK
**Blocked by:** #1
**User stories:** 8, 9, 10, 11, 20

### What to build

Put mysterious items on the floor and let the player hoard them. Items render as yellow `?` glyphs; the floor is kept stocked at 6 via a steady-cap spawner; walking onto an item collects it and increments a score counter shown in the HUD. Karma is **not** introduced yet — a pickup is just `+1` score.

### Acceptance criteria

- [ ] Items render as yellow `?` glyphs at random empty cells.
- [ ] The floor is kept stocked at 6 items; collecting one triggers a replacement spawn.
- [ ] A new item never spawns on the player's cell or on another item's cell.
- [ ] Walking the player onto an item collects it with no key press.
- [ ] A score counter in the HUD increments by exactly 1 per collected item.
- [ ] `pytest` covers, through the core with a seeded RNG: the spawner keeps the cap, a spawn never overlaps the player or another item, and score increments per pickup.

---

## Slice 3 — Sanity: decay, karma, bar, death

**Type:** AFK
**Blocked by:** #2
**User stories:** 12, 13, 14, 15, 16, 17, 18

### What to build

Turn each pickup into a gamble. Sanity starts at 100 and decays at 1.5/sec. Each item carries a hidden karma rolled 50/50; on pickup it applies `+12` (good) or `−12` (bad) sanity, clamped to `[0, 100]`, with a HUD flash showing the swing. A color-coded sanity bar shows danger. Sanity reaching 0 ends the run immediately.

### Acceptance criteria

- [ ] Sanity starts at 100 and is shown as a color-coded HUD bar (green >60, yellow 30–60, red <30).
- [ ] Sanity decays passively at 1.5/sec.
- [ ] Each item carries a hidden karma rolled 50/50; on pickup it applies `+12` or `−12` sanity, clamped to `[0, 100]`.
- [ ] A pickup flash shows the swing (`+12` green / `−12` red) for ~0.4s.
- [ ] When sanity reaches 0 the run ends immediately.
- [ ] `pytest` covers, with a seeded RNG: decay equals `rate × dt`, karma applies exactly `±12` and clamps, and the run ends at sanity ≤ 0.

---

## Slice 4 — Timer, game-over, restart loop

**Type:** AFK
**Blocked by:** #3
**User stories:** 19, 21, 22, 23

### What to build

Make it a real 60-second run with an end and a replay. A countdown timer drives the run; it ends at 0 seconds (`TIME UP`) or at sanity 0 (`SANITY LOST`). A game-over screen shows the end reason and the final (frozen) score; R starts a fresh run, Q/Esc quits.

### Acceptance criteria

- [ ] A 60-second countdown is shown in the HUD and drives the run length.
- [ ] The run ends at 0 seconds (`TIME UP`) or at sanity 0 (`SANITY LOST`).
- [ ] A game-over screen shows the end reason and the final score, frozen at the end moment.
- [ ] R starts a new run; Q or Esc quits from the game-over screen.
- [ ] `pytest` covers: time-up fires at elapsed ≥ 60s, score freezes on death, and the end reason is correct for each path.

---

## Slice 5 — Title screen and countdown

**Type:** AFK
**Blocked by:** #4
**User stories:** 2, 3

### What to build

Wrap the run in a front end. Launch shows a title screen ("KARMA RUSH", controls, "press any key"); a key press starts a 3-2-1 countdown before the timer runs. Formalize the app state machine: TITLE → COUNTDOWN → PLAYING → GAMEOVER, with R looping GAMEOVER → COUNTDOWN.

### Acceptance criteria

- [ ] Launch shows a title screen with the game name, controls, and a "press any key" prompt.
- [ ] After a key press, a 3-2-1 countdown plays before the timer starts.
- [ ] The app runs the state machine TITLE → COUNTDOWN → PLAYING → GAMEOVER; R goes GAMEOVER → COUNTDOWN.
- [ ] Q or Esc quits cleanly from any state.

---

## Slice 6 — Persistent high score

**Type:** AFK
**Blocked by:** #4 (parallel with #5)
**User stories:** 24, 25

### What to build

Give the player a long-term target. A high-score store loads the best score at launch and saves a new best when beaten; the best score shows in the HUD during a run and on the game-over screen.

### Acceptance criteria

- [ ] The best score loads from a local file at launch; a missing file reads as 0.
- [ ] The best score shows in the HUD during a run and on the game-over screen.
- [ ] When a run beats the best score, the new best is written to the file.
- [ ] `pytest` covers the high-score store: missing-file reads 0, save/load round-trips, and saving a lower score does not overwrite a higher best.

---

## Slice 7 — Playtest and balance pass

**Type:** HITL — requires a human to play and judge feel.
**Blocked by:** #5, #6
**User stories:** (none — tuning, not new behavior)

### What to build

A human plays full runs and tunes the balance constants in the config module — decay rate, karma magnitudes, item cap, arena size — until the Standard preset feels right. No new mechanics; config values only. Also write a short README.

### Acceptance criteria

- [ ] Several full runs played end-to-end, reaching both `SANITY LOST` and `TIME UP`.
- [ ] Balance constants adjusted if runs feel trivially survivable or unfairly punishing.
- [ ] Final tuned constants recorded in `.context/decisions.md`.
- [ ] A short README documents how to install, run, and play.
