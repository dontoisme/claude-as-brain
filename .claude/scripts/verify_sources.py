#!/usr/bin/env python3
"""Citation bookkeeping for `sources:` frontmatter (Memoryfield Improvements Spec §6).

Notes may carry a list of the URLs their claims rest on:

    sources:
      - url: https://example.com/pricing-page
        fetched: '2026-08-14'
        claim: "Enterprise tier starts at $40/seat"

This script does the mechanical half of /verify. Judging whether a fetched
page still supports a claim is the reader's job (Claude, in the command);
this script only lists, fetches, and marks.

    python3 .claude/scripts/verify_sources.py list [PATH] [--stale N]        # what needs checking
    python3 .claude/scripts/verify_sources.py fetch URL [--grep TERM ...]     # page text, or excerpts around terms
    python3 .claude/scripts/verify_sources.py mark PATH URL --ok|--failed [--index N]   # update the entry

Config, in CLAUDE.md's `retrieval` YAML block:

    verify:
      skip_domains: []      # never fetch these
      max_fetches: 30       # per run
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

import yaml

FM_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?", re.S)
SKIP_DIRS = {".index", ".beads", ".claude", ".git", ".obsidian", "Templates", "node_modules"}
DEFAULT_STALE_DAYS = 60
DEFAULT_MAX_FETCHES = 30


# ----------------------------------------------------------------- helpers

def split_frontmatter(text: str) -> tuple[dict, str | None]:
    m = FM_RE.match(text)
    if not m:
        return {}, None
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}, m.group(1)
    return (data if isinstance(data, dict) else {}), m.group(1)


def load_config(vault: Path) -> dict:
    cfg = {"skip_domains": [], "max_fetches": DEFAULT_MAX_FETCHES}
    claude_md = vault / "CLAUDE.md"
    if not claude_md.exists():
        return cfg
    m = re.search(r"```yaml\n(retrieval:\n.*?)```", claude_md.read_text(encoding="utf-8"), re.S)
    if not m:
        return cfg
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return cfg
    v = data.get("verify") or {}
    cfg["skip_domains"] = [str(d).lower().lstrip(".") for d in (v.get("skip_domains") or [])]
    if isinstance(v.get("max_fetches"), int) and v["max_fetches"] > 0:
        cfg["max_fetches"] = v["max_fetches"]
    return cfg


def walk(vault: Path):
    for p in sorted(vault.rglob("*.md")):
        rel = p.relative_to(vault)
        if any(part in SKIP_DIRS or part.startswith(".") for part in rel.parts[:-1]):
            continue
        yield p, str(rel).replace("\\", "/")


def as_date(v) -> dt.date | None:
    if v is None or v == "":
        return None
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    m = re.match(r"(\d{4}-\d{2}-\d{2})", str(v))
    return dt.date.fromisoformat(m.group(1)) if m else None


def domain_of(url: str) -> str:
    return (urllib.parse.urlsplit(url).hostname or "").lower()


def skipped(url: str, skip_domains: list[str]) -> bool:
    d = domain_of(url)
    return any(d == s or d.endswith("." + s) for s in skip_domains)


def replace_fm_key(text: str, key: str, value) -> str:
    """Rewrite one top-level frontmatter key in place, leaving the rest untouched."""
    m = FM_RE.match(text)
    if not m:
        raise ValueError("note has no frontmatter")
    raw = m.group(1)
    lines = raw.split("\n")
    start = end = None
    for i, line in enumerate(lines):
        if start is None and re.match(rf"^{re.escape(key)}\s*:", line):
            start = i
            continue
        if start is not None and re.match(r"^[A-Za-z0-9_\-]+\s*:", line) and not line.startswith(" "):
            end = i
            break
    dumped = yaml.safe_dump({key: value}, sort_keys=False, allow_unicode=True, default_flow_style=False, width=1000).rstrip("\n")
    if start is None:
        new_raw = raw.rstrip("\n") + "\n" + dumped
    else:
        end = len(lines) if end is None else end
        new_raw = "\n".join(lines[:start] + dumped.split("\n") + lines[end:])
    return text[: m.start(1)] + new_raw + text[m.end(1):]


# ---------------------------------------------------------------- commands

def collect(vault: Path, only: str | None):
    for p, rel in walk(vault):
        if only and rel != only and str(p) != only:
            continue
        fm, _ = split_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
        srcs = fm.get("sources")
        if not isinstance(srcs, list):
            continue
        for i, s in enumerate(srcs):
            if isinstance(s, str):
                s = {"url": s}
            if not isinstance(s, dict) or not s.get("url"):
                continue
            yield rel, i, s


def cmd_list(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    cfg = load_config(vault)
    today = dt.date.today()
    stale_days = args.stale if args.stale is not None else (None if args.path else DEFAULT_STALE_DAYS)
    out, skipped_n = [], 0
    for rel, i, s in collect(vault, args.path):
        url = str(s["url"])
        if skipped(url, cfg["skip_domains"]):
            skipped_n += 1
            continue
        fetched = as_date(s.get("fetched"))
        age = (today - fetched).days if fetched else None
        if stale_days is not None and age is not None and age < stale_days:
            continue
        out.append({"path": rel, "index": i, "url": url, "fetched": fetched.isoformat() if fetched else None,
                    "age_days": age, "claim": s.get("claim"), "status": s.get("status")})
    out.sort(key=lambda e: (e["age_days"] is None, -(e["age_days"] or 0)))
    capped = out[: cfg["max_fetches"]]
    if args.json:
        print(json.dumps({"entries": capped, "over_cap": max(0, len(out) - len(capped)), "skipped_domains": skipped_n}, indent=2))
        return 0
    if not out:
        print("nothing to verify" + (f" ({skipped_n} skipped by skip_domains)" if skipped_n else ""))
        return 0
    for e in capped:
        age = "never fetched" if e["age_days"] is None else f"{e['age_days']}d ago"
        print(f"{e['path']}  [{e['index']}]  {e['url']}  ({age})")
        if e["claim"]:
            print(f"    claim: {e['claim']}")
        if e["status"]:
            print(f"    status: {e['status']}")
    extra = len(out) - len(capped)
    if extra:
        print(f"… {extra} more over the {cfg['max_fetches']}-fetch cap; run again after this batch")
    if skipped_n:
        print(f"({skipped_n} entries skipped by verify.skip_domains)")
    return 0


def fetch_text(url: str, timeout: int = 30) -> str:
    try:
        res = subprocess.run(["curl", "-sSL", "-m", str(timeout), "-A", "claude-as-brain/verify", url],
                             capture_output=True, text=True, check=True, errors="replace")
        raw = res.stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        import urllib.request
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "claude-as-brain/verify"}), timeout=timeout) as r:
            raw = r.read().decode("utf-8", errors="replace")
    if "<" in raw and re.search(r"<(html|body|div|p|h1)\b", raw, re.I):
        raw = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", raw)
        raw = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</h\d>|</li>|</tr>", "\n", raw)
        raw = re.sub(r"(?s)<[^>]+>", " ", raw)
        raw = html.unescape(raw)
    raw = re.sub(r"[ \t\r\f\v]+", " ", raw)
    raw = re.sub(r"\n\s*\n+", "\n\n", raw)
    return raw.strip()


def cmd_fetch(args: argparse.Namespace) -> int:
    cfg = load_config(Path(args.vault).resolve())
    if skipped(args.url, cfg["skip_domains"]):
        print(f"refusing: {domain_of(args.url)} is in verify.skip_domains", file=sys.stderr)
        return 2
    try:
        text = fetch_text(args.url)
    except Exception as e:  # noqa: BLE001
        print(f"fetch failed: {e}", file=sys.stderr)
        return 1
    if not text:
        print("fetched, but the page has no readable text", file=sys.stderr)
        return 1
    if args.grep:
        low = text.lower()
        shown = 0
        for term in args.grep:
            for m in re.finditer(re.escape(term.lower()), low):
                a, b = max(0, m.start() - args.context), min(len(text), m.end() + args.context)
                print(f"--- {term} @ {m.start()} ---\n…{text[a:b]}…\n")
                shown += 1
                if shown >= args.max_excerpts:
                    return 0
        if shown == 0:
            print(f"no occurrences of {', '.join(args.grep)} in {len(text)} chars of page text; first {args.max_chars} chars follow\n")
            print(text[: args.max_chars])
        return 0
    print(text[: args.max_chars])
    if len(text) > args.max_chars:
        print(f"\n… truncated at {args.max_chars} of {len(text)} chars; use --grep TERM for excerpts", file=sys.stderr)
    return 0


def cmd_mark(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    path = (vault / args.path) if not Path(args.path).is_absolute() else Path(args.path)
    if not path.exists():
        print(f"no such note: {args.path}", file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")
    fm, _ = split_frontmatter(text)
    srcs = fm.get("sources")
    if not isinstance(srcs, list):
        print("note has no sources: list", file=sys.stderr)
        return 1
    today = args.date or dt.date.today().isoformat()
    matches = [i for i, s in enumerate(srcs) if str((s.get("url") if isinstance(s, dict) else s)) == args.url]
    if len(matches) > 1 and args.index is None:
        print(f"{len(matches)} entries share that URL (indexes {matches}); pass --index N to pick one", file=sys.stderr)
        return 1
    hit = False
    new_srcs = []
    for i, s in enumerate(srcs):
        if isinstance(s, str):
            s = {"url": s}
        s = dict(s) if isinstance(s, dict) else s
        if isinstance(s, dict) and str(s.get("url")) == args.url and (args.index is None or i == args.index):
            hit = True
            s["fetched"] = today
            if args.failed:
                s["status"] = f"⚠ verify failed {today}"
            elif "status" in s and str(s["status"]).startswith("⚠"):
                s.pop("status", None)
        new_srcs.append(s)
    if not hit:
        print(f"url not found in {args.path}: {args.url}", file=sys.stderr)
        return 1
    path.write_text(replace_fm_key(text, "sources", new_srcs), encoding="utf-8")
    print(f"{'⚠ marked failed' if args.failed else '✓ marked verified'}: {args.path} ← {args.url} ({today})")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)
    l = sub.add_parser("list", help="entries due for verification")
    l.add_argument("path", nargs="?", help="one note; otherwise the whole vault")
    l.add_argument("--stale", type=int, help=f"only entries fetched more than N days ago (default {DEFAULT_STALE_DAYS} for a vault-wide run, all entries for one note)")
    l.add_argument("--json", action="store_true")
    l.set_defaults(func=cmd_list)
    f = sub.add_parser("fetch", help="fetch a URL and print readable text")
    f.add_argument("url")
    f.add_argument("--grep", nargs="*", help="print excerpts around these terms instead of the whole page")
    f.add_argument("--context", type=int, default=300)
    f.add_argument("--max-excerpts", type=int, default=8)
    f.add_argument("--max-chars", type=int, default=6000)
    f.set_defaults(func=cmd_fetch)
    m = sub.add_parser("mark", help="update one sources entry after checking it")
    m.add_argument("path")
    m.add_argument("url")
    g = m.add_mutually_exclusive_group(required=True)
    g.add_argument("--ok", action="store_true")
    g.add_argument("--failed", action="store_true")
    m.add_argument("--date", help="override today's date (YYYY-MM-DD)")
    m.add_argument("--index", type=int, help="entry index from `list`, when several entries share a URL")
    m.set_defaults(func=cmd_mark)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
