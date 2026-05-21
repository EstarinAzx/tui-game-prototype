---
name: skeleton
description: Plan code as plain-English logic steps written as comments INSIDE the source file, before any code. AI drafts each file as a comment-only skeleton (file purpose, deps, data shapes, per-function summary, numbered steps), user approves the batch, then code is filled in under each comment. After fill, step comments that merely restate the code are pruned; the file-top block and summary comments stay as permanent docs. Use when user runs /skeleton, says "blueprint this", "skeleton first", "plan in prose before coding", or wants logic written in English before syntax. For the learning-mode variant that keeps every comment, see /skeleton-verbose.
---

# Skeleton

Write the logic in plain English first, as comments inside the real source file. Code second, filled in directly under each comment.

There is **no separate blueprint tree**. The English plan lives inline in the code file. Comment and code are **peers** — written together, edited together, neither outranks the other. The file-top block and per-construct summary comments are permanent inline documentation. Step comments that merely echo the code are pruned once code lands (Phase 2); step comments carrying non-obvious intent stay.

## When to invoke

- `/skeleton <natural language task>` — forward mode. AI plans files, writes comment-only skeletons, asks one approval, then fills code per file with approval gates.
- `/skeleton backfill <path-or-glob>` — reverse mode. AI reads existing code and inserts step comments into those files in place. Comments-only edit, no logic change.

Skill is **manual only**. Do not auto-trigger on every Write/Edit.

## What files get skeletoned

Logic-bearing source only:

```
.py .ts .tsx .js .jsx .mjs .cjs .go .rs .java .kt .swift .rb .php .c .cpp .cc .h .hpp .cs .scala .ex .exs .clj .dart .lua .m .mm
```

Skip: `.md .txt .json .yaml .yml .toml .ini .css .scss .html .svg .sql .csv .lock .gitignore`, dotfiles, configs, fixtures, generated code, vendored deps.

## File structure

Every skeletoned file has two comment layers:

### 1. File-top comment block

A block comment at the top of the file containing, in order:

- **One-line file purpose.**
- **Depends on** — external libs (each with a one-line role) and internal modules.
- **Data shapes** — types described in prose. Skip if the file has none.

Use the language's block-comment syntax (`/* */`, `"""..."""`, `#` stack — whatever is idiomatic).

### 2. Per-construct comments

For each top-level function or class, in source order:

- **A one-line summary comment** directly above the construct — what it does, in plain English.
- **Step comments** inside the body — one `-` dash comment per logical block. Code is filled in directly under each. No numbering — inserting or removing a step never forces a renumber.

If a file has no functions/classes (a module-level script), give it a single summary comment then step comments.

## The two phases

### Phase 1 — comment-only skeleton (written to disk)

Each planned file is written to disk as a **parseable comment-only skeleton**: file-top block, function signatures, summary comments, and dash step comments stacked inside each body. Add the minimum stub body the language needs to parse (`pass` in Python, `throw new Error("not implemented")` / `return undefined` in TS/JS, `panic!()` in Rust, etc.). JS/Go bodies of only comments already parse — no stub needed.

Skeleton phase of `src/auth/login.ts`:

```ts
/*
 * login.ts — user authentication: sign in and sign out.
 *
 * Depends on:
 *   - bcrypt (password hashing)
 *   - ../db/users (users + sessions table access)
 *
 * Data shapes:
 *   User has: id (number), email (string), passwordHash (string), createdAt (date).
 *   LoginResult has: token (string) and expiresAt (date).
 */

// Sign a user in: verify credentials, issue a session token.
async function login(email: string, password: string): Promise<LoginResult> {
  // - Look up the user by email in the users table.
  // - If the user is missing, send back 404 "not found".
  // - Compare the supplied password to the stored hash using bcrypt.
  // - If the comparison fails, send back 401 "invalid credentials".
  // - Create a new session token tied to the user id.
  // - Store the token in the sessions table with a 24-hour expiry.
  // - Send back a LoginResult containing the token and its expiry.
  throw new Error("not implemented");
}

// Sign a user out: drop the session. Idempotent.
async function logout(token: string): Promise<void> {
  // - Look up the session by token.
  // - If not found, stop (idempotent).
  // - Otherwise, delete the session row.
  throw new Error("not implemented");
}
```

### Phase 2 — fill code

Real code is filled in directly under each dash step comment, 1:1. The stub body is removed.

Then **prune**. Walk the step comments just written and delete any that only restate self-evident code. Keep:

- the file-top block — always,
- every per-construct summary comment — always,
- step comments that carry non-obvious information: *why* a step exists, edge cases, ordering constraints, gotchas, anything the code itself does not say.

Rule of thumb: if deleting a step comment loses nothing a competent reader could not recover from the line below it, delete it. Comment the *why*, not the *what*.

For the learning-mode variant that keeps **every** step comment permanently — training wheels for vibecoders and codebase newcomers — use `/skeleton-verbose`.

`example/login.ts` shows a filled result with all comments kept (the `/skeleton-verbose` style); default `/skeleton` would prune the self-evident ones.

## Phrasing guidelines

Write English a smart non-programmer could read. Natural patterns:

| Code concept              | English phrasing                                    |
|---------------------------|-----------------------------------------------------|
| `if cond { ... }`         | "If [cond], then [...]"                             |
| `else`                    | "Otherwise, ..."                                    |
| `for x in xs`             | "For each x in [xs], ..." / "Loop through [xs], ..."|
| `while cond`              | "As long as [cond], ..."                            |
| `return x`                | "Send back x"                                       |
| `let x = ...`             | "Store this as x" / "Remember x as ..."             |
| `new Foo(...)`            | "Create a new Foo with ..."                         |
| `foo.bar(args)`           | "Call bar on foo with args" / "Ask foo to bar ..."  |
| Callback / promise / event | "This runs LATER when [trigger]: ..."              |
| `try / catch`             | "Attempt ... If it fails, ..."                      |
| `throw`                   | "Stop and report ..."                               |
| `async / await`           | "Wait for ... before continuing"                    |
| Early return / guard      | "First check ... if so, send back ... and stop."    |

Granularity: **logical block, not line-by-line**. One dash step per if-branch, loop, try-block, or short sequence of related assignments. Group variable bookkeeping, don't split per line. Guidelines, not gates — use natural prose.

## Workflow: forward mode (`/skeleton <task>`)

1. **Plan files.** From the task, list every code file you will create or modify. Group into a plan.
2. **Write skeletons for all files.** Write each planned file to disk as a Phase 1 comment-only skeleton.
3. **One batch approval.** Present the full set in chat: paths written + a one-line summary each. Ask the user to approve, reject, or describe edits.
   - If user describes edits: rewrite affected skeletons, re-ask.
   - If user edits files directly: re-read and proceed.
4. **Fill code per file, gated.** For each approved file, fill the code under every comment, then pause and ask the user to approve that file's code before the next.
5. **Mid-code discrepancy.** If while filling code you realize a comment is wrong, fix the comment in the same edit and note it when you ask approval. Do not silently diverge.

## Workflow: backfill mode (`/skeleton backfill <path-or-glob>`)

1. Resolve target files. Skip non-logic-bearing extensions (see allowlist above).
2. For each target, read the code and insert the file-top block, per-construct summary comments, and dash step comments in place. Comments only — no logic change.
3. After writing all, present the list and ask the user to review/edit/approve.

## Sync rule

Comment and code are peers. When a later code change touches a skeletoned file, **update the matching comment in the same edit** — summary and step comments stay true to the code. No separate approval gate for routine edits; they change as one unit. Never leave a comment describing code that no longer exists.

## What this skill does NOT do

- Does not create a separate `blueprints/` tree — the plan lives inline in the source file.
- Does not auto-trigger on every Write/Edit. Manual only.
- Does not skeleton configs, markup, styles, or data files.
- Does not skip the Phase 1 approval gate — human review of logic before syntax is the point.
- Does not delete the file-top block or summary comments — those are permanent. It prunes only step comments that merely restate the code (Phase 2). To keep every comment, use `/skeleton-verbose`.
- Does not silently diverge — if reality requires a change, fix the comment with the code.

## See also

- `/skeleton-verbose` — learning-mode variant; keeps every step comment permanently.
- `example/login.ts` — full reference file showing the filled (Phase 2) result.
