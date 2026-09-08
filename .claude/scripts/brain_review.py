#!/usr/bin/env python3
"""Review-time analysis over the vault: promotion proposals and contradiction candidates.

Memoryfield Improvements Spec §5 (auto-promotion between layers) and §3
(contradiction detection). Both PROPOSE. Nothing here writes a note, a bead,
or a memory; the human accepts each item in /weekly-review or /save-to-brain.

    python3 .claude/scripts/brain_review.py promote [--text "sentence"] [--json]
    python3 .claude/scripts/brain_review.py neighbors [--since 7] [--k 5] [--cap 20] [--json]

Reads the retrieval index (.index/brain.sqlite3) for note metadata and
retrieval counts, the tracked beads export (.beads/issues.jsonl, or `bd` when
it answers) for memories and open issues, and the notes themselves.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brain_index import (  # noqa: E402
    Embedder, WIKILINK_RE, cosine, iso, now_utc, open_index, parse_ts, resolve_link, split_frontmatter, unpack,
)

FUZZY = 0.85
MIN_NOTES = 3
SENT_MIN, SENT_MAX = 40, 300
RESOURCE_CITES = 5
RESOURCE_WINDOW_DAYS = 30
INBOX_MAX_AGE = 14
STATE_TYPES = ("area", "resource", "person", "moc")
GENERIC = set("""the a an and or of to in on for with is are was were be been this that it its as by at from we our you
your they their not no yes have has had do does did will would can could should may might""".split())


# ------------------------------------------------------------------ inputs

def load_beads(vault: Path) -> tuple[list[dict], dict[str, str]]:
    """(issues, memories) — live from bd when it answers, else the tracked export."""
    issues: list[dict] = []
    memories: dict[str, str] = {}
    try:
        res = subprocess.run(["bd", "list", "--status", "open,in_progress,blocked", "--json"], cwd=vault,
                             capture_output=True, text=True, check=True, timeout=60)
        data = json.loads(res.stdout or "[]")
        issues = data if isinstance(data, list) else data.get("issues", [])
    except Exception:  # noqa: BLE001
        issues = []
    path = vault / ".beads" / "issues.jsonl"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("_type") == "memory" and d.get("key"):
                memories[d["key"]] = str(d.get("value") or "")
            elif not issues and d.get("id") and d.get("status") in ("open", "in_progress", "blocked"):
                issues.append(d)
    return issues, memories


def all_beads(vault: Path) -> list[dict]:
    out: list[dict] = []
    try:
        res = subprocess.run(["bd", "list", "--status", "all", "--json"], cwd=vault, capture_output=True, text=True, check=True, timeout=60)
        data = json.loads(res.stdout or "[]")
        out = data if isinstance(data, list) else data.get("issues", [])
    except Exception:  # noqa: BLE001
        out = []
    if out:
        return out
    path = vault / ".beads" / "issues.jsonl"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("id"):
                out.append(d)
    return out


def note_bodies(vault: Path, conn) -> dict[str, str]:
    """Bodies of knowledge notes. Root docs and other `other`-typed files are system, not knowledge."""
    out = {}
    for r in conn.execute("SELECT path FROM notes WHERE note_type != 'other'"):
        p = vault / r["path"]
        if p.exists():
            _, body = split_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
            out[r["path"]] = body
    return out


# ---------------------------------------------------------------- sentences

def sentences(body: str):
    text = re.sub(r"```.*?```", " ", body, flags=re.S)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", r"\1", text)
    text = re.sub(r"^\s*(#+|[-*>]|\d+\.)\s*", "", text, flags=re.M)
    text = re.sub(r"[*_`]", "", text)
    for chunk in re.split(r"(?<=[.!?])\s+|\n+", text):
        s = chunk.strip()
        if SENT_MIN <= len(s) <= SENT_MAX and not s.startswith("|"):
            yield s


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()


def tokens(s: str) -> set[str]:
    return {t for t in norm(s).split() if len(t) > 2 and t not in GENERIC}


class Union:
    def __init__(self):
        self.p: dict[int, int] = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def join(self, a, b):
        self.p[self.find(a)] = self.find(b)


def duplicate_groups(bodies: dict[str, str]):
    """Groups of near-identical sentences appearing in >= MIN_NOTES distinct notes."""
    sents: list[tuple[str, str, str]] = []  # (path, sentence, normalized)
    for path, body in bodies.items():
        seen = set()
        for s in sentences(body):
            n = norm(s)
            if n and n not in seen:
                seen.add(n)
                sents.append((path, s, n))
    by_tok: dict[str, list[int]] = defaultdict(list)
    for i, (_, _, n) in enumerate(sents):
        for t in tokens(n):
            by_tok[t].append(i)
    uf = Union()
    compared: set[tuple[int, int]] = set()
    for i, (path_i, _, n_i) in enumerate(sents):
        toks = tokens(n_i)
        counts: dict[int, int] = defaultdict(int)
        for t in toks:
            if len(by_tok[t]) > 200:
                continue  # too common to discriminate
            for j in by_tok[t]:
                if j > i and sents[j][0] != path_i:
                    counts[j] += 1
        for j, c in counts.items():
            if c < max(3, len(toks) // 2) or (i, j) in compared:
                continue
            compared.add((i, j))
            if n_i == sents[j][2] or difflib.SequenceMatcher(None, n_i, sents[j][2]).ratio() >= FUZZY:
                uf.join(i, j)
    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(len(sents)):
        if i in uf.p:
            groups[uf.find(i)].append(i)
    out = []
    for members in groups.values():
        paths = sorted({sents[i][0] for i in members})
        if len(paths) >= MIN_NOTES:
            out.append({"sentence": sents[members[0]][1], "notes": paths})
    return sorted(out, key=lambda g: -len(g["notes"]))


def text_matches(text: str, bodies: dict[str, str]):
    """Which notes already contain each sentence of `text` (fuzzy)."""
    results = []
    for s in sentences(text + " ") or [text.strip()]:
        n = norm(s)
        hits = []
        for path, body in bodies.items():
            for cand in sentences(body):
                if difflib.SequenceMatcher(None, n, norm(cand)).ratio() >= FUZZY:
                    hits.append(path)
                    break
        results.append({"sentence": s, "notes": sorted(hits), "proposal": "bd remember" if len(hits) >= MIN_NOTES else None})
    return results


# ---------------------------------------------------------------- promote

def subjects(memory_value: str) -> set[str]:
    caps = set(re.findall(r"\b[A-Z][a-zA-Z0-9_]{2,}\b", memory_value))
    idents = set(re.findall(r"\b[a-z0-9]+(?:_[a-z0-9]+)+\b", memory_value))
    return {s for s in caps | idents if s.lower() not in GENERIC and s not in ("The", "Any", "Remote", "Dolt", "Run")}


def cmd_promote(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    conn = open_index(vault)
    if conn is None:
        print("no index — run /reindex", file=sys.stderr)
        return 3
    bodies = note_bodies(vault, conn)
    proposals: list[dict] = []

    if args.text:
        for m in text_matches(args.text, bodies):
            if m["notes"]:
                proposals.append({"signal": "text-already-present", "sentence": m["sentence"], "notes": m["notes"],
                                  "proposal": m["proposal"] or f"already in {len(m['notes'])} note(s); not yet a memory (needs {MIN_NOTES})"})
    else:
        for g in duplicate_groups(bodies):
            proposals.append({"signal": "same-fact-3-notes", "sentence": g["sentence"], "notes": g["notes"],
                              "proposal": "bd remember — repeated in %d notes" % len(g["notes"])})

        issues, memories = load_beads(vault)
        for key, value in memories.items():
            subs = subjects(value)
            if not subs:
                continue
            for iss in issues:
                hay = f"{iss.get('title','')} {iss.get('description','')}"
                notes = iss.get("notes") or ""
                if f"memory: {key}" in notes:
                    continue
                hit = [s for s in subs if re.search(rf"\b{re.escape(s)}\b", hay)]
                if hit:
                    proposals.append({"signal": "memory-subject-in-open-bead", "memory": key, "bead": iss.get("id"),
                                      "bead_title": iss.get("title"), "matched": hit,
                                      "proposal": f"bd update {iss.get('id')} --append-notes \"see memory: {key}\""})

        cutoff = iso(now_utc() - dt.timedelta(days=RESOURCE_WINDOW_DAYS))
        for r in conn.execute("SELECT n.path, COUNT(*) AS c FROM retrievals r JOIN notes n ON n.path=r.path"
                              " WHERE n.note_type='resource' AND r.kind IN ('ask','thread','prep') AND r.ts >= ?"
                              " GROUP BY n.path HAVING c >= ?", (cutoff, RESOURCE_CITES)):
            proposals.append({"signal": "resource-cited-often", "note": r["path"], "cites_30d": r["c"],
                              "proposal": "add to the relevant MOC, or promote its one-line summary to a memory"})

        cutoff = now_utc() - dt.timedelta(days=INBOX_MAX_AGE)
        for r in conn.execute("SELECT path, updated FROM notes WHERE note_type='inbox'"):
            upd = parse_ts(r["updated"])
            if upd and upd < cutoff:
                proposals.append({"signal": "inbox-stale", "note": r["path"], "age_days": (now_utc() - upd).days,
                                  "proposal": "route: Area / Resource / bead / delete"})

    if args.json:
        print(json.dumps(proposals, indent=2, ensure_ascii=False))
        return 0
    if not proposals:
        print("no promotion proposals")
        return 0
    for p in proposals:
        if p["signal"] in ("same-fact-3-notes", "text-already-present"):
            print(f"[{p['signal']}] \"{p['sentence'][:110]}\"\n    in: {', '.join(p['notes'])}\n    → {p['proposal']}")
        elif p["signal"] == "memory-subject-in-open-bead":
            print(f"[{p['signal']}] memory {p['memory']} ↔ {p['bead']} \"{p['bead_title']}\" (matched {', '.join(p['matched'])})\n    → {p['proposal']}")
        elif p["signal"] == "resource-cited-often":
            print(f"[{p['signal']}] {p['note']} cited {p['cites_30d']}× in {RESOURCE_WINDOW_DAYS}d\n    → {p['proposal']}")
        else:
            print(f"[{p['signal']}] {p['note']} ({p['age_days']}d)\n    → {p['proposal']}")
    print(f"{len(proposals)} proposal(s). Nothing was changed; accept each one explicitly.")
    return 0


# --------------------------------------------------------------- neighbors

def links_of(body: str) -> set[str]:
    return {m.group(1).strip().lower().replace(".md", "") for m in WIKILINK_RE.finditer(body)}


def existing_contradiction_pairs(vault: Path) -> set[frozenset]:
    pairs: set[frozenset] = set()
    for iss in all_beads(vault):
        labels = [str(l).lower() for l in (iss.get("labels") or [])]
        if "contradiction" not in labels:
            continue
        text = f"{iss.get('title','')}\n{iss.get('description','')}\n{iss.get('notes','')}"
        found = {m.group(1).strip().lower().replace(".md", "") for m in WIKILINK_RE.finditer(text)}
        if len(found) >= 2:
            for a in found:
                for b in found:
                    if a < b:
                        pairs.add(frozenset((a, b)))
    return pairs


def cmd_neighbors(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    conn = open_index(vault)
    if conn is None:
        print("no index — run /reindex", file=sys.stderr)
        return 3
    notes = {r["path"]: dict(r) for r in conn.execute("SELECT path, note_type, updated, tags, embedding FROM notes WHERE note_type != 'other'")}
    bodies = note_bodies(vault, conn)
    cutoff = iso(now_utc() - dt.timedelta(days=args.since))
    recent = [p for p, n in notes.items() if n["updated"] >= cutoff]
    emb_on = (conn.execute("SELECT value FROM meta WHERE key='embeddings'").fetchone() or ["off"])[0] == "on"
    use_emb = emb_on and Embedder.detect() is not None and all(notes[p]["embedding"] for p in recent)
    done = existing_contradiction_pairs(vault)
    key = lambda p: p.lower().replace(".md", "")  # noqa: E731
    pairs: list[dict] = []
    seen: set[frozenset] = set()
    for p in recent:
        scored = []
        if use_emb:
            v = unpack(notes[p]["embedding"])
            for q, n in notes.items():
                if q == p or not n["embedding"]:
                    continue
                scored.append((cosine(v, unpack(n["embedding"])), q, "embedding"))
        else:
            lp, tp = links_of(bodies.get(p, "")), set(json.loads(notes[p]["tags"] or "[]"))
            for q, n in notes.items():
                if q == p:
                    continue
                lq, tq = links_of(bodies.get(q, "")), set(json.loads(n["tags"] or "[]"))
                shared = len(lp & lq) + (2 if key(q) in lp else 0) + (2 if key(p) in lq else 0)
                tag_overlap = len((tp & tq) - {"#example-seed"}) / max(len(tp | tq), 1)
                s = shared + tag_overlap
                if s > 0:
                    scored.append((s, q, f"{len(lp & lq)} shared links{', direct link' if key(q) in lp or key(p) in lq else ''}, tag overlap {tag_overlap:.2f}"))
        scored.sort(key=lambda x: -x[0])
        for s, q, why in scored[: args.k]:
            fs = frozenset((key(p), key(q)))
            if fs in seen or fs in done:
                continue
            seen.add(fs)
            newer, older = (p, q) if notes[p]["updated"] >= notes[q]["updated"] else (q, p)
            pairs.append({"newer": newer, "older": older, "score": round(s, 3), "why": why,
                          "older_state_shaped": notes[older]["note_type"] in STATE_TYPES})
    pairs.sort(key=lambda d: (not d["older_state_shaped"], -d["score"]))
    total = len(pairs)
    pairs = pairs[: args.cap]
    if args.json:
        print(json.dumps({"pairs": pairs, "total": total, "cap": args.cap, "mode": "embedding" if use_emb else "links+tags",
                          "excluded_existing": len(done)}, indent=2))
        return 0
    if not pairs:
        print(f"no neighbour pairs for notes updated in the last {args.since} days")
        return 0
    print(f"{len(pairs)} pair(s) of {total} ({'embedding' if use_emb else 'links+tags'} neighbours; {len(done)} pair(s) already have a contradiction bead)")
    for d in pairs:
        flag = " [older is state-shaped]" if d["older_state_shaped"] else ""
        print(f"newer: {d['newer']}\nolder: {d['older']}   score {d['score']} · {d['why']}{flag}\n")
    print("Ask, per pair: does the newer note contain a claim that conflicts with a claim in the older note? Quote both if so.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)
    pr = sub.add_parser("promote", help="layer-promotion proposals (§5)")
    pr.add_argument("--text", help="check this text against the vault instead of running the full table")
    pr.add_argument("--json", action="store_true")
    pr.set_defaults(func=cmd_promote)
    nb = sub.add_parser("neighbors", help="candidate pairs for the contradiction pass (§3)")
    nb.add_argument("--since", type=int, default=7)
    nb.add_argument("--k", type=int, default=5)
    nb.add_argument("--cap", type=int, default=20)
    nb.add_argument("--json", action="store_true")
    nb.set_defaults(func=cmd_neighbors)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
