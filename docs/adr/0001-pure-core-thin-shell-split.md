# Pure core engine, thin terminal shell

The game splits into a pure **core engine** and a thin **terminal shell**. The
core (`GameState.tick(directions, dt)`) imports no `blessed`, reads no real
clock, and touches no files — time arrives as `dt`, randomness as an injected
RNG, input as a plain set of directions. The shell does all rendering, input,
and file I/O. We chose this because it is the only thing that makes the game
rules unit-testable without a TTY, and `dt`-driving keeps frame hitches from
changing game speed.

## Consequences

- Load-bearing: `blessed` must stay out of the core from the first commit — a
  single import breaks testability.
- A reader will see the core take no clock and no `random` and may "fix" it;
  this is deliberate — injected `dt` and RNG make a seeded Run fully
  deterministic under test.
- The 71-test `pytest` suite covers the core; rendering, input, screens, and the
  loop are terminal-coupled and verified only by manual playtest.
