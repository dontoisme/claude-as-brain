# /rebuild-dashboard — Regenerate the Command Center

Rebuild `Dashboard.md` by reading the vault.

In an Obsidian-first setup this file would be Dataview queries. Here you read the actual files — which is slower, but lets the dashboard do something queries can't: **notice things**. "Three projects haven't moved in a month" is not a query result.

## Step 1: Gather

**Active projects** — read `Projects/`. For each: status, target date, last modified. Flag anything untouched in 30+ days.

**Areas** — list `Areas/`. When was each last updated? An Area with no insight added in two months is a signal.

**Recent daily notes** — last 7 days in `Days/`. Which days have notes, which are missing.

**Recent meetings** — last 14 days in `Meetings/`.

**Task state** (if `bd`):
```bash
bd ready --json
bd list --overdue --json
bd stale --json
bd list --status blocked --json
```

**Inbox** — count items in `Inbox/`.

**Link health** — a quick orphan count, or defer to `/link-check` for detail.

## Step 2: Write It

```markdown
---
tags: ["#dashboard"]
generated: YYYY-MM-DD HH:MM
---

# 🎯 Dashboard

> **Generated.** Run `/rebuild-dashboard` to refresh. Don't hand-edit.

## Needs Attention

<!-- Lead with this. Only include things that are genuinely off. -->

- ⚠️ **cab-22 overdue 12 days** — waiting on Legal since Apr 4
- ⚠️ **Projects/Billing Migration** — no activity in 34 days
- ⚠️ **Inbox at 14** — worth a `/weekly-review`

## Active Projects

| Project | Target | Last touched | Status |
|---------|--------|-------------|--------|
| [[Projects/Q3 Pricing]] | 2025-06-30 | 3 days ago | on track |

## Ready Now

- cab-12 — Draft Q3 timeline `p1`

## Areas

| Area | Last insight |
|------|-------------|
| [[Areas/Pricing]] | 4 days ago |
| [[Areas/Onboarding]] | 62 days ago ⚠️ |

## This Week

**Daily notes:** Mon ✅ Tue ✅ Wed ✅ Thu — Fri —
**Meetings:** 3 processed

## Quick Links

[[INDEX]] · [[Todos]] · [[Knowledge Changelog]] · [[MOCs/]]

---

*Generated YYYY-MM-DD HH:MM*

<!-- OBSIDIAN + DATAVIEW USERS
     If you install Obsidian with the Dataview plugin, these render live
     and this file stops needing regeneration. Uncomment to use.

```dataview
TABLE status, target FROM "Projects" WHERE status != "done"
```

```dataview
LIST FROM "Days" SORT file.name DESC LIMIT 7
```
-->
```

## Rules

**Lead with what's wrong.** A dashboard that opens with a tidy inventory gets skimmed. One that opens with three problems gets read.

**Only flag real problems.** A project untouched for 3 days is fine. 30 is worth a line. Inventing urgency trains the user to ignore the section.

**Be specific about time.** "34 days" beats "a while."

**Keep the Dataview block commented.** It's forward compatibility, not decoration — it means an Obsidian user can switch this file to live queries in one edit.

**Skip empty sections.**

## Report

```
✅ Dashboard.md — 3 items need attention
```

## Begin

Read the vault and regenerate the dashboard.
