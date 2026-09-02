---
tags: ["#changelog"]
---

# 📚 Knowledge Changelog

A chronological index of what you've learned and where it lives.

Notes get filed into folders and disappear. This answers the question folders
can't: *"I learned something about this a few months ago — where did I put it?"*

Written automatically by `/save-to-brain`. Add entries by hand any time.

---

## Format

```markdown
### YYYY-MM-DD — [Topic]
**Category:** [Area/Resource/Project]
**Summary:** [One line]
**Location:** [[Link]]
```

---

## Entries

<!-- Newest first. Add below this line. -->

### 2026-09-02 — Weekly review distills instead of summarising
**Category:** Project
**Summary:** Event notes (Days, Meetings) get their durable content moved to Areas, memories, beads, or Resources, then are marked `distilled_to` so they can decay. `/brief` shows what's cooling off undistilled; `/link-check` catches dangling targets. Seed pricing thread distilled as the worked example.
**Location:** [[Projects/Temporal Retrieval Spec]] · [[Areas/Pricing]]

### 2026-09-02 — Semantic search, if and only if a local ollama is running
**Category:** Project
**Summary:** `/reindex` embeds notes with `nomic-embed-text` when ollama serves it and `/ask` unions semantic with grep candidates; otherwise nothing changes. No cloud embeddings, no other model. Memoryfield exports carry the vector index when one exists.
**Location:** [[Projects/Temporal Retrieval Spec]]

### 2026-09-02 — Notes you keep coming back to stay warm; questions carry intent
**Category:** Project
**Summary:** Every note read to answer is a retrieval that resets its recency clock and raises ACT-R activation (Phase B). `/ask` classifies questions into current / decision / archival profiles from trigger phrases and adjusts decay accordingly (Phase C).
**Location:** [[Projects/Temporal Retrieval Spec]]

### 2026-09-02 — Notes now say who wrote them, what they rest on, and when a memory should be re-checked
**Category:** Project
**Summary:** `source: human|inferred|external|mixed` on every note with `^inferred` markers; `sources:` URLs re-checked by `/verify`; beads memories get a confirm clock in `.beads/memory-meta.jsonl` that `/brief` surfaces.
**Location:** [[Projects/Memoryfield Improvements Spec]]

### 2026-09-02 — /ask now knows how old a note is
**Category:** Project
**Summary:** `/reindex` builds a deletable sqlite index; `/ask` reranks by relevance × recency (per-type half-lives, none for state-shaped notes) and cites with age labels. A bulk-committed note keeps its own `date:` rather than reading as written today.
**Location:** [[Projects/Temporal Retrieval Spec]]

### 2026-09-02 — The vault can speak memoryfield
**Category:** Project
**Summary:** `/export-memoryfield` packages Resources/ and Areas/ as a spec-conformant zip (uuids written back, 8 KB pages split at `##`); `/import-memoryfield` quarantines incoming pages as `(imported, unverified)` and refuses a bad sha256.
**Location:** [[Projects/Memoryfield Improvements Spec]]

### 2026-09-02 — Beads can run from a phone: remote sessions build bd and round-trip through issues.jsonl
**Category:** Area
**Summary:** The Dolt DB is a cache; `.beads/issues.jsonl` is the state. SessionStart hook builds `bd`, `/sync-todos` exports back. No need to commit the database.
**Location:** [[Areas/Claude-as-Brain]]

### 2026-09-02 — bd 1.2.2 memories have no metadata fields
**Category:** Project
**Summary:** `bd remember` takes only `--key`, so Memoryfield §4 decay uses the committed sidecar fallback, not tags on the memory.
**Location:** [[Projects/Memoryfield Improvements Spec]]

### 2026-09-01 — Two retrieval specs filed: temporal scoring and memoryfield interop
**Category:** Project
**Summary:** Recency × relevance × activation over a deletable sqlite index; provenance, contradiction detection, memory decay, citations, memoryfield export/import. Tracked as beads under `spec:temporal` and `spec:memoryfield`.
**Location:** [[Projects/Temporal Retrieval Spec]] · [[Projects/Memoryfield Improvements Spec]]

### 2025-04-18 — Conditional decisions need numeric triggers
**Category:** Area
**Summary:** "Revisit if churn moves" never fired because nobody defined "moves" — two signals accumulated with no revisit.
**Location:** [[Areas/Pricing]]

### 2025-04-02 — Policy and practice drifted on contract terms
**Category:** Area
**Summary:** Annual-only was scoped to enterprise; sales applied it across all tiers.
**Location:** [[Areas/Pricing]]

<!-- EXAMPLE SEED ENTRIES — delete during /install -->

---

## Tips

- **One line per entry.** This is an index, not content.
- **Write the summary for future you** — searchable words, not clever ones.
- **Review during weekly review.** What you capture reveals what you actually care about.
- **Don't backfill.** Start today; a partial changelog is still useful.
