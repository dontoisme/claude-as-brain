---
date: 2026-09-02
tags: ["#area", "#claude-as-brain", "#retrieval"]
status: active
source: human
uuid: 000ea256-88a7-4cb4-aa27-2a69c59dae6c
---

# Claude-as-Brain

**What this covers:** The design and upkeep of this vault as a system — retrieval quality, the three memory layers (notes / beads issues / beads memories), command behavior, and interoperability with other memory formats. Not the content of the vault; that lives in the other Areas.

**Why I own it:** Nobody else will. A knowledge system that isn't maintained decays into an archive, and the retrieval layer only improves if someone treats it as a product.

---

## Current State

Both specs shipped on 2026-09-02; their beads are closed and the epics with them. What exists now, by layer:

- **Retrieval** — `/reindex` builds `.index/brain.sqlite3`; `/ask` reranks by relevance × recency × activation with intent profiles, provenance labels, and age labels; embeddings switch on automatically when a local `ollama` serves `nomic-embed-text`. Scripts: `.claude/scripts/brain_index.py`.
- **Provenance** — `source:` on every note, `^inferred` markers, `sources:` URLs re-checked by `/verify` (`verify_sources.py`).
- **Memory hygiene** — `.beads/memory-meta.jsonl` confirm clock surfaced by `/brief` (`memory_meta.py`).
- **Weekly review** — distillation of event notes, promotion proposals, and a contradiction pass (`brain_review.py`), then `/reindex`.
- **Interop** — `/export-memoryfield`, `/import-memoryfield` (`memoryfield.py`).

Specs, kept as the design record: [[Projects/Memoryfield Improvements Spec]] · [[Projects/Temporal Retrieval Spec]]. `bd list -l contradiction` shows what the contradiction pass has filed.

Known limits worth remembering: the live ollama embedding path is written to the documented API but was verified only with a test embedder; prompt-level acceptance tests (`/ask` labelling) are untested headless.

## Decisions

| Decision | Date | Rationale |
|----------|------|-----------|
| Beads is an accelerator; markdown stays the source of truth | 2026-09-01 | Both specs restate this as the unbreakable constraint. See [[PLAN]]. |
| Remote (mobile) sessions build `bd` from source via a SessionStart hook and persist state through `.beads/issues.jsonl` | 2026-09-02 | The Dolt database is an ephemeral cache. Committing it would mean binary diffs for no benefit. |
| A retrieval resets a note's recency clock (age from the later of `updated` and last retrieval) | 2026-09-02 | The only reading under which Temporal Phase B's acceptance can pass; matches the spec's "decays from last retrieval, not creation". |
| Wikilink bumps weigh 0.5× a read-for-answer; `mixed` provenance scores 0.95 | 2026-09-02 | Both left open by the specs; both are one-line knobs in CLAUDE.md. |
| Memory decay lives in a committed sidecar, not on the memory | 2026-09-02 | bd 1.2.2 has no memory metadata. |

## Related

- [[PLAN]] — design rationale for the whole system
- [[Beads Guide]] — how the task and memory layers work
- [[MOCs/README]]
