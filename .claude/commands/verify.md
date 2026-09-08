# /verify — Re-check What the Web Told You

Refetch the URLs a note's claims rest on and flag the ones the page no longer supports. Implements [[Projects/Memoryfield Improvements Spec]] §6.

Usage: `/verify <path>` · `/verify --stale 60` · `/verify` (vault-wide, entries older than 60 days)

Notes carry their sources in frontmatter:

```yaml
sources:
  - url: https://example.com/pricing-page
    fetched: '2026-08-14'
    claim: "Enterprise tier starts at $40/seat"
```

`/save-to-brain` writes these when it saves anything derived from a fetched page. The `claim` is optional but it's what makes verification meaningful: without it you can only confirm the page still exists.

## Step 1: List What's Due

```bash
python3 .claude/scripts/verify_sources.py list [PATH] [--stale N]
```

For a single note every entry is listed. Vault-wide, only entries fetched more than N days ago (default 60). Domains under `retrieval.verify.skip_domains` in `CLAUDE.md` are never fetched; the run stops at `max_fetches` (default 30) and says how many remain.

## Step 2: Fetch and Judge, One Entry at a Time

```bash
python3 .claude/scripts/verify_sources.py fetch URL --grep <two or three key terms from the claim>
```

Read the excerpts. Answer one question per entry, and only that question:

> *Does the fetched page still support this claim? Quote the supporting or contradicting passage.*

Three outcomes:

- **Supported** — you found a passage that says it. Quote it.
- **Contradicted** — the page now says something incompatible. Quote that.
- **Can't tell** — the page fetched but the excerpts don't settle it, or it didn't fetch at all. Say so. **Do not guess.** An unverifiable claim stays as it was, with a note in the report.

In `parallel` mode, dispatch one `note-reader`-style reader per entry with the page text and the claim; it returns a verdict plus a verbatim quote, never a rewrite of the note.

## Step 3: Mark the Entry

```bash
python3 .claude/scripts/verify_sources.py mark PATH URL --ok        # supported: bumps fetched
python3 .claude/scripts/verify_sources.py mark PATH URL --failed    # contradicted: bumps fetched, adds "⚠ verify failed <date>"
```

Leave "can't tell" entries unmarked so they come up again next run.

**On a contradiction, also file a bead** — the same label §3 contradiction detection uses, so one query finds both kinds:

```bash
bd create "Possible contradiction: <note title> vs <domain>" -l contradiction -p 2 \
  -d "Claim in [[<note path>]]: \"<claim>\"\nPage now says: \"<quoted passage>\"\nURL: <url>\nChecked: <date>"
```

Never edit the note's body. The human decides whether the note was wrong, the page changed, or both.

## Step 4: Report

```
🔍 Verified 6 sources across 4 notes
  ✓ 4 supported
  ⚠ 1 contradicted → cab-91 (Resources/Competitor Pricing.md — the $40/seat claim)
  ? 1 unverifiable (paywalled) — left for next run
  3 more entries over the 30-fetch cap; run again to continue
```

Then `/sync-todos` if any beads were created.

## Rules

- **≤ 30 fetches per run.** The script enforces it; don't work around it by calling `fetch` directly on a list you assembled by hand.
- **Skip domains are skipped silently.** They're in `CLAUDE.md` because the user put them there.
- **Quotes, not paraphrase.** The bead description carries the page's own words so the reader can check you.
- **A failed fetch is not a failed claim.** Timeouts, 404s, and login walls are "can't tell."

## Acceptance

Add a `sources` entry whose `claim` is deliberately wrong, run `/verify <path>`; it should come back contradicted, marked, with a bead filed.

## Begin

List what's due, then work through it.
