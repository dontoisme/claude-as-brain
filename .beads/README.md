# .beads/

## What's tracked here

Only `issues.jsonl` (and this file). The Dolt database itself is generated locally and gitignored.

`issues.jsonl` is beads' own git-tracked export format — `bd import` with no arguments reads exactly this path. It's plain text, so the seed content is readable, diffable, and reviewable directly in the repo. Nothing binary ships.

## The seed

This repo ships example issues **and example memories** in `issues.jsonl`. Lines tagged `"_type":"memory"` import as persistent memories, equivalent to running `bd remember`.

That matters because the memory layer is the least obvious part of this system. Shipping working examples means a new user can see auto-injected context happen on their first session instead of reading a description of it.

## Unpacking

`/install` does this for you. Manually:

```bash
bd init --prefix cab     # create .beads/ and the local database
bd import                # unpack issues.jsonl
bd setup claude          # wire up Claude Code integration
bd hooks install         # auto-inject `bd prime` at session start
```

## Clearing the examples

`/install` offers this. To do it by hand, close or delete the seeded issues and run `bd forget <key>` for each example memory. `bd memories` lists what's stored.

## For a private or work vault

```bash
bd init --stealth
```

Configures `.git/info/exclude` so beads artifacts are never committed — useful when you want the tracked repo to stay pure markdown.
