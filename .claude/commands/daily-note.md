# /daily-note — Open Today

Create or open today's note. Most days this is the only file the user touches directly.

## Step 0: Reconcile Yesterday (fallback for a skipped `/end-day`)

Before creating today's note, check the most recent prior note in `Days/` for a `## 📋 Scheduled Tasks` section with checked boxes: `- [x] cab-xx — ...`.

For each checked bead ID, check its current status (`bd show <id>`). If it's still open, close it (`bd close <id>`) — this is the same close `/end-day` would have done. If it's already closed (because `/end-day` already ran, or the user closed it directly), skip silently — don't double-report.

**Only mention this if it actually did something.** If nothing was closed (either the section was empty, nothing was checked, or everything was already closed), say nothing about reconciliation at all. If it did close something, one line: *"Also closed cab-a3 and cab-h0 from yesterday — looks like `/end-day` didn't run."*

Don't touch unchecked items here — that's a carry-forward decision `/end-day` makes deliberately (asking whether to carry, defer, or drop). This step only ever closes what's already checked.

## Step 1: Check

`Days/YYYYMMDD.md`.

**Exists** → read it, report where they stand in two lines (focus set? anything completed?), ask what they want to add. Don't regenerate it.

**Doesn't exist** → create from `Templates/Daily Note.md`.

## Step 2: Create It Seeded

An empty template is a worse starting point than no note. Fill in what you can already know:

**Substitute the dates.** `{{date:YYYY-MM-DD}}` → the actual date, `{{date:dddd}}` → the weekday name. **Never write the literal `{{date:...}}` string into the note.**

**Carry yesterday forward.** Read the most recent note in `Days/` and pull its "Tomorrow's Priorities" into today's Focus section. This is the single most valuable thing this command does — it's the handoff the user already wrote and would otherwise never reread.

If the last note is several days old, seed from it anyway but say so: *"Last note was Thursday — carrying its priorities forward, may be stale."*

**Pull ready work:**
```bash
bd ready                        # blocker-aware; genuinely claimable
bd list --overdue               # past due, lead with these
bd list --due-before tomorrow   # due today
```
Put overdue items in front of the user. Don't bury them under a heading they'll scroll past.

**Seed `## 📋 Scheduled Tasks`** — one checkbox line per bead relevant to today, formatted `- [ ] <bead-id> — <title>` (the ID has to be parseable back out later, so keep that exact `id — title` shape). Pull from:
- Beads labeled `calendar-scheduled` whose block falls today (cross-reference the `.ics`/calendar if one was generated via `/schedule-tasks`)
- Overdue and due-today beads from the queries above

Don't dump the entire `bd ready` pool in here — same "if it doesn't change what they do today, cut it" filter as `/brief`. This section is the thing `/end-day` reads back, so it should only contain beads the user actually intends to touch today.

**Note today's meetings** if any are already captured in the vault.

## Step 3: Hand It Over

Report in three lines, maximum:

```
📅 Days/20250318.md

Carried forward: draft Q3 timeline · follow up with Dana
⚠️  cab-22 overdue (waiting on Legal since Mar 4)

Set your three?
```

**Three focus items, not ten.** If they list eight, say so once — three is what makes the note useful, and a list of eight is a wish rather than a plan. Say it once and then let it go; it's their day.

## Judgment

**Don't fill the note for them.** Seed the structure and the known facts; the thinking is theirs. A note pre-populated with your guesses about their priorities is worse than a blank one.

**Don't lecture about gaps.** If they haven't written a daily note in a week, one gentle line. Not a paragraph about habit formation.

**Weekend or holiday?** Just make the note. Don't editorialize about working on a Saturday.

## If `bd` Isn't Installed

Carry forward from yesterday's note and pull deadlines from `Todos.md` by date-parsing the table. Everything else works.

## Related

- `/brief` — the read-only version; use it when they want state without creating anything
- `/capture` — for things arriving through the day
- `/weekly-review` — where the week's notes get synthesized upward
- `/start-day` — orchestrates this command plus the calendar and a prep-needed check into one morning table
- `/end-day` — the evening half; closes what's checked in `## 📋 Scheduled Tasks` and asks about what's not
- `/schedule-tasks` — if today's calendar has open gaps and there are unscheduled ready P1/P2s, mention it once as a follow-on. Don't run it automatically — its confirmation step only works as a safeguard if it's invoked deliberately.

## Begin

Check for today's note and create or open it.
