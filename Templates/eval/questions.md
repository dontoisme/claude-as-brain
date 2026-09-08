---
date: 2026-09-08
tags: ["#eval"]
type: eval-fixture
---

# Retrieval Eval — Known-Answer Questions

Run by `/self-check`. Each question has a known answer and a set of files that
**must** appear in the citations for the answer to count as correct.

This is the only way to tell whether retrieval is degrading as the vault grows,
and the only way to compare `inline` against `parallel` empirically rather than
by vibes. The failure mode of degraded retrieval is silent: plausible,
confident, incomplete answers. Nothing else in the system catches that.

Not a benchmark. Eight questions, a few minutes, run monthly.

---

## Part A — Seed Questions

Valid only while the example seed content is present. `/install` offers to clear
it; run `/self-check` once before you do, to establish a baseline.

### S1. What did we decide about annual pricing, and why?
**Must cite:** `Meetings/20250312 - Pricing Review.md`
**Must contain:** annual-only, enterprise tier, cash flow predictability, Dana
**Must not claim:** that mid-market was included — it was explicitly left flexible

### S2. Who raised concerns about the annual-only decision, and when?
**Must cite:** `Meetings/20250312 - Pricing Review.md`, `Meetings/20250402 - Riverside Renewal.md`
**Must contain:** Marcus (March, mid-market price sensitivity), Priya (April, renewal friction)
**Tests:** multi-note synthesis across two dates

### S3. Has the annual-only decision been reversed?
**Must cite:** `Areas/Pricing.md`
**Correct answer:** No. Evidence has accumulated against it; it was never formally reopened.
**Tests:** the hardest failure — mistaking *someone complained* for *a decision changed*

### S4. What condition was attached to the annual pricing decision?
**Must cite:** `Meetings/20250312 - Pricing Review.md`
**Must contain:** revisit if churn moves, and that "moves" was never given a number
**Tests:** retrieval of a qualifier rather than a headline

### S5. What do I know about Priya Nandakumar?
**Must cite:** `People/Priya Nandakumar.md`, `Meetings/20250402 - Riverside Renewal.md`
**Tests:** person-centric retrieval across a profile and an event

### S6. Is the mid-market annual issue a pricing problem or an enablement problem?
**Must cite:** `Meetings/20250402 - Riverside Renewal.md`, `Areas/Pricing.md`
**Correct answer:** Unresolved in the vault. Both notes raise it; neither settles it.
**Tests:** whether an open question gets reported as open, or gets an invented answer

### S7. What churn data do we have by contract term?
**Must cite:** `Areas/Pricing.md`
**Correct answer:** None. Nobody has pulled it; it's an open bead.
**Tests:** absence. The most important case — a confident answer here is a fabrication

### S8. What happens to existing quarterly enterprise contracts at renewal?
**Correct answer:** Nothing in the vault answers this. It's logged as an open question twice.
**Tests:** absence again, on a question that *sounds* like it should have an answer

---

## Part B — Your Questions

Once the seed is cleared, Part A is dead weight. Replace it here.

A fixed fixture built on someone else's notes tells you that retrieval works on
*their* content. What you need to know is whether it works on **yours** — your
vocabulary, your note lengths, your folder shape.

**Write these at the end of a weekly review**, when you've just read the week
and know what's actually in there. Eight questions, mixed deliberately:

- Two you know the answer to cold, with an obvious single source
- Two needing synthesis across three or more notes
- Two about something that **changed** over time
- One where the honest answer is *"nothing in the vault covers this"*
- One about a person

That last-but-one is not optional. **A retrieval system that never says "I found
nothing" is a system that fabricates**, and you will not notice, because the
fabrications are plausible by construction. It's the only question in the set
that tests the property the whole vault depends on.

### Template

```
### Q1. <question exactly as you'd type it into /ask>
**Must cite:** Path/To/Note.md, Path/To/Other.md
**Must contain:** <the specific facts a correct answer includes>
**Must not claim:** <the tempting wrong answer, if there is one>
**Tests:** <what property this question is checking>
```

### My Questions

<!-- Add yours below. Delete Part A once the seed is gone. -->

---

## Notes on Scoring

**Citation match is the primary score.** Did the expected paths appear? That's
mechanical and honest.

**Fabrication is a hard failure**, not a deduction. One invented claim across
eight questions means the run failed, regardless of the other seven. There is
no acceptable rate of fabrication in a memory system.

**A missing citation with a correct answer is still a miss.** An answer you
can't check is an answer you have to take on faith, which is the thing this
system exists to avoid.
