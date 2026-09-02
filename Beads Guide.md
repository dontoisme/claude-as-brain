---
tags: ["#reference"]
---

# Beads Guide

How this vault uses [beads](https://github.com/steveyegge/beads) (`bd`), and the gotchas worth knowing.

**Beads is optional.** The vault works without it — tasks fall back to hand-maintained markdown and the memory layer is unavailable. Install: `brew install beads`.

Verified against **bd 1.0.2**.

---

## Why It's Here

Two jobs that markdown does badly.

**1. Commitments with dependencies.** A markdown checklist is a list of strings. It can't answer *"what can I actually start right now?"* — the question you have every morning. Beads models blockers as a graph:

```bash
bd ready
```

Blocker-aware. Excludes in-progress, blocked, deferred, and hooked issues, returning only genuinely claimable work.

> ⚠️ `bd list --ready` is **not** the same command. It filters by status only. Always use `bd ready`.

**2. Durable facts that load themselves.**

```bash
bd remember "Priya owns renewals, not Marcus" --key priya-renewals
```

Injected via `bd prime` at session start, so every future Claude session in this folder already knows it. No note to open. **This is the highest-leverage habit in the system** and the one people forget exists.

```bash
bd memories              # list all
bd memories renewals     # search
bd recall priya-renewals # full content by key
bd forget priya-renewals # remove
```

**Memories don't expire, so confirm them.** `bd` has no metadata on memories, so a committed sidecar (`.beads/memory-meta.jsonl`) records when each was last confirmed and how long it stays trusted (90 days; 60 for facts about people). `/brief` lists the overdue ones, five at a time, with three answers: confirm, retire, edit.

```bash
python3 .claude/scripts/memory_meta.py confirm priya-renewals --kind person   # after bd remember, or when it's still true
python3 .claude/scripts/memory_meta.py confirm fiscal-year --permanent        # never ask again
python3 .claude/scripts/memory_meta.py due                                    # what /brief will show
```

---

## The Three Layers

| Layer | Holds | Retrieved |
|---|---|---|
| Notes | Prose, reasoning, records | Claude reads them |
| Beads issues | Commitments — owner, state, deps | `bd ready`, `bd stale` |
| Beads memories | One-line durable facts | Auto-injected |

> **Read it later → note. Do it → bead. Just know it → memory.**

The common mistake is writing a note for something that should be a memory. If it fits on one line and you'd want it in every session, it's a memory. A note requires remembering to open it.

---

## Daily Use

```bash
bd ready                          # what's claimable now
bd q "follow up with Dana"        # quick capture, returns just an ID
bd create "Draft Q3 plan" -p 1    # full create
bd close cab-42                   # done
bd show cab-42                    # detail
bd stale                          # what you've quietly abandoned
bd list --overdue
bd list --status blocked
```

## Dependencies

The reason beads beats a checklist:

```bash
bd create "Write pricing doc" --deps "blocks:cab-12"   # at create time
bd dep add cab-15 cab-12                               # after the fact
bd graph                                               # visualize
```

`--deps` takes a bare ID or a typed form (`blocks:`, `discovered-from:`), comma-separated for several.

Once modeled, `bd ready` hides the pricing doc until Legal answers — instead of nagging you about work that can't start.

## Decisions as Issues

Beads has a first-class `decision` type (alias `adr`):

```bash
bd create "Annual-only billing for enterprise" -t decision \
  --notes "Rationale: cash flow. Rejected quarterly — billing overhead. Revisit if churn moves."
bd list -t decision --status all
```

This makes decisions **queryable** rather than buried in meeting prose. `/ask` and `/prep` both check it. `/process-meeting` creates them.

---

## Gotchas

Learned the hard way. `/process-meeting` and `AGENTS.md` repeat the critical ones.

**`bd create`, not `bd add`.**

**`bd update` does not accept `--deps`.** Use `bd dep add <blocked> <blocker>`. Do **not** recreate the issue — you'll orphan its history.

**Tasks can't depend on epics.** `--deps <epic-id>` warns and silently skips. Depend on the epic's relevant child task.

**`--notes` on create; `--append-notes` on update.** Plain `--notes` on update *overwrites*.

**`-l` / `--labels`, not `--tag`.** There is no `--tag` flag on create.

**`bd search` only searches titles, and excludes closed issues.**
```bash
bd search "pricing" --status all       # include closed — often where the answer is
bd search "pricing" --desc-contains    # descriptions
bd list --notes-contains "pricing"     # notes bodies
```
This one causes real misses. "What did we decide" is usually answered by a *closed* issue.

**`--parent <id>`** at create time for hierarchy. Children inherit parent labels.

**Use `--json`** when a command parses output. Table formatting will change; JSON won't.

---

## Git

`.beads/issues.jsonl` is the git-tracked export — plain text, diffable. The Dolt database is generated locally and gitignored.

```bash
bd export        # database → issues.jsonl
bd import        # issues.jsonl → database (after a git pull)
```

For a private or work vault:
```bash
bd init --stealth   # .git/info/exclude so beads artifacts never commit
```

---

## Troubleshooting

```bash
bd doctor      # check and fix installation health — start here
bd where       # which database is active
bd info        # database stats
bd prime       # what gets injected at session start
```

Fresh clone with no local database: `bd bootstrap`, or `bd init` then `bd import`.
