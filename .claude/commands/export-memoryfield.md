# /export-memoryfield — Package Notes in the Open Memoryfield Format

Export part of the vault as a `.memoryfield.zip` that any memoryfield-aware tool can read. Implements [[Projects/Memoryfield Improvements Spec]] §7 against Cal Paterson's format (a flat directory of Markdown pages with YAML frontmatter, optionally zipped).

Markdown stays the source of truth. This command only maps frontmatter and packages files; the one thing it writes into the vault is a `uuid` for any note that lacks one, so the same note keeps the same identity across exports.

## Usage

```
/export-memoryfield                              # Resources/ and Areas/
/export-memoryfield Resources Projects           # specific folders
/export-memoryfield --out pricing.memoryfield.zip
```

## Step 1: Run the Exporter

```bash
python3 .claude/scripts/memoryfield.py export [FOLDER ...] [--out NAME.memoryfield.zip]
```

Default folders are `Resources/` and `Areas/`. Folder `README.md` files are navigation, not knowledge, and are skipped.

What it does, per note:

- **Frontmatter mapping** — `title` (from `title:` or the filename), `created`, `updated`, `summary`, `uuid`. Dates come from frontmatter first, then git committer dates, then mtime. A missing `uuid` is generated and **written back into the source note**. Nothing else in the note changes.
- **Splitting** — a note over 8 KB is split at `##` headings into `<title> (1 of N)` pages, each with a fresh uuid and an `x-cab.parent_uuid` pointing at the original. The split is export-only.
- **Vault-specific keys** — `source`, `confidence`, `distilled_to`, `distilled_on`, and the vault-relative path move under an `x-cab` mapping rather than being dropped. The spec allows extra keys; a re-import can use them to find its way home.
- **`index.md` and `listing.md`** — a short introduction (no catalogue, per the spec) and a page catalogue.
- **Vector index, when there is a local embedder.** If `ollama` serves `nomic-embed-text`, the zip also carries `<model>.sqlite3` in the spec's suggested schema, with each page embedded *as exported* (the spec requires the complete page file, frontmatter included, as the embedding input). Without an embedder the index is omitted; the spec makes it optional.

The output zip lands in the vault root by default and is gitignored (`*.memoryfield.zip`).

## Step 2: Report

Relay the script's report verbatim — page count, splits, uuids written back, path, and **the sha256**. The recipient needs the hash to verify the archive on import; put it where they will see it.

If uuids were written back, say which notes changed so a `git diff` doesn't surprise the user.

## Rules

- **Never edit note bodies.** Only `uuid` is ever written into a source note.
- **Wikilinks are exported as-is.** They may not resolve in the recipient's tool. Say so once if the user asks about portability.
- **Don't export `Days/` or `Meetings/` by default.** They are event-shaped and full of names; the user names them explicitly if they want them.

## Begin

Run the exporter with the user's folders, then report.
