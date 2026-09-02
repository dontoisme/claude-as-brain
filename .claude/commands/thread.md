# /thread — Trace How Thinking Evolved

Follow a topic chronologically across the vault and report the arc: what you believed, what changed it, where it stands now.

This is the command no note-taking app can do. Search finds mentions; graph view finds connections. Neither can tell you *"you were confident in March, a customer call shook it in April, and you never formally resolved it."*

## The Failure Mode to Avoid

**Models love to impose a tidy narrative.** Real thinking is messy, repetitive, and often goes nowhere.

If the notes show no evolution — the same position stated four times — **say that**. "Your position hasn't changed since March; here's where it was stated" is a true and useful answer. Manufacturing an arc out of noise is the specific way this command fails, and it fails invisibly, because a clean story reads as insight.

Related: do not mistake *someone raising a concern* for *a decision changing*. A complaint in a customer call is evidence, not a reversal. Report it as what it was.

## Step 1: Collect Everything, Then Order It

Sweep the same way `/ask` does — keywords, wikilink anchors, MOCs, tags, filenames, beads (`bd search "<topic>" --status all`, and `--desc-contains`). If the index exists, start with it in the **archival** profile, which switches recency decay off — a thread needs the six-month-old note as much as yesterday's:

```bash
python3 .claude/scripts/brain_index.py rank "<topic>" --profile archival --k 20
```

Then **date every hit**:

| Source | Date from |
|---|---|
| `Days/YYYYMMDD.md` | filename |
| `Meetings/YYYYMMDD - Name.md` | filename prefix |
| Other notes | frontmatter `date:` |
| Dated sections inside Area notes | the section heading |
| Beads | created / closed timestamps |

**Sort strictly chronologically.** Area notes are the tricky case: they accrete dated entries over time, so a single file may contribute several points at different dates. Split them rather than treating the file as one event.

## Step 2: Find the Actual Turns

Read the sequence and identify:

- **Initial position** — where does this topic first appear, and what was believed?
- **Turns** — where did the position change? What specifically caused it? Name the note.
- **Evidence** — what data, conversation, or event moved it?
- **Current state** — where does it stand in the most recent note?
- **Unresolved** — what's open? Questions never answered, beads never closed, contradictions never reconciled.

Distinguish three different things that look similar in notes:

1. **A decision changed** — you concluded something different
2. **Evidence accumulated against it** — but no decision was revisited
3. **It went quiet** — the topic just stopped appearing

Number 2 is the most valuable thing this command surfaces, and the easiest to misreport as number 1.

## Step 3: Report

**Open with the shape of it in two or three sentences.** The arc, or the absence of one. This is what the user actually wants; the timeline is supporting evidence.

Then the timeline:

```
2025-03-12  Decided annual-only for enterprise
            Rationale: cash flow predictability. Dana drove it.
            → Meetings/20250312 - Pricing Review.md

2025-04-02  First pushback
            Two mid-market accounts asked for quarterly; one said annual
            "was the reason we almost didn't sign."
            → Meetings/20250402 - Riverside Renewal.md

2025-04-18  You flagged the rationale may no longer hold
            The cash position the decision assumed has changed.
            Opened cab-31 to revisit. Still open, untouched since.
            → Areas/Pricing.md
```

Close with:

- **Where it stands** — the current position, stated plainly
- **What's unresolved** — open questions and open beads
- **What you'd flag** — e.g. *"the original rationale has been undermined twice and never revisited"*

## After Reporting: Bump

```bash
python3 .claude/scripts/brain_index.py bump <every note you read in full> --kind thread
```

Same rule as `/ask`: read-to-answer, not listed-as-candidate.

## Special Cases

**Fewer than three data points** — say so. "Only two notes touch this; that's not enough for an arc, but here's both." Don't stretch.

**The topic goes quiet** — worth naming explicitly. "Nothing since May 4" is often the most useful sentence in the answer.

**Circular** — if the same debate recurs without resolution, say that. Recurring unresolved debates are a real pattern and worth surfacing as one.

**Contradiction never noticed** — the highest-value output. Flag it directly: *"Your Mar 12 note and your Jun 2 note take opposite positions and nothing reconciles them."*

## Scaling: Parallel Retrieval

If `retrieval_mode: parallel` in `CLAUDE.md`, fan out the collection step — `vault-scout` per angle, then `note-reader` batches over the candidates. Same contract as `/ask`: **subagents return dated verbatim excerpts; you build the timeline.**

The ordering and arc analysis must stay in the main thread. A subagent seeing three of eleven notes will confidently report a turning point that isn't one — the arc is only visible from the whole sequence, which is exactly what a partial view cannot show.

Batch readers **by time period** rather than by topic, so each returns a contiguous slice you can stitch in order.

## If `bd` Isn't Installed

Markdown-only timeline. Skip the bead lifecycle points. Everything else works.

## Examples

**`/thread annual pricing`** — the arc of a decision and the evidence that accumulated against it.

**`/thread onboarding`** — how understanding of a problem space developed as research came in.

**`/thread Dana`** — how a working relationship and their scope evolved. Useful before a review or a difficult conversation.

## Begin

Take the user's topic, collect every dated mention, and trace it.
