# /ramp — Capture What You Only Learn Once

Structured capture for a new role: the org, the people, the acronyms, the systems, and the unwritten rules.

Most of this knowledge arrives in your first 90 days, is never written down, and becomes invisible the moment it's internalized. Six months in you can't remember what confused you — which is exactly when it stops being recoverable.

**This command is expected to fall out of use after a few months. That's what ramping means.**

## The Layer Question Dominates Here

More than any other command, `/ramp` should be routing to **`bd remember`**, not writing notes.

> "Priya owns renewals, not Marcus."
> "Deploys are frozen the last week of the quarter."
> "The `arr_monthly` table is the source of truth; the dashboard lags a day."

These are one-line facts you need in *every* session. A note requires remembering to open it. A memory arrives automatically:

```bash
bd remember "<fact>" --key <short-key>
```

**When in doubt during ramp, prefer the memory.** Being wrong costs one line; the note-shaped alternative costs a file nobody reopens.

## Modes

### `/ramp` — general session

Ask what they learned. Route each item. Batch the questions rather than interrogating one fact at a time.

### `/ramp person <name>`

Create or update `People/<Name>.md` from `Templates/Person.md`. Get:
- Role and team
- **What they actually own** — be specific. Not "engineering" but "the billing service and anything touching invoicing."
- How they prefer to work
- Your relationship: what you owe each other

Then `bd remember` the ownership fact — that's the part you'll need in six months when deciding who to ask.

### `/ramp org`

Build or update an org map in `Areas/Org.md`: teams, who leads what, how decisions get made, who has to be in the room.

The unwritten parts matter more than the chart. *"Nothing ships without Priya's sign-off even though it's not in her title"* is the kind of thing that takes a quarter to learn and one line to record.

### `/ramp glossary`

Acronyms, internal product names, system names, jargon. Maintain `Resources/Glossary.md`, alphabetized, and `bd remember` the ones that come up constantly.

Every company has fifty of these and assumes they're universal. Write down the ones you had to ask about — that list is worth more than you think, and it expires as your memory of being confused does.

### `/ramp systems`

Tools, dashboards, repos, data sources. What lives where, what's authoritative, what's deprecated but still running.

Capture **where the real data lives** and its caveats. "The exec dashboard pulls from a stale replica" is the kind of thing you learn by being wrong in a meeting.

## Prompts That Work

Ask these when the user doesn't know where to start:

- What did you have to ask someone about this week?
- What surprised you about how things work here?
- Who did you get pointed to, and for what?
- What acronym did you nod along to without knowing?
- What did you assume that turned out wrong?

That last one is the highest-yield question in the set.

## Rules

**Don't build a wiki.** You're capturing what *this person* needs, not documenting the company. If it's already in an internal doc, record the pointer, not the content.

**Prefer memories over notes** for anything under a sentence.

**Names and specifics.** "Someone on the data team" is worthless in three months.

**Capture confusion, not just conclusions.** *"Took me two weeks to understand why X and Y are separate services"* helps the next person and reminds you what's non-obvious.

**Don't over-structure early.** Weeks one through four are for volume. Organize in month two, when you know which parts mattered.

## Report

```
🧠 4 memories: priya-renewals, deploy-freeze, arr-table, sso-owner
📝 People/Priya Rao.md created
📝 Resources/Glossary.md — 6 terms added
✅ 1 follow-up → cab-51 (ask Marcus about the billing split)
```

## Winding Down

Around month three, when sessions turn up little new, say so once:

> *"Not much new lately — you may be past the ramp. Worth a `/thread org` to see how your understanding shifted; it's usually a good read."*

## If `bd` Isn't Installed

Facts go into `Resources/Glossary.md` and `Areas/Org.md`. Note once that `bd remember` is what makes this stick, since the auto-injection is most of the value during ramp.

## Begin

Ask what they've learned, or take the mode they specified.
