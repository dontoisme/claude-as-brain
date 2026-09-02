# Templates

Note templates. These use Obsidian Templater syntax (`{{date:YYYY-MM-DD}}`).

Claude substitutes those values when creating notes. If Obsidian is installed later, Templater fills them natively — no edits needed.

## Provenance

Every template carries `source:`. Values: `human` (restates what the user said or wrote), `inferred` (Claude concluded it), `external` (derived from a fetched page or pasted material), `mixed` (both). Notes derived from the web also carry a `sources:` list (`url`, `fetched`, optional `claim`) that `/verify` re-checks. In a `mixed` note, any paragraph Claude wrote that is not a restatement ends with `^inferred`.
