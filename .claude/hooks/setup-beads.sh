#!/usr/bin/env bash
# SessionStart hook: make `bd` (beads) available and load the vault's issue database.
#
# Idempotent. On a local machine where bd is already installed it only runs a
# quick init-if-missing. On an ephemeral remote container (Claude Code on the
# web / mobile) it builds bd from source, which takes a few minutes the first
# time in each container.
#
# The tracked file .beads/issues.jsonl is the durable state. The Dolt database
# this creates is a gitignored cache. After writing beads in a remote session,
# run /sync-todos (which exports back to issues.jsonl) before pushing.

set -u
cd "$(dirname "$0")/../.." || exit 0

BD_VERSION="${BD_VERSION:-latest}"
PREFIX="${BEADS_PREFIX:-cab}"

say() { printf '[setup-beads] %s\n' "$*"; }

install_bd() {
  if ! command -v go >/dev/null 2>&1; then
    say "bd not installed and no Go toolchain; skipping (brew install beads on a local machine)"
    return 1
  fi
  # Beads embeds Dolt, whose regex engine needs ICU headers to compile.
  if [ ! -f /usr/include/unicode/uregex.h ] && command -v apt-get >/dev/null 2>&1; then
    say "installing libicu-dev"
    if ! apt-get install -y -q libicu-dev >/dev/null 2>&1; then
      apt-get update -q >/dev/null 2>&1
      apt-get install -y -q libicu-dev >/dev/null 2>&1 || say "libicu-dev install failed; build may fail"
    fi
  fi
  local bin="${HOME}/.local/bin"
  mkdir -p "$bin"
  say "building bd@${BD_VERSION} from source (a few minutes on first run in this container)"
  if GOBIN="$bin" GOTOOLCHAIN=auto go install "github.com/steveyegge/beads/cmd/bd@${BD_VERSION}" >"${TMPDIR:-/tmp}/setup-beads-build.log" 2>&1; then
    export PATH="$bin:$PATH"
    say "built $(bd --version 2>/dev/null | head -1)"
  else
    say "build failed; see ${TMPDIR:-/tmp}/setup-beads-build.log"
    return 1
  fi
}

# A previous session in this container may have built it already.
if ! command -v bd >/dev/null 2>&1 && [ -x "${HOME}/.local/bin/bd" ]; then
  export PATH="${HOME}/.local/bin:$PATH"
fi
command -v bd >/dev/null 2>&1 || install_bd || exit 0

# bd has no --init-if-missing, and the on-disk layout of the store is not a
# stable thing to test: it has been .beads/embeddeddolt and .beads/dolt across
# versions, and in shared-server mode it isn't under .beads at all. So ask bd
# whether it can open the store rather than guessing at paths.
#
# Seed via --from-jsonl in the same call: a separate `bd import` against a
# just-created database fails with "database name must not be empty", because
# the store isn't configured until init returns.
if bd list -n 1 >/dev/null 2>&1; then
  :   # already initialized; the summary below reports it
else
  seed=""
  [ -f .beads/issues.jsonl ] && seed="--from-jsonl"
  if bd init --prefix "$PREFIX" --skip-agents --skip-hooks --non-interactive $seed -q >/dev/null 2>&1; then
    say "initialized ${PREFIX} store${seed:+ from .beads/issues.jsonl}"
  else
    say "bd init failed; run 'bd doctor' (continuing without beads)"
    exit 0
  fi
fi

say "$(bd ready 2>/dev/null | grep -c '^[○◐]') issue(s) claimable; run 'bd ready'. Export with /sync-todos before pushing."
exit 0
