# /daily-note — Open Today

Create or open today's note. Most days this is the only file the user touches directly.

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

## Begin

Check for today's note and create or open it.
