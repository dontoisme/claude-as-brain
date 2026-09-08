# /process-inbox — Drain the Inbox

Take what `/capture` dropped and put it where it belongs. Automatically, by default.

`/capture` is deliberately frictionless, which means the Inbox fills faster than any deliberate process empties it. **A capture system without a drain doesn't degrade gracefully — it dies.** Within a month the vault has two tiers: the notes filed properly and the pile that wasn't. Nothing is lost, but confidence is, and confidence is the whole product.

## The Governing Decision: Auto-File

**File by default. Ask by exception. Never block.**

The instinct here is propose-and-approve, and it's wrong. That pattern comes from navigation-first PKM, where the folder *is* the retrieval path and a misfile genuinely loses the note. Here `/ask` finds a note wherever it sits, so a wrong guess costs a slightly worse folder tree. Approval gates buy nearly nothing and cost the one thing that decides whether this system survives: the chance the drain runs at all.

If you catch yourself writing *"Here are 9 items — shall I file them?"*, you have rebuilt the thing that fails.

## Step 1: Read Everything

Sources, in order:

- `Inbox/Quick Captures.md` — the line-item captures
- Any loose `.md` files directly in `Inbox/`
- `Inbox/unclear/` — only when invoked as `/process-inbox unclear`, or when an item there has aged past 14 days

Read the full text of each item. Do not route from a fragment; a rushed capture is exactly the kind of text that reads one way in isolation and another in context.

## Step 2: Route Each Item by Confidence

Confidence is about **whether you know where this goes**, not about how important it is.

**High** — the item names an Area, a project, a person, or a system that already exists in the vault, or it's an unambiguous type match (a reference URL, a person fact).
→ File it. Silently.

**Medium** — plausible home, no direct evidence. One reasonable reading and no competing one.
→ File it. Silently. Stamp `confidence: medium` so `/audit-routing` looks at it later.

**Low** — two plausible homes with nothing to choose between them, or a fragment you can't interpret, or something referencing context that isn't in the vault.
→ `Inbox/unclear/YYYYMMDD-<slug>.md`. Still captured, still readable by `/ask`, just flagged. **Do not ask the user.**

Destinations:

| The item is | Goes to |
|---|---|
| About an ongoing responsibility | `Areas/<Area>.md` — dated section |
| Tied to active, time-bounded work | `Projects/<Project>/` |
| Reference material, no owner | `Resources/<Topic>.md` |
| A fact about a person | `People/<Name>.md` |
| A durable one-line operational fact | Propose `bd remember` (see Step 4) |
| Something to *do* | Propose a bead (see Step 4) |
| No longer useful | Propose deletion — never delete silently |

## Step 3: File Without Editing

**Move the words. Do not improve them.**

A rushed capture's phrasing carries context that a tidied version loses — *"does anyone actually track churn by contract term, or have we just been assuming"* says something about the user's state of mind that *"Investigate churn tracking by contract term"* has thrown away.

Append to an existing note under a dated `###` heading. Create a new note from the appropriate template when there's no home yet, substituting `{{date:...}}` values rather than copying them.

**Stamp every routing decision.** This is what makes silent filing safe — the record is auditable and greppable, which is why you don't need an approval gate.

Into a new note's frontmatter:

```yaml
routed_by: auto
routed_at: 2026-09-08
routed_from: Inbox/Quick Captures.md
confidence: high
routing_rationale: names Riverside and contract term; Areas/Pricing covers both
```

Appending to an existing note instead, put it inline on the heading line so it survives:

```markdown
### 2026-09-08 — Churn by contract term
<!-- routed_by: auto · confidence: medium · from: Inbox/Quick Captures.md · rationale: pricing-adjacent, no direct Area reference -->
```

One line of rationale. Enough that a human reading the note in six months knows why it's there.

## Step 4: Beads Are the Exception

**A misfiled note is clutter. A wrongly-created bead is a false obligation that produces real guilt, and a missed one is a genuine commitment that never became trackable.** Both cost more than a folder mistake, and neither is visible until much later.

So: **propose, don't create.** List proposed beads at the end as a single block the user can accept or wave off in one word.

```
Proposed as commitments — say "no" to any:
  · ask Dana what number would reopen the pricing call
  · send Riverside the revised terms before Thursday
```

If they say nothing, create them and confirm in one line each. If a capture is *unmistakably* a task (verb, owner, deadline — `/capture` would already have made it a bead), create it and confirm. The confirmation is the point: an auto-created bead the user never saw is the failure mode.

Same for `bd remember` — propose the fact and the key.

Pin every `bd` call to the brain's store:

```bash
(cd "$CLAUDE_BRAIN" && bd q "<the thing>")
```

## Step 5: Clear What You Filed

Remove filed items from `Inbox/Quick Captures.md`. An item that got filed and stayed in the Inbox is a duplicate, and duplicates are how a vault stops being trusted.

Leave the file's structure and headers intact. If everything drained, the capture section is empty — that's the goal state, not an error.

## Step 6: Commit

**This step is not optional, and it's what makes Step 2 defensible.** Auto-filing is safe because it's revertible; an uncommitted auto-file is not revertible, and then "git is the undo" was just something we said.

```bash
git add -A && git commit -m "process-inbox: filed 9, 2 unclear"
```

If the vault isn't a git repo, say so once — and route more conservatively for the rest of the run, because the undo doesn't exist.

## Step 7: Report in One Line

```
📥 Filed 9 · 2 unclear · 1 bead proposed
```

Then, only if there's something to act on:

```
Unclear (Inbox/unclear/):
  · "the thing Marcus mentioned about the eligibility file" — no context in the vault
  · "Q4?" — can't interpret

Proposed as commitments — say "no" to any:
  · ask Dana what number would reopen the pricing call
```

That's the whole response. No table of what went where, no summary of themes, no offer to explain the routing. The stamps are the record; nobody wants to read a filing report.

## Judgment

**One capture, several things?** Split it. A blob is unprocessable later, and splitting is the one edit to the text that's clearly worth making.

**Deleting is a valid outcome and the most under-used one.** An item that's sat three weeks and still has no home wasn't important. Propose deletion plainly; don't file junk to avoid the awkwardness of saying so.

**An item that would create a new Area?** That's a low-confidence item, not a high-confidence one. New Areas are a real structural decision — `Inbox/unclear/`, and mention it once.

**Never ask a routing question mid-run.** Batch anything genuinely needing input to the final report. The run completes either way.

**Aging.** Anything in `Inbox/unclear/` past 14 days is surfaced by `/brief`. Under `/process-inbox unclear`, work those first — a second look with fresh context resolves most of them.

## If `bd` Isn't Installed

Tasks go into `Todos.md` under the right section rather than becoming beads; durable facts get filed as normal notes. Everything else is unchanged. Say it once, at most.

## Related

- `/capture` — the write side. Fast, no routing.
- `/daily-note` — runs a light pass of this automatically
- `/audit-routing` — the calibration loop that keeps the confidence thresholds honest
- `/weekly-review` — the deliberate cleanup, including `Inbox/unclear/`

## Begin

Read the Inbox and file it.
