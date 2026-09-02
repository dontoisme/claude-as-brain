# Claude-as-Brain

A personal knowledge system where **Claude Code is the retrieval layer**.

No app to install. No plugins. No proprietary format. A folder of markdown files, an optional task database, and a set of commands that make Claude genuinely good at operating them.

```
> /ask what did we decide about annual pricing, and has anything contradicted it since?

Three notes touch this.

You landed on annual-only for enterprise in the Mar 12 pricing review
(Meetings/20250312 - Pricing Review.md) — rationale was cash flow
predictability, and Dana pushed for it.

Two things have since cut against it:

- Apr 2 customer call: two mid-market accounts asked for quarterly and
  one said annual was "the reason we almost didn't sign"
  (Meetings/20250402 - Riverside Renewal.md)
- Your own note on Apr 18 flags that the finance rationale assumed a
  cash position that has since changed (Areas/Pricing.md)

Nothing has formally reopened the decision. There's an open bead —
cab-31, "revisit annual-only for mid-market" — created Apr 18, still
unblocked and untouched since.
```

That question has no answer in a conventional note-taking app. Not in search, not in graph view, not in a Dataview query. That is the point of this system.

---

## What Makes It Different

Conventional PKM optimizes for **navigation** — links, graphs, backlink panes. You find things by clicking toward them.

This optimizes for **retrieval and synthesis**. You find things by asking. The reader is a model that can read fifty notes, rank them, notice two of them disagree, and tell you so.

**But the files stay ordinary.** Full PARA + MOC structure, YAML frontmatter, `[[wikilinks]]`, plain markdown throughout. If you install Obsidian tomorrow the vault lights up with graph view and backlinks and nothing needs migrating. If you lose every tool, you still have a folder of readable notes.

That's a hard constraint, not an aspiration: **markdown is the source of truth, and everything else is an accelerator that could vanish without costing you knowledge.**

---

## Three Memory Layers

Most systems have one layer and bolt tasks onto the side. This has three, with a clear rule for what goes where.

| Layer | What it holds | How it comes back |
|---|---|---|
| **Notes** | Prose, reasoning, meeting records, decisions | Claude reads and synthesizes |
| **Beads issues** | Commitments — owner, state, dependencies | `bd ready`, `bd stale`, `bd graph` |
| **Beads memories** | Durable one-line facts | **Auto-injected into every session** |

> **Want to read it later → note. Need to do it → bead. Should Claude just know it → memory.**

The third layer is the one people don't expect. `bd remember "Dana owns the billing roadmap"` costs one command mid-conversation, and that fact is present in every future session in this folder — no note to open, no command to run. Near-zero capture cost is exactly why it gets used.

---

## Install

```bash
git clone https://github.com/dontoisme/claude-as-brain.git my-brain
cd my-brain
claude
```

Then run:

```
/install
```

The repo ships as a **distribution**, not a working vault. `/install` unpacks it into yours: asks about your work, fills in `CLAUDE.md`, creates your real Areas, sets up beads, and offers to clear the example content.

### Or just paste this prompt

If you'd rather not clone first — or you want Claude to set the whole thing up from scratch in a folder of your choosing — paste this into Claude Code:

```
I want to set up a Claude-as-Brain: a personal knowledge system where you are
the retrieval layer, stored as plain markdown so it stays portable.

Please:

1. Clone https://github.com/dontoisme/claude-as-brain.git into a folder I'll
   name, then remove the git remote so my notes never push to the template.

2. Check whether `bd` (beads) is installed. If not, tell me `brew install beads`
   and that it's optional — it powers task tracking and a memory layer that
   loads into every session. Continue either way.

3. Ask me about my work — what I'm responsible for ongoing, what's active with
   a deadline, who I work with most. Keep it conversational, a few exchanges,
   not a form.

4. From my answers, fill in the customizable sections of CLAUDE.md: what the
   vault is for, my Areas (4-8, each with a one-line scope), my tag vocabulary,
   and my current context. Remove the placeholder markers as you go.

5. Create an Area note for each Area from Templates/Area Note.md. Substitute
   the {{date:...}} values — never write that syntax literally into a note.

6. If beads is installed: bd init, bd import to unpack the seed, bd setup claude,
   bd hooks install. Then store one real fact from my answers with `bd remember`
   and show me that it'll be in every future session. That's the part people
   miss.

7. Before clearing the examples, run `/thread annual pricing` so I can see what
   this system does that a notes app can't. Then clear the example content.

8. Capture one real thing from my actual day, so the vault starts with
   something true in it.

9. Finish by telling me just three commands to start with, not thirteen.

Ask me my folder name and what I do, and let's go.
```

Works in a fresh directory or an existing one. If you're setting this up for work notes, tell Claude — it'll recommend a private remote or none at all.

### Optional: beads

[Beads](https://github.com/steveyegge/beads) powers the task and memory layers. Strongly recommended, not required.

```bash
brew install beads
```

Without it, the vault still works — task tracking falls back to hand-maintained markdown and the memory layer is unavailable. Commands say so once and then get on with it.

---

## Commands

### Retrieval — the reason this exists
| | |
|---|---|
| `/ask <question>` | Search, read, and answer across the vault, with citations |
| `/thread <topic>` | Trace how your thinking on something evolved over time |
| `/prep <meeting\|person\|topic>` | Everything relevant before a conversation, including what you owe them |
| `/brief` | Morning state-of-the-world |

### Capture
| | |
|---|---|
| `/capture` | Thought → Inbox, or straight to a task. Zero friction. |
| `/save-to-brain` | Session insight → routed note, changelog, daily note |
| `/process-meeting` | Raw notes → structured note + commitments as beads |
| `/daily-note` | Today's note, seeded with ready work and yesterday's carryover |

### Maintenance
| | |
|---|---|
| `/rebuild-dashboard` | Regenerate `Dashboard.md` from actual files |
| `/sync-todos` | Render beads state into readable `Todos.md` |
| `/update-mocs` | Keep Maps of Content current |
| `/link-check` | Find broken links and orphaned notes |
| `/weekly-review` | The Friday synthesis — distills event notes, proposes promotions, files contradictions |
| `/reindex` | Rebuild the deletable retrieval index behind `/ask` (recency, usage, optional embeddings) |
| `/verify` | Refetch the URLs a note's claims rest on and flag what no longer holds |

### Interop
| | |
|---|---|
| `/export-memoryfield` | Package `Resources/` and `Areas/` as an open-format `.memoryfield.zip` |
| `/import-memoryfield` | Bring one in, quarantined as `(imported, unverified)` until you've read it |
| `/ramp` | New-role capture: org, people, acronyms, systems |

### Setup
| | |
|---|---|
| `/install` | Unpack the distribution into your own vault |

---

## Try It Before You Clear the Examples

The repo ships with a worked example: a pricing decision that gets quietly undermined over five weeks. Five notes, five beads, three memories — all tagged `example-seed` and removed in one step.

Before deleting it, run:

```
/thread annual pricing
```

It'll walk you from March to April and tell you the decision was explicitly conditional, that the condition was never given a number, and that two independent signals accumulated against it without ever triggering the revisit.

That's the pitch. Search can't do it, graph view can't do it, and neither can you at 8am before a planning meeting.

---

## Scaling Up

Set `retrieval_mode: parallel` in `CLAUDE.md` and `/ask`, `/thread`, and `/prep` fan out to subagents instead of searching in one thread — scouts sweep each search angle concurrently, readers process candidate notes in batches, and the main thread synthesizes.

It costs more tokens and buys better answers on large vaults, where reading eight notes in a single context starts crowding out the reasoning that comes after. Under a few hundred notes the default `inline` mode is genuinely better; spawn latency exceeds the benefit.

Model tiering is where the cost lands: scouts run on Haiku (mechanical search and ranking), readers on Sonnet (extraction with judgment). Adjust in `.claude/agents/`.

**The rule that makes it safe:** subagents return verbatim quotes with file paths and never conclusions. Synthesis stays in the main thread. A memory system that summarizes a summary will eventually tell you something you never wrote — and you'll believe it, because that's the entire point of keeping one.

---

## Structure

```
├── Projects/     Areas/     Resources/     Archive/    ← PARA
├── MOCs/         Days/      Meetings/      People/
├── Inbox/        Templates/
│
├── Dashboard.md            (generated)
├── Todos.md                (generated from beads)
├── INDEX.md                Knowledge Changelog.md
│
├── CLAUDE.md               ← the heart; customize this
├── AGENTS.md               .beads/issues.jsonl
├── .claude/commands/       Slash commands
└── .claude/agents/         vault-scout, note-reader (parallel mode)
```

Identical to a conventional Obsidian vault. That's deliberate — approval day should be a no-op, not a migration.

What changes is *who maintains* each artifact. MOCs are Claude-maintained instead of hand-curated. `Dashboard.md` is regenerated by reading files instead of running Dataview queries. `Todos.md` is a rendered mirror of the beads graph. Same files, same format, no staleness tax.

---

## Status

Early. See [`PLAN.md`](PLAN.md) for the full design and build phases.

## License

MIT
