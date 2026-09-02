# /process-meeting — Meeting Input to Structured Record

Turn raw meeting material into a structured note, with every commitment modeled as a bead.

Takes scratch notes, an AI summary (Granola, Gemini, Otter, Zoom), a transcript, or just what the user remembers.

## What You Need

Ask only for what's missing:
- Meeting name, date (default today), attendees
- The raw material

**Vague recall still processes.** A partial note beats no note — write it, and mark the gaps explicitly rather than smoothing over them.

## Step 1: Separate What Raw Notes Blur

Before writing anything, sort the material into five buckets. Most raw notes mix these together, and the whole value of processing is pulling them apart:

- **Decisions** — choices actually made. Not options discussed.
- **Commitments** — someone owes someone something. Has an owner.
- **Insights** — strategic learning worth extracting to an Area.
- **Questions** — raised and not resolved.
- **Context** — background a future reader needs.

The two that get lost most often are **commitments made by the user in passing** ("yeah I'll take a look at that") and **questions that were raised and dodged**. Hunt for both specifically.

## Step 2: Write the Note

Start from `Templates/Meeting Notes.md`. Path: `Meetings/YYYYMMDD - Meeting Name.md`.

**Delete sections that don't apply.** An empty Decisions table is worse than no Decisions section — it implies nothing was decided rather than that nothing was recorded.

Substitute `{{date:...}}` values; never write the literal string.

**For decisions, capture what was rejected.** The alternatives and why they lost are the part people re-litigate three months later, and the part raw notes always omit.

**Attribute claims to people.** "Dana thinks the timeline is at risk" is far more useful in six months than "the timeline is at risk."

**Provenance.** The template sets `source: mixed`, because a processed meeting note is their material shaped by you. Anything you concluded rather than transcribed — "this probably means finance was already worried", a reading of someone's tone, a gap you filled — ends with `^inferred`. Attributed statements may end with `^human`. `/ask` uses these to keep your interpretation from being replayed later as what was said.

**Mark uncertainty inline.** `<!-- unclear from notes -->` beats a confident guess. You are writing this into a memory system; a plausible invention here is indistinguishable from a fact later.

## Step 3: Commitments Become Beads

Every commitment gets an issue:

```bash
bd create "<action>" --type task --priority 2 \
  --notes "From [[Meetings/YYYYMMDD - Name]] — <context>"
```

`--type task` and `--priority 2` are the defaults; state them anyway when it aids clarity.

Model the dependencies — this is what makes beads worth using over a checklist:

```bash
bd create "<action>" --deps "blocks:cab-12"      # typed, at create time
bd dep add <blocked-id> <blocker-id>             # after the fact
```

`--deps` accepts either a bare ID or a typed form (`blocks:`, `discovered-from:`), comma-separated for several.

If the pricing doc can't start until Legal answers, that's an edge. Once modeled, `bd ready` correctly hides the doc until it's actually actionable, instead of nagging about work that can't begin.

**Decisions can be beads too:**
```bash
bd create "<decision>" --type decision --notes "<rationale, alternatives rejected>"
```
This makes decisions queryable — `bd list -t decision` becomes "what have we settled," which `/ask` and `/prep` both check.

**Gotchas** (see `Beads Guide.md`):
- `bd create`, not `bd add`
- `bd update` does **not** take `--deps` — use `bd dep add`. Don't recreate the issue.
- Tasks can't depend on epics; depend on the epic's relevant child
- `--notes` on create; `--append-notes` on update
- `-l/--labels`, not `--tag`

Then run `/sync-todos` so `Todos.md` reflects the new state.

## Step 4: Link It Into the Vault

Check what exists before linking — a wikilink to a nonexistent note is a broken link, not a promise.

1. **Areas** — which ongoing responsibility does this touch? Append insights with a date and source link.
2. **Projects** — link if it relates to active work.
3. **People** — every attendee should have a `People/` note. Create missing ones from `Templates/Person.md`, and update the "I owe them / they owe me" sections from this meeting's commitments. **This is what makes `/prep` work later** — skip it and prep degrades to grep.
4. **Today's daily note** — link the meeting under Meetings.
5. **Bump the link targets** — `python3 .claude/scripts/brain_index.py bump --links-of "Meetings/YYYYMMDD - Name.md" --kind wikilink` (skip when there is no index). Areas and People this meeting links to just became warmer.

## Step 5: Verify Before Reporting

- ✓ File in `Meetings/` named `YYYYMMDD - Name.md`
- ✓ Frontmatter complete (date, attendees, tags, `source: mixed`)
- ✓ Your inferences end with `^inferred`
- ✓ Every wikilink points at a real note
- ✓ Every commitment is a bead with a source reference
- ✓ Dependencies modeled where they exist
- ✓ `People/` notes updated for attendees
- ✓ Linked from today's daily note
- ✓ `/sync-todos` run

## By Meeting Type

**Decision meetings** — lead with Decisions and the rejected alternatives.
**Technical** — architecture choices, tradeoffs, debt incurred.
**1:1s** — commitments both directions, concerns raised, anything about scope or growth. Update the `People/` note substantively.
**User research** — quotes verbatim, observations separate from interpretations, link to the research Area.
**Standups** — usually just commitments and blockers. Don't over-structure; a short note is the right output.

## Report

```
✅ Meetings/20250318 - Pricing Review.md
✅ 4 commitments → cab-44 … cab-47 (cab-46 blocked on cab-44)
✅ 1 decision → cab-48
✅ Insights → [[Areas/Pricing]]
✅ People/ updated: Dana, Marcus
✅ Todos.md synced
```

Then offer to draft any follow-up messages the commitments imply.

## If `bd` Isn't Installed

Commitments go into `Todos.md` as a table with source links, and dependencies become a "blocked on" note in the Context column. Say once that beads would model this properly.

## Begin

Ask for the meeting details and raw material.
