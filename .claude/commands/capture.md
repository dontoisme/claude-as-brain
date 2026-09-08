# /capture — Fast Inbox Drop

Get a thought out of the user's head and into the vault. Nothing else.

## Step 0: Resolve the Vault, Silently

This command runs from anywhere on the machine, so `cwd` doesn't tell you which vault to write to. Resolve per *Where the Vault Lives* in `CLAUDE.md`: `--vault` → `$CLAUDE_BRAIN` → `~/.config/claude-brain/config.toml` → `~/brain`.

Costs no user time. **If the resolved vault isn't the one you're standing in, say which one you wrote to in the confirmation line** — that's the difference between a misroute caught today and a misroute found in a month.

## Speed Is the Whole Point

**No routing questions. No follow-ups. No template.** The user is mid-thought and will not tolerate a conversation.

If you find yourself about to ask "which Area should this go in?" — you've broken the command. That decision belongs to weekly review. Capture beats organize, every time, because the alternative to a messy Inbox isn't a tidy vault; it's a lost thought.

## Step 1: Triage in One Beat

Look at what they said and pick one destination. Don't ask — decide.

**It's a task** (has a verb and an implied owner: "follow up with Dana", "send the deck"):
```bash
(cd "$CLAUDE_BRAIN" && bd q "<the thing>")     # quick capture, returns just an ID
```

**It's a durable fact** (a stable truth about how the world works: "Dana owns billing", "fiscal year starts in April"):
```bash
(cd "$CLAUDE_BRAIN" && bd remember "<the fact>" --key <short-key>)
```

**It's anything else** — an idea, an observation, a half-formed thought → append to `Inbox/Quick Captures.md`.

**Genuinely unsure?** Inbox. Always. Inbox is the safe default and the entire reason it exists.

## Step 1b: The Boundary Guard

**Only when the resolved vault is marked `employer_owned = true`** and the content trips a sensitivity heuristic — job search, compensation, health, legal exposure, personal relationships, family.

Then, once:

> *"This looks personal and this vault is on your employer's org — admins can read it and you lose it at offboarding. Send it to `~/brain` instead? (This is a keyword guess, not a real check.)"*

Say the limitation out loud. A heuristic misses things, and this is not a compliance control. It exists for the realistic failure — not a decision to put something in the wrong place, but a fast capture that never got a decision at all.

**One line, default to their answer, never a second prompt.** If they don't respond, capture where they asked. A guard that costs the user a conversation is a guard that gets ignored, and then it's worse than nothing.

Also relevant in reverse: a capture made from inside a client or employer repo (`git_repo`, below) is the strongest hint it belongs in the *work* vault. Route accordingly, mention nothing.

## Step 2: Write It

For the Inbox, append under the capture marker, matching the file's existing style:

```markdown
- **HH:MM** — [content]
```

Preserve their words. Don't clean up phrasing, expand shorthand, or make it a proper sentence — the raw phrasing carries context that a tidied version loses.

If the file doesn't exist, create it with a `## Quick Captures` heading.

### Stamp provenance when captured from outside the vault

Context is free at write time and unrecoverable later. Two seconds of `git` gets you a retrieval dimension you otherwise have no access to:

```bash
pwd
git rev-parse --show-toplevel 2>/dev/null && git branch --show-current 2>/dev/null
hostname -s
```

Line captures get a compact suffix; a standalone note gets it in frontmatter:

```markdown
- **14:22** — the eligibility sync drops records when the file has a BOM
  <!-- from: ~/dev/health-platform · acme/health-platform@fix/eligibility-sync · work-mbp -->
```

```yaml
captured_at: 2026-09-08T14:22:11-05:00
captured_from: ~/dev/health-platform
git_repo: acme/health-platform
git_branch: fix/eligibility-sync
host: work-mbp
```

A note that knows it was written mid-debugging on a specific branch is substantially richer than the same prose floating free. Repo and branch names often reconstruct what a rushed capture didn't have time to say.

**Two limits, both firm.** Record the *location* — never file contents, never diffs, never the code you were looking at. Otherwise the vault quietly accumulates employer source. And the path is itself information: writing `captured_from: ~/dev/acme-eligibility-rewrite` into a personal vault leaks a client name. Stamping from a work directory into a personal vault, record `git_repo: <work>` unless the user has said otherwise.

Captured from inside the vault? No stamp. There's nothing to reconstruct.

**Always pin `bd` to the brain's store.** Run from a work repo without pinning and the bead lands in *that* project's database, silently, surfacing in no future brain session. It's the most expensive silent failure in the system, and the subshell above costs nothing.

## Step 3: Confirm in One Line

```
✅ Inbox (7 items)
```
```
✅ cab-42 — follow up with Dana on billing scope
```
```
✅ Remembered: dana-billing
```

Captured from outside the resolved vault, name it:

```
✅ Inbox (7 items) → ~/work-brain
```

That's the entire response. No summary, no "let me know if you'd like me to...", no offer to elaborate.

Only exception: if the Inbox passes 10 items, add one line — *"Inbox is at 12 — `/process-inbox` will drain it."* Once. Not every time. Point at the drain, not at weekly review; the drain is the cheap answer and `/daily-note` runs it anyway.

## If `bd` Isn't Installed

Everything goes to the Inbox, including tasks. Note it once per session at most.

## Judgment

**Multiple things in one capture?** Split them. Three thoughts get three entries — a blob is unprocessable later.

**Obviously belongs somewhere specific?** Capture it to Inbox anyway. Don't ask, don't offer, don't mention it — `/process-inbox` files by confidence and an obvious home is exactly what it routes best. Never turn a ten-second action into a decision.

**Sounds urgent?** Make it a bead with a priority rather than an Inbox line. `bd q` then `bd priority <id> 1`.

## Examples

> "users over 70 struggle with the multi-step wizard"
→ Inbox. It's an observation, not a task.

> "ask Chris about scope before Tuesday"
→ `bd q`. Verb, owner, deadline.

> "Priya is the actual decision maker on renewals, not Marcus"
→ `bd remember`. Durable fact, will matter in every future session.

> "what if checklist completion had streak tracking"
→ Inbox. Idea.

## Related

- `/process-inbox` — the drain. Files what this drops, automatically.
- `/save-to-brain` — the deliberate version, for something worked out in session

## Begin

Capture it. Fast.
