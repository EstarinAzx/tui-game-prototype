# Items stored as a `{cell: karma}` dict

Floor items live in `GameState.items` as a dict mapping each item's `(x, y)`
cell to its hidden Karma swing — there is no `Item` class. We chose this because
collection stays an O(1) `player in items` lookup, Karma reads as `items[cell]`,
and `render.py` iterating `for ix, iy in state.items` works unchanged since dict
iteration yields keys.

## Considered Options

- **A set of frozen `Item` objects** — rejected: would force `render.py` and
  every test off plain cells for no functional gain.

## Consequences

- Reversibility is hard: `core.py`, `render.py`, and `test_core.py` all read
  this shape directly.
- If Items ever need per-item state beyond Karma (multiple types, per-item
  glyph — currently out of scope), the dict value must grow or an `Item` class
  must be introduced, touching all three files.
