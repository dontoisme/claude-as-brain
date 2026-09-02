# /reindex — Rebuild the Retrieval Index

Build or refresh `.index/brain.sqlite3`, the deletable accelerator behind recency-aware retrieval. Implements [[Projects/Temporal Retrieval Spec]] Part 1.

The index is gitignored and rebuildable from scratch at any time. Deleting it costs nothing but this command's runtime. If it is missing, `/ask` falls back to grep-only retrieval and says so once.

## Run

```bash
python3 .claude/scripts/brain_index.py reindex
```

Incremental: it walks the vault, hashes each note body, and only rewrites rows whose content changed. Rows for deleted notes are removed. Retrieval history (`retrievals` table, `ref_count`, `last_referenced`) survives a reindex — that data is not derivable from the files and must not be reset here.

What each row records:

- **`note_type`** — inferred from the top folder (`Days/` → day, `Meetings/` → meeting, `Projects/` → project, `Areas/` → area, `Resources/` → resource, `People/` → person, `MOCs/` → moc, `Inbox/` → inbox, else other). Frontmatter `type:` overrides it when the value is one of those names; any other `type:` (e.g. `spec`) is left to the folder.
- **`created` / `updated`** — frontmatter `created`/`date` and `updated` first, then git committer dates, then mtime. Git matters: in a fresh clone every mtime is "now", which would make recency scoring meaningless.
- **`summary`, `title`, `status`, `tags`, `word_count`** — read from frontmatter for scoring and display.
- **`embedding`** — always null in Phase A. When Temporal Phase D lands and `ollama` + `nomic-embed-text` are detected, this is where vectors go.

Skipped: `Templates/`, folder `README.md` files, the generated `Todos.md` and `Dashboard.md`, and dot-directories.

## Report

Relay the script's one line:

```
reindexed 23 notes: 2 added, 5 updated, 1 removed, 0 truncated, 15 unchanged · embeddings off · .index/brain.sqlite3
```

If embeddings are off, do not apologise for it or suggest installing ollama unless the user asks — Phase D is tracked (`cab-659`).

## When to Run

- At the end of `/weekly-review` (the spec's Part 7).
- After `/import-memoryfield`.
- Whenever `/ask` reports the index is missing.
- Any time the user asks. It's cheap.

## Never

- **Never bump retrieval counts from here.** A reindex is a mechanical pass, not evidence that anything was relevant.
- **Never commit `.index/`.** It's in `.gitignore`; keep it there.

## Begin

Run the reindex and relay the report.
