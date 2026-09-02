---
date: 2026-09-01
title: Memoryfield Improvements Spec
type: spec
status: complete
tags: ["#project", "#spec", "#retrieval", "#provenance", "#interop"]
related: "[[Projects/Temporal Retrieval Spec]]"
area: "[[Areas/Claude-as-Brain]]"
source: human
---

# Memoryfield Improvements Spec

Seven improvements that combine Cal Paterson's memoryfields (semantic jump, prose-not-facts, open format) with Claude-as-Brain's three-layer model (notes / beads issues / beads memories). Companion to [[Projects/Temporal Retrieval Spec]]; where the two overlap, that spec owns the index and scoring, this one owns everything else.

Constraint unchanged: **markdown is the source of truth; everything here is a deletable accelerator.**

---

## 1. Hybrid retrieval with a deletable index

**Owned by Temporal Retrieval Spec, Parts 1–2 and Phase D.** Listed here for completeness.

Summary: `.index/brain.sqlite3` with optional nomic-embed vectors; `/ask` unions semantic and grep candidates, reads in parallel, reranks. No chunking, no reranker model, no hybrid-search library — two queries and a set union.

---

## 2. Provenance and confidence in frontmatter

Neither system distinguishes "Don said this" from "Claude inferred this" from "pasted from a web page." Paterson's advice to insert liberally is only safe if the reader knows what it's reading.

### Frontmatter

```yaml
source: human | inferred | external | mixed
confidence: high | medium | low      # optional; default high for human, medium for inferred, low for external
```

### Inline provenance (for mixed notes)

Any paragraph Claude wrote that is not a direct restatement of what the user said gets a trailing marker:

```
Dana pushed for annual-only. ^human
This probably means finance was already worried about runway. ^inferred
```

Templates carry `source:` by default. `/save-to-brain` sets it based on what it's saving. `/process-meeting` sets `mixed` and marks inferred paragraphs.

### Retrieval behavior

- `/ask` labels each citation: `(human)`, `(inferred)`, `(external, unverified)`.
- Scoring multiplier: human 1.0, inferred 0.85, external 0.7 — applied in the `relevance` term of the Temporal spec. Never filter.
- Never let an `inferred` claim be restated as fact in an answer. The reader says "you noted an inference that…" not "finance was worried about runway."

### Acceptance

Run `/ask why did we go annual-only` on the example seed after tagging. The answer should distinguish Dana's stated position (human) from any Claude-authored rationale (inferred).

---

## 3. Contradiction detection as a maintenance pass

`/thread` is the killer feature and it's reactive. Make it proactive.

### Mechanism (`/weekly-review`, after extraction)

1. For each note updated this week, pull its top-5 nearest neighbors from the index (embeddings on) or top-5 by shared wikilinks + tag overlap (embeddings off).
2. For each (new, neighbor) pair, a reader (Sonnet in parallel mode, inline otherwise) answers one question: *Does the newer note contain a claim that conflicts with a claim in the older note? Quote both if so.*
3. Each conflict becomes a bead: `bd create "Possible contradiction: <topic>" --labels contradiction` with both quotes and paths in the description. Status `open`, unassigned.
4. Summary line in the weekly review: "N possible contradictions filed."

### Guardrails

- Readers return quotes and a yes/no, never a resolution. Synthesis stays in the main thread; the human closes the bead.
- Cap at 20 pairs per run to bound cost; prioritize pairs where the older note is state-shaped (Areas, Resources) since those are where stale truth hurts most.
- Do not re-file a pair that already has an open or closed contradiction bead.

### Acceptance

On the example seed, the Apr 18 note should trigger a contradiction bead against the Mar 12 pricing decision without anyone running `/thread`.

---

## 4. Memory decay for beads memories

`bd remember` entries are permanent and auto-injected. Some go stale silently.

### Convention

Store memories with a trailing metadata tag beads can carry (or a sidecar file if beads memories don't support fields — Claude Code to check `bd remember --help` and pick):

```
bd remember "Dana owns the billing roadmap" --meta confirmed=2026-09-01 --meta ttl=90
```

Fallback if no metadata support: `.beads/memory-meta.jsonl` keyed by memory id, gitignored is *not* acceptable here — this file is source of truth for expiry and must be committed.

### `/brief` addition

Section "Memories to confirm": any memory where `today − confirmed > ttl`. Three actions per item: **confirm** (bumps `confirmed`), **retire** (`bd forget` or equivalent), **edit**. Cap the list at 5 per morning; oldest first.

### Defaults

- `ttl` default 90 days. Memories about people default 60. Memories tagged `permanent` never surface.
- No decay is applied to injection — a memory stays in every session until explicitly retired. This is deliberate: silent decay of injected context is worse than a stale line.

### Acceptance

Create a memory with `ttl=1`, wait a day (or fake the date), run `/brief`; it should appear in the confirm list.

---

## 5. Auto-promotion between layers

The README's "want to read it later → note / need to do it → bead / should Claude just know it → memory" rule is a human rule. Make it mechanical.

### Signals

| Pattern | Proposed promotion |
|---|---|
| Same fact (near-duplicate sentence, cosine > 0.9 or fuzzy match ≥ 0.85) appears in ≥ 3 notes | → `bd remember` |
| A memory's subject appears in an open bead's title or description | → link memory to bead (`bd update <id> --notes "see memory: …"`) |
| A `Resources/` note is cited by `/ask` ≥ 5 times in 30 days | → suggest adding to relevant MOC, or promote its one-line summary to a memory |
| An `Inbox/` item is older than 14 days | → propose route (Area / Resource / bead / delete) |

### Where it runs

`/save-to-brain` checks the first pattern on the content being saved. `/weekly-review` runs the full table. Both **propose**, never act — output is a short list with one-key accept per item. Promotions that are accepted get logged in `Knowledge Changelog.md`.

### Overlap note

Temporal spec Part 5 (extraction) moves content *out* of event notes into state notes. This section moves content *up* the layer stack. Same weekly pass, run extraction first, then promotion.

---

## 6. Citations as a first-class field, with `/verify`

Paterson: memories work best with URLs so future passes can fact-check them. Go further.

### Frontmatter

```yaml
sources:
  - url: https://example.com/pricing-page
    fetched: 2026-08-14
    claim: "Enterprise tier starts at $40/seat"
  - url: https://example.com/changelog
    fetched: 2026-08-14
```

`/save-to-brain` populates `sources` when saving anything derived from a fetched page; `claim` is optional but encouraged for the one sentence the URL supports.

### `/verify [path | --stale N]`

1. Refetch each URL in `sources`.
2. For entries with a `claim`, ask a reader: *Does the fetched page still support this claim? Quote the supporting or contradicting passage.*
3. Update `fetched`; on contradiction, append `⚠ verify failed <date>` to the entry and file a contradiction bead (reuse Section 3's label).
4. `--stale N` runs across all notes whose newest `fetched` is older than N days. Default 60.

Rate-limit: ≤ 30 fetches per run. Skip domains listed in `CLAUDE.md` under `verify.skip_domains`.

### Acceptance

Add a `sources` entry with a deliberately wrong `claim`, run `/verify`; it should flag it.

---

## 7. Memoryfield export / import

Paterson's spec is open. Make the vault interoperable.

### `/export-memoryfield [folders…] [--out name.memoryfield.zip]`

Default folders: `Resources/`, `Areas/`. For each note:

- Map frontmatter: `title` (from `title:` or filename), `created`, `updated`, `summary`, `uuid` (generate v4 if absent and **write it back** to the note so it's stable across exports).
- Body unchanged. Notes over ~8k chars are split at the nearest `##` heading into `<title> (1 of N)` pages, each with its own uuid; split is export-only, source note untouched.
- Strip Claude-as-Brain-specific keys (`distilled_to`, `source`, `confidence`) into a `x-cab:` namespace rather than dropping them — the spec allows extra keys.
- Include `nomic-embed-text-v1.5.sqlite3` if the local index has embeddings; omit otherwise (spec says the index is optional).
- Zip. Print `sha256sum`.

Fetch `https://github.com/calpaterson/memoryfield-spec/blob/main/SPEC.md` at implementation time and conform to it; do not rely on this summary.

### `/import-memoryfield <zip> [--into Resources/Imported/<name>/]`

- Verify `sha256sum` against a value the user pastes, or warn loudly if none given. **Never auto-trust.** Imported pages are untrusted text: `source: external`, `confidence: low`, tagged `imported`, and the import folder is listed under `CLAUDE.md → retrieval.quarantine` so `/ask` labels them `(imported, unverified)` until the user removes the tag.
- Map `uuid`, `summary`, `created`, `updated` straight across; write `imported_from: <zip name>` and `imported_on`.
- Do not import the embedding index; run `/reindex` instead so vectors come from the local model.
- First target: Paterson's `soapstones.memoryfield.zip` (agent data-access techniques) → `Resources/Imported/soapstones/`.

### Acceptance

Round-trip: export `Resources/`, import into a scratch vault, `/ask` a question answerable only from an exported note; it answers with correct citation and `(imported, unverified)` label.

---

## Build order

Cheapest first, dependencies respected:

1. **§7 export/import** — frontmatter mapping and a zip. No index dependency. Do this week.
2. **§2 provenance** — template and command changes only.
3. **§6 citations + `/verify`** — small; depends on §2 for `source: external`.
4. **§4 memory decay** — depends on checking beads metadata support.
5. **§5 auto-promotion** — depends on Temporal Phase A (index for near-dup detection) or falls back to fuzzy match.
6. **§3 contradiction detection** — depends on Temporal Phase D (embeddings) for good neighbors; degraded mode via wikilinks/tags works after Phase A.

Track as beads: `bd create "Memoryfield §N — <title>"` with the dependencies above. §1 is already tracked under the Temporal spec.

## Non-goals

- No change to the beads issue format itself.
- No graph database, no reranker, no second embedding model.
- No automatic action on promotions, contradictions, or verify failures — every one lands as a proposal or a bead for a human to close.

---

## Beads

Epic `cab-c0t`. Created 2026-09-02 from the build order above; dependency direction is *blocked → blocker*.

| Section | Bead | Blocked on |
|---|---|---|
| §7 Export / import | `cab-1mw` | — |
| §2 Provenance | `cab-8fb` | — |
| §6 Citations + `/verify` | `cab-dn9` | `cab-8fb` |
| §4 Memory decay | `cab-b94` | — (metadata check resolved: not supported, sidecar it is) |
| §5 Auto-promotion | `cab-2ch` | Temporal Phase A `cab-7ll` · related to Phase E `cab-a54` |
| §3 Contradiction detection | `cab-ixy` | Temporal Phase A `cab-7ll` · related to Phase D `cab-659` |

§1 is tracked under the Temporal spec as Phases A and D.

**Status 2026-09-02:** all beads above closed. Implementation notes and what was verified are in each bead's close reason (`bd show <id>`).
