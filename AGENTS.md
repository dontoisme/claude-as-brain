# Agent Instructions

This vault is operated primarily through Claude Code. Full context lives in `CLAUDE.md` — read that first.

## Issue Tracking

This vault uses **bd (beads)** for task tracking and persistent memory.

Run `bd prime` for workflow context, or install hooks (`bd hooks install`) for auto-injection.

**Quick reference:**
- `bd ready` — find unblocked work
- `bd create "Title" --type task --priority 2` — create issue
- `bd close <id>` — complete work
- `bd remember "<fact>" --key <key>` — store a durable fact, auto-injected next session
- `bd dolt push` — push beads to remote

For full workflow details: `bd prime`

## Beads Is Optional

If `bd` is not installed, this vault still works — notes are unaffected. What's actually lost: `bd ready` (blocker-aware claimable work) and `bd stale` (quiet abandonment), neither of which a markdown table can answer, plus the memory layer entirely. `Todos.md` becomes hand-maintained.

That's a real downgrade, not a cosmetic one. State it once, precisely, then proceed without nagging.

Install: `brew install beads`

## Pin Every Call

Beads resolves its active project from the working directory. A `bd` call made
from inside some other project's directory lands in **that** project's store,
silently, and surfaces in no future brain session — the user finds out weeks
later when a memory they're sure they stored isn't there.

Always pin to the brain's store:

```bash
(cd "$CLAUDE_BRAIN" && bd remember "..." --key ...)
(cd "$CLAUDE_BRAIN" && bd ready)
```

The reverse holds too: a brain command must never read or mutate the bead store
of whatever directory it happened to be launched from. `/brief` asserts which
store is active in one line, daily, so a misroute is visible within a day.

## Gotchas

Documented in full in `Beads Guide.md`. The ones that bite most often:

- `bd create`, not `bd add`
- `bd update` does **not** accept `--deps` — use `bd dep add <blocked> <blocker>`. Don't recreate the issue.
- Tasks can depend on tasks, not on epics. `--deps <epic-id>` warns and silently skips.
- `--notes` on create; `--append-notes` on update (plain `--notes` overwrites)
- `-l` / `--labels` for categorization — there is no `--tag` flag on create
- `bd list --ready` is **not** `bd ready`. Only the latter is blocker-aware.
- Never create a bead silently on the user's behalf. A wrong bead is a false obligation; a missed one is a commitment that never became trackable. Propose, or confirm in one line.
