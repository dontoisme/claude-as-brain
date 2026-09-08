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
(cd "$CLAUDE_BRAIN" && bd ready)                        # blocker-aware; genuinely claimable
(cd "$CLAUDE_BRAIN" && bd list --overdue)               # past due, lead with these
(cd "$CLAUDE_BRAIN" && bd list --due-before tomorrow)   # due today
```

Pin every `bd` call to the brain's store — never ambient `cwd`. See *Where the Vault Lives* in `CLAUDE.md`.
Put overdue items in front of the user. Don't bury them under a heading they'll scroll past.

**Note today's meetings** if any are already captured in the vault.

## Step 2b: Drain the Inbox — Quietly

Attaching a chore to an existing daily habit is the only reliable way to get it run. But the transfer goes both ways: **the host command inherits the friction**, and this command survives precisely because it's cheap. A heavy inbox pass bolted on here eventually gets skipped wholesale, and then you lose the drain *and* the daily note.

So it has to stay a report, not a workload:

- Run the `/process-inbox` routine. **File what you can, silently.**
- Anything low-confidence goes to `Inbox/unclear/`. Never ask a routing question here.
- Beads stay proposals — surface them in one line with the rest.
- Commit what was filed.
- Report **one line**: *"Filed 9, 2 unclear."*

**Nothing to approve unless beads were proposed.** If the pass would take more than a few seconds of the user's attention, it's too heavy — file less, flag more, move on. `/process-inbox` exists as its own command for the deliberate version.

**Signal to watch:** if this command stops getting run within a month of adding this step, the attached work was too heavy. It's far easier to loosen than to rebuild the habit.

## Step 3: Hand It Over

Report in three lines, maximum:

```
📅 Days/20250318.md

Carried forward: draft Q3 timeline · follow up with Dana
📥 Inbox: filed 9, 2 unclear
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
- `/process-inbox` — the full drain; Step 2b is its light version
- `/weekly-review` — where the week's notes get synthesized upward

## Begin

Check for today's note and create or open it.
