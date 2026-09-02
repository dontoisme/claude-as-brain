# /link-check — Find Structural Rot

Check the vault for broken wikilinks, orphans, and malformed notes.

Obsidian showed you unresolved links for free. Without it, link rot is completely silent — a typo'd wikilink looks identical to a working one until the day you need the note.

## Step 1: Audit

**`retrieval_mode: inline`** — walk the vault yourself.

**`retrieval_mode: parallel`** — dispatch one `vault-auditor` per top-level folder concurrently. This is mechanical work that parallelizes cleanly, and it's the command where fan-out pays off most on a large vault.

Check for:

- **Broken wikilinks** — `[[Target]]` with no matching file
- **Orphans** — notes with no inbound links
- **Missing frontmatter** — no YAML, or no `date` / `tags`
- **Naming violations** — `Days/` not `YYYYMMDD.md`, `Meetings/` not `YYYYMMDD - Name.md`, generic names
- **Literal `{{date:...}}` in notes** — a real bug; something wrote a template without substituting
- **Empty notes**
- **Dangling `distilled_to`** — an event note claims its content was extracted to a note or bead that doesn't exist. `python3 .claude/scripts/brain_index.py distilled-check` lists them; a note with a dangling target must not be allowed to decay as if it were banked.

## Step 2: Sort by What's Actually Wrong

Not all findings are problems. Rank honestly:

**Broken links — always worth fixing.** Distinguish two kinds:
- *Typo* — a near-match exists. Offer the fix; usually a one-character change.
- *Missing* — no match. Either the note was never written (the link was a promise) or it was deleted. Ask which.

**Literal template syntax — always a bug.** Fix immediately.

**Dangling `distilled_to` — always worth fixing.** Either the target was renamed (fix the link) or the extraction never happened (remove the key so the note shows up in `/weekly-review` again). Ask which.

**Missing frontmatter — usually worth fixing.** Cheap, and it's what tags and dates depend on.

**Orphans — judgment.** A reference note nobody links to is fine. A meeting note with no inbound links means it never got connected to an Area or a daily note, and it's effectively lost. **Report orphans by folder**, since `Resources/` orphans are normal and `Meetings/` orphans are not.

**Naming — low priority** unless it breaks date sorting in `Days/` or `Meetings/`, which it usually does.

## Step 3: Report

```markdown
## Link Check — 47 notes

### Broken links (3)

**Likely typos — fix these:**
- `Areas/Pricing.md:34` → `[[Meetings/20250312 - Pricing Reveiw]]`
  → did you mean `Pricing Review`?

**Missing notes (2)** — never written, or deleted?
- `Days/20250402.md:12` → `[[Projects/Q3 Pricing]]`
- `MOCs/Pricing MOC.md:8` → `[[Areas/Contract Terms]]`

### Orphans (4)
- `Meetings/20250228 - Vendor Sync.md` ← worth linking; meeting notes shouldn't float
- 3 in `Resources/` — normal, no action

### Bugs (1)
- `Areas/Onboarding.md:3` — literal `{{date:YYYY-MM-DD}}` in frontmatter

### Missing frontmatter (2)
- `Resources/Scratch.md`, `Areas/Vendor Management.md`
```

## Step 4: Offer to Fix

Batch the offer, don't ask file by file:

> *"Want me to fix the 1 typo and the template-syntax bug? The 2 missing notes need your call — write them, or remove the links?"*

**Fix without asking:** literal template syntax, and unambiguous typos where exactly one near-match exists.

**Ask first:** anything requiring a decision — creating a missing note, deleting a link, renaming a file.

**Never bulk-delete links.** A link to a note that doesn't exist yet is often intentional — it marks something worth writing. That's a feature of wikilink systems, not an error.

## Clean Result

Say so in one line and stop. `✅ 47 notes, no issues.` Don't manufacture findings to justify the run.

## Runs Inside

`/weekly-review` calls this. Also worth running after bulk edits or a rename.

## Begin

Audit the vault and report.
