# /brief — Morning State of the World

Where things stand, in under a page.

## Length Is the Feature

**Hard cap: one screen.** If the user has to scroll, this failed.

A brief is not a report. It's the thing that replaces opening the app and looking around, and its entire value is that it takes thirty seconds. The instinct to be thorough is wrong here — thoroughness is what `/ask` and `/weekly-review` are for.

Ruthless filtering: **if it doesn't change what they do today, cut it.**

## Step 1: Gather

**Yesterday** — the most recent note in `Days/`. What was completed, what didn't get done, what "Tomorrow's Priorities" said. If the last note is several days old, say how long it's been rather than pretending yesterday exists.

**Ready work** — `bd ready`. Genuinely claimable, blocker-aware. (`bd list --ready` filters on status only — not the same thing.)

**Due** —
```bash
bd list --overdue                  # past due, still open — lead with these
bd list --due-before tomorrow      # due today
```

**Stale** — `bd stale`. Surface only the top two or three, and only if they're actually rotting.

**Blocked** — `bd list --status blocked`, sorted oldest first via `--sort updated`. These are the chase candidates.

**Inbox** — count items in `Inbox/`. Mention only if over five.

**Memories to confirm** —
```bash
python3 .claude/scripts/memory_meta.py due --limit 5
```
Memories past their ttl (default 90 days, 60 for people), oldest first, capped at five. Skip the section when it's empty.

**Today's meetings** — anything already captured in `Days/` or `Meetings/`. Don't invent a calendar you can't see; if there's no meeting info in the vault, skip the section silently.

## Step 2: Write It

```markdown
## Tuesday, March 18

**Yesterday:** Shipped the pricing doc. Onboarding review slipped again.

**Today's carryover:** Draft Q3 timeline · follow up with Dana on billing scope

### Ready now
- cab-12 — Draft Q3 timeline `p1`
- cab-19 — Review onboarding metrics

### Needs attention
- cab-31 — "Revisit annual-only pricing" — open 3 weeks, untouched
- Waiting on Legal since Mar 4 (cab-22) — worth chasing

**Inbox:** 7 items

### Memories to confirm
- `dana-billing` — "Dana owns the billing roadmap" — confirmed 94 days ago
  confirm · retire · edit
```

For each memory the user answers with one word. **confirm** → `python3 .claude/scripts/memory_meta.py confirm <key>`. **retire** → `python3 .claude/scripts/memory_meta.py retire <key>` (runs `bd forget`). **edit** → `bd remember "<new text>" --key <key>` then confirm it. Anything they don't answer stays listed tomorrow; nothing expires on its own — a memory is injected into every session until someone retires it, by design.

Then **one line** of orientation. Not analysis — a pointer:

> *Two things are blocked on other people and both are over two weeks old. Might be a chasing day.*

That's the whole brief.

## After Writing: Bump

The daily note you read for "Yesterday" was read to produce the brief. Record it, and nothing else — the brief lists beads, not notes:

```bash
python3 .claude/scripts/brain_index.py bump Days/YYYYMMDD.md --kind brief
```

Skip when there is no index.

## Judgment Calls

**Don't list everything ready.** If `bd ready` returns fifteen items, show the top three or four by priority and say "+11 more." A wall of tasks is the thing people close the terminal to avoid.

**Escalate what's genuinely rotting.** An item open three weeks with no activity deserves a call-out. An item open three days does not.

**Lead with carryover.** What they said they'd do today, said yesterday, is more useful than anything you compute.

**Note streaks and gaps.** "No daily note since Thursday" is worth one line — gently, once, without a lecture.

**Skip empty sections.** No stale items means no stale heading.

## If `bd` Isn't Installed

Build the brief from `Todos.md` and the last few daily notes. Overdue items come from date-parsing the todo table. Say once that beads would make the ready/stale detection real, then don't mention it again.

## Follow-On

End with at most one suggestion, and only when it's earned:

- Inbox over ten → "Worth a `/weekly-review`"
- Meeting today with prior notes → "`/prep <meeting>` before that call?"
- No daily note yet → "`/daily-note` to start today's"

One. Not a menu.

## Begin

Gather and write the brief. Keep it to a screen.
