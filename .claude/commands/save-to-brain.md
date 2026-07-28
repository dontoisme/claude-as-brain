# /save-to-brain — Capture a Session Insight

Turn something worked out in this session into a note that'll be findable in six months.

Distinct from `/capture`, which is a fast Inbox drop with no thinking. This one routes deliberately and links properly.

## Step 1: Get Their Framing

"What's the key thing you want to capture?"

Offer a suggestion if the session has an obvious subject — but **let them name it.** Their framing is how they'll search for it later, and it's almost never how you'd have titled it.

## Step 2: Check the Layer First

Before writing a note, ask whether it even *is* a note.

**If the insight is one durable line** — "Priya owns renewals", "the staging DB resets nightly" — this is Layer 3. Say so and do that instead:

```bash
bd remember "<fact>" --key <key>
```

**Don't write three paragraphs around a one-line fact.** A note requires opening; a memory arrives automatically. Getting this wrong is the most common way this system accumulates weight without value.

If there's a durable fact *inside* a larger insight, do both: write the note, and pull the fact out into a memory.

## Step 3: Route It

**Look at what actually exists first** — list `Areas/`, `Projects/`, `Resources/`. Routing to a folder that isn't there creates orphans.

| Content | Destination |
|---|---|
| Relates to an ongoing responsibility | `Areas/<Area>.md` — append a dated section |
| Reference material, no ownership | `Resources/<Topic>.md` — new note |
| Tied to a specific active project | `Projects/<Project>/<Topic>.md` |
| A decision with a rationale | New note **plus** `bd create -t decision` |
| Genuinely unclear | `Inbox/Quick Captures.md` |

Two plausible homes? Ask once: *"Areas/Pricing or Resources/Billing — which is how you'd look for it later?"* Never file it twice; duplicates are how a vault stops being trustworthy.

## Step 4: Write It

New standalone note:

```markdown
---
date: YYYY-MM-DD
tags: ["#insight", "<topic>"]
type: capture
---

# [Topic in their words]

## Context
[What prompted this — 1-2 sentences]

## Key Points
- [Insight]

## Details
[Enough that this makes sense in six months to someone who wasn't here]

## Decisions
[If applicable — including what was rejected and why]

## Related
- [[Related note]]

---
*Captured YYYY-MM-DD*
```

Appending to an existing Area note instead? Skip the frontmatter, add a dated `###` section under Insights.

**Write for retrieval.** The test is not "is this accurate" but "would I find this when I need it?" Use the words they'd search for, not the most precise ones. Name specific people, dates, and systems — those are what grep catches.

## Step 5: Link It Up

Three connections, all required:

1. **`Knowledge Changelog.md`** — one line, newest first:
   ```markdown
   ### YYYY-MM-DD — [Topic]
   **Category:** [Area/Resource/Project]
   **Summary:** [One line]
   **Location:** [[Full note link]]
   ```

2. **Today's daily note** — under Insights & Learnings. Create today's note if missing. This is what makes weekly review work; insights surface chronologically instead of vanishing into folders.

3. **Wikilinks in both directions** — the note links out, and at least one existing note links in. A note nothing points at is nearly invisible.

## Step 6: Extract Any Commitments

If the insight implies action:

```bash
bd create "<action>" --type task --priority 2 --notes "From <note path>"
```

Use `--deps` where one blocks another. Then `/sync-todos`.

## Step 7: Confirm

```
✅ Resources/Rate Limiting Patterns.md
📝 Knowledge Changelog
📅 Linked from Days/20250318.md
🧠 Remembered: staging-db-resets
✅ 2 tasks → cab-44, cab-45
```

Drop the lines that don't apply.

## Guidelines

- **Their framing first** — don't guess the topic
- **Prefer new notes** when content stands alone; append when it deepens an existing thread
- **Descriptive filenames** — `Notes.md` is where things go to die
- **One home per idea**
- **Say what you inferred** — if you're synthesizing beyond what was actually discussed, mark it

## If `bd` Isn't Installed

Skip the memory and task steps; put action items in `Todos.md` directly. Mention once that `bd remember` would have suited the durable-fact case, then move on.

## Begin

Ask what they want to capture.
