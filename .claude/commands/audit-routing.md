# /audit-routing — Calibrate the Auto-Filer

Re-read what `/process-inbox` filed automatically and ask whether it was right.

Auto-filing is defensible because it's stamped and revertible. It stays defensible only if something checks it. Without a calibration loop the confidence threshold is guesswork — and a systematically miscalibrated filer produces a vault that looks organized and isn't, which is worse than a visible mess.

Runs weekly, as part of `/weekly-review`. Takes a few minutes.

## Step 1: Find What Was Auto-Filed

```bash
grep -rn "routed_by: auto" --include="*.md" .
grep -rn "routed_by: auto" --include="*.md" . | head -50
```

Both the frontmatter form (new notes) and the inline HTML-comment form (appended sections) carry the stamp. Default window: since the last audit, or the last 14 days if there hasn't been one.

Also list `Inbox/unclear/` with ages:

```bash
ls -la Inbox/unclear/
```

## Step 2: Re-Route Each One, Cold

For each item: read the note's content **without looking at the stamped rationale first**. Decide where you'd put it today. Then compare.

Reading the rationale first is how this audit becomes theater — you'll agree with reasoning you find persuasive, which is all of your own reasoning.

Three outcomes:

- **Same destination** — correct. Count it, move on.
- **Different destination, and the original was defensible** — a near-miss. Count it separately. These are the calibration signal, not errors.
- **Different destination, and the original was wrong** — a miss. These get fixed.

## Step 3: Fix the Misses

Move the content. Update the stamp:

```yaml
routed_by: auto
routed_at: 2026-09-01
rerouted_at: 2026-09-08
rerouted_from: Resources/Billing.md
confidence: high
routing_rationale: names Riverside and contract term; Areas/Pricing covers both
audit_note: originally filed as reference; it's an active pricing decision
```

**Keep the history.** A note that shows it was re-routed once is more informative than one that pretends it landed correctly, and the trail is what makes the next audit possible.

Don't rewrite content while fixing placement. Same rule as filing.

## Step 4: Re-Examine `Inbox/unclear/`

Items land there because context was missing at the time. A week later the context often exists — the meeting happened, the Area got created, the person got a note.

Route what's now routable. Anything past **14 days** that still can't be routed gets a decision, out loud:

> *"'the thing Marcus mentioned about the eligibility file' has been unclear for 3 weeks. Nothing in the vault gives it context. Delete it?"*

An item nobody can interpret after three weeks isn't being preserved, it's being avoided. Say that plainly and let them choose.

## Step 5: Report the Number

The point of this command is one number and one pattern.

```
🎯 Routing audit — 24 auto-filed since Sep 1

Correct:     19  (79%)
Near-miss:    4  (defensible, filed elsewhere)
Wrong:        1  (fixed → Areas/Pricing.md)

Unclear backlog: 3 items, oldest 19 days

Pattern: pricing content keeps landing in Resources/ when it names a
customer. Areas/Pricing is the better default for anything with an
account name in it.
```

**The pattern line is the deliverable.** A percentage tells you whether to trust the filer; a named systematic error tells you what to change. If there's no pattern, say so — "one-off miss, no pattern" is a real finding and better than a manufactured one.

## Step 6: Act on the Calibration

| Correct rate | What it means | Do |
|---|---|---|
| Above 90% | Threshold may be too conservative | Consider auto-filing more of what currently lands in `unclear/` |
| 70–90% | Working as designed | Nothing. Note the pattern. |
| Below 70% | Filer is guessing | Tighten: more items to `unclear/`, and write the specific rule that would have caught the misses |

When a pattern is stable across two audits, **write it into `CLAUDE.md`** under your Areas — that's how calibration becomes durable rather than something rediscovered every week. One line: *"Anything naming a customer account goes to `Areas/Pricing`, not `Resources/`."*

## Judgment

**Don't audit what a human filed.** `routed_by: user` is out of scope. They know where their notes go.

**Small windows are fine.** Four items audited weekly beats forty audited never.

**Resist re-litigating close calls.** A near-miss where both homes are reasonable is not a miss, and treating it as one drives the threshold toward uselessly conservative — which means everything lands in `unclear/`, which means the drain stopped working.

**This command is architecture work.** Keep it to a few minutes. If auditing the filer becomes more engaging than using the vault, that's the failure this whole system is meant to discipline.

## Related

- `/process-inbox` — what this audits
- `/weekly-review` — calls this
- `/brain-check` — broader vault-health diagnostic

## Begin

Find the auto-filed notes and re-route them cold.
