# /sync-todos — Render Beads Into Readable Markdown

Regenerate `Todos.md` from the beads database.

`Todos.md` is a **generated mirror**, never a source of truth. Beads holds state; this renders it into something readable without tooling, openable in Obsidian, and survivable if `bd` ever goes away.

## When This Runs

Automatically, after any command that writes beads — `/process-meeting`, `/save-to-brain`, `/capture` when it creates a task, `/weekly-review`. Also on demand.

Cheap enough to run whenever state changed. Run it.

## Step 1: Pull State

```bash
bd list --status open,in_progress,blocked --json
bd list --overdue --json
bd ready --json
bd list --status closed --closed-after <7 days ago> --json
```

Use `--json`. Parsing the human-readable table is fragile and will break when the CLI formatting changes.

If `bd` isn't installed, **stop immediately and change nothing.** Say: *"No beads database — `Todos.md` is hand-maintained in this vault."* Overwriting a hand-maintained file with an empty render would destroy real work.

## Step 1b: Persist to the Tracked Export

The Dolt database under `.beads/` is a gitignored cache. The file git actually carries is `.beads/issues.jsonl`, and `bd` does **not** update it on its own. Every run of this command refreshes it:

```bash
bd export -o .beads/issues.jsonl --include-memories
```

`--include-memories` matters — memories are excluded from exports by default, and losing them silently is worse than losing tasks. Commit the file with whatever else changed. In a remote or ephemeral session (Claude Code on the web, mobile) this is the only thing standing between the beads you just created and the container being reclaimed.

## Step 2: Write the File

```markdown
---
tags: ["#todos"]
generated: YYYY-MM-DD HH:MM
---

# ✅ Action Items

> **Generated from beads.** Edit via `bd`, not by hand — changes here are
> overwritten on the next `/sync-todos`.

## 🔥 Overdue

| Task | Owner | Source | Due | ID |
|------|-------|--------|-----|-----|
| Chase Legal on contract language | You | [[Meetings/20250402 - Riverside Renewal]] | 2025-04-10 | cab-22 |

## 📅 Ready Now

<!-- bd ready — blocker-aware, genuinely claimable -->

| Task | Owner | Source | Due | ID |
|------|-------|--------|-----|-----|

## ⏳ In Progress

| Task | Owner | Source | ID |
|------|-------|--------|-----|

## 🤝 Blocked

| Task | Blocked On | Since | ID |
|------|-----------|-------|-----|

## 📋 Open, No Deadline

| Task | Owner | Source | ID |
|------|-------|--------|-----|

---

## ✅ Recently Closed

<!-- Last 7 days. Seeing progress matters. -->

- ~~Draft Q3 timeline~~ — closed 2025-04-16 (cab-12)

---

*Generated YYYY-MM-DD HH:MM · `bd ready` for the live view*
```

## Rules

**Convert source references to wikilinks.** A bead's `--notes` field usually carries `From [[Meetings/...]]`. Extract it into the Source column so the file works as a linked note in Obsidian, not just a table.

**Drop empty sections entirely.** A file with five "no items" headings reads as broken.

**Keep IDs visible.** The whole point is being able to jump back to `bd show cab-22`.

**Never edit beads from here.** This command is one-directional: beads → markdown. If the user asks to change a task, run the `bd` command and then re-render.

**Preserve nothing from the old file.** It's a full regeneration. That's why the header warns against hand-editing.

## Report

One line:

```
✅ Todos.md — 3 overdue, 7 ready, 2 blocked
```

If something's overdue, say so — that's the part worth noticing.

## Begin

Pull beads state and regenerate `Todos.md`.
