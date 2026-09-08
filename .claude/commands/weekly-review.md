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

## Step 2: Distill (10 min)

**This is the step that matters most.** Event-shaped notes — `Days/`, `Meetings/` — decay in retrieval by design. State-shaped notes — `Areas/`, `Resources/`, `People/`, beads, memories — do not. Distillation moves the durable content out of the first kind into the second, so the event note can fade without losing anything. ([[Projects/Temporal Retrieval Spec]] Part 5.)

List what's in scope:

```bash
python3 .claude/scripts/brain_index.py undistilled --since 7      # event-shaped notes updated this week without distilled_to
```

For each note, sort its content into four bins and act on each:

| Durable content | Goes to |
|---|---|
| A decision | The relevant `Areas/` note under `## Decisions`, dated, with a `[[source]]` link back |
| A stable fact about a person or system | `bd remember` (then `memory_meta.py confirm`); without beads, append to `People/` or `Areas/` |
| A commitment | A bead — `/process-meeting` should already have made it; verify with `bd list --notes-contains "<note>"` |
| A reference, link, or how-to | `Resources/` |

Rules that make this compound instead of accumulate:

- **Synthesize, don't paste.** If the Area already covers the ground, deepen the existing point. An Area note that's a stack of dated fragments has failed.
- **Every extraction carries a dated link back** to the note it came from: `→ [[Days/YYYYMMDD]]`.
- **Say what you judged non-durable** and left behind. The user may disagree, and that's the conversation worth having.
- **Distinguish inference.** If the distilled sentence is your reading rather than their words, end it with `^inferred`.

Then mark the source note as distilled — this is what lets it decay:

```bash
python3 .claude/scripts/brain_index.py distill "Days/20260905.md" --to "[[Areas/Pricing]]" --to "bd:cab-31"
```

That writes `distilled_to` and `distilled_on` into the note's frontmatter. A note with nothing durable in it still gets marked (`--to none`), so it stops showing up.

**Retired pattern:** no more `week-NN-summary.md` or monthly knowledge-log notes. Summaries compress, which makes them bad traversal points. `Knowledge Changelog.md` stays as the append-only ledger of what moved where — add a line there for each extraction that created or materially changed a state-shaped note.

**Report** — two short lists: what was extracted and where; what was judged non-durable.

### Step 2b: Promotion Proposals

After distillation, run the layer-promotion table ([[Projects/Memoryfield Improvements Spec]] §5):

```bash
python3 .claude/scripts/brain_review.py promote
```

It **proposes, never acts.** Four signals:

| It found | It proposes |
|---|---|
| The same sentence in three or more notes | `bd remember` it — a fact repeated that often is a memory, not a note |
| A memory's subject named in an open bead | link them: `bd update <id> --append-notes "see memory: <key>"` |
| A `Resources/` note cited by `/ask` five or more times in 30 days | add it to the relevant MOC, or promote its one-line summary to a memory |
| An `Inbox/` item older than 14 days | route it: Area, Resource, bead, or delete |

Read the list to the user, one line each, and take a one-word answer per item. Accepted promotions get a line in `Knowledge Changelog.md`. Declined ones are dropped without comment; the script will re-propose next week only if the evidence grew.

### Step 2c: Contradiction Pass

Proactive `/thread` ([[Projects/Memoryfield Improvements Spec]] §3). For each note updated this week, find its nearest neighbours and ask one question per pair:

```bash
python3 .claude/scripts/brain_review.py neighbors --since 7 --cap 20
```

Neighbours come from embeddings when the index has them, otherwise from shared wikilinks and tag overlap. State-shaped older notes (Areas, Resources) are prioritised — that's where stale truth hurts. Pairs that already have a `contradiction` bead, open or closed, are excluded.

For each pair, a reader — a `note-reader` in `parallel` mode, you inline — answers exactly this, quoting both sides:

> *Does the newer note contain a claim that conflicts with a claim in the older note? Quote both if so.*

**Yes with quotes → file a bead. Anything else → nothing.**

```bash
bd create "Possible contradiction: <topic>" -l contradiction -p 2 \
  -d "Newer: [[<newer path>]] — \"<quote>\"\nOlder: [[<older path>]] — \"<quote>\"" \
  --notes "Filed by /weekly-review contradiction pass <date>. The human resolves this; readers never do."
```

Readers return quotes and a yes/no, never a resolution. You don't resolve either — the bead stays open until the user closes it, with whatever they decide recorded in its notes.

Summary line in the review: **"N possible contradictions filed."** Zero is a fine number.

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
- `/link-check` — broken links, orphans, dangling `distilled_to`
- `/rebuild-dashboard` — refresh the command center
- `/reindex` — refresh the retrieval index so next week's `/ask` sees this week's notes at their true age (last, after the file edits above)

## Step 6: Plan Next Week

1. Review what's coming — deadlines in beads, milestones in `Projects/`
2. Set the **top three** for next week — most important outcome, what needs deep work, what has a hard deadline
3. Offer to pre-create Monday's daily note with those filled in

## Step 6b: Cooling Off

```bash
python3 .claude/scripts/brain_index.py cooling
```

Notes whose activation has dropped below 0.6 — retrieved once, not since — and that have no `distilled_to`. Each is a small decision: distill it now (Step 2), or let it go. Offer both, in one line per note. Don't distill everything; a note nobody has needed since March is usually telling you something.

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
