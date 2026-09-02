#!/usr/bin/env python3
"""Expiry bookkeeping for beads memories (Memoryfield Improvements Spec §4).

`bd remember` entries are permanent and auto-injected into every session, and
bd (1.2.2) has no metadata fields on memories. So the confirmed date and
time-to-live live in a committed sidecar, .beads/memory-meta.jsonl, keyed by
memory key. That file is the source of truth for expiry and MUST be tracked in
git (the .gitignore carries an exception for it).

    python3 .claude/scripts/memory_meta.py confirm KEY [--ttl DAYS] [--kind person] [--permanent]
    python3 .claude/scripts/memory_meta.py due [--limit 5] [--json]
    python3 .claude/scripts/memory_meta.py retire KEY [--keep-memory]
    python3 .claude/scripts/memory_meta.py list

Defaults: ttl 90 days; --kind person → 60; --permanent never surfaces.
No decay is applied to injection: a memory stays in every session until it is
explicitly retired. `due` only lists what to confirm.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

META_REL = Path(".beads") / "memory-meta.jsonl"
ISSUES_REL = Path(".beads") / "issues.jsonl"
DEFAULT_TTL = {"fact": 90, "person": 60}


def today_of(args) -> dt.date:
    return dt.date.fromisoformat(args.today) if getattr(args, "today", None) else dt.date.today()


def load_meta(vault: Path) -> dict[str, dict]:
    path = vault / META_REL
    out: dict[str, dict] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("key"):
            out[d["key"]] = d
    return out


def save_meta(vault: Path, meta: dict[str, dict]) -> None:
    path = vault / META_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(meta[k], ensure_ascii=False, sort_keys=True) for k in sorted(meta)]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def bd_memories(vault: Path) -> dict[str, str]:
    """key -> content. Live from bd when possible, else from the tracked export."""
    try:
        res = subprocess.run(["bd", "memories", "--json"], cwd=vault, capture_output=True, text=True, check=True, timeout=60)
        data = json.loads(res.stdout or "[]")
        items = data.get("memories", data) if isinstance(data, dict) else data
        out = {}
        for m in items or []:
            key = m.get("key") or m.get("id")
            if key:
                out[str(key)] = str(m.get("value") or m.get("content") or m.get("text") or "")
        if out:
            return out
    except Exception:  # noqa: BLE001 — bd missing, blocked, or non-JSON; fall through
        pass
    out = {}
    issues = vault / ISSUES_REL
    if issues.exists():
        for line in issues.read_text(encoding="utf-8").splitlines():
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("_type") == "memory" and d.get("key"):
                out[d["key"]] = str(d.get("value") or "")
    return out


def cmd_confirm(args) -> int:
    vault = Path(args.vault).resolve()
    meta = load_meta(vault)
    entry = meta.get(args.key, {"key": args.key})
    kind = args.kind or entry.get("kind") or "fact"
    entry["kind"] = kind
    entry["confirmed"] = today_of(args).isoformat()
    if args.ttl is not None:
        entry["ttl"] = args.ttl
    elif args.kind:
        entry["ttl"] = DEFAULT_TTL.get(kind, DEFAULT_TTL["fact"])  # a stated kind brings its default ttl
    else:
        entry.setdefault("ttl", DEFAULT_TTL.get(kind, DEFAULT_TTL["fact"]))
    if args.permanent:
        entry["permanent"] = True
    elif args.not_permanent:
        entry["permanent"] = False
    meta[args.key] = entry
    save_meta(vault, meta)
    p = " · permanent" if entry.get("permanent") else f" · ttl {entry['ttl']}d"
    print(f"✓ confirmed {args.key} on {entry['confirmed']} ({kind}{p})")
    return 0


def cmd_retire(args) -> int:
    vault = Path(args.vault).resolve()
    meta = load_meta(vault)
    forgot = ""
    if not args.keep_memory:
        try:
            subprocess.run(["bd", "forget", args.key], cwd=vault, capture_output=True, text=True, check=True, timeout=60)
            forgot = " · bd forget done"
        except Exception as e:  # noqa: BLE001
            forgot = f" · bd forget FAILED ({str(e).strip() or 'bd unavailable'}); run it by hand"
    meta.pop(args.key, None)
    save_meta(vault, meta)
    print(f"✓ retired {args.key}{forgot}")
    return 0


def cmd_due(args) -> int:
    vault = Path(args.vault).resolve()
    today = today_of(args)
    meta = load_meta(vault)
    memories = bd_memories(vault)
    seeded = 0
    for key in memories:
        if key not in meta:
            meta[key] = {"key": key, "kind": "fact", "confirmed": today.isoformat(), "ttl": DEFAULT_TTL["fact"]}
            seeded += 1
    if seeded and not args.dry_run:
        save_meta(vault, meta)
    due = []
    for key, m in meta.items():
        if m.get("permanent"):
            continue
        if memories and key not in memories:
            continue  # retired outside this tool; ignore
        confirmed = dt.date.fromisoformat(m.get("confirmed", today.isoformat()))
        ttl = int(m.get("ttl", DEFAULT_TTL.get(m.get("kind", "fact"), 90)))
        age = (today - confirmed).days
        if age > ttl:
            due.append({"key": key, "kind": m.get("kind", "fact"), "confirmed": confirmed.isoformat(),
                        "ttl": ttl, "overdue_days": age - ttl, "value": memories.get(key, "")})
    due.sort(key=lambda d: (d["confirmed"], d["key"]))
    total = len(due)
    due = due[: args.limit]
    if args.json:
        print(json.dumps({"due": due, "total_due": total, "seeded": seeded, "today": today.isoformat()}, indent=2, ensure_ascii=False))
        return 0
    if seeded:
        print(f"(started tracking {seeded} memor{'y' if seeded == 1 else 'ies'} as confirmed today)")
    if not due:
        print("no memories due for confirmation")
        return 0
    print(f"Memories to confirm ({total} due{', showing ' + str(len(due)) if total > len(due) else ''}, oldest first):")
    for d in due:
        print(f"  {d['key']}  — confirmed {d['confirmed']}, ttl {d['ttl']}d, {d['overdue_days']}d over")
        if d["value"]:
            print(f"      {d['value'][:140]}")
    print("  actions: confirm KEY · retire KEY · edit (bd remember \"new text\" --key KEY, then confirm KEY)")
    return 0


def cmd_list(args) -> int:
    vault = Path(args.vault).resolve()
    meta = load_meta(vault)
    if not meta:
        print("no memory metadata yet; `due` seeds it")
        return 0
    for k in sorted(meta):
        m = meta[k]
        flag = "permanent" if m.get("permanent") else f"ttl {m.get('ttl')}d"
        print(f"{k:32s} {m.get('kind','fact'):7s} confirmed {m.get('confirmed')}  {flag}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault", default=".")
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD), for testing")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("confirm", help="record that a memory was confirmed today")
    c.add_argument("key")
    c.add_argument("--ttl", type=int)
    c.add_argument("--kind", choices=["fact", "person"])
    c.add_argument("--permanent", action="store_true")
    c.add_argument("--not-permanent", action="store_true")
    c.set_defaults(func=cmd_confirm)
    d = sub.add_parser("due", help="memories past their ttl, oldest first")
    d.add_argument("--limit", type=int, default=5)
    d.add_argument("--json", action="store_true")
    d.add_argument("--dry-run", action="store_true", help="don't write seeded entries")
    d.set_defaults(func=cmd_due)
    r = sub.add_parser("retire", help="bd forget the memory and drop its metadata")
    r.add_argument("key")
    r.add_argument("--keep-memory", action="store_true", help="drop metadata only")
    r.set_defaults(func=cmd_retire)
    l = sub.add_parser("list")
    l.set_defaults(func=cmd_list)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
