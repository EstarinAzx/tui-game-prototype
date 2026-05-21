# KARMA RUSH

A 60-second top-down terminal arcade game: hoard mysterious items, each a hidden
50/50 karma gamble that swings your sanity, and chase the high score. This is the
domain glossary — every term means one thing here.

## Language

### Play units

**Run**:
One 60-second unit of play — sanity drains, score counts, ends on TIME UP or
SANITY LOST.
_Avoid_: game, round, match (for this concept).

**Session**:
One launch of the game, start to final quit, containing one or more **Runs**
(pressing R after a Run starts another within the same Session).
_Avoid_: game, run (for this concept).

**Game**:
The product itself — "KARMA RUSH". Never the 60-second unit.
_Avoid_: using "game" to mean a single **Run**.

### App lifecycle

**Phase**:
One of the four stages a Session moves through — TITLE, COUNTDOWN, PLAYING,
GAMEOVER. The **phase machine** transitions between them.
_Avoid_: state (for this concept — `GameState` is the core's Run state), mode,
screen.

**Screen**:
The full-window overlay drawn for a non-arena Phase — title, countdown, or
game-over. PLAYING has no Screen; it draws the **Arena** instead.
_Avoid_: page, view; "screen" for the `(text, style)` lines block that fills it.

### Loop

**Tick**:
One advance of the core — a call to `GameState.tick()` or `Countdown.tick()`.
The core's unit of time; takes `dt`, carries no rate of its own.
_Avoid_: step, update, frame (for this concept).

**Frame**:
One full shell loop iteration: read input, tick the core, render, pace. Runs
1:1 with a **Tick** (one Tick per Frame, no accumulator).
_Avoid_: tick (for this concept).

**Intents**:
The per-Frame input bundle the shell reads from the keyboard — the directions
held, plus quit / any-key / restart flags. The core's `tick` receives only the
**directions** out of it, never the whole bundle.
_Avoid_: input, keys, commands; "intents" for the bare directions set.

### Core mechanics

**Sanity**:
The Run's lifeline — a float in `[0, 100]`, starts at 100, decays passively, and
swings on every pickup. Hitting 0 ends the Run.
_Avoid_: health, HP, life.

**Karma**:
The hidden signed sanity swing an item carries, rolled 50/50 at spawn and
revealed only on pickup. Positive is "good karma", negative is "bad karma" —
the sign *is* the alignment; there is no separate "swing" concept.
_Avoid_: luck, fate, alignment (as a separate term).

**Score**:
The current Run's item count — one point per item collected. Resets each Run.
_Avoid_: points, count.

**High score**:
The highest **Score** across every Run in every Session; a single number
persisted to disk (no leaderboard, no name entry). Shown as `BEST` in the HUD —
that label is display text, not a separate term.
_Avoid_: best (as a domain term), top score, record.

### Arena entities

**Arena**:
The fixed bordered play area — a rectangle of cells with a drawn wall border,
no interior obstacles. The **Player** and all **Items** live inside it.
_Avoid_: board, grid, map, field.

**Player**:
The single square the human controls, moving one cell per axis per Tick,
clamped inside the **Arena** walls.
_Avoid_: character, avatar, square (as a term).

**Item**:
A collectible on the **Arena** floor — an identical `?` glyph hiding a 50/50
**Karma**. Has no class of its own; it is a `{cell: karma}` entry. The floor is
kept stocked at a fixed cap.
_Avoid_: pickup (for the thing on the floor), token, orb.

**Pickup**:
The event of the **Player** collecting one **Item** — the `Pickup` record
`tick` returns. At most one Pickup per Tick. The "pickup flash" is the HUD
reaction to it.
_Avoid_: collection, grab (as a term); item (for the event).

## Relationships

- A **Session** contains one or more **Runs**
- Each **Run** has one **Sanity** value and one **Score**
- Each item carries one **Karma** value
- A **Run**'s **Score** can beat the **High score**, replacing it
- An **Arena** holds one **Player** and many **Items**
- A **Pickup** happens when the **Player** moves onto an **Item**'s cell
- A **Session** is in exactly one **Phase** at a time
- The TITLE, COUNTDOWN, and GAMEOVER **Phases** each draw a **Screen**; PLAYING
  draws the **Arena**

## Example dialogue

> **Dev:** "When the timer hits 0, the Run ends — does that end the Session?"
> **Designer:** "No. The Run ends, the game-over Screen shows, and R starts a
> fresh Run inside the same Session. The Session only ends when the player quits."
>
> **Dev:** "On a Pickup, the flash shows `+12` or `-12` — is that the Karma?"
> **Designer:** "Yes. Karma *is* that signed number — it's the Item's hidden
> swing. A positive one is 'good karma', it raises Sanity; negative is 'bad
> karma'. There's no separate 'alignment' — the sign carries it."
>
> **Dev:** "The PLAYING Phase — what Screen does it draw?"
> **Designer:** "None. PLAYING draws the Arena. Only TITLE, COUNTDOWN, and
> GAMEOVER draw a Screen."

## Flagged ambiguities

- **"game"** meant both the 60-second unit and the product — resolved: the unit
  is a **Run**, "game" is the product only, a launch-to-quit is a **Session**.
- **"best" / "high score" / "highscore"** all named the persisted top score —
  resolved: the term is **High score**; `BEST` survives only as a HUD label.
- **"karma"** read as both a value and an alignment — resolved: one concept, the
  signed swing; the sign is the alignment.
- **"tick" vs "frame"** — resolved: **Tick** is a core advance, **Frame** is a
  shell loop iteration; they run 1:1.
- **"screen"** meant both the overlay and a `(text, style)` list — resolved:
  **Screen** is the overlay; the list is a "lines block".
- **"intents"** named both the input bundle and the bare directions set passed
  to the core — resolved: **Intents** is the bundle; the core takes `directions`.
