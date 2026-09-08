---
date: 2026-09-02
updated: 2026-09-08
tags: ["#area", "#claude-as-brain", "#retrieval"]
status: active
source: mixed
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

## What Running It Taught, 2026-09-08

Three PRs merged, then the merged system was run for the first time. Five defects
surfaced that no amount of reading had caught, because each was a claim about the
world rather than about the code: `bd init --init-if-missing` is not a flag that
exists, and `.beads/embeddeddolt` is not a path that exists. Both had shipped
through review. The merge conflicts, which looked like the risk going in, were the
easy half.

**The `example-` prefix is load-bearing, and nothing enforces it.** `/install`
clears seed content by looking for the `example-seed` label on issues and the
`example-` prefix on memories. Three of the five defects were the same failure:
something in the seed lacked the marker and would therefore have *survived* the
cleanup. The worst was a `priya-renewals` memory duplicating
`example-priya-renewals` — a new user would have finished install carrying an
auto-injected assertion that "Priya owns renewals end to end, not Marcus" about
people who exist nowhere in their vault. That is the fabrication failure
[[CLAUDE]] names as the worst one available, shipped by default.

The root cause is that cleanup is **opt-in**: content must declare itself
disposable, and anything that forgets to is kept. Opt-out would be safer — keep
only what is marked as real, drop the rest — because the failure mode then costs
a deletion the user can undo from git, not a fabricated memory they never see
being formed. ^inferred

**Two checkouts of this vault on one machine collide silently.** Cloning it and
running `.claude/hooks/setup-beads.sh` made the clone seize the shared Dolt
server's `cab` database; the original repo then refused to connect with
`PROJECT IDENTITY MISMATCH`. The error surfaces in the innocent checkout, which
is what makes it hard to reason about. The database name derives from the
prefix, so any two vaults sharing a prefix on one machine will do this.

**The recovery is the good news.** The store was rebuilt entirely from the
committed `.beads/issues.jsonl`, losing only one bead created after the last
export. The durability constraint below — beads is an accelerator, markdown and
JSONL are the source of truth — has now been tested by accident rather than
asserted. It held.

Open defects from this pass: `bd list -l bugfix`. The one that needs a decision
rather than a fix is that `issues.jsonl` is simultaneously the distribution seed
and the working task list, which became a real problem the moment the repo was
flagged as a GitHub template.

## Decisions

| Decision | Date | Rationale |
|----------|------|-----------|
| Beads is an accelerator; markdown stays the source of truth | 2026-09-01 | Both specs restate this as the unbreakable constraint. See [[PLAN]]. |
| Remote (mobile) sessions build `bd` from source via a SessionStart hook and persist state through `.beads/issues.jsonl` | 2026-09-02 | The Dolt database is an ephemeral cache. Committing it would mean binary diffs for no benefit. |
| A retrieval resets a note's recency clock (age from the later of `updated` and last retrieval) | 2026-09-02 | The only reading under which Temporal Phase B's acceptance can pass; matches the spec's "decays from last retrieval, not creation". |
| Wikilink bumps weigh 0.5× a read-for-answer; `mixed` provenance scores 0.95 | 2026-09-02 | Both left open by the specs; both are one-line knobs in CLAUDE.md. |
| Memory decay lives in a committed sidecar, not on the memory | 2026-09-02 | bd 1.2.2 has no memory metadata. |
| Cleanup keys on an opt-in marker (`example-seed` / `example-` prefix) | 2026-09-08 | Inherited, not chosen. Recorded here because it failed three times in one day and the fix is a design change, not a patch. |
| CI enforces vault invariants, and only invariants the README claims | 2026-09-08 | `.claude/scripts/vault_check.py`. First run: 25 findings, 24 false — it fired on the docs that *describe* `[[wikilinks]]` and `{{date:...}}`. A checker that cries wolf on its own README gets switched off, so it strips code spans and skips `Templates/`. |

## Related

- [[PLAN]] — design rationale for the whole system
- [[Beads Guide]] — how the task and memory layers work
- [[MOCs/README]]
