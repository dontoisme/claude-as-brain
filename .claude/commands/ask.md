# /ask — Question the Vault

Answer a question using everything in this vault, with citations.

This is the flagship command. It replaces the search bar you'd have in a note-taking app, and it should be meaningfully better: it reads, ranks, notices disagreement, and says when it found nothing.

## The One Rule

**A memory system that invents things is worse than no memory system.**

Everything below serves that. If you take nothing else from this file: never fill a gap with something plausible. "I found nothing on that" is a good answer. A confident synthesis of notes that don't exist is a catastrophic one, because the user will believe it — that's the entire point of having a brain they trust.

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

## Step 3: Answer

Lead with the answer. Not with your process, not with what you searched.

**Cite every claim** with its source path: `Meetings/20250312 - Pricing Review.md`. The user must be able to open the file and check you.

**Mark inference explicitly.** There is a hard line between:
- *"You decided X"* — the note says so
- *"This suggests X"* — you concluded it

Never blur these. When you're reading between the lines, say you're reading between the lines.

**Surface disagreement.** If two notes conflict, that IS the answer — report both with dates and let the user resolve it. Do not silently prefer the recent one; a later note isn't automatically a decision to change course, and conflating "someone complained" with "we reversed the decision" is a serious error.

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
