# /install — Unpack the Distribution

Turn the cloned repo into this user's brain.

The repo ships as a **distribution**: complete structure, example content, placeholder context. This is the one-time step that makes it theirs.

## Tone

Conversational, quick, and adaptive. Ten minutes, not an interview. Skip anything they clearly don't need, and don't over-explain the methodology — they can read `PARA Explained.md` later. The goal is a working vault today, not a fully understood one.

## Step 0: Check State

If `CLAUDE.md` has no 👉 placeholder blocks, this vault is already installed. Say so and offer `/brain-check` or a re-run of a specific step instead of overwriting their setup.

## Step 1: Where Does This Live, and Whose Is It?

Two questions, asked before anything else, because both are painful to retrofit once notes exist.

**Path.** Offer a default rather than asking an open question — *"where's your vault?"* has no good one-keystroke answer, and `~/brain` accepted in one keystroke is worth more than a perfect path chosen after thinking about it:

> *"I'll set this up at `~/brain` unless you'd rather it lived elsewhere. On a work machine I'd suggest `~/work-brain`, so a personal vault can sit alongside it later."*

**Ownership.** Ask directly, once:

> *"Will this vault's git remote be an employer-owned org, a personal private repo, or no remote at all?"*

If employer-owned, say the two consequences plainly — they aren't obvious and both bite late:

> *"Two things worth knowing. A private repo in a company org is company infrastructure: org owners, security tooling, and legal hold can reach it. And access ends at offboarding, so anything you'd want to keep is on infrastructure you don't control. Most people end up with two vaults — `~/brain` personal, `~/work-brain` for work. I'll flag this one so captures that look personal get a warning."*

Don't lecture past that. State it, record the answer, move on.

### Write the resolution config

Global commands need an absolute path — `cwd` stops being an answer the moment `/capture` runs from somewhere else. **Multi-vault is not a someday concern**; anyone running this on a work machine has two within a year, and retrofitting resolution after notes exist is worse than designing for it now.

```bash
mkdir -p ~/.config/claude-brain
```

```toml
# ~/.config/claude-brain/config.toml
default = "personal"

[vaults.personal]
path = "~/brain"
employer_owned = false
```

Then print the export line for their shell rc, and say which file to put it in:

```bash
export CLAUDE_BRAIN="$HOME/brain"
```

**Check bead project pinning once, here.** Beads resolves its project from the working directory, so an unpinned `bd` call from a work repo lands in that repo's store, silently.

```bash
command -v bd && bd --help | grep -i "project" || true
```

If this `bd` build supports a project flag, record that in `CLAUDE.md` under *Where the Vault Lives* and prefer it. Otherwise the portable form — `(cd "$CLAUDE_BRAIN" && bd ...)` — is already what every command uses.

## Step 2: Understand Their Work

Ask, conversationally — two or three exchanges, not a form:

- What do you do, and where?
- What are you responsible for on an ongoing basis?
- What's active right now with an actual deadline?
- Who do you work with most?

That third question separates Areas from Projects, which is the distinction that determines whether PARA works for them. Don't lecture about it; just use their answers.

## Step 3: Write `CLAUDE.md`

Fill the four 👉 blocks from their answers:

**What this vault is for** — one or two sentences in their words.

**My Areas** — the highest-value part. Derive 4–8 from their ongoing responsibilities. Each gets a one-line scope.

Sanity-check the count out loud: fewer than three usually means Projects got miscategorized as Areas; more than ten means several are really Projects. Say it once, take their answer, move on.

**Tags** — adapt the topic line to their domain. Leave type and status tags alone.

**Current context** — role, focus, active projects. Note that it's worth refreshing every month or two.

**Remove the 👉 markers and the instructional blockquotes** as you fill each section. Leaving them makes the file read as unfinished.

## Step 4: Create Their Areas

For each Area, create `Areas/<Name>.md` from `Templates/Area Note.md`. Fill in the scope and "why I own it" from their answers. **Substitute the `{{date:...}}` values** — never write the literal string.

Empty Area notes are fine. They're targets for insight extraction, and having them exist is what lets routing work from day one.

## Step 5: Set Up Beads

```bash
command -v bd
```

**Not installed** — say it plainly, once, and be specific about what's lost. The vault works without beads, but "the memory layer is unavailable" understates a real downgrade, and users who discover the gap later feel misled:

> *"Beads isn't installed. Notes work identically. What you lose: `bd ready` (what's genuinely claimable, blocker-aware) and `bd stale` (what you've quietly abandoned) — a markdown table can't answer either — and the memory layer entirely, which is the part people say they'd miss most. `Todos.md` becomes hand-maintained. `brew install beads` if you can; re-run `/install` after and I'll wire it up."*

Then continue, genuinely. **Don't push, and don't make it a hard requirement.** The machines where this system matters most are often the machines where installing a second binary isn't yours to decide — that constraint is why this repo exists at all.

**Installed** — set it up:

```bash
cd "$CLAUDE_BRAIN"
bd init --prefix <2-4 letters from their vault name>
bd import                  # unpacks the seeded issues and memories
bd setup claude            # wires up Claude Code integration
bd hooks install           # auto-injects `bd prime` at session start
```

**Initialize from inside the vault, always.** `bd init` in the wrong directory creates a store the brain will never find, and nothing announces it.

Then **demonstrate the memory layer** — it's the least obvious part of the system and the most valuable, and describing it doesn't land:

```bash
bd remember "<a real fact from their Step 2 answers>" --key <key>
```

> *"That's now in every future session in this folder — no note to open, no command to run. Add facts with `bd remember` whenever they come up. It's the habit that makes this feel like it knows you."*

**For a private or work vault**, mention `bd init --stealth` — it configures `.git/info/exclude` so beads artifacts never get committed.

## Step 6: Clear the Examples

Ask:

> *"Want me to clear the example content? Or keep it for one `/ask` run first — it's the fastest way to see what this does."*

**Before clearing, offer one `/self-check` run.** The seed doubles as a retrieval baseline, and it's the only chance to get one on known-answer questions:

> *"One thing worth doing first: `/self-check` runs eight questions with known answers against the seed and scores the citations. Takes a few minutes and gives you a number to compare against later, when the vault is yours and full. After that the questions are dead weight — you'd replace them with your own."*

**Keep** — note that `/install --clean` removes it later.

**Clear:**
- Delete seeded notes from `Meetings/`, `Days/`, `Areas/`, `People/`, `MOCs/`, `Projects/`
- Close or delete seeded beads (`bd list` to find them)
- `bd forget <key>` for each example memory (`bd memories` lists them)
- Reset `Knowledge Changelog.md`, `Todos.md`, `Dashboard.md` to empty state
- Empty `Inbox/Quick Captures.md` and `Inbox/unclear/`
- Delete **Part A** of `Templates/eval/questions.md` — it's keyed to the seed. Leave Part B and its template.
- **Keep** all folder `README.md` files, `Templates/`, and the docs

## Step 7: First Real Note

Don't end on configuration. End with them using it:

> *"Let's put something real in. Anything from today — a meeting, a decision, something you learned?"*

Route it live with `/capture` or `/save-to-brain` so they see the flow once. A vault whose first real note gets written during setup is dramatically more likely to survive week one.

Then `/daily-note` to create today's.

## Step 8: Hand Off

```
✅ Installed

Vault:  ~/brain  (CLAUDE_BRAIN exported — add the line to your shell rc)
Areas:  Pricing · Onboarding · Team · Vendor Management
Beads:  12 issues, 3 memories, hooks installed
Today:  Days/20260728.md

Start with:
  /capture        anything, anytime — works from any directory
  /ask <question> when you need something back
  /daily-note     each morning

Everything else in README.md.
```

**Three commands, not sixteen.** They'll find the rest when they need them; a wall of options at the end of setup is where good systems get abandoned. These three are the write-read-habit loop and nothing else is load-bearing in week one.

## Git

**If they cloned from GitHub, `origin` still points at the template. Remove it now, before asking anything:**

```bash
git remote -v
git remote remove origin
```

Don't offer, don't ask, don't wait. A user who fills this vault with work notes and later runs `git push` on autopilot is one muscle-memory command away from publishing them to a public template repo. Removing the remote is free and reversible; leaving it is not.

Say what you did in one line, then offer the replacement:

> *"Removed `origin` — it pointed at the template. Want to point this at your own repo?"*

**If the vault will hold work content, recommend a private remote or none at all.** If they said employer-owned in Step 1, remind them once here that `Private/` is gitignored and exists for whatever shouldn't reach that remote.

`bd init --stealth` is worth mentioning for a private work clone — it configures `.git/info/exclude` so beads artifacts never get committed and the tracked repo stays pure markdown.

## Begin

Check whether the vault is already installed, then start with their work.
