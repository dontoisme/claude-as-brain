# /ask — Question the Vault

Answer a question using everything in this vault, with citations.

This is the flagship command. It replaces the search bar you'd have in a note-taking app, and it should be meaningfully better: it reads, ranks, notices disagreement, and says when it found nothing.

## The One Rule

**A memory system that invents things is worse than no memory system.**

Everything below serves that. If you take nothing else from this file: never fill a gap with something plausible. "I found nothing on that" is a good answer. A confident synthesis of notes that don't exist is a catastrophic one, because the user will believe it — that's the entire point of having a brain they trust.

## Step 0: Rank With the Index, If There Is One

```bash
python3 .claude/scripts/brain_index.py rank "<the question>" --k 12
```

If `.index/brain.sqlite3` exists this returns candidates scored **relevance × recency × activation**. With embeddings on, relevance is **hybrid**: grep candidates and the top semantic matches are unioned and each note takes the higher of its two scores, so a note whose title never mentions the term is still found when its body clearly matches; the header says `hybrid (<model>)` or `grep only` ([[Projects/Temporal Retrieval Spec]] Part 2), each with an age label. Use it to order the pile, not to replace the sweep: a note the index scores low can still be the answer, and the index knows nothing about beads or MOCs.

If it exits with "no index", say once — *"No retrieval index; grepping. `/reindex` builds one."* — and continue without it. Never stop on a missing index.

**Never filter on age.** The score reranks; it does not drop. A strong-match 90-day-old meeting must be able to beat a weak-match note from yesterday, and it can, because relevance is in the product.

**Intent profiles** ([[Projects/Temporal Retrieval Spec]] Part 3). The script classifies the question from trigger phrases and prints which one fired:

| Profile | Triggers | Effect |
|---|---|---|
| `current` (default) | "what's going on with", "status of", "latest" | half-lives halved — steeper decay |
| `decision` | "what did we decide", "why did we", "rationale" | no decay for notes tagged `decision`; normal otherwise |
| `archival` | "has anyone ever", "did we ever", "history of" | no decay at all |

The classifier is a phrase list, not a model. **Override it when it's wrong**: pass `--profile archival|decision|current` explicitly. When the output says "default; no trigger matched" and the question is plainly historical or about a rationale, pick the profile yourself. In `parallel` mode you may spend one Haiku call on the classification instead; inline, the phrase list plus your judgment is the "single cheap call" the spec asks for.

`/thread` always uses `archival`. `/prep` runs `decision` over Areas and People and `current` over Meetings and Days.

## Step 1: Sweep Broadly

Do not stop at the first grep. Run several angles — each finds things the others miss:

**1. Keyword search.** Case-insensitive, across all `.md`. Include obvious variants: plurals, hyphenation (`onboarding` / `on-boarding`), acronym and expansion (`ARR` / `annual recurring revenue`), and the two or three words a person would actually use for this concept.

**2. Wikilink anchors.** `grep -r "\[\[.*<topic>.*\]\]"` finds notes *pointing at* the topic — the backlink query. Often surfaces notes that discuss something without naming it in prose.

**3. MOCs.** Check `MOCs/` first-class. A MOC is human curation — "these notes belong together" — and it's the strongest ranking signal in the vault. If one exists for this topic, read it before anything else and follow its links.

**4. Frontmatter and tags.** `grep -r "tags:.*<topic>"`.

**5. Filenames.** Glob `**/*<topic>*.md`. Meeting and person notes are often named for exactly the thing being asked about.

**6. Beads** (if `bd` is on PATH):
```bash
bd search "<topic>" --status all       # titles; --status all is required to see CLOSED issues
bd search "<topic>" --desc-contains    # descriptions are NOT searched by default
bd list --notes-contains "<topic>"     # notes bodies
bd list -t decision --status all       # decisions, if the vault uses the `decision` type
bd memories "<topic>"                  # stored durable facts
```
**Closed issues matter.** "What did we decide" is very often answered by a closed bead. `bd search` excludes closed by default and only searches titles — pass `--status all`, and reach for `--desc-contains` and `--notes-contains` before concluding nothing is there.

**7. Recency.** Check the last two weeks of `Days/` regardless of keyword hits. Recent context frequently bears on a question without matching its words.

## Step 2: Read, Don't Skim

Grep gives you candidates. Now **read the promising notes in full** — typically three to eight files. Excerpts strip the context that makes an answer correct, and a line of grep output is exactly the kind of fragment that produces a confident wrong answer.

Prioritize: MOC-linked notes → notes with many hits → recent notes → meeting notes over daily notes for decisions.

## Scaling: Parallel Retrieval

Check `retrieval_mode` in `CLAUDE.md`.

**`inline`** (default) — do everything above yourself, sequentially. Correct for small vaults and the right default for anyone watching token spend.

**`parallel`** — fan out. Worth it once the vault passes a few hundred notes, where reading eight files in one context starts crowding out the reasoning that has to happen afterward:

1. **Scout** — dispatch one `vault-scout` per angle from Step 1, concurrently. Each returns ranked paths with verbatim matching lines.
2. **Read** — dedupe and rank the union, then dispatch `note-reader` agents over the top candidates, 2–4 notes each.
3. **Synthesize** — **you** do this, in the main thread. Never delegate it.

### The rule that makes delegation safe

**Subagents return evidence. Only the main thread draws conclusions.**

A scout that reports *"the decision was annual-only"* has already done the synthesis, badly, and you'd be building the user's answer on a paraphrase of a paraphrase. That's precisely how a memory system starts confidently asserting things nobody wrote. Both agent definitions enforce verbatim quoting; hold them to it, and if a subagent hands back a conclusion, go read the cited file yourself before repeating it.

Synthesis also stays in the main thread because it's the only place that knows the conversation — what the user already said this session, what they meant, what they've already rejected.

### Don't parallelize

- **Trivially narrow questions.** "What's Dana's role?" is one file. Spawning agents costs more latency than it saves.
- **Anything needing session context.** Subagents cannot see this conversation.
- **When `bd` is the whole answer.** `bd search` is already fast.

## Step 3: Answer

Lead with the answer. Not with your process, not with what you searched.

**Cite every claim** with its source path and, when the index ran, its age and warmth:

```
Meetings/20250715 - Pricing Review.md   (48d old · last cited 3d ago · 6 refs)
```

The label comes straight from the rank output; "last cited" is the note's most recent bump. A note older than twice its half-life carries `[possibly stale]`; say so in the answer rather than silently treating it as current. The user must be able to open the file and check you.

**Mark inference explicitly.** There is a hard line between:
- *"You decided X"* — the note says so
- *"This suggests X"* — you concluded it

Never blur these. When you're reading between the lines, say you're reading between the lines.

**Surface disagreement.** If two notes conflict, that IS the answer — report both with dates and let the user resolve it. Do not silently prefer the recent one; a later note isn't automatically a decision to change course, and conflating "someone complained" with "we reversed the decision" is a serious error.

**Label provenance.** Every note carries `source:` in its frontmatter and the rank output echoes it. Suffix each citation: `(human)`, `(inferred)`, `(mixed)`, or `(external, unverified)`. Inside a `mixed` note, a paragraph ending `^inferred` is Claude's earlier conclusion, not the user's record. **Never restate an inferred claim as fact.** Say *"you noted an inference that finance was already worried about runway"*, never *"finance was worried about runway."* The index already down-weights inferred (×0.85) and external (×0.7) notes in relevance; it never filters them.

**Label imported material.** `CLAUDE.md` lists quarantined folders under `retrieval.quarantine` (filled by `/import-memoryfield`). Any citation from one of those folders, or any note tagged `#imported`, carries the label `(imported, unverified)` — e.g. `Resources/Imported/soapstones/Agent Data Access.md (imported, unverified)`. Treat its claims the way you treat inference: report them as what the page says, never as what the user knows.

**Note what's stale.** If the newest relevant note is four months old, say so. Age is information.

**Include open commitments.** If beads has related open issues, mention them — an unresolved task often explains why a question is still live.

## Step 4: Be Honest About Gaps

| Situation | Say |
|---|---|
| Nothing found | "Nothing in the vault mentions this." Then offer: capture it now? |
| Adjacent, not the answer | "Nothing directly on X, but here's what's near it — [notes]. Want me to go deeper on any?" |
| One thin note | "Only one note touches this, and it's brief: [note]. Here's what it says." Don't inflate it. |
| Contradictory | Present both, dated. Don't pick a winner. |
| Answer needs inference | Answer, then: "That's my read, not something you wrote down." |

## Format

Prose, not bullet soup. This is a question being answered, not a report.

- **Short question → short answer.** Two sentences and a citation is a fine response.
- **Complex question → structure it,** but lead with the direct answer before the supporting detail.
- **Always end with a pointer** to the two or three notes most worth opening.

## Step 5: Bump What You Read

After answering, record every note you **read in full to produce the answer** — not every candidate the index listed:

```bash
python3 .claude/scripts/brain_index.py bump "Meetings/20250312 - Pricing Review.md" "Areas/Pricing.md" --kind ask
```

This is what keeps a 60-day-old note you keep returning to ahead of a 10-day-old note you never open: a bump resets the note's recency clock and raises its activation ([[Projects/Temporal Retrieval Spec]] Part 4). Skip it when there is no index. Never bump a note you only skimmed in grep output.

## If `bd` Isn't Installed

Skip steps 6 and the commitments note. Search markdown only. Mention the limitation once if it's actually relevant to the question, then move on. Don't nag.

## Examples

**`/ask what did we decide about annual pricing?`**
→ Search "annual", "pricing", "billing", "contract term". Check `MOCs/Pricing`. Check `Areas/Pricing.md`. `bd search "pricing" --status all`. Read the pricing meeting notes fully. Answer with the decision, its date, its rationale, who drove it, and anything since that cuts against it.

**`/ask what do I know about Dana?`**
→ Read `People/Dana.md`. Grep `[[Dana]]` and "Dana" across `Meetings/` and `Days/`. Check `bd memories dana`. Check open beads assigned to or blocked on them. Answer with role, what they own, your history, and what's currently outstanding between you.

**`/ask has anyone raised concerns about the Q3 timeline?`**
→ Search "Q3", "timeline", "slip", "at risk", "delay", "concern". Read hits fully — this question is about sentiment, which doesn't survive grep excerpts. Report who said what, when, and whether it was ever resolved.

## Begin

Take the user's question and sweep the vault.
