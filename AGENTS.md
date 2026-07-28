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

If `bd` is not installed, this vault still works. Task tracking falls back to hand-maintained markdown in `Todos.md`, and the memory layer is unavailable. Mention it once, then proceed without nagging.

Install: `brew install beads`

## Gotchas

Documented in full in `Beads Guide.md`. The ones that bite most often:

- `bd create`, not `bd add`
- `bd update` does **not** accept `--deps` — use `bd dep add <blocked> <blocker>`. Don't recreate the issue.
- Tasks can depend on tasks, not on epics. `--deps <epic-id>` warns and silently skips.
- `--notes` on create; `--append-notes` on update (plain `--notes` overwrites)
- `-l` / `--labels` for categorization — there is no `--tag` flag on create
- `bd list --ready` is **not** `bd ready`. Only the latter is blocker-aware.
