---
description: Delegate a sub-task to a parallel AI conversation and optionally snap back
---

# Delegation Workflow

Use this workflow to delegate tasks to parallel AI conversations via the Antigravity Orchestrator.

## Prerequisites

1. Read the scripts path:
```bash
$sp = Get-Content ".antigravity/scripts-path.txt"
```

## Delegate a Task

// turbo
1. Auto-detect your current conversation title (so you can snap back later):
```bash
$title = (node "$sp/get-chat-title.js" 2>$null)
```

2. Create the delegation:
```bash
node "$sp/delegate.js" "<task description>" "no-snapback"
```

3. Snap back to your original conversation:
```bash
node "$sp/returntomainchat.js" "$title"
```

## Full Sequence (One Command)

// turbo
```bash
$sp = Get-Content ".antigravity/scripts-path.txt"; $title = (node "$sp/get-chat-title.js" 2>$null); node "$sp/delegate.js" "<task description>" "no-snapback"; node "$sp/returntomainchat.js" $title
```

## Check Sub-Task Results

Sub-tasks write their results to `subtask-results/task-N.md` in the workspace root. After delegation, periodically check for completed results:

// turbo
```bash
Get-ChildItem subtask-results/ -Filter "*.md" | Select-Object Name, LastWriteTime
```

Read a specific result:
// turbo
```bash
Get-Content subtask-results/task-1.md
```

## When to Delegate

- **DO delegate**: Independent tasks, research, file generation, code in separate modules
- **DON'T delegate**: Tasks that depend on your current conversation context, quick edits, questions
