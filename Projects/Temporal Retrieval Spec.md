---
date: 2026-09-01
title: Temporal Retrieval Spec
type: spec
status: active
tags: ["#project", "#spec", "#retrieval", "#index"]
related: "[[Projects/Memoryfield Improvements Spec]]"
area: "[[Areas/Claude-as-Brain]]"
source: human
---

# Temporal Retrieval Spec

Add recency- and usage-aware retrieval to Claude-as-Brain without breaking the core constraint: **markdown is the source of truth; everything here is a deletable accelerator.**

Inspired by Cal Paterson's memoryfields (semantic jump over graph walking) plus ACT-R declarative memory (activation decays from last retrieval, not creation).

---

## Problem

- A 30-day-old meeting note is usually less relevant than yesterday's, but may hold a nugget worth finding fast.
- Rolling archive windows are hard cutoffs and lose nuggets.
- Weekly/monthly summary notes compress, so they make bad traversal points.
- Pure semantic search treats every hit as equally current.

## Core insight

A note has two separate clocks:

| Clock | Meaning | Decays? |
|---|---|---|
| **Event date** | When the thing happened / was written | Yes, by note type |
| **Truth horizon** | How long the contents stay valid | Only by contradiction |

Event-shaped notes (Days, Meetings) decay. State-shaped notes (Areas, Resources, decisions, memories) do not. Durable content gets **extracted** out of event-shaped notes so those can decay freely.

---

## Part 1 — Index (`.index/brain.sqlite3`)

Gitignored. Rebuildable from scratch at any time via `/reindex`. If the file is missing, every command falls back to grep-only retrieval and says so once.

### Schema

```sql
CREATE TABLE notes (
  path            TEXT PRIMARY KEY,
  note_type       TEXT NOT NULL,      -- day | meeting | project | area | resource | person | moc | inbox | other
  created         TEXT NOT NULL,      -- ISO 8601, from frontmatter or file birth
  updated         TEXT NOT NULL,      -- ISO 8601, from frontmatter or mtime
  last_referenced TEXT,               -- ISO 8601, bumped on retrieval or new inbound wikilink
  ref_count       INTEGER DEFAULT 0,  -- lifetime retrieval + inbound-link count
  content_hash    TEXT NOT NULL,      -- sha256 of body; skip re-embed if unchanged
  summary         TEXT,               -- frontmatter summary, if present
  embedding       BLOB                -- nullable; null if embeddings unavailable
);

CREATE TABLE retrievals (
  path TEXT NOT NULL,
  ts   TEXT NOT NULL,                 -- one row per retrieval event, for ACT-R activation
  kind TEXT NOT NULL                  -- ask | thread | prep | brief | wikilink
);
```

### note_type inference

From folder first, overridden by frontmatter `type:` if present:

```
Days/      → day
Meetings/  → meeting
Projects/  → project
Areas/     → area
Resources/ → resource
People/    → person
MOCs/      → moc
Inbox/     → inbox
```

### Embeddings

Optional. Detect `ollama` + `nomic-embed-text` at `/reindex`. If present, embed body (cap ~8k chars; longer notes embed the first 8k plus summary and get a `truncated` warning in the reindex report). If absent, `embedding` stays null and retrieval is grep + decay only. Do not add any other embedding dependency.

### Incremental reindex

`/reindex` walks the vault, compares `content_hash`, re-embeds only changed files, removes rows for deleted files. Report: N added, N updated, N removed, N truncated, embeddings on/off.

---

## Part 2 — Scoring

Final score for a candidate note given a query:

```
score = relevance × recency × activation
```

### relevance (0–1)

- Embeddings on: cosine similarity, normalized.
- Embeddings off: grep hit count normalized by note length, plus 0.3 bonus for title/summary match.
- Hybrid when both available: union candidates from both, take max.

### recency (0–1)

```
recency = 2 ^ ( -age_days / half_life[note_type] )
```

Defaults, overridable in `CLAUDE.md`:

```yaml
retrieval:
  half_life_days:
    day: 7
    meeting: 21
    inbox: 14
    project: 60        # applies only once status: complete/archived; active projects = inf
    area: inf
    resource: inf
    person: inf
    moc: inf
```

`age_days` uses `updated`, not `created`.

### activation (ACT-R base-level)

```
activation = ln( Σ  t_i ^ (-d) )     for each retrieval i, t_i = days since that retrieval
d = 0.5 (default)
```

Normalize to 0.5–1.5 so a never-retrieved note scores 1.0 (neutral), a hot note scores up to 1.5, a note last touched a year ago and never since scores ~0.5. This is the layer that keeps old nuggets alive: frequent retrieval beats calendar age.

### Never filter, always rerank

Return top-K by score. Do not drop candidates on age. A strong-match 90-day-old meeting must be able to beat a weak-match note from yesterday.

### Presentation

Reader labels each note it cites with age and warmth:

```
Meetings/20260715 - Pricing Review.md   (48d old · last cited 3d ago · 6 refs)
```

Notes older than 2× their half-life get a `[possibly stale]` marker in the answer.

---

## Part 3 — Query intent profiles

Before searching, `/ask` classifies the question into one profile (single cheap call; Haiku if parallel mode, inline otherwise):

| Profile | Trigger examples | Half-life multiplier |
|---|---|---|
| `current` | "what's going on with", "status of", "latest" | 0.5× (steeper decay) |
| `decision` | "what did we decide", "why did we", "rationale" | ∞ for notes tagged `decision`; 1× otherwise |
| `archival` | "has anyone ever", "did we ever", "history of" | ∞ (no decay) |

Default is `current`. `/thread` always uses `archival`. `/prep` uses `decision` for the person/topic's Area and `current` for their Meetings.

---

## Part 4 — Retrieval bumps

Every time a note is **read to produce an answer** (not merely listed as a candidate), insert a row into `retrievals` and update `last_referenced` / `ref_count`.

Also bump when a **new inbound wikilink** to the note is created by `/save-to-brain`, `/process-meeting`, or `/daily-note`. Kind = `wikilink`.

Do not bump on `/reindex`, `/link-check`, or `/rebuild-dashboard` — mechanical passes are not evidence of relevance.

---

## Part 5 — Extraction in `/weekly-review`

Replace summary-note generation with **distillation**. For each event-shaped note updated this week:

1. Identify durable content:
   - A decision → append to the relevant `Areas/` note under `## Decisions`, dated, with `[[source]]` link
   - A stable fact about a person/system → `bd remember` (if beads) else append to `People/` or `Areas/`
   - A commitment → bead (already handled by `/process-meeting`; verify)
   - A reference/link/how-to → `Resources/`
2. Append to the **source** note's frontmatter:
   ```yaml
   distilled_to:
     - "[[Areas/Pricing]]"
     - "bd:cab-31"
   distilled_on: 2026-09-05
   ```
3. Report what was extracted and what was judged non-durable.

A note with `distilled_to` set may decay freely — its diamonds are already in the bank. The old `week-NN-summary.md` / monthly knowledge-log pattern is retired; `Knowledge Changelog.md` continues as the append-only ledger of what moved where.

---

## Part 6 — Frontmatter additions

Add to `Templates/`:

```yaml
summary:        # one line, used for embedding and display
type:           # optional override of folder-inferred type
distilled_to:   # set by /weekly-review
distilled_on:
```

Do not require these on existing notes. Index tolerates absence.

---

## Part 7 — Commands to add / modify

| Command | Change |
|---|---|
| `/reindex` | **New.** Build/refresh `.index/brain.sqlite3`. |
| `/ask` | Classify intent → search (semantic + grep) → score → read top-K → bump → answer with age/warmth labels. |
| `/thread` | Force `archival` profile. Bump. |
| `/prep` | Mixed profile per Part 3. Bump. |
| `/brief` | Add section: "Cooling off" — notes whose activation crossed below 0.6 this week that have no `distilled_to`. Prompt to distill or let go. |
| `/weekly-review` | Extraction per Part 5. Runs `/reindex` at end. |
| `/save-to-brain`, `/process-meeting`, `/daily-note` | Bump targets of any new wikilinks. |
| `/link-check` | Also report notes with `distilled_to` pointing at nonexistent targets. |

`vault-scout` agent (parallel mode): return candidates with scores, not just paths. `note-reader`: unchanged, still verbatim quotes only.

---

## Part 8 — Build phases

**Phase A — index + scoring, grep only** (no ollama)
- Schema, `/reindex`, note_type inference, recency scoring, `/ask` rerank + labels.
- Acceptance: `/ask what's going on with <active area>` ranks this week's notes above last month's with equal grep hits.

**Phase B — retrieval bumps + activation**
- `retrievals` table, bump logic, ACT-R scoring.
- Acceptance: cite a 60-day-old meeting note three times via `/ask`; it should then outrank a 10-day-old note with equal relevance.

**Phase C — intent profiles**
- Acceptance: "has anyone ever mentioned X" surfaces a 6-month-old note that `/ask what's going on with X` does not.

**Phase D — embeddings**
- ollama detection, hybrid retrieval.
- Acceptance: a note whose title does not mention the query term is found by `/ask` when its body clearly matches.

**Phase E — extraction**
- `/weekly-review` distillation, `distilled_to`, `/brief` cooling-off section.
- Acceptance: run on the `example-seed` pricing thread; the Apr 18 cash-position observation lands in `Areas/Pricing.md` with a dated link back.

Track phases as beads: `bd create "Temporal retrieval — Phase A" ...`, dependencies A→B→C, A→D, B→E.

---

## Non-goals

- No pgvector, no external DB, no reranker model, no chunking.
- No decay applied to beads memories (they retire via `/brief` confirm-or-retire, separate spec).
- No change to the memoryfield export format if/when added — `created`/`updated`/`summary` map directly.

## Open questions for Claude Code to raise, not decide

- Should `ref_count` from wikilinks weigh the same as retrieval-for-answer? (Proposed: 0.5×.)
- Where does the intent classifier live in inline mode — a prompt block inside `/ask` or a tiny agent?

---

## Beads

Epic `cab-2ap`. Created 2026-09-02; dependency direction is *blocked → blocker*.

| Phase | Bead | Blocked on |
|---|---|---|
| A — index + scoring, grep only | `cab-7ll` | — |
| B — retrieval bumps + activation | `cab-m6r` | A |
| C — intent profiles | `cab-7wb` | B |
| D — embeddings | `cab-659` | A |
| E — extraction | `cab-a54` | B |

Memoryfield §5 and §3 also block on Phase A.
