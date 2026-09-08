# /install — Unpack the Distribution

Turn the cloned repo into this user's brain.

The repo ships as a **distribution**: complete structure, example content, placeholder context. This is the one-time step that makes it theirs.

## Tone

Conversational, quick, and adaptive. Ten minutes, not an interview. Skip anything they clearly don't need, and don't over-explain the methodology — they can read `PARA Explained.md` later. The goal is a working vault today, not a fully understood one.

## Step 0: Check State

If `CLAUDE.md` has no 👉 placeholder blocks, this vault is already installed. Say so and offer `/brain-check` or a re-run of a specific step instead of overwriting their setup.

## Step 1: Understand Their Work

Ask, conversationally — two or three exchanges, not a form:

- What do you do, and where?
- What are you responsible for on an ongoing basis?
- What's active right now with an actual deadline?
- Who do you work with most?

That third question separates Areas from Projects, which is the distinction that determines whether PARA works for them. Don't lecture about it; just use their answers.

## Step 2: Write `CLAUDE.md`

Fill the four 👉 blocks from their answers:

**What this vault is for** — one or two sentences in their words.

**My Areas** — the highest-value part. Derive 4–8 from their ongoing responsibilities. Each gets a one-line scope.

Sanity-check the count out loud: fewer than three usually means Projects got miscategorized as Areas; more than ten means several are really Projects. Say it once, take their answer, move on.

**Tags** — adapt the topic line to their domain. Leave type and status tags alone.

**Current context** — role, focus, active projects. Note that it's worth refreshing every month or two.

**Remove the 👉 markers and the instructional blockquotes** as you fill each section. Leaving them makes the file read as unfinished.

## Step 3: Create Their Areas

For each Area, create `Areas/<Name>.md` from `Templates/Area Note.md`. Fill in the scope and "why I own it" from their answers. **Substitute the `{{date:...}}` values** — never write the literal string.

Empty Area notes are fine. They're targets for insight extraction, and having them exist is what lets routing work from day one.

## Step 4: Set Up Beads

```bash
command -v bd
```

**Not installed** — say it plainly, once:

> *"Beads isn't installed. The vault works without it — task tracking falls back to markdown and the memory layer is unavailable. `brew install beads` if you want it; re-run `/install` after and I'll wire it up."*

Then continue. Don't push.

**Installed** — set it up:

```bash
bd init --prefix <2-4 letters from their vault name>
bd import                  # unpacks the seeded issues and memories
bd setup claude            # wires up Claude Code integration
bd hooks install           # auto-injects `bd prime` at session start
```

Then **demonstrate the memory layer** — it's the least obvious part of the system and the most valuable, and describing it doesn't land:

```bash
bd remember "<a real fact from their Step 1 answers>" --key <key>
python3 .claude/scripts/memory_meta.py confirm <key>
```

> *"That's now in every future session in this folder — no note to open, no command to run. Add facts with `bd remember` whenever they come up. It's the habit that makes this feel like it knows you."*

**For a private or work vault**, mention `bd init --stealth` — it configures `.git/info/exclude` so beads artifacts never get committed.

## Step 5: Clear the Examples

Ask:

> *"Want me to clear the example content? Or keep it for one `/ask` run first — it's the fastest way to see what this does."*

**Keep** — note that `/install --clean` removes it later.

**Clear:**
- Delete seeded notes from `Meetings/`, `Days/`, `Areas/`, `People/`, `MOCs/`, `Projects/`
- Close or delete seeded beads (`bd list` to find them)
- `bd forget <key>` for each example memory (`bd memories` lists them)
- Reset `Knowledge Changelog.md`, `Todos.md`, `Dashboard.md` to empty state
- **Keep** all folder `README.md` files, `Templates/`, and the docs

## Step 6: First Real Note

Don't end on configuration. End with them using it:

> *"Let's put something real in. Anything from today — a meeting, a decision, something you learned?"*

Route it live with `/capture` or `/save-to-brain` so they see the flow once. A vault whose first real note gets written during setup is dramatically more likely to survive week one.

Then `/daily-note` to create today's.

## Step 7: Hand Off

```
✅ Installed

Areas: Pricing · Onboarding · Team · Vendor Management
Beads: 12 issues, 3 memories, hooks installed
Today: Days/20260728.md

Start with:
  /brief          each morning
  /capture        anything, anytime
  /ask <question> when you need something back

Everything else in README.md.
```

**Three commands, not thirteen.** They'll find the rest when they need them; a wall of options at the end of setup is where good systems get abandoned.

## Git

If they cloned from GitHub, `origin` still points at the template. Offer:

> *"Want me to point this at your own repo? Your notes shouldn't push to the template."*

**If the vault will hold work content, recommend a private remote — or none.** Say it once, clearly, and let them decide.

## Begin

Check whether the vault is already installed, then start with their work.
