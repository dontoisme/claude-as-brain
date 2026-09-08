# /brain-check — Is This System Still Alive?

A diagnostic on the vault itself, not its contents. Answers one question: **is this thing still being used the way it needs to be used, or has it quietly become an archive?**

Retrieval commands are pull-based and immediately rewarding, so they thrive on their own. The maintenance commands are recurring, unprompted, and low-reward — they stop silently, and nothing announces it. This is what announces it.

Run it monthly, or when something feels off.

## Step 1: Measure

Gather without commentary first. Numbers, then interpretation.

**Content flow**
```bash
find . -name "*.md" -not -path "./.git/*" | wc -l       # total notes
ls -t Days/*.md | head -1                                # last daily note
ls -t Meetings/*.md | head -1                            # last meeting note
find Areas Projects Resources -name "*.md" -mtime -30 | wc -l   # notes touched in 30d
```

**Inbox health**
```bash
grep -c "^- \*\*" "Inbox/Quick Captures.md"     # pending captures
ls Inbox/unclear/ 2>/dev/null | wc -l           # unclear backlog
find Inbox/unclear -name "*.md" -mtime +14 2>/dev/null | wc -l   # past SLA
```

**Maintenance freshness** — last modification of each generated artifact:
```bash
ls -lt Dashboard.md Todos.md "Knowledge Changelog.md" MOCs/*.md
```

**Commitments** (pinned to the brain's store):
```bash
(cd "$CLAUDE_BRAIN" && bd ready | wc -l)
(cd "$CLAUDE_BRAIN" && bd stale)
(cd "$CLAUDE_BRAIN" && bd list --status blocked)
(cd "$CLAUDE_BRAIN" && bd memories | wc -l)
```

**Bead store identity** — assert which store is actually answering. A misrouted store is the failure that hides longest:
```bash
(cd "$CLAUDE_BRAIN" && bd list 2>/dev/null | head -1)
```

**Link integrity** — run `/link-check` and take its counts. Don't duplicate its logic.

**The architecture-vs-content ratio** — the one nobody thinks to measure:
```bash
git log --since="6 weeks ago" --name-only --pretty=format: | grep -c "^\.claude/\|^CLAUDE.md\|^PLAN.md\|^README.md"
git log --since="6 weeks ago" --name-only --pretty=format: | grep -c "^Areas/\|^Meetings/\|^People/\|^Days/\|^Projects/\|^Resources/"
```

## Step 2: Interpret

Report state, not judgment. One line each, and only for things that are actually off.

| Signal | Threshold | Reads as |
|---|---|---|
| Days since last daily note | > 5 | The daily habit has lapsed |
| Days since last `/weekly-review` | > 21 | Capture without compounding |
| Inbox pending | > 15 | The drain isn't running |
| `Inbox/unclear/` past SLA | any | Aged items need a decision, not a re-file |
| Notes added to `Areas/` in 30d | 0 | Nothing is being extracted upward |
| `Dashboard.md` / `Todos.md` age | > 14d | Generated artifacts are stale and being trusted anyway |
| Stale beads | > 5 | Commitments are being made and abandoned |
| Broken links | > 10 | Structural rot |
| Memories stored | 0 | Layer 3 is unused — the highest-leverage habit, unstarted |
| Architecture commits > content commits | — | **See below** |

## Step 3: The Uncomfortable One

**If commits touching `.claude/`, `CLAUDE.md`, `PLAN.md`, and `README.md` outnumber commits adding notes under `Areas/`, `Meetings/`, `People/`, and `Days/` — say so plainly.**

This is the most likely failure mode of this project, and it isn't a bug. Refining `retrieval_mode`, tuning model tiering, and adding commands are all genuinely more rewarding than running `/ask` on a boring question. The tool gets captured by the exact instinct it was built to discipline, and it happens without any single bad decision.

Say it as an observation, once:

> *Last six weeks: 14 commits to `.claude/` and `CLAUDE.md`, 3 notes added. The architecture is outpacing the content. Worth a rule — no new commands until there are 30 real notes in here.*

Don't moralize, don't repeat it in a later run if nothing changed. One line, and it's their call.

## Step 4: Report

One screen. Same discipline as `/brief`.

```markdown
## Brain check — 2026-09-08

**Content:** 47 notes · last daily note 2 days ago · 6 notes touched in 30d
**Inbox:** 4 pending · 2 unclear (1 past SLA, 19 days)
**Commitments:** 8 ready · 2 stale · 1 blocked 3 weeks
**Memories:** 11 stored
**Generated:** Dashboard 9d · Todos 1d · MOCs 12d
**Links:** 2 broken, 5 orphans

⚠️  No weekly review in 24 days — insights aren't reaching Areas.
⚠️  cab-22 blocked on Legal since Aug 18.

Otherwise healthy.
```

End with **at most one** suggestion, and only when earned. A diagnostic that ends in a to-do list is a diagnostic nobody runs twice.

## What This Is Not

**Not a nag.** Surfacing decay costs nothing and converts an invisible failure into a visible one. That's the entire job. Guilt is not part of the job.

**Not a fixer.** It reports. `/weekly-review`, `/process-inbox`, `/link-check`, and `/update-mocs` do the work. Offer one; don't chain them automatically.

**Not a substitute for use.** A vault with perfect health metrics and nothing in it has failed. Content flow is the first section for a reason.

## Which Maintenance Actually Matters

When reporting, weight accordingly — they are not equally required:

- **`/weekly-review`** — genuinely required. Skip it and the vault accumulates instead of compounding.
- **`/process-inbox`** — required, but it rides on `/daily-note`, so it mostly runs itself.
- **`/sync-todos`, `/update-mocs`** — mechanical, invoked automatically by the commands that need them. Never run these by hand.
- **`/rebuild-dashboard`** — monthly is plenty.
- **`/link-check`** — quarterly. A nicety. Link rot is slow.
- **`/audit-routing`** — weekly at first, monthly once the correct rate stabilizes above 85%.

Users who skip a "required" step feel they've broken the system. Users who skip an explicitly optional one don't. Say which is which.

## If `bd` Isn't Installed

Skip the commitment and memory sections. Report the note-count, inbox, and maintenance-age signals. Mention once that the commitment health check isn't available.

## Related

- `/brief` — the daily version; carries a one-line vault-health summary
- `/weekly-review` — where most of what this finds gets fixed
- `/audit-routing` — auto-filing calibration
- `/link-check` — the structural detail behind the link counts

## Begin

Measure, then interpret. Numbers before judgment.
