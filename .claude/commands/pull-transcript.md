---
description: Fetch a Zoom meeting transcript directly via the Zoom MCP and run it through /process-meeting — no manual export needed
argument-hint: [meeting name, date, "last meeting", or leave blank to process all unprocessed transcripts in ~/Documents/Transcripts/]
---

# /pull-transcript — Process Transcripts from Folder or Zoom

Two modes depending on whether `$ARGUMENTS` is provided:

- **No argument** → **Inbox mode**: scan `~/Documents/Transcripts/` for unprocessed files and run `/process-meeting` on each one.
- **With argument** → **Named mode**: find the transcript by checking the folder first (token-efficient), falling back to the Zoom MCP only if no local file matches.

---

## Mode A — Inbox Mode (no argument)

### A1. Scan for unprocessed transcripts

List all `.txt` and `.vtt` files in `~/Documents/Transcripts/` that are **not** inside the `Processed/` subfolder:

```bash
ls ~/Documents/Transcripts/*.txt ~/Documents/Transcripts/*.vtt 2>/dev/null
```

**Nothing found** → say so and stop. Suggest downloading from Zoom desktop (meeting → Transcript tab → Download).

**Files found** → list them for the user with a count, then process each one in sequence (not in parallel — each runs the full `/process-meeting` pipeline and the output should be readable as it goes).

### A2. Process each file

For each file:
1. Run the full `/process-meeting` pipeline against it (read the file, extract structure, write meeting note, create beads, update Areas).
2. After `/process-meeting` completes successfully, move the file to `~/Documents/Transcripts/Processed/`:
   ```bash
   mv "~/Documents/Transcripts/filename.txt" "~/Documents/Transcripts/Processed/filename.txt"
   ```
3. Report completion for that file before moving to the next.

**If a file fails** (can't be parsed, too sparse to extract a title/date) → say so, leave it in the inbox unprocessed, and continue to the next file. Don't abort the whole batch.

### A3. Final report

```
📥 Inbox processed: 3 transcripts
  ✅ Q3 Planning Sync March 12 2025.txt → Meetings/20250312 - Q3 Planning Sync.md
  ✅ Onboarding Review March 14 2025.txt → Meetings/20250314 - Onboarding Review.md
  ⚠️  notes-messy.txt — too sparse to extract meeting structure, left in inbox
```

---

## Mode B — Named Mode (argument provided)

`$ARGUMENTS` is a meeting name, a date, or something like "last meeting" / "today's standup".

### B1. Check the local folder first

Scan `~/Documents/Transcripts/` (not `Processed/`) for a filename that fuzzy-matches `$ARGUMENTS` — same meeting name, approximate date, or obvious substring. If a match is found:

```
📂 Found locally: ~/Documents/Transcripts/Q3 Planning Sync March 12 2025.txt
→ Skipping Zoom API. Running /process-meeting...
```

Then proceed directly to B4 (process and move).

### B2. Fall back to Zoom MCP

Only if no local file matches. Requires the Zoom MCP to be connected — if it isn't, say so and stop.

Call `search_meetings` with:
- `q` — the meeting name/topic
- `from` / `to` — a UTC date range. For "last meeting" or no date, use the last 24–48 hours. For a named recurring meeting with no date, widen to the last 2 weeks. Compute from the current date in session context.

**Multiple candidates** → list them (topic, date, duration) and ask which one.
**Nothing found** → say so and stop. Don't fabricate.

### B3. Pull and assemble transcript from Zoom

Call `get_meeting_assets` with the resolved `meetingId` (prefer UUID). Extract the transcript from `my_notes.transcript.transcript_items`, assembling entries in chronological order:

```
HH:MM:SS --> HH:MM:SS
Display Name: text
```

**No transcript available** (audio-only, transcription disabled, still processing) → say exactly which and stop. Don't substitute the AI summary.

### B4. Archive and process

Save the assembled transcript to `~/Documents/Transcripts/Processed/` with a filename matching the meeting topic and date. Then run the full `/process-meeting` pipeline against it.

If Zoom returned a `summary` or `next_steps` payload, note it exists but **build the meeting note from the transcript**, not the AI summary.

### B5. Report

```
🎥 Pulled: "Q3 Planning Sync" (2025-03-12, 27 min)
📄 Archived: Documents/Transcripts/Processed/Q3 Planning Sync 2025-03-12.txt
→ Running /process-meeting...
```

---

## Begin

Check `$ARGUMENTS`: if empty, run Mode A. If provided, run Mode B.
