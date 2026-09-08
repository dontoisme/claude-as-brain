---
description: Close the loop on today's note — close finished beads, decide what carries forward, seed tomorrow's priorities
---

# /end-day — Close The Loop

The evening half of `/daily-note`. Reads today's `## 📋 Scheduled Tasks` checklist, closes what's checked, and asks a real question about what's not: carry forward, defer, or drop.

**This is the deliberate path.** If you forget to run it, `/daily-note` reconciles the checked boxes automatically the next time it's opened — but only the mechanical close, not the carry-forward/defer/drop judgment below. Run this when you want that judgment made with you in the room.

## Step 1: Open Today's Note

`Days/YYYYMMDD.md`. If it doesn't exist, say so and stop — there's nothing to reconcile. Don't create one just to close it.

## Step 2: Close What's Checked

Parse `## 📋 Scheduled Tasks` for lines matching `- [x] <bead-id> — ...`. For each ID, check current status (`bd show <id>`) — if still open, `bd close <id>`. If already closed, skip silently (means `/daily-note`'s fallback reconciliation already caught it, or the user closed it directly).

Report what actually got closed in one line: *"Closed cab-a3, cab-h0, cab-2g."*

## Step 3: Decide What's Unchecked

For each `- [ ] <bead-id> — ...` still unchecked, ask — as one batched question, not one at a time:

```
Still open from today:
- cab-q6 — Draft the Q3 timeline
- cab-be — Follow up with Dana on billing scope

Carry to tomorrow, defer, or leave as-is?
```

**Default assumption if the user just says "carry them"**: they land in tomorrow's `/daily-note` seed automatically (Step 2 of `/daily-note` will pick them back up from `bd ready` since they're still open — no action needed here beyond noting it).

**Defer** → `bd defer <id> --until="<date>"` if they name a date, otherwise ask which date.

**Leave as-is** → no bd action; it just stays open and ready, same as carry — the distinction is whether the user wants it flagged as a plan for tomorrow specifically.

Don't decide this for them. An item sitting open for one day isn't a problem worth a judgment call from you.

## Step 4: Anything Done Off-Beads?

Check the `## ✅ Completed` section for anything the user logged there that never had a bead — real work, just not tracked. Ask once if any of it is worth a retroactive bead (mostly so `bd stats`/history reflect reality) — don't nag if they say no.

## Step 5: Seed Tomorrow's Priorities

Update today's note's `## Tomorrow's Priorities` section: carried-forward items from Step 3, plus anything the user mentions fresh in this conversation. Same three-item discipline as `/daily-note`'s focus section — don't let it become a wishlist.

## Step 6: Report

```
✅ Closed: cab-a3, cab-h0, cab-2g
↪️  Carrying forward: cab-q6, cab-be
📅 Deferred: cab-i5 → next Monday
```

One-line follow-on, only if earned: *"Beads changed — worth a `/sync-todos` to refresh Todos.md?"*

## If `bd` Isn't Installed

Nothing to close programmatically — just talk through what got done and hand-edit `Todos.md`'s checkboxes directly. Say once that beads would make this a one-command step.

## Related

- `/daily-note` — the morning half; also runs the mechanical close (Step 0) as a fallback if this never gets run
- `/schedule-tasks` — the thing that put beads into today's Scheduled Tasks section in the first place
- `/sync-todos` — refresh the `Todos.md` mirror after closes/defers

## Begin

Open today's note, close what's checked, ask about what's not, seed tomorrow.
