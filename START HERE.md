---
tags: ["#guide"]
---

# Start Here

You cloned a distribution. This gets you to a working brain.

---

## 1. Install (10 minutes)

Open Claude Code in this folder and run:

```
/install
```

It asks about your work, fills in `CLAUDE.md`, creates your Areas, sets up beads, and offers to clear the example content.

**Optional but recommended first:** `brew install beads`. It powers the task and memory layers. The vault works without it, but the memory layer is the part people end up liking most.

---

## 2. Try It Before You Clear the Examples

The repo ships with a small worked example — a pricing decision that gets quietly undermined over five weeks. Before deleting it, run:

```
/ask what did we decide about annual pricing, and has anything contradicted it since?
```

```
/thread annual pricing
```

The second one is the pitch. It'll walk you through March to April and tell you that the decision was conditional, that the condition was never given a number, and that two independent signals accumulated against it without triggering a revisit.

No note-taking app can answer that. That's the system.

Then `/install --clean` to clear the examples.

---

## 3. The Daily Loop

**Morning** — `/brief`, then `/daily-note`
**Through the day** — `/capture` anything, no thinking required
**After meetings** — `/process-meeting`
**When you need something back** — `/ask`
**Friday** — `/weekly-review`

That's it. Everything else is situational.

---

## 4. The One Habit That Matters

When you learn a durable fact — who owns what, where the real data lives, an unwritten rule — say so, and Claude will offer to store it:

```bash
bd remember "Priya owns renewals, not Marcus" --key priya-renewals
```

That fact is now in **every future session** in this folder. No note to open. No command to run.

Most people underuse this because it feels too small to bother with. It isn't. Fifty of these is what makes the difference between a folder of notes and something that actually knows your world.

---

## 5. Where Things Go

> **Read it later → note. Do it → bead. Just know it → memory.**

| | |
|---|---|
| `Projects/` | Has a deadline |
| `Areas/` | Ongoing, no end date |
| `Resources/` | Reference |
| `Archive/` | Done |
| `Days/` `Meetings/` `People/` | Chronological and relational records |
| `MOCs/` | Topic navigation — Claude maintains these |
| `Inbox/` | Undecided, empty it weekly |

If you're unsure, `/capture` it to the Inbox and decide on Friday. Capture beats organize, every time.

---

## 6. New Role?

`/ramp` is built for the first 90 days — org map, who owns what, acronyms, the unwritten rules. It routes most of it to the memory layer, which is exactly where that knowledge belongs.

It's meant to fall out of use once you've ramped.

---

## If You Install Obsidian Later

Nothing to migrate. The vault is ordinary markdown with PARA + MOC structure, YAML frontmatter, and `[[wikilinks]]` throughout. Open the folder as a vault and graph view, backlinks, and search light up on top of what's already there.

`Dashboard.md` ships with commented-out Dataview queries — uncomment them and it stops needing regeneration.

---

## Docs

- [`README.md`](README.md) — what this is and why
- [`Beads Guide.md`](Beads%20Guide.md) — task and memory layer, with gotchas
- [`CLAUDE.md`](CLAUDE.md) — how Claude behaves here; customize it
- [`PLAN.md`](PLAN.md) — design rationale and build phases
