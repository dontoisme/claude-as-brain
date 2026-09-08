---
description: One table for today — meetings, ready tasks, and what needs prep — then hand off to /schedule-tasks or /prep if wanted
---

# /start-day — What's On The Docket

The thing you run once in the morning instead of separately checking the calendar, `bd ready`, and whether you're walking into anything unprepared. This is an orchestrator, not a new gathering path — it reuses `/brief`'s calendar pull and `bd`'s task queries, then hands off to `/daily-note`, `/schedule-tasks`, and `/prep` rather than reimplementing any of them.

## Step 0: Open Today's Note

Run `/daily-note` first, always — before anything else in this command. This does two things that everything downstream depends on: it reconciles yesterday's checked-off beads (the `/end-day` fallback), and it creates or opens `Days/YYYYMMDD.md` with the `## 📋 Scheduled Tasks` section seeded — the same section `/end-day` reads back tonight.

Don't skip this because the table below feels like it covers the same ground — `/daily-note`'s note is the persistent, checkbox-driven record; this command's table is a one-time read of it plus the calendar. Both matter; the note is what survives the day.

## Step 1: Pull Today's Calendar

Same as `/brief` Step 1's calendar gather: if the Microsoft 365 MCP is connected, call `outlook_calendar_search` with `query: "*"`, `afterDateTime: "today"`, `beforeDateTime: "tomorrow"`, `order: "oldest"`. Present each event's time with its own returned `timeZone` — don't re-interpret as UTC.

Include everything the calendar returns — don't pre-filter to "important" meetings; the point of this view is completeness, filtering happens visually in the table, not by omission.

If the MCP isn't connected, fall back to what's in today's `Days/` note, same as `/brief`.

## Step 2: Pull Ready Tasks

```bash
bd ready              # everything claimable
bd list --overdue     # past due, still open — these lead
bd list --due-before tomorrow
```

Filter to P0–P2 for the table; mention P3/P4 counts only as a footer ("+6 more low-priority ready").

## Step 3: Flag What Needs Prep

For each meeting from Step 1, check — don't fully run `/prep` for each one, that's expensive and most days most meetings don't need it:

- Does a `People/` note exist for the attendee(s)? If not, flag as "no notes yet."
- Does that person have anything open against them — `bd list -a "<name>" --status open,blocked`, or an "I owe them" / "they owe me" item in their note?
- Is this a recurring meeting with a prior instance in `Meetings/` that had unresolved open items?

If any of those are true, mark the meeting **needs prep** in the table. Don't guess at *what* the prep would say — that's `/prep`'s job, offered as a follow-on, not inlined here.

## Step 4: The Table

One table, chronological, meetings and task blocks interleaved:

```markdown
## Tuesday, March 18

| Time        | Item                                  | Type     | Notes                          |
|-------------|---------------------------------------|----------|---------------------------------|
| 9:00–9:30   | Team standup                          | Meeting  | —                                |
| 10:00–10:30 | 1:1 with Dana                         | Meeting  | ⚠️ needs prep — pricing decision still open |
| —           | Approve expense report                | Task     | due today                       |
| 11:00       | Onboarding review sync                | Meeting  | —                                |
| —           | cab-14 — Draft the Q3 timeline        | Ready P1 | unscheduled                     |

**Ready but unscheduled:** 3 P1/P2 items · +6 more P3/P4
```

Keep it to what changes today's plan — this inherits `/brief`'s "if it doesn't change what they do today, cut it" rule for anything beyond the table itself. No extra prose analysis section; the table *is* the brief here.

## Step 5: Offer Next Actions

At most two follow-ons, only when earned:

- Ready P1/P2s unscheduled and calendar has open gaps → *"3 unscheduled ready items — run `/schedule-tasks` now?"* If yes, invoke it directly rather than describing what it would do.
- Any meeting flagged **needs prep** → *"1:1 with Dana needs prep — run `/prep Dana` now?"* If yes, invoke it directly.

Don't chain into either automatically — both have their own confirmation models (`/schedule-tasks` requires an explicit batch confirmation; `/prep` produces a full briefing) and running them unasked defeats the point of a single quick morning command.

## If `bd` Isn't Installed

Task rows come from `Todos.md` instead of `bd ready`; overdue detection is best-effort from date-parsing. Say once, don't nag.

## If the Microsoft 365 MCP Isn't Connected

Meeting rows come from today's `Days/` note if anything's already logged there. Don't fabricate a calendar you can't see.

## Begin

Open today's note via `/daily-note`, pull the calendar, pull ready tasks, flag prep gaps, render the table, then offer at most two next actions.
