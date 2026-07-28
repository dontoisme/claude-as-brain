# /prep — Walk In Prepared

Pull everything relevant before a meeting, a conversation, or a decision. The inverse of `/process-meeting`.

Usage: `/prep <person>` · `/prep <meeting name>` · `/prep <topic>`

The goal is a short briefing you can read in ninety seconds and walk in knowing what's outstanding — especially the commitments you forgot you made.

## Step 1: Resolve the Target

**A person** → `People/<Name>.md`, plus every meeting they attended, every note mentioning them, beads assigned to or blocked on them.

**A recurring meeting** → prior instances in `Meetings/` by name. The last one matters most: what was decided, what was promised, what's still open.

**A topic** → same sweep as `/ask`, narrowed to what's actionable rather than what's known.

**Ambiguous** → ask once, with the candidates you found. Don't guess between two people with the same first name.

## Step 2: Gather

1. **Last interaction** — when, and what happened. Lead with this.
2. **Open commitments, both directions:**
   - What you owe them — `bd list` filtered to them, plus the "I owe them" section of their `People/` note, plus unfulfilled promises in meeting notes
   - What they owe you — blocked beads, waiting-on items, requests you made
3. **Unresolved questions** — open questions from prior meetings that were never answered
4. **Recent context** — anything from the last two weeks touching them or the topic, even indirectly
5. **Decisions in flight** — active decisions this conversation might affect
6. **Stored facts** — `bd memories "<name or topic>"`

Useful beads queries:
```bash
bd list -a "<name>" --status open,blocked   # what's on their plate
bd list --status blocked                    # what you're waiting on
bd list --overdue                           # past due, not closed
bd search "<name or topic>" --status all    # --status all to include closed
bd list --notes-contains "<name>"           # mentions buried in issue notes
bd list -t decision --status all            # decisions touching this
bd memories "<name or topic>"
```

Beads has a first-class `decision` issue type (alias `adr`). If the vault uses it, `bd list -t decision` is the fastest route to "what have we already settled" — check it before reading meeting notes.

## Step 3: The Briefing

Keep it short. This is read while walking to a meeting, not at a desk.

```markdown
## Prep: [Target]

**Last interaction:** [date] — [one line] → [note path]

### You owe them
- [Thing] — promised [date], status → cab-31

### They owe you
- [Thing] — asked [date], no movement since

### Open questions
- [Question raised and never answered, with date]

### Recent context
- [Anything relevant from the last two weeks]

### Worth raising
- [Suggested talking point, grounded in the above]
```

**Drop empty sections entirely.** A briefing with four "None" headings wastes the ninety seconds it was supposed to save.

## What Makes This Useful

**Lead with what's overdue.** The single most valuable line is usually *"you promised them X three weeks ago and it hasn't moved."* That's the thing people walk into meetings having forgotten.

**Be specific about age.** "Asked March 3, no movement in six weeks" beats "outstanding."

**Suggest, don't script.** Two or three grounded talking points. Not an agenda — the user knows their job.

**Flag the awkward thing.** If they've dropped a commitment or a question has been dodged twice, say so plainly. Prep that omits the uncomfortable part isn't prep.

**Cite everything.** Every claim gets a note path. They may want to reread the source before walking in.

**Say when there's nothing.** "No prior notes on this person — first meeting?" is useful and takes one line. Then offer to create the `People/` note after.

## Scaling: Parallel Retrieval

If `retrieval_mode: parallel` in `CLAUDE.md`, the six gathers in Step 2 are independent — dispatch them concurrently as `vault-scout` assignments (meeting history, open commitments, unresolved questions, recent context, decisions in flight, stored facts).

Worth it when someone has a long history in the vault. For a first meeting with two prior mentions, inline is faster.

Assembly and the "worth raising" judgment stay in the main thread. Deciding which outstanding item is the awkward one requires seeing all six results together.

## If `bd` Isn't Installed

Commitments come from meeting notes and the "I owe them / they owe me" sections of `People/` notes. Less reliable, still valuable — say once that beads would make this sharper.

## After the Meeting

Suggest `/process-meeting` to close the loop. Prep and process are two halves of the same cycle: what's outstanding going in, what's newly outstanding coming out.

## Begin

Resolve the target and build the briefing.
