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

**Your notes survive the tool.** Full PARA + MOC structure, YAML frontmatter, `[[wikilinks]]`, plain markdown throughout. Install Obsidian tomorrow and the vault lights up with graph view and backlinks, no migration. Lose every tool and you still have a folder of readable files.

That isn't a design principle anyone arrived at by reasoning. **Obsidian was removed from the machine this was built on — by policy, with no notice — and the notes survived because they were just files.** The retrieval layer exists because clicking toward things stopped being available and asking was what remained. Markdown is the source of truth and everything else is an accelerator that could vanish tomorrow without costing you any knowledge. That's a constraint the system was actually tested against, not one it aspires to.

The second half follows from the first. Conventional PKM optimizes for **navigation** — links, graphs, backlink panes; you find things by clicking toward them. This optimizes for **retrieval and synthesis**: you find things by asking, and the reader is a model that can read fifty notes, rank them, notice two of them disagree, and tell you so.

Retrieval-by-asking is not the differentiator — Obsidian with an LLM plugin does that, so do Notion AI and Mem, and it'll be table stakes shortly. The differentiator is that **the files stay ordinary and the tooling is disposable.**

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

## Start Here

Three commands. Everything else can wait until you want it.

| | |
|---|---|
| `/capture` | Get a thought out of your head. Works from any directory. |
| `/ask <question>` | Get it back, with citations. |
| `/daily-note` | Open today. Carries yesterday forward, drains the inbox. |

The full set is sixteen commands, listed below. A new vault does not need them.

---

## Install

```bash
git clone https://github.com/dontoisme/claude-as-brain.git my-brain
cd my-brain
git remote remove origin        # your notes are yours — don't push them to the template
claude
```

**Don't skip the third line.** Clone, fill the vault with work notes, run `git push` on autopilot six weeks later, and you've published them to a public template repo.

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

Works in a fresh directory or an existing one. If you're setting this up for work notes, tell Claude — it'll recommend a private remote or none at all, and flag the vault so personal captures get a warning before they land there.

`/install` also writes `~/.config/claude-brain/config.toml` and prints the `CLAUDE_BRAIN` export line for your shell rc. That's what makes `/capture` and `/ask` work from any directory instead of only inside the vault.

### Optional: beads

[Beads](https://github.com/steveyegge/beads) powers the task and memory layers. Strongly recommended, not required.

```bash
brew install beads
```

Without it, notes work identically. What you actually lose:

- **`bd ready`** — what's genuinely claimable right now, blocker-aware. A markdown table cannot answer this.
- **`bd stale`** — what you've quietly abandoned. Same.
- **The memory layer, entirely.** No durable facts auto-injected into sessions. This is the part people say they'd miss most.

`Todos.md` becomes hand-maintained. That's a real downgrade rather than a cosmetic one, and it's stated here rather than discovered later.

It stays optional anyway, deliberately. The machines where this system matters most are often the machines where installing a second binary isn't your call — which is the same constraint that produced this repo. Requiring `bd` would reintroduce it. Commands say what's missing once and then get on with it.

---

## Once It's Part of Your Day

The rest of the set. Nothing here is needed on day one.

### Retrieval — the reason this exists
Runs from **any directory**, not just inside the vault. Global capture without global retrieval is a half-loop: writing gets cheaper, reading doesn't, and the ratio gets worse.

| | |
|---|---|
| `/ask <question>` | Search, read, and answer across the vault, with citations |
| `/thread <topic>` | Trace how your thinking on something evolved over time |
| `/prep <meeting\|person\|topic>` | Everything relevant before a conversation, including what you owe them |
| `/brief` | Morning state-of-the-world, plus one line of vault health |

### Capture
| | |
|---|---|
| `/capture` | Thought → Inbox, or straight to a task. Zero friction, works anywhere. |
| `/save-to-brain` | Session insight → routed note, changelog, daily note |
| `/process-meeting` | Raw notes → structured note + commitments as beads |
| `/daily-note` | Today's note — carryover, ready work, and a silent inbox drain |
| `/process-inbox` | The drain. Auto-files by confidence; flags what it can't place. |

### Maintenance
Not equally required, and the README used to imply they were. Skipping something labeled required feels like breaking the system; skipping something labeled optional doesn't.

| | | |
|---|---|---|
| `/weekly-review` | The Friday synthesis | **Required.** Skip it and the vault accumulates instead of compounding. |
| `/audit-routing` | Re-check what got auto-filed | **Weekly at first**, monthly once calibrated |
| `/sync-todos` | Render beads into `Todos.md` | Automatic — never run by hand |
| `/update-mocs` | Keep Maps of Content current | Automatic, via weekly review |
| `/rebuild-dashboard` | Regenerate `Dashboard.md` | Monthly is plenty |
| `/brain-check` | Is this system still being used? | Monthly, or when something feels off |
| `/self-check` | Is retrieval still working? | Monthly, or after big vault growth |
| `/link-check` | Broken links and orphans | **Quarterly.** A nicety — link rot is slow. |
| `/ramp` | New-role capture: org, people, acronyms | First 90 days only |

### Setup
| | |
|---|---|
| `/install` | Unpack the distribution into your own vault |

---

## The Inbox Has a Drain

Zero-friction capture without a drain is how every previous system in this lineage actually died. Within a month the vault has two tiers — the notes filed properly and the pile that wasn't.

`/process-inbox` **auto-files by default.** Not propose-and-approve: that pattern comes from navigation-first PKM, where the folder *is* the retrieval path and a misfile genuinely loses the note. Here `/ask` finds a note wherever it sits, so a wrong guess costs a slightly worse folder tree. Approval gates buy little and cost the thing that decides whether any of this survives — the chance the drain actually runs.

- **Routed by confidence, not category.** Confident items file silently. The rest go to `Inbox/unclear/` — still captured, still readable by `/ask`, just flagged, under a 14-day SLA that `/brief` enforces.
- **Every routing decision is stamped** in frontmatter — `routed_by`, `confidence`, and a one-line rationale. Auditable and greppable, which is what makes silent filing safe.
- **Git is the undo.** The drain commits what it filed; a bad batch is one `git revert`.
- **Beads are the exception.** A misfiled note is clutter; a wrongly-created commitment is false guilt and a missed one is a real obligation that never became trackable. Those get proposed, never created silently.

`/daily-note` runs a light pass automatically, so the drain rides on a habit that already exists rather than needing one of its own.

---

## Two Vaults, and What Goes In Each

A brain accumulates the highest-regret content you own: candid assessments of named colleagues, compensation figures, health details, job-search activity, an API key pasted into a meeting note at speed. Where it's hosted decides who else reads all of that.

**`People/` is the most sensitive directory in the vault.** Honest observations about named coworkers, written for an audience of one, are exactly what nobody wants surfaced.

### If the remote is an employer-owned org

Committing a work vault to a private repo in a company GitHub org is a reasonable setup, and it's also the configuration where the boundary matters most. Two consequences, neither obvious:

- **Org admins can read it, and it's discoverable.** A private repo in a company org is company infrastructure — within reach of org owners, security tooling, and, if it comes to that, legal hold and eDiscovery. A vault built for zero-friction capture will attract personal content unless the boundary is explicit.
- **You lose it at offboarding.** Access ends when employment does. A brain holding several years of your own thinking is a bad thing to host on infrastructure you don't control.

**So: two vaults, hard-separated.** `~/brain` on a personal remote, `~/work-brain` on the employer org. Commands route by explicit target — `--vault`, then `$CLAUDE_BRAIN`, then `~/.config/claude-brain/config.toml`, then `~/brain` — never by whatever directory you happen to be in.

`/capture` warns once when something that looks personal is about to land in a vault flagged as employer-owned. It's a keyword heuristic, it will miss things, and it says so. It isn't a compliance control — it's there for the realistic failure, which isn't deciding to put something in the wrong place. It's a fast capture that never got a decision at all.

A `Private/` directory at the vault root is gitignored by default, for anything that shouldn't reach the remote at all.

---

## Multi-Device

Markdown in a folder, so use whatever you already use.

- **Git with a private remote** is the recommended answer. Notes are text; conflicts are readable and rare, since you're rarely editing the same note on two machines at once.
- **Any file sync** (iCloud, Dropbox, Syncthing) works fine for the markdown.
- **Beads** stores state in a local Dolt database, with `.beads/issues.jsonl` as its git-tracked export. Sync the JSONL through git and `bd import` on the other machine. Don't file-sync the `.db` — that's a binary two machines can corrupt between them.
- **Mobile** is read-mostly: any plain-markdown app. If Obsidian is available on your phone, this vault opens in it unmodified — that's the point of keeping the structure conventional.

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

It costs more tokens and buys better answers on large vaults, where reading eight notes in a single context starts crowding out the reasoning that comes after.

**Concrete trigger, since nobody switches on a vibe:** under **200 notes**, `inline` is genuinely better — spawn latency exceeds the benefit. Past **500 notes**, `parallel` starts to win. In between it depends on note length; total vault word count above ~150k is the better signal. `/brief` counts and tells you once when you cross it, because otherwise nobody is counting.

Then don't take anyone's word for it: **`/self-check` runs the same known-answer questions in both modes** and reports citation recall, fabrication count, and rough token cost side by side. That's the only way to compare them empirically rather than by feel, and a mode switch made on feel is a permanent unexamined cost.

Model tiering is where the cost lands: scouts run on Haiku (mechanical search and ranking), readers on Sonnet (extraction with judgment). Adjust in `.claude/agents/`.

**The rule that makes it safe:** subagents return verbatim quotes with file paths and never conclusions. Synthesis stays in the main thread. A memory system that summarizes a summary will eventually tell you something you never wrote — and you'll believe it, because that's the entire point of keeping one.

---

## The Citation Invariant

That rule is not a property of parallel mode. It's a property of the system, and it's written into `CLAUDE.md` as a top-level invariant:

> **Every claim about what the vault contains carries a file path. A claim that can't carry one is labeled as inference, out loud.**

Three states, always exactly one of them: **recorded** (here's the file), **inferred** (that's my read, not something you wrote), or **absent** (nothing in the vault mentions this). There is no fourth state, in either retrieval mode.

This is the selling point, not the fine print. A memory system that occasionally invents a decision you never made is worse than no memory system at all — you stopped holding the information yourself, which was the entire deal. `/self-check` treats a single fabrication across eight questions as a failed run regardless of the other seven, because there is no acceptable rate.

---

## Structure

```
├── Projects/     Areas/     Resources/     Archive/    ← PARA
├── MOCs/         Days/      Meetings/      People/
├── Inbox/        Inbox/unclear/    Templates/
├── Private/      (gitignored)
│
├── Dashboard.md            (generated)
├── Todos.md                (generated from beads)
├── INDEX.md                Knowledge Changelog.md
│
├── CLAUDE.md               ← the heart; customize this
├── AGENTS.md               .beads/issues.jsonl
├── Templates/eval/         known-answer questions for /self-check
├── .claude/commands/       Slash commands
└── .claude/agents/         vault-scout, note-reader (parallel mode)
```

**Four things look like they answer "what's my state right now." They don't overlap:**

| | |
|---|---|
| `/brief` | Read-only orientation. Thirty seconds, writes nothing. |
| `/daily-note` | Where you **write** today. The only one you edit by hand. |
| `Dashboard.md` | Generated project and area overview. Never hand-edited. |
| `Todos.md` | Generated mirror of beads. Never hand-edited. |

Open `/daily-note` in the morning. Everything else is generated or read-only.

Identical to a conventional Obsidian vault. That's deliberate — approval day should be a no-op, not a migration.

What changes is *who maintains* each artifact. MOCs are Claude-maintained instead of hand-curated. `Dashboard.md` is regenerated by reading files instead of running Dataview queries. `Todos.md` is a rendered mirror of the beads graph. Same files, same format, no staleness tax.

---

## Status

Early. See [`PLAN.md`](PLAN.md) for the full design and build phases.

## License

MIT
