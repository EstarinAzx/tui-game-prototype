# KARMA RUSH

A top-down terminal arcade maze game: thread a procedurally generated maze and
hoard mysterious items — each a hidden 50/50 karma gamble that swings your sanity
— while a Hunter stalks you through the corridors. Survive the clock and chase
the high score. This is the domain glossary — every term means one thing here.

## Language

### Play units

**Run**:
One unit of play — nominally 60 seconds, extendable by **Bonus time**. Sanity
drains, score counts, ends on TIME UP, SANITY LOST, or CAUGHT.
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
the sign *is* the alignment; there is no separate "swing" concept. Karma swings
**Sanity** only — granting **Bonus time** is a separate effect.
_Avoid_: luck, fate, alignment (as a separate term).

**Bonus time**:
Extra **Run** seconds granted by a chance roll that fires only on a good-**Karma**
**Pickup**. Extends the Run past its nominal 60 seconds, uncapped. Distinct from
Karma — Karma swings Sanity, Bonus time extends the clock.
_Avoid_: extra time, time bonus, reprieve.

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
its interior filled by a **Maze**. The **Player**, the **Hunter**, and all
**Items** live inside it.
_Avoid_: board, grid, map, field.

**Maze**:
The wall layout filling the Arena interior — a *braided* maze (corridors loop,
no dead ends), regenerated fresh for every **Run**. Made of **Wall** and
**Floor** cells.
_Avoid_: level, labyrinth, map.

**Wall**:
A blocked cell of the **Maze**. Neither the **Player** nor the **Hunter** can
enter one; **Items** never spawn on one.
_Avoid_: obstacle, block, barrier.

**Floor**:
An open, enterable cell of the **Maze** — the corridors. The **Player** and
**Hunter** move only on Floor; **Items** spawn only on Floor.
_Avoid_: path, corridor (as the term), passage, open cell.

**Player**:
The single square the human controls, moving one **Floor** cell per axis per
Tick — blocked by **Wall** cells and the **Arena** border.
_Avoid_: character, avatar, square (as a term).

**Hunter**:
The single AI predator that hunts the **Player** — each Tick it steps toward the
Player along the shortest open **Floor** path, moving slower than the Player.
Sharing the Player's cell ends the **Run** instantly (CAUGHT).
_Avoid_: enemy, monster, chaser, stalker, ghost.

**Item**:
A collectible on a **Maze** **Floor** cell — an identical `?` glyph hiding a
50/50 **Karma**. Has no class of its own; it is a `{cell: karma}` entry. The
floor is kept stocked at a fixed cap.
_Avoid_: pickup (for the thing on the floor), token, orb.

**Pickup**:
The event of the **Player** collecting one **Item** — the `Pickup` record
`tick` returns, carrying the revealed **Karma** and any **Bonus time** it
granted. At most one Pickup per Tick. The "pickup flash" is the HUD reaction
to it.
_Avoid_: collection, grab (as a term); item (for the event).

## Relationships

- A **Session** contains one or more **Runs**
- Each **Run** has one **Sanity** value and one **Score**
- Each item carries one **Karma** value
- A **Run**'s **Score** can beat the **High score**, replacing it
- An **Arena** holds one **Maze**, one **Player**, one **Hunter**, and many
  **Items**
- A **Maze** is made of **Wall** and **Floor** cells; the **Player**, **Hunter**,
  and **Items** occupy only **Floor**
- A **Pickup** happens when the **Player** moves onto an **Item**'s cell
- A good-**Karma** **Pickup** may grant **Bonus time**, extending the **Run**
- The **Hunter** reaching the **Player** ends the **Run** (CAUGHT)
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
>
> **Dev:** "The Hunter touches the Player — that's like SANITY LOST?"
> **Designer:** "Same kind of end, different reason. Sanity hitting 0 is SANITY
> LOST; the Hunter sharing your cell is CAUGHT. Both end the Run instantly."
>
> **Dev:** "A good-karma Pickup gave `+12` and `+5s` — both Karma?"
> **Designer:** "No. The `+12` is Karma — a Sanity swing. The `+5s` is Bonus
> time — extra seconds on the clock. Bonus time only ever rides on a good-Karma
> Pickup, and only sometimes."

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
- **"karma" vs "bonus time"** — good karma now also grants time; resolved: Karma
  swings **Sanity** only, **Bonus time** is its own term that extends the clock.
- **Arena "no interior obstacles"** (decision D3) — superseded: the Arena
  interior is now a **Maze** of **Wall** and **Floor** cells.
