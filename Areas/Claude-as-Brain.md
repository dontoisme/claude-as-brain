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

Two specs are active as Projects. Work is tracked in beads under the labels `spec:memoryfield` and `spec:temporal`.

- [[Projects/Memoryfield Improvements Spec]] — provenance, contradiction detection, memory decay, auto-promotion, citations, memoryfield export/import
- [[Projects/Temporal Retrieval Spec]] — a deletable sqlite index, recency and usage scoring, intent profiles, extraction in weekly review

Build order and dependencies are in each spec. `bd ready -l spec:memoryfield` or `bd ready -l spec:temporal` shows what is claimable.

## Decisions

| Decision | Date | Rationale |
|----------|------|-----------|
| Beads is an accelerator; markdown stays the source of truth | 2026-09-01 | Both specs restate this as the unbreakable constraint. See [[PLAN]]. |
| Remote (mobile) sessions build `bd` from source via a SessionStart hook and persist state through `.beads/issues.jsonl` | 2026-09-02 | The Dolt database is an ephemeral cache. Committing it would mean binary diffs for no benefit. |

## Related

- [[PLAN]] — design rationale for the whole system
- [[Beads Guide]] — how the task and memory layers work
- [[MOCs/README]]
