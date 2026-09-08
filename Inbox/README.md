# Inbox

Quick captures awaiting routing.

Fed by `/capture`. Drained by `/process-inbox`, which `/daily-note` runs a light
pass of automatically — so most days this empties itself.

`unclear/` holds what couldn't be routed confidently. 14-day SLA, surfaced by
`/brief`, forced to a decision in `/weekly-review`.
