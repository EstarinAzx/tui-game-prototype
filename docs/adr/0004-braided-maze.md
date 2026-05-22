# Braided maze fills the Arena interior

The Arena interior is filled by a procedurally generated **braided** maze —
corridors loop, with no dead ends — regenerated fresh for every Run. We chose
braided over a classic perfect maze because a slower **Hunter** chases the
Player through it: a dead end is a death trap with no counterplay, whereas
looped corridors always give the Player a way to juke the Hunter around a
block. Braiding (carving extra walls out of a perfect maze) keeps the maze
identity while keeping the chase fair.

This **supersedes decision D3** ("Arena: fixed bordered box, empty, no interior
obstacles"). D3's reasoning — tension comes from sanity, not layout — no longer
holds once a Hunter and a navigable space are core to the game.

## Considered Options

- **Perfect maze** (exactly one path between any two cells) — rejected: dead
  ends become unescapable death traps under a chasing Hunter; brutal in a
  60-second twitch game.
- **Sparse arena** (mostly open, scattered wall chunks) — rejected: weakest
  maze identity and trivial to navigate; the maze stops mattering.

## Consequences

- The Arena grows to odd dimensions (81×25) so standard maze generation lands
  cleanly — walls and floor both occupy whole cells, corridors are one cell
  wide. Required terminal size grows accordingly.
- Maze generation lives in the pure core (RNG injected, no `blessed`), so a
  seeded Run reproduces an identical maze — see ADR-0001.
- The Hunter's pathfinding may assume a connected floor graph: braiding
  guarantees every Floor cell reaches every other, so a path to the Player
  always exists.
- Items spawn only on Floor cells; the item cap may need rebalancing since the
  maze roughly halves the open-cell count versus the old empty Arena.
- Reversibility is moderate: the generator is swappable, but the Hunter's
  fairness tuning and the item cap are balanced against a braided topology.
