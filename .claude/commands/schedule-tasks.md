---
description: Time-block ready beads as calendar events (Motion-style), with a confirmation step before anything is generated
argument-hint: [optional — a specific bead ID, or a day like "tomorrow"]
---

# /schedule-tasks — Time-Block Beads Onto the Calendar

Turns claimable beads into calendar blocks so task load has real visibility — instead of living only in `bd ready`. This is the Motion-style piece: propose blocks in open slots, confirm once, then generate them.

**These are visibility blocks, not busy blocks.** The point is to see task load on the calendar, not to reserve the time against real meetings — someone (or something) scheduling with you should still be able to book over it. Free/busy status is always `free`/`TRANSPARENT`, never `busy`/`OPAQUE`.

**Write-access caveat.** Some calendar MCP connections (notably Microsoft 365, as of this writing) expose `create_event`/`update_event`/`delete_event` in the tool list but don't actually enable them — this can't always be diagnosed from the client UI, only from a write call failing. Check for a stored `bd memories` note about this before every run rather than re-discovering it: if a prior session found write access blocked, don't retry the write API "just in case" — go straight to the `.ics` path in Step 4. If a future session finds write access has actually been enabled, update that memory and switch back to direct creation.

**Read access (finding open slots) is unaffected** by this — availability lookups typically work even when writes don't.

## The One Rule

**Propose, then generate. Never produce calendar events without a single explicit confirmation for the batch.**

This is not `/capture`. A calendar event is visible to the user and potentially to anyone who can see their free/busy — it is not a private note that costs nothing to be wrong. Getting this wrong (double-booking a real meeting slot, blocking time no task actually needs) is expensive to undo and erodes trust in this feature fast.

## Step 0: Config (ask once, then remember)

Check `bd memories schedule` for prior answers. If not found, ask once and `bd remember` the results:

- **Working hours window** — e.g. "9am–5pm" — and the IANA timezone to interpret it in. `bd remember "Working hours: 9am-5pm America/Chicago" --key schedule-working-hours`
- **Default block duration** — beads don't carry a time estimate, so pick a sane default (e.g. 30 min) unless the user says otherwise. `bd remember "Default task block duration: 30 min" --key schedule-block-duration`

Don't re-ask once these exist. If the user wants to change them, they'll say so — update the memory with `bd remember --key <key> "new value"` rather than asking again.

## Step 1: Pick Candidates

Default candidate pool: `bd ready` filtered to priority ≤ 2 (P0/P1/P2), excluding anything already labeled `calendar-scheduled` (see Step 4). If `$ARGUMENTS` names a specific bead ID, use only that one. If `$ARGUMENTS` names a day, scope the search window to that day instead of today.

**Show the candidate list before doing anything else** — title, priority, ID — and let the user trim it. Don't assume every P1/P2 ready item deserves a block; some are multi-day efforts that don't fit a single slot (flag those rather than force-fitting a 30-minute block onto a "write the roadmap" task).

## Step 2: Find Open Slots

For each candidate, call the calendar MCP's find-available-time tool with `participants: []` (self only — this is focus time, not a meeting), `durationMinutes` from config, and a date range spanning the target day in UTC.

**Filter to the configured working-hours window yourself** — the tool's suggestions are not confined to working hours by default. Discard slots outside it.

If two candidate tasks would land in the same slot, don't double-book — take the first, re-search for the next with a start time past the first block's end.

## Step 3: Confirm

Present the full proposed schedule as one block, not a chain of individual confirmations:

```
📅 Proposed schedule for Tuesday, March 18:

10:00–10:30  Draft the Q3 timeline                            cab-14
11:00–11:30  Follow up with Dana on billing scope              cab-19
14:00–14:30  Review onboarding metrics                         cab-22

Create these 3 blocks?
```

**Wait for an explicit yes.** Drop or adjust anything the user pushes back on before creating anything. A partial "yes to 2 of 3" is a normal, good outcome — don't treat it as a failure requiring another full pass.

## Step 4: Generate and Record

**If write access is confirmed enabled** (checked per the note at the top): call the calendar MCP's create-event tool per confirmed slot — `subject` (bead title, optionally ID-prefixed), `start`/`end` in the working-hours timezone, `showAs: "free"` (visibility only — don't block the time), `body` linking back to the bead/source note, no `attendees`. Record the event id: `bd label <id> calendar-scheduled` + `bd update <id> --append-notes "Calendar block created: <event id>, <date/time>"`.

**Standing path while write access is blocked — generate a `.ics` file:**

1. Build one `VEVENT` per confirmed slot in a single `.ics` file (one file for the whole batch, not one per task — fewer things for the user to import).
2. Use UTC times (`DTSTART`/`DTEND` with a trailing `Z`) rather than a `TZID` block — this avoids needing a full `VTIMEZONE` definition and imports correctly regardless of the destination calendar's zone.
3. Put full context in `DESCRIPTION` (plain text, RFC5545-escaped: backslash, comma, semicolon, and literal `\n` for newlines) and mirror it in `X-ALT-DESC;FMTTYPE=text/html` so Outlook renders clickable links.
4. **Mark it free, not busy.** Set `TRANSP:TRANSPARENT` (the RFC5545 property) *and* `X-MICROSOFT-CDO-BUSYSTATUS:FREE` (Outlook-specific; some Outlook builds ignore bare `TRANSP` on import and only respect this). Without both, Outlook may import it as busy regardless of `TRANSP`.
5. **Fold every line at 75 octets per RFC5545** — a continuation line starts with a single space. Don't skip this; unfolded long lines can silently corrupt import in some clients.
6. **Write the file with no newline translation** (e.g. Python's `open(path, "w", newline="")`) and join lines with a literal `"\r\n"` yourself. Using `newline="\r\n"` while also joining on `"\r\n"` double-translates every line ending into `\r\r\n` and produces a file that looks fine in a text preview but fails to parse — this bit once already, don't repeat it.
7. **Before handing it to the user, validate the file programmatically**: unfold continuation lines, confirm `BEGIN:VEVENT`/`END:VEVENT` counts match, and confirm every link/detail you meant to include actually appears in the unfolded `DESCRIPTION`. Don't eyeball a large HTML/ICS blob by hand to check this — that's exactly the kind of transcription work that silently introduces wrong links or dropped items. Write and run a short script instead.
8. **Never hand-transcribe link URLs from a screenshot or a large raw HTML blob.** If the source is an email with real `<a href>` tags, fetch it and extract `(text, url)` pairs with a script (e.g. `re.findall(r'<a href="([^"]+)">([^<]+)</a>', html_unescaped_body)`), not by reading the raw string yourself. If it's a screenshot with no accessible source, say the links can't be verified and ask for them directly rather than guessing.
9. Save to `~/Downloads/<bead-id>-<short-name>.ics` (single-bead run) or `~/Downloads/schedule-<YYYYMMDD>.ics` (multi-task batch — see the "Batching" note below) and tell the user to double-click it to import.
10. Record on each bead: `bd label <id> calendar-scheduled` and `bd update <id> --append-notes "Calendar block generated as .ics: <path>, <date/time>. Import manually - write API unavailable."`

**Batching — one file, many events.** A single `.ics` is just a `VCALENDAR` wrapper around as many `VEVENT` blocks as it contains — there's no meaningful limit for a day's or a week's worth of task blocks. This is the normal case for `/schedule-tasks`, not a special mode: propose the whole day's candidate list in Step 1, confirm the whole batch in Step 3, then emit *one* `.ics` with one `VEVENT` per confirmed task and a distinct `UID` for each. One double-click imports the entire day. Only fall back to a single-event file when `$ARGUMENTS` names one specific bead.

## Step 5: Report

Write API path:
```
✅ 3 blocks created for Tuesday
🔗 cab-14, cab-19, cab-22 now labeled calendar-scheduled
```

`.ics` path:
```
📅 ~/Downloads/schedule-20250318.ics — 3 blocks for Tuesday
Double-click to import into your calendar app.
🔗 cab-14, cab-19, cab-22 now labeled calendar-scheduled
```

## Handling Drift

**Bead closed before its block passes** — leave the block. It already reserved the time and the work got done; nothing to clean up.

**Block's time has passed and the bead is still open** — this is a real signal, not a bug to silently paper over. On the next `/schedule-tasks` or `/daily-note` run, surface it: *"cab-14 was blocked for 10am yesterday but is still open — reschedule?"* Don't auto-reschedule without asking; the user may have deliberately deprioritized it.

**Bead's calendar block needs to move** (a real meeting got scheduled into it): with write access, use the calendar MCP's update-event tool on the stored event id rather than delete-and-recreate. On the `.ics` path, there's no live object to update — the user edits the imported event directly in their calendar app; just note the change if they mention it.

## What This Doesn't Do

- Doesn't schedule recurring/habitual review commands (`/weekly-review`, `/daily-note` itself) — those are session-driven, not calendar-blockable in a meaningful way.
- Doesn't touch beads with dependencies still blocking them — `bd ready` already excludes those, which is exactly right here too.
- Doesn't guess durations from task complexity. If the default block size is consistently wrong for a class of task, that's a config change (Step 0), not something to infer per-task.

## Related

- `/daily-note` and `/brief` can offer this as a one-line follow-on ("3 ready P1s unscheduled — `/schedule-tasks`?") but don't run it automatically as part of either — this command's confirmation step is the whole safety model, and that only works if it's invoked deliberately.

## Begin

Check config, gather candidates, propose the schedule, and wait for confirmation before creating anything.
