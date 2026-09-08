---
title: Ephemeral Beads — session execution pattern
type: inbox
status: to-route
date: 2026-09-01
created: 2026-09-01
source: human
tags: [beads, claude-code, pattern, inbox]
related:
  - "[[Beads Guide]]"
  - "[[Projects/Temporal Retrieval Spec]]"
  - "[[Projects/Memoryfield Improvements Spec]]"
---

# Ephemeral Beads — session execution pattern

**This is an Inbox note, not a spec.** Route each section into the artifact named in its header, then move this file to `Archive/` with `distilled_to` set. Do not leave it at root.

---

## The pattern (observed 2026-09-01, Claude Code cloud container via mobile app)

1. Point Claude Code at a spec (or two).
2. It decomposes the spec into beads with dependencies — 13 nodes in this case — and verifies the ready set, checks for cycles, confirms the dependency graph is sound.
3. A goal prompt ("complete all the beads") drives execution. `bd ready` is the scheduler; the graph is the plan.
4. Commit and push at each milestone so nothing dies with the container.
5. The beads database is **not committed**. It's a throwaway execution graph for a single job.

Why it works: the dependency graph lives on disk, so context can be blown away and the next step is still derivable. A todo list in context can't survive that.

---

## → Route to `Beads Guide.md` — new section "Two lifetimes"

Beads now plays two roles. Same tool, different lifetime. Don't merge them.

| | Durable commitments | Ephemeral execution graph |
|---|---|---|
| Lives in | `.beads/issues.jsonl`, committed | Container-local `.beads/`, gitignored or never committed |
| Created by | `/process-meeting`, `/capture`, `bd create` mid-conversation | Claude Code decomposing a spec at session start |
| Lifetime | Weeks to months, closed by a human | One job, drained by a goal loop |
| Rendered to | `Todos.md` via `/sync-todos` | A task tree in the session's daily note (see below) |
| Memory layer | `bd remember` facts persist across sessions | Session-scoped rules (e.g. "export before commit") — also `bd remember`, but prefixed `session:` so they can be purged |

Rule of thumb: **if a human will close it, commit it. If a goal loop will close it, don't.**

Add to the guide's gotchas: a cycle in the graph silently stalls `bd ready`. Always verify after bulk creation (see command post-condition below).

---

## → Route to `.claude/commands/` — post-condition for bulk bead creation

Any command that creates more than one bead in a single run (`/install`, `/process-meeting`, and any future spec-decomposition step) must end with:

```
bd ready            # non-empty, or explain why
bd graph --check    # or equivalent: no cycles, no dangling deps
```

and report the ready set count. Claude Code did this unprompted as step three in the observed session; make it a standard, not a habit.

If `bd graph` has no cycle check, implement a 10-line DFS over `issues.jsonl` and call it from the command. Track as a bead.

---

## → Route to `.claude/commands/` — checkpoint SHA on close

When a bead is closed as part of a goal loop that commits at milestones, write the commit SHA into the bead:

```
bd close <id> --notes "commit <sha>: <one-line summary>"
```

Recovery procedure if the container dies mid-run: fresh session runs `git log --oneline -20`, reads the beads export (or the daily-note task tree), reconciles which nodes have a matching SHA, marks those closed, and resumes from `bd ready`. No re-survey.

Add this as a short "Resuming an interrupted goal loop" section in the Beads Guide as well.

---

## → Route to `/daily-note` and `/save-to-brain` — export the graph once, at the end

The database is throwaway. The **plan shape** is not. At the end of a goal loop, render the task tree with outcomes into the day's note:

```markdown
## Session: <spec name> — <date>

- [x] cab-01 Memoryfield §7 export/import — commit a1b2c3
  - [x] cab-02 uuid write-back — commit a1b2c3
  - [x] cab-03 8k split at headings — commit d4e5f6
- [x] cab-04 Temporal Phase A — commit 789abc
  - [ ] cab-05 intent classifier — deferred, see note
...
```

This is the temporal spec's extraction move (event-shaped → state-shaped) applied to build sessions: the ephemeral graph decays with the container, the rendered tree lives in `Days/` and later gets distilled into the Project note by `/weekly-review`.

---

## → Route to `README.md` — one paragraph, after "Three Memory Layers"

Draft:

> The same three layers show up at two scales. At vault scale: notes, beads commitments, beads memories. At session scale, when Claude Code takes on a large piece of work: the spec is the note, the beads it decomposes the spec into are the commitments, and the session rules it stores with `bd remember` are the memories. The session-scale beads are never committed — they're a throwaway execution graph, drained by a goal loop, checkpointed by commits, and rendered into the daily note when the job is done. Same tool, same rule for what goes where, different lifetime.

---

## Not routing anywhere (judged non-durable)

- The specific container permission finagling — environment-specific, will change.
- The count of 13 beads — incidental.

---

## Beads to create from this note

```
bd create "Beads Guide: Two lifetimes section"                  --labels docs
bd create "Beads Guide: Resuming an interrupted goal loop"       --labels docs
bd create "Commands: bulk-create post-condition (ready + cycle)" --labels commands
bd create "Commands: close-with-SHA convention in goal loops"    --labels commands
bd create "Daily note: render session task tree on loop end"    --labels commands
bd create "README: two-scales paragraph"                         --labels docs
bd create "Archive this note with distilled_to after routing"    --labels housekeeping
```

Last one depends on all others.
