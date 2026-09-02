# Templates

Note templates. These use Obsidian Templater syntax (`{{date:YYYY-MM-DD}}`).

Claude substitutes those values when creating notes. If Obsidian is installed later, Templater fills them natively — no edits needed.

## Provenance

Every template carries `source:`. Values: `human` (restates what the user said or wrote), `inferred` (Claude concluded it), `external` (derived from a fetched page or pasted material), `mixed` (both). Notes derived from the web also carry a `sources:` list (`url`, `fetched`, optional `claim`) that `/verify` re-checks. In a `mixed` note, any paragraph Claude wrote that is not a restatement ends with `^inferred`.

## Retrieval keys

- `summary:` — one line, used for embedding and display. Fill it when the title alone wouldn't tell a reader what the note is for.
- `type:` — optional override of the folder-inferred note type (`day`, `meeting`, `project`, `area`, `resource`, `person`, `moc`, `inbox`). Rarely needed.
- `distilled_to:` / `distilled_on:` — set by `/weekly-review` on event-shaped notes (Days, Meetings) once their durable content has been extracted: a list of `[[wikilinks]]` and `bd:<id>` references, and the date. A note with `distilled_to` may decay freely; its diamonds are already in the bank.

None of these are required on existing notes. The index tolerates their absence.
