# /weekly-review — The Friday Synthesis

Turn a week of scattered capture into durable knowledge, and leave the system clean.

About 30 minutes. This is the step that makes the vault compound instead of just accumulate. Skip it for a month and you have an archive, not a brain.

## Your Role

Facilitate. Read their notes, surface patterns they can't see from inside the week, do the file editing. They should finish with a clean system and a clear head.

**Always summarize before asking.** "What were your themes this week?" from a blank prompt is work. "Three things recurred — pricing pressure, the Legal bottleneck, and onboarding drop-off. Sound right?" is a conversation.

If `Templates/Weekly Review.md` exists, create this week's note from it and fill it in as you go.

## Step 1: Read the Week (10 min)

Read this week's `Days/` notes and any `Meetings/` from the same span.

Look for:
- **Recurring themes** — anything appearing three or more times is a signal, not noise
- **Unfinished carryover** — priorities that moved forward day after day and never got done. That pattern is worth naming.
- **Decisions made** — often recorded in passing and never captured properly
- **Insights** that never made it out of a daily note
- **Gaps** — days with no note

Then report what you found and ask:
- What were the big themes?
- What surprised you?
- What would you do differently?

## Step 2: Extract Insights to Areas (10 min)

**This is the step that matters most.** Daily notes are disposable; Areas are what persists.

For each insight worth keeping:

1. List `Areas/` and route it
2. **Synthesize, don't paste.** If the Area already covers this ground, deepen the existing point rather than appending a near-duplicate. An Area note that's just a stack of dated fragments has failed.
3. Include the date and source: `[[Days/YYYYMMDD]]`
4. If it has no home, propose a new Area — but only for a genuine ongoing responsibility, not a one-off

**Check the memory layer too.** If an insight is really a durable one-line fact, `bd remember` it instead of burying it in an Area note.

## Step 3: Clean Up Tasks

```bash
bd stale                      # untouched, possibly abandoned
bd list --overdue             # past due
bd list --status blocked      # waiting on someone
bd ready                      # what's genuinely claimable
```

Work through them with the user:

- **Stale items** — do it, schedule it, or close it. Say this out loud; people need explicit permission to close things. An item untouched for a month is a decision that's already been made, just not recorded.
- **Blocked items** — who's it waiting on, and for how long? Anything over two weeks needs a chase or a different plan.
- **Overdue** — re-date or close. Leaving a dead date is how a task list stops being trusted.

Then run `/sync-todos`.

## Step 4: Empty the Inbox

For each item in `Inbox/`: route it to Projects, Areas, Resources, a bead, or delete it.

**Deleting is a valid outcome and the most under-used one.** If it's been sitting three weeks and still doesn't have a home, it wasn't important. Say that plainly.

**Goal: empty.**

## Step 5: Maintenance

Run these and report only what's notable:

- `/update-mocs` — new notes into maps, propose new MOCs
- `/link-check` — broken links, orphans
- `/rebuild-dashboard` — refresh the command center

## Step 6: Plan Next Week

1. Review what's coming — deadlines in beads, milestones in `Projects/`
2. Set the **top three** for next week — most important outcome, what needs deep work, what has a hard deadline
3. Offer to pre-create Monday's daily note with those filled in

## Step 7: Write the Review Note

Save to `Days/` or a `Weeks/` folder if the vault has one. It becomes input to `/thread` later — a chain of weekly reviews is one of the most useful things `/thread` can trace.

## Flag These

Say something if you see them — as fixable, not as failures, and suggest **one** change, not five:

- Multiple weeks since the last review
- Inbox over 10
- No insights extracted to Areas in weeks — the system is capturing but not compounding
- Daily notes sporadic or stopped
- The same item carried forward five days running

## Close

1. Name what the week actually produced. People systematically underestimate this, and the review is the only place it gets counted.
2. Suggest committing if the vault is a git repo.

## Begin

Read the week and start the review.
