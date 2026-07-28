# /update-mocs — Keep Maps of Content Current

Refresh `MOCs/` against what's actually in the vault.

MOCs are the topic-level navigation layer — the only way to browse by subject rather than by folder. They're also the strongest ranking signal `/ask` has, because a MOC is a human saying *"these notes belong together."*

The reason MOCs die in most systems is manual upkeep. This command removes that tax while keeping the part that matters: the curation.

## Step 1: Inventory

Read every file in `MOCs/`. For each, note the topic and the notes it links to.

Then read the vault: `Areas/`, `Projects/`, `Resources/`, `Meetings/`, and notes created since the MOC's `updated:` frontmatter date.

## Step 2: Reconcile

For each MOC:

**Add** — new notes that clearly belong. Match on topic overlap, shared tags, and existing wikilinks. When adding, write the one-line description; a bare link is nearly useless.

**Remove** — links to notes that no longer exist. Report these; don't silently drop them, since a missing note may be a rename you should follow instead.

**Re-sort** — is "Start Here" still the right two or three notes? A MOC whose entry points are eighteen months old is failing at its main job.

**Refresh `updated:`** in frontmatter.

## Step 3: Propose New MOCs

Look for clusters with no map: four or more notes sharing a topic, tag, or dense mutual linking, with no MOC covering them.

**Propose, don't create.** A MOC needs a through-line, and the through-line is human judgment:

> *"Six notes have accumulated around vendor evaluation — Areas/Procurement, three meeting notes, two resources. Want a MOC? If so, what's the through-line?"*

Creating one with an auto-generated summary produces exactly the hollow hub note that makes people abandon MOCs.

## Step 4: Flag Decay

Report, don't fix:

- **MOC not updated in 90+ days** while its topic notes have grown
- **MOC with fewer than 3 links** — probably should be a note, not a map
- **MOC with 30+ links** — probably should be split
- **Orphan notes** — no MOC, no inbound links. Not always a problem, but a pile of them means retrieval is degrading.

## What Never Changes

**Don't touch the through-line.** The "what connects these notes" line is the user's, always. You may add links beneath it; you may not rewrite the thesis.

**Don't restructure sections.** If they've organized a MOC their own way, add within it.

**Don't add speculative links.** A note that's *maybe* related makes the map worse. When unsure, leave it out and mention it.

## Report

```
✅ MOCs/Pricing MOC.md — added 3, removed 1 broken link
✅ MOCs/Onboarding MOC.md — no changes

⚠️  MOCs/Vendor MOC.md — 104 days stale, 6 new notes on the topic
💡 Possible new MOC: 5 notes on hiring with no map. Through-line?
🔗 1 broken link removed: [[Areas/Old Pricing]] — renamed, or deleted?
```

## Runs Inside

`/weekly-review` calls this. Also fine standalone after a burst of note-writing.

## Begin

Inventory the MOCs and reconcile them against the vault.
