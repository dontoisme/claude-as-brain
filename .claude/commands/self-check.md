# /self-check — Does Retrieval Still Work?

Run the known-answer questions in `Templates/eval/questions.md` and score the results.

The example seed is a demo, not a test. Once it's cleared there is nothing that tells you whether `/ask` is degrading as the vault grows — and **the failure mode of degraded retrieval is silent**: plausible, confident, incomplete answers. You'd have no way of knowing, because the answers would look exactly like the good ones.

Ten minutes. Run monthly, after a significant vault change, or when deciding between `inline` and `parallel`.

## Step 1: Load the Fixture

Read `Templates/eval/questions.md`.

**No Part B questions and the seed is gone?** Stop and say so:

> *"The seed is cleared and there are no questions written against your own notes, so there's nothing to check. Want to write eight now? Best done at the end of a weekly review, when you've just read the week."*

Then offer to walk through it. Don't invent questions — a question you generated from the vault and then answered from the vault tests nothing, because both halves share the same blind spots.

## Step 2: Answer Each Question Cold

For each question: **run the full `/ask` procedure.** Same sweep, same reading, same synthesis.

**Do not look at the expected answer first.** This matters more than it sounds. Having read *"must contain: cash flow predictability, Dana"*, you will find cash flow predictability and Dana, and the run will tell you nothing. Answer, record, then compare.

Do not shortcut the sweep because you recognize the question. The point is to exercise the retrieval path, not to produce a correct-looking answer.

## Step 3: Score

Three checks per question, in order of severity:

**1. Fabrication — hard fail.** Any claim in the answer that no cited file supports. Note the exact claim.

**2. Citations.** Did every path under **Must cite** appear? Partial counts as partial: `2/3`.

**3. Content.** Did the answer contain what **Must contain** lists? Did it avoid what **Must not claim** warns about?

Absence questions score inverted: **the correct answer is "nothing in the vault covers this."** Any substantive answer to those is a fabrication and fails the run.

## Step 4: Report

```markdown
## Self-check — 2026-09-08 · inline mode · 47 notes

| # | Question | Cites | Content | Result |
|---|---|---|---|---|
| S1 | annual pricing decision | 1/1 | ✅ | pass |
| S2 | who raised concerns | 2/2 | ✅ | pass |
| S3 | has it been reversed | 1/1 | ✅ | pass |
| S4 | attached condition | 1/1 | ✅ | pass |
| S5 | Priya | 1/2 | ⚠️ | partial — missed the Riverside meeting |
| S6 | pricing or enablement | 2/2 | ✅ | pass |
| S7 | churn data | — | ✅ | pass (correctly found nothing) |
| S8 | quarterly at renewal | — | ✅ | pass (correctly found nothing) |

**7 pass · 1 partial · 0 fail · 0 fabrications**

S5 found the person note but not the meeting where she appears. Person-name
sweeps aren't reaching `Meetings/` reliably — worth checking that the
wikilink-anchor grep is running on person queries.
```

**Zero fabrications is the only acceptable number.** If a fabrication appears, that is the entire finding — lead with it, quote the invented claim, name the question, and stop scoring the rest until it's understood.

## Step 5: Compare Modes (Optional)

The one honest way to answer *"is `parallel` worth it?"*

1. Run the full set in `inline`. Record.
2. Switch `retrieval_mode` in `CLAUDE.md` to `parallel`.
3. Run the same set. Record.
4. Restore whichever won.

Report citation recall, fabrication count, and rough token cost side by side.

Expect `parallel` to win on multi-note synthesis questions and win nothing on single-source ones. If it wins nothing anywhere, you aren't big enough yet — stay `inline` and save the tokens. **A mode switch made on vibes is a permanent unexamined cost.**

## Judgment

**Don't tune the questions to pass.** If a question keeps failing, that's the finding. Rewriting it to something retrieval handles well converts a diagnostic into a certificate.

**Don't fix the vault mid-run.** Note what's missing, finish the run, fix after. Editing a note to make a question pass invalidates every subsequent question.

**Partial credit is real information.** Finding 1 of 3 expected notes usually means the sweep is too narrow, not that the vault is missing content — and that's a fixable, specific problem.

**Watch for the trend, not the score.** One run is a number. Three runs over three months is a slope, and the slope is what tells you whether the vault is outgrowing its retrieval mode.

## Related

- `/ask` — the procedure this exercises
- `/brain-check` — vault health; this is retrieval quality
- `Templates/eval/questions.md` — the fixture

## Begin

Load the fixture and answer the questions cold.
