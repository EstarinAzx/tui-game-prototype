---
name: skeleton-verbose
description: Learning-mode variant of /skeleton. Same workflow — plan logic in plain English as inline comments, get one batch approval, then fill code under each comment — but EVERY step comment is kept permanently as training wheels, none pruned. For vibecoders and anyone learning a codebase who wants the English kept next to every block. Use when user runs /skeleton-verbose, says "skeleton in learning mode", "keep all the comments", or wants a plain-English line above every block of filled code.
---

# Skeleton-verbose

Learning-mode variant of the `/skeleton` skill.

Follow the **`/skeleton` skill exactly** — same file selection, same file structure (file-top block + per-construct comments), same two phases, same forward and backfill workflows, same phrasing guidelines, same sync rule, same approval gates.

## The one difference

`/skeleton` Phase 2 ends with a **prune** step — step comments that merely restate self-evident code are deleted.

`/skeleton-verbose` **skips the prune**. Every comment stays in the file permanently:

- the file-top block,
- every per-construct summary comment,
- **every dash step comment** — including ones that only restate the code directly below them.

Nothing is removed after fill.

## Why keep the redundant comments

This variant is training wheels. The reader is learning the codebase, or is a vibecoder who cannot yet verify code against intent. A plain-English line above every block keeps the whole file legible to them. The redundancy is the point — it is what makes the reader's eyes land on each step.

Switch to the default `/skeleton` once the reader no longer needs the English twin on self-evident lines.

## Caveat — comment drift

Every kept comment is a comment that can rot. A reader who relies on `/skeleton-verbose` output usually cannot check a comment against the code. The `/skeleton` **sync rule** is therefore mandatory here, not optional: when code changes, update the matching comment in the same edit. A stale comment in learning mode actively misleads the reader it was written for.

## See also

- `/skeleton` — default mode; prunes self-evident step comments after fill. Full workflow detail lives there.
