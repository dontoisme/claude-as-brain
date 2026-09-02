#!/usr/bin/env python3
"""Deletable retrieval index for a Claude-as-Brain vault.

Implements Temporal Retrieval Spec Part 1 (index), Part 2 (scoring) and the
/reindex command. Phase A: grep-based relevance × recency, no embeddings.
Phase B: every note read to produce an answer, and every new inbound wikilink,
is a row in `retrievals`. Activation is ACT-R base-level over those rows, and
a retrieval also resets the recency clock: age is measured from the later of
`updated` and the last retrieval. That is the spec's core insight ("activation
decays from last retrieval, not creation") and the only reading under which
its Phase B acceptance test can pass.

    python3 .claude/scripts/brain_index.py reindex
    python3 .claude/scripts/brain_index.py rank "what's going on with pricing" [--k 10] [--json]
    python3 .claude/scripts/brain_index.py show Areas/Pricing.md
    python3 .claude/scripts/brain_index.py bump PATH... --kind ask|thread|prep|brief     # Phase B: read-for-answer
    python3 .claude/scripts/brain_index.py bump --links-of NOTE --kind wikilink          # Phase B: new inbound links

The index lives at .index/brain.sqlite3, is gitignored, and can be deleted at
any time. If it is missing, `rank` exits 3 so callers fall back to grep.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import re
import sqlite3
import struct
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

INDEX_REL = Path(".index") / "brain.sqlite3"
FM_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?", re.S)
FOLDER_TYPES = {
    "Days": "day", "Meetings": "meeting", "Projects": "project", "Areas": "area",
    "Resources": "resource", "People": "person", "MOCs": "moc", "Inbox": "inbox",
}
KNOWN_TYPES = set(FOLDER_TYPES.values()) | {"other"}
SKIP_DIRS = {".index", ".beads", ".claude", ".git", ".obsidian", "Templates", "node_modules"}
SKIP_FILES = {"README.md", "Todos.md", "Dashboard.md"}
DEFAULT_HALF_LIFE: dict[str, float] = {
    "day": 7, "meeting": 21, "inbox": 14, "project": 60,
    "area": math.inf, "resource": math.inf, "person": math.inf, "moc": math.inf, "other": math.inf,
}
PROFILE_MULT = {"current": 0.5, "decision": 1.0, "archival": math.inf}
# Part 3 — query intent profiles. First matching trigger wins; default current.
PROFILE_TRIGGERS = [
    ("archival", ["has anyone ever", "have we ever", "did we ever", "did anyone ever", "ever mention", "ever talk", "ever discuss",
                  "history of", "over the years", "all time", "back when", "originally", "first time", "ever come up", "ever raised"]),
    ("decision", ["what did we decide", "did we decide", "what was decided", "why did we", "why do we", "rationale",
                  "the decision", "decided", "decision on", "reasoning behind", "settled on", "what did we agree", "why is it"]),
    ("current", ["what's going on", "whats going on", "going on with", "status of", "latest", "currently", "right now",
                 "where are we", "where do we stand", "state of", "update on", "recent", "this week", "lately"]),
]


def classify(question: str) -> tuple[str, str | None]:
    q = " " + re.sub(r"\s+", " ", question.replace("\u2019", "'").lower()).strip() + " "
    for profile, triggers in PROFILE_TRIGGERS:
        for trig in triggers:
            if f" {trig}" in q or f"{trig} " in q:
                return profile, trig
    return "current", None
SOURCE_MULT = {"human": 1.0, "mixed": 0.95, "inferred": 0.85, "external": 0.7}
SCHEMA_VERSION = "3"
ACTIVATION_D = 0.5
EMBED_CHARS = 8000            # spec: cap ~8k chars; longer notes embed the first 8k plus summary, flagged truncated
OLLAMA_URL = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
EMBED_MODEL_PREFIX = "nomic-embed-text"
SEMANTIC_TOP = 25             # semantic candidates unioned with grep candidates
STOPWORDS = set("""a an and are as at be by for from has have how in is it its of on or that the this to was we
what whats when where which who why with our your you i me my about going latest status did do does
has have anyone ever mentioned mention know anything something things there here been being""".split())

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
  path            TEXT PRIMARY KEY,
  note_type       TEXT NOT NULL,
  created         TEXT NOT NULL,
  updated         TEXT NOT NULL,
  last_referenced TEXT,
  ref_count       INTEGER DEFAULT 0,
  content_hash    TEXT NOT NULL,
  summary         TEXT,
  embedding       BLOB,
  title           TEXT,
  status          TEXT,
  tags            TEXT,
  word_count      INTEGER DEFAULT 0,
  source          TEXT,
  confidence      TEXT,
  distilled_to    TEXT
);
CREATE TABLE IF NOT EXISTS retrievals (
  path TEXT NOT NULL,
  ts   TEXT NOT NULL,
  kind TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS retrievals_path ON retrievals(path);
CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT
);
"""


# ----------------------------------------------------------------- helpers

def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def parse_ts(s: str | None) -> dt.datetime | None:
    if not s:
        return None
    try:
        d = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        m = re.match(r"(\d{4}-\d{2}-\d{2})", str(s))
        if not m:
            return None
        d = dt.datetime.fromisoformat(m.group(1))
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d.astimezone(dt.timezone.utc)


def iso(d: dt.datetime) -> str:
    return d.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def split_frontmatter(text: str) -> tuple[dict, str]:
    m = FM_RE.match(text)
    if not m:
        return {}, text
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        data = {}
    return (data if isinstance(data, dict) else {}), text[m.end():]


def fm_date(fm: dict, *keys: str) -> dt.datetime | None:
    for k in keys:
        v = fm.get(k)
        if v is None or v == "":
            continue
        if isinstance(v, dt.datetime):
            return v if v.tzinfo else v.replace(tzinfo=dt.timezone.utc)
        if isinstance(v, dt.date):
            return dt.datetime(v.year, v.month, v.day, tzinfo=dt.timezone.utc)
        d = parse_ts(str(v))
        if d:
            return d
    return None


def load_config(vault: Path) -> dict:
    """Read the `retrieval:` YAML block from CLAUDE.md, if present."""
    cfg: dict = {"half_life_days": dict(DEFAULT_HALF_LIFE), "quarantine": [], "wikilink_weight": 0.5}
    claude_md = vault / "CLAUDE.md"
    if not claude_md.exists():
        return cfg
    m = re.search(r"```yaml\n(retrieval:\n.*?)```", claude_md.read_text(encoding="utf-8"), re.S)
    if not m:
        return cfg
    try:
        data = (yaml.safe_load(m.group(1)) or {}).get("retrieval") or {}
    except yaml.YAMLError:
        return cfg
    for k, v in (data.get("half_life_days") or {}).items():
        if isinstance(v, str) and v.strip().lower() in ("inf", "infinity", "none", "never"):
            cfg["half_life_days"][k] = math.inf
        elif isinstance(v, (int, float)) and v > 0:
            cfg["half_life_days"][k] = float(v)
    cfg["quarantine"] = [str(q).rstrip("/") for q in (data.get("quarantine") or [])]
    if isinstance(data.get("wikilink_weight"), (int, float)) and data["wikilink_weight"] >= 0:
        cfg["wikilink_weight"] = float(data["wikilink_weight"])
    return cfg


def git_dates(vault: Path) -> dict[str, tuple[dt.datetime, dt.datetime]]:
    """rel path -> (first commit date, last commit date) for every tracked .md."""
    out: dict[str, list] = {}
    try:
        res = subprocess.run(
            ["git", "log", "--format=%x00%cI", "--name-only", "--", "*.md"],
            cwd=vault, capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {}
    current: dt.datetime | None = None
    for line in res.stdout.splitlines():
        if line.startswith("\x00"):
            current = parse_ts(line[1:].strip())
            continue
        p = line.strip().replace("\\", "/")
        if not p or current is None:
            continue
        rec = out.setdefault(p, [current, current])  # [last, first]; log is newest-first
        rec[1] = current
    return {k: (v[1], v[0]) for k, v in out.items()}


def git_dirty(vault: Path) -> set[str]:
    try:
        res = subprocess.run(["git", "status", "--porcelain", "--", "*.md"], cwd=vault,
                             capture_output=True, text=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()
    dirty = set()
    for line in res.stdout.splitlines():
        p = line[3:].strip().strip('"')
        if " -> " in p:
            p = p.split(" -> ", 1)[1]
        dirty.add(p.replace("\\", "/"))
    return dirty


def infer_type(rel: str, fm: dict) -> str:
    override = str(fm.get("type") or "").strip().lower()
    if override in KNOWN_TYPES:
        return override
    top = rel.split("/", 1)[0] if "/" in rel else ""
    return FOLDER_TYPES.get(top, "other")


def walk_vault(vault: Path):
    for root, dirs, files in os.walk(vault):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
        for f in sorted(files):
            if not f.endswith(".md") or f in SKIP_FILES or f.startswith("."):
                continue
            p = Path(root) / f
            yield p, str(p.relative_to(vault)).replace("\\", "/")


def open_index(vault: Path, create: bool = False) -> sqlite3.Connection | None:
    path = vault / INDEX_REL
    if not path.exists() and not create:
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(retrievals)")}
    if "weight" not in cols:
        conn.execute("ALTER TABLE retrievals ADD COLUMN weight REAL DEFAULT 1.0")
    if "origin" not in cols:
        conn.execute("ALTER TABLE retrievals ADD COLUMN origin TEXT")
    row = conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
    version = row["value"] if row else None
    if version != SCHEMA_VERSION:
        if not create:
            print("index schema is out of date — run /reindex", file=sys.stderr)
            conn.close()
            return None
        # notes are derivable from the files; retrievals are not, so keep them
        conn.execute("DROP TABLE notes")
        conn.executescript(SCHEMA)
        conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('schema_version', ?)", (SCHEMA_VERSION,))
        conn.commit()
    return conn


# -------------------------------------------------------------- embeddings

class Embedder:
    """nomic-embed-text via a local ollama, or a deterministic stand-in for tests.

    BRAIN_EMBED=off   never embed (grep + decay only)
    BRAIN_EMBED=fake  hashed bag-of-words vectors; for exercising the plumbing, not for real retrieval
    unset             use ollama if it is running and serves a nomic-embed-text model
    """

    def __init__(self, name: str, dims: int, fake: bool = False):
        self.name, self.dims, self.fake = name, dims, fake

    @classmethod
    def detect(cls) -> "Embedder | None":
        mode = os.environ.get("BRAIN_EMBED", "").strip().lower()
        if mode == "off":
            return None
        if mode == "fake":
            return cls("fake-bow-v0", 256, fake=True)
        try:
            req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as r:  # noqa: S310 — loopback only
                tags = json.loads(r.read().decode())
        except (urllib.error.URLError, OSError, ValueError, TimeoutError):
            return None
        names = [m.get("name", "") for m in tags.get("models", [])]
        hit = next((n for n in names if n.startswith(EMBED_MODEL_PREFIX)), None)
        if not hit:
            return None
        e = cls(hit[:-len(":latest")] if hit.endswith(":latest") else hit, 0)
        try:
            e.dims = len(e.embed("search_document: probe"))
        except Exception:  # noqa: BLE001
            return None
        return e if e.dims else None

    def embed(self, text: str) -> list[float]:
        if self.fake:
            return self._fake(text)
        payload = json.dumps({"model": self.name, "prompt": text}).encode()
        req = urllib.request.Request(f"{OLLAMA_URL}/api/embeddings", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:  # noqa: S310
            return list(json.loads(r.read().decode()).get("embedding") or [])

    def _fake(self, text: str) -> list[float]:
        v = [0.0] * self.dims
        for tok in re.findall(r"[a-z0-9]+", text.lower()):
            tok = re.sub(r"(ing|ies|es|ed|s)$", "", tok) if len(tok) > 4 else tok
            if len(tok) < 3:
                continue
            h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
            v[h % self.dims] += 1.0
        n = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / n for x in v]


def pack(vec: list[float]) -> bytes:
    return struct.pack(f"<{len(vec)}f", *vec)


def unpack(blob: bytes) -> list[float]:
    return list(struct.unpack(f"<{len(blob) // 4}f", blob))


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (na * nb)


def embed_input(body: str, summary: str | None) -> tuple[str, bool]:
    """The text a note is embedded from; True if it had to be truncated."""
    head = "search_document: " + (f"{summary}\n\n" if summary else "")
    if len(body) <= EMBED_CHARS:
        return head + body, False
    return head + body[:EMBED_CHARS], True


# ----------------------------------------------------------------- reindex

def cmd_reindex(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    conn = open_index(vault, create=True)
    assert conn is not None
    gdates = git_dates(vault)
    dirty = git_dirty(vault)
    embedder = Embedder.detect()
    prev_model = (conn.execute("SELECT value FROM meta WHERE key='embed_model'").fetchone() or [None])[0]
    model_changed = bool(embedder) and prev_model != embedder.name
    existing = {r["path"]: r for r in conn.execute("SELECT path, content_hash, embedding IS NOT NULL AS has_emb FROM notes")}
    seen: set[str] = set()
    added = updated = unchanged = truncated = embedded = 0

    for path, rel in walk_vault(vault):
        seen.add(rel)
        text = path.read_text(encoding="utf-8", errors="replace")
        fm, body = split_frontmatter(text)
        h = hashlib.sha256(body.encode("utf-8")).hexdigest()
        first, last = gdates.get(rel, (None, None))
        mtime = dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc)
        created = fm_date(fm, "created", "date") or first or mtime
        # `updated`: frontmatter wins. Otherwise a note edited since it was
        # committed uses git's last commit date; a note committed exactly once
        # (or never) is as old as its own date: line — a bulk import of last
        # year's meetings must not read as "written today".
        edited_since_first = first is not None and last is not None and last != first
        note_type = infer_type(rel, fm)
        if fm_date(fm, "updated"):
            updated_at = fm_date(fm, "updated")
        elif note_type in ("day", "meeting") and fm_date(fm, "date"):
            # event-shaped: the event date is the clock, whatever git says about later touch-ups
            updated_at = fm_date(fm, "date")
        elif rel in dirty:
            updated_at = fm_date(fm, "date") if last is None and fm_date(fm, "date") else mtime
        elif edited_since_first:
            updated_at = last
        else:
            updated_at = fm_date(fm, "date") or last or mtime
        tags = fm.get("tags") or []
        if isinstance(tags, str):
            tags = [tags]
        row = {
            "path": rel,
            "note_type": note_type,
            "created": iso(created),
            "updated": iso(updated_at),
            "content_hash": h,
            "summary": str(fm["summary"]) if fm.get("summary") else None,
            "title": str(fm.get("title") or path.stem),
            "status": str(fm["status"]) if fm.get("status") else None,
            "tags": json.dumps([str(t) for t in tags]),
            "word_count": len(body.split()),
            "source": str(fm["source"]).strip().lower() if fm.get("source") else None,
            "confidence": str(fm["confidence"]).strip().lower() if fm.get("confidence") else None,
            "distilled_to": json.dumps([str(x) for x in fm["distilled_to"]]) if isinstance(fm.get("distilled_to"), list) else None,
        }
        if rel not in existing:
            conn.execute(
                "INSERT INTO notes (path, note_type, created, updated, content_hash, summary, title, status, tags, word_count, source, confidence, distilled_to)"
                " VALUES (:path, :note_type, :created, :updated, :content_hash, :summary, :title, :status, :tags, :word_count, :source, :confidence, :distilled_to)", row)
            added += 1
        elif existing[rel]["content_hash"] != h:
            conn.execute(
                "UPDATE notes SET note_type=:note_type, created=:created, updated=:updated, content_hash=:content_hash,"
                " summary=:summary, title=:title, status=:status, tags=:tags, word_count=:word_count, embedding=NULL,"
                " source=:source, confidence=:confidence, distilled_to=:distilled_to WHERE path=:path", row)
            updated += 1
        else:
            # metadata can move without the body changing (a date edit, a git commit)
            conn.execute("UPDATE notes SET note_type=:note_type, created=:created, updated=:updated, summary=:summary,"
                         " title=:title, status=:status, tags=:tags, source=:source, confidence=:confidence, distilled_to=:distilled_to WHERE path=:path", row)
            unchanged += 1
        if embedder and (rel not in existing or existing[rel]["content_hash"] != h or not existing[rel]["has_emb"] or model_changed):
            text_in, was_truncated = embed_input(body, row["summary"])
            try:
                vec = embedder.embed(text_in)
            except Exception as e:  # noqa: BLE001 — an ollama hiccup leaves the row grep-only rather than aborting the pass
                print(f"embedding failed for {rel}: {e}", file=sys.stderr)
                vec = []
            if vec:
                conn.execute("UPDATE notes SET embedding=? WHERE path=?", (pack(vec), rel))
                embedded += 1
                truncated += int(was_truncated)

    removed = 0
    for rel in set(existing) - seen:
        conn.execute("DELETE FROM notes WHERE path=?", (rel,))
        conn.execute("DELETE FROM retrievals WHERE path=?", (rel,))
        removed += 1

    if embedder:
        conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('embeddings', 'on')")
        conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('embed_model', ?)", (embedder.name,))
        conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('embed_dims', ?)", (str(embedder.dims),))
    else:
        conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('embeddings', 'off')")
    conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('reindexed_at', ?)", (iso(now_utc()),))
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    emb = f"embeddings on ({embedder.name}, {embedded} embedded)" if embedder else "embeddings off"
    print(f"reindexed {total} notes: {added} added, {updated} updated, {removed} removed, {truncated} truncated, "
          f"{unchanged} unchanged · {emb} · {INDEX_REL}")
    return 0


# -------------------------------------------------------------------- rank

def query_terms(q: str) -> list[str]:
    terms = []
    q = q.replace("\u2019", "'").lower()
    for t in re.findall(r"[a-z0-9][a-z0-9'\-]+", q):
        t = re.sub(r"'s$", "", t.strip("'-"))
        if len(t) >= 3 and t not in STOPWORDS and t not in terms:
            terms.append(t)
    return terms


def count_hits(text: str, terms: list[str]) -> int:
    low = text.lower()
    return sum(len(re.findall(r"(?<![a-z0-9])" + re.escape(t) + r"[a-z]{0,3}(?![a-z0-9])", low)) for t in terms)


def activation(conn: sqlite3.Connection, rel: str, now: dt.datetime) -> tuple[float, int, dt.datetime | None]:
    """ACT-R base-level activation, normalized to 0.5–1.5; 1.0 if never retrieved."""
    rows = conn.execute("SELECT ts, weight FROM retrievals WHERE path=?", (rel,)).fetchall()
    if not rows:
        return 1.0, 0, None
    last = None
    total = 0.0
    for r in rows:
        ts = parse_ts(r["ts"])
        if not ts:
            continue
        last = ts if last is None or ts > last else last
        t_days = max((now - ts).total_seconds() / 86400.0, 1 / 24)
        total += (r["weight"] if r["weight"] is not None else 1.0) * t_days ** (-ACTIVATION_D)
    if total <= 0:
        return 1.0, len(rows), last
    raw = math.log(total)  # ~ -3 (one retrieval a year ago) .. ~ +3 (many recent)
    return max(0.5, min(1.5, 1.0 + raw / 6.0)), len(rows), last


def half_life_for(note: sqlite3.Row, cfg: dict, profile: str, tags: list[str]) -> float:
    hl = cfg["half_life_days"].get(note["note_type"], math.inf)
    if note["note_type"] == "project" and str(note["status"] or "").lower() not in ("complete", "completed", "archived", "done"):
        hl = math.inf
    if profile == "decision" and any(str(t).lstrip("#") == "decision" for t in tags):
        return math.inf
    mult = PROFILE_MULT.get(profile, 1.0)
    return hl * mult if math.isfinite(hl) and math.isfinite(mult) else math.inf


def cmd_rank(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    conn = open_index(vault)
    if conn is None:
        print("no index at .index/brain.sqlite3 — run /reindex; falling back to grep-only retrieval", file=sys.stderr)
        return 3
    cfg = load_config(vault)
    terms = query_terms(args.query)
    if not terms:
        print("query has no searchable terms", file=sys.stderr)
        return 1
    trigger = None
    if args.profile == "auto":
        args.profile, trigger = classify(args.query)
    types = {x.strip().lower() for x in args.types.split(",")} if args.types else None
    now = now_utc()
    # semantic candidates (Phase D): cosine over stored vectors, min-max normalized across the top N
    semantic: dict[str, float] = {}
    emb_on = (conn.execute("SELECT value FROM meta WHERE key='embeddings'").fetchone() or ["off"])[0] == "on"
    embedder = Embedder.detect() if emb_on and not args.no_embeddings else None
    if embedder:
        try:
            qvec = embedder.embed("search_query: " + args.query)
        except Exception as e:  # noqa: BLE001
            print(f"query embedding failed ({e}); grep only", file=sys.stderr)
            qvec = []
        if qvec:
            sims = sorted(((cosine(qvec, unpack(r["embedding"])), r["path"])
                           for r in conn.execute("SELECT path, embedding FROM notes WHERE embedding IS NOT NULL")), reverse=True)
            top = [s for s in sims[:SEMANTIC_TOP] if s[0] > 0]
            if top:
                hi, lo = top[0][0], top[-1][0]
                for s, path in top:
                    semantic[path] = 1.0 if hi == lo else (s - lo) / (hi - lo)
    cands = []
    for note in conn.execute("SELECT * FROM notes"):
        if types and note["note_type"] not in types:
            continue
        p = vault / note["path"]
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        _, body = split_frontmatter(text)
        hits = count_hits(body, terms)
        title_hit = count_hits(note["title"] or "", terms) + count_hits(note["summary"] or "", terms) + count_hits(note["path"], terms)
        sem = semantic.get(note["path"])
        if hits == 0 and title_hit == 0 and sem is None:
            continue
        density = hits / max(note["word_count"] or 1, 50) * 100.0
        cands.append([note, hits, title_hit, density, sem])
    if not cands:
        print(json.dumps({"profile": args.profile, "trigger": trigger, "terms": terms, "results": []}) if args.json else "no candidates")
        return 0
    max_density = max(c[3] for c in cands) or 1.0
    results = []
    for note, hits, title_hit, density, sem in cands:
        tags = json.loads(note["tags"] or "[]")
        source = (note["source"] or "").lower() or None
        grep_rel = min(1.0, density / max_density + (0.3 if title_hit else 0.0)) if (hits or title_hit) else 0.0
        relevance = max(grep_rel, sem or 0.0) * SOURCE_MULT.get(source or "human", 1.0)
        act, refs, last_ref = activation(conn, note["path"], now)
        updated = parse_ts(note["updated"]) or now
        clock = max(updated, last_ref) if last_ref else updated  # a retrieval resets the recency clock
        age_days = max((now - clock).total_seconds() / 86400.0, 0.0)
        hl = half_life_for(note, cfg, args.profile, tags)
        recency = 1.0 if not math.isfinite(hl) else 2.0 ** (-age_days / hl)
        score = relevance * recency * act
        stale = math.isfinite(hl) and age_days > 2 * hl
        quarantined = any(note["path"].startswith(q + "/") for q in cfg["quarantine"]) or "#imported" in tags or "imported" in tags
        results.append({
            "path": note["path"], "score": round(score, 4), "relevance": round(relevance, 3),
            "recency": round(recency, 3), "activation": round(act, 3), "hits": hits, "title_hit": bool(title_hit),
            "note_type": note["note_type"], "age_days": round(age_days, 1), "half_life": None if not math.isfinite(hl) else hl,
            "updated_days": round(max((now - updated).total_seconds() / 86400.0, 0.0), 1),
            "ref_count": refs, "last_referenced": iso(last_ref) if last_ref else None,
            "stale": stale, "quarantined": quarantined, "updated": note["updated"],
            "source": source, "confidence": note["confidence"],
            "grep_relevance": round(grep_rel, 3), "semantic": None if sem is None else round(sem, 3),
        })
    results.sort(key=lambda r: (-r["score"], -r["hits"], r["path"]))
    results = results[: args.k]
    if args.json:
        print(json.dumps({"profile": args.profile, "trigger": trigger, "terms": terms, "results": results}, indent=2))
        return 0
    why = f" (matched \"{trigger}\")" if trigger else (" (default; no trigger matched)" if args.profile == "current" else "")
    mode = f"hybrid ({embedder.name})" if embedder else "grep only"
    print(f"terms: {', '.join(terms)} · profile: {args.profile}{why} · {mode} · {len(cands)} candidate(s)")
    for r in results:
        cited = "never cited" if not r["last_referenced"] else f"last cited {round((now - parse_ts(r['last_referenced'])).total_seconds()/86400)}d ago"
        label = f"({int(r['updated_days'])}d old · {cited} · {r['ref_count']} refs)"
        prov = {"external": "(external, unverified)"}.get(r["source"], f"({r['source']})" if r["source"] else "(source unset)")
        flags = f" {prov}" + (" [possibly stale]" if r["stale"] else "") + (" (imported, unverified)" if r["quarantined"] else "")
        print(f"{r['score']:.3f}  {r['path']}   {label}{flags}")
        sem = f" · semantic {r['semantic']:.2f}" if r["semantic"] is not None else ""
        print(f"       relevance {r['relevance']:.2f} × recency {r['recency']:.2f} × activation {r['activation']:.2f} · {r['hits']} hits{sem} · {r['note_type']}")
    return 0


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")


def resolve_link(conn: sqlite3.Connection, target: str) -> str | None:
    """Map a wikilink target to an indexed path: exact, folder-relative, or basename match."""
    t = target.strip().replace("\\", "/")
    if t.endswith(".md"):
        t = t[:-3]
    cands = [f"{t}.md"]
    rows = {r["path"] for r in conn.execute("SELECT path FROM notes")}
    for c in cands:
        if c in rows:
            return c
    base = t.rsplit("/", 1)[-1].lower() + ".md"
    matches = [p for p in rows if p.rsplit("/", 1)[-1].lower() == base]
    return matches[0] if len(matches) == 1 else None


def cmd_bump(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    conn = open_index(vault)
    if conn is None:
        print("no index — nothing to bump (run /reindex first)", file=sys.stderr)
        return 3
    cfg = load_config(vault)
    now = now_utc()
    ts = iso(now)
    targets: list[tuple[str, str | None]] = [(p, None) for p in args.paths]
    if args.links_of:
        origin = args.links_of.replace("\\", "/")
        src = vault / origin
        if not src.exists():
            print(f"no such note: {origin}", file=sys.stderr)
            return 1
        _, body = split_frontmatter(src.read_text(encoding="utf-8", errors="replace"))
        seen = set()
        for m in WIKILINK_RE.finditer(body):
            resolved = resolve_link(conn, m.group(1))
            if resolved and resolved != origin and resolved not in seen:
                seen.add(resolved)
                targets.append((resolved, origin))
    weight = args.weight if args.weight is not None else (cfg["wikilink_weight"] if args.kind == "wikilink" else 1.0)
    bumped, skipped = [], []
    for path, origin in targets:
        path = path.replace("\\", "/")
        if not conn.execute("SELECT 1 FROM notes WHERE path=?", (path,)).fetchone():
            resolved = resolve_link(conn, path)
            if not resolved:
                skipped.append(path)
                continue
            path = resolved
        if origin and conn.execute("SELECT 1 FROM retrievals WHERE path=? AND kind='wikilink' AND origin=?", (path, origin)).fetchone():
            continue  # this inbound link was already counted
        conn.execute("INSERT INTO retrievals (path, ts, kind, weight, origin) VALUES (?, ?, ?, ?, ?)", (path, ts, args.kind, weight, origin))
        conn.execute("UPDATE notes SET last_referenced=?, ref_count=COALESCE(ref_count,0)+1 WHERE path=?", (ts, path))
        bumped.append(path)
    conn.commit()
    print(f"bumped {len(bumped)} note(s) as {args.kind}" + (f" ×{weight:g}" if weight != 1.0 else "") + (": " + ", ".join(bumped) if bumped else ""))
    if skipped:
        print(f"  not indexed, skipped: {', '.join(skipped)}", file=sys.stderr)
    return 0


def replace_fm_keys(text: str, values: dict) -> str:
    """Set top-level frontmatter keys in place, preserving everything else; creates frontmatter if absent."""
    def render(key, value):
        if isinstance(value, (list, dict)):
            return f"{key}: " + yaml.safe_dump(value, default_flow_style=True, allow_unicode=True, width=1000).strip()
        return f"{key}: " + re.sub(r"\n\.\.\.$", "", yaml.safe_dump(value, allow_unicode=True, width=1000).strip())
    m = FM_RE.match(text)
    if not m:
        block = "\n".join(render(k, v) for k, v in values.items())
        return f"---\n{block}\n---\n\n{text.lstrip()}"
    raw = m.group(1)
    lines = [l for l in raw.split("\n") if l.strip()]
    for key, value in values.items():
        dumped = [render(key, value)]
        start = end = None
        for i, line in enumerate(lines):
            if start is None and re.match(rf"^{re.escape(key)}\s*:", line):
                start = i
                continue
            if start is not None and re.match(r"^[A-Za-z0-9_\-]+\s*:", line) and not line.startswith(" "):
                end = i
                break
        if start is None:
            lines = lines + dumped
        else:
            lines = lines[:start] + dumped + lines[len(lines) if end is None else end:]
    return text[: m.start(1)] + "\n".join(lines) + text[m.end(1):]


def cmd_undistilled(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    conn = open_index(vault)
    if conn is None:
        print("no index — run /reindex", file=sys.stderr)
        return 3
    cutoff = iso(now_utc() - dt.timedelta(days=args.since))
    rows = conn.execute("SELECT path, updated, note_type FROM notes WHERE note_type IN ('day','meeting') AND updated >= ?"
                        " AND (distilled_to IS NULL) ORDER BY updated", (cutoff,)).fetchall()
    if args.json:
        print(json.dumps([dict(r) for r in rows], indent=2))
        return 0
    if not rows:
        print(f"nothing undistilled in the last {args.since} days")
        return 0
    for r in rows:
        print(f"{r['updated'][:10]}  {r['path']}")
    print(f"{len(rows)} event-shaped note(s) without distilled_to")
    return 0


def cmd_distill(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    path = vault / args.note
    if not path.exists():
        print(f"no such note: {args.note}", file=sys.stderr)
        return 1
    targets = [] if (len(args.to) == 1 and args.to[0].lower() == "none") else args.to
    today = args.date or dt.date.today().isoformat()
    text = path.read_text(encoding="utf-8")
    path.write_text(replace_fm_keys(text, {"distilled_to": targets, "distilled_on": today}), encoding="utf-8")
    conn = open_index(vault)
    if conn is not None:
        conn.execute("UPDATE notes SET distilled_to=? WHERE path=?", (json.dumps(targets), args.note.replace("\\", "/")))
        conn.commit()
    print(f"✓ {args.note} distilled_on {today} → {', '.join(targets) if targets else 'nothing durable'}")
    return 0


def cmd_cooling(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    conn = open_index(vault)
    if conn is None:
        print("no index — run /reindex", file=sys.stderr)
        return 3
    now = now_utc()
    then = now - dt.timedelta(days=args.since) if args.since else None
    out = []
    for r in conn.execute("SELECT path, note_type, distilled_to, last_referenced FROM notes WHERE ref_count > 0 AND distilled_to IS NULL"):
        act_now, refs, last = activation(conn, r["path"], now)
        if act_now >= args.threshold:
            continue
        if then is not None:
            act_then, _, _ = activation(conn, r["path"], then)
            if act_then < args.threshold:
                continue  # was already cold; not a crossing this window
        out.append({"path": r["path"], "note_type": r["note_type"], "activation": round(act_now, 3), "refs": refs,
                    "last_referenced": iso(last) if last else None})
    out.sort(key=lambda d: d["last_referenced"] or "")
    if args.json:
        print(json.dumps(out, indent=2))
        return 0
    if not out:
        print("nothing cooling off" + (f" in the last {args.since} days" if args.since else ""))
        return 0
    for d in out[: args.limit]:
        print(f"{d['activation']:.2f}  {d['path']}   (last cited {d['last_referenced'][:10] if d['last_referenced'] else '—'} · {d['refs']} refs · {d['note_type']})")
    if len(out) > args.limit:
        print(f"… {len(out) - args.limit} more")
    return 0


def cmd_distilled_check(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    conn = open_index(vault)
    if conn is None:
        print("no index — run /reindex", file=sys.stderr)
        return 3
    bead_ids: set[str] = set()
    issues = vault / ".beads" / "issues.jsonl"
    if issues.exists():
        for line in issues.read_text(encoding="utf-8").splitlines():
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("id"):
                bead_ids.add(d["id"])
    dangling = []
    for r in conn.execute("SELECT path, distilled_to FROM notes WHERE distilled_to IS NOT NULL"):
        for target in json.loads(r["distilled_to"] or "[]"):
            tgt = str(target).strip()
            if tgt.startswith("bd:"):
                if bead_ids and tgt[3:] not in bead_ids:
                    dangling.append((r["path"], tgt, "no such bead"))
            else:
                inner = tgt[2:-2] if tgt.startswith("[[") and tgt.endswith("]]") else tgt
                if resolve_link(conn, inner) is None:
                    dangling.append((r["path"], tgt, "no such note"))
    if args.json:
        print(json.dumps([{"path": p, "target": t_, "problem": why} for p, t_, why in dangling], indent=2))
        return 0
    if not dangling:
        print("all distilled_to targets resolve")
        return 0
    for p_, tgt, why in dangling:
        print(f"{p_}  →  {tgt}   ({why})")
    print(f"{len(dangling)} dangling distilled_to target(s)")
    return 1


def cmd_show(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    conn = open_index(vault)
    if conn is None:
        print("no index — run /reindex", file=sys.stderr)
        return 3
    row = conn.execute("SELECT * FROM notes WHERE path=?", (args.path,)).fetchone()
    if not row:
        print("not indexed", file=sys.stderr)
        return 1
    d = dict(row)
    d.pop("embedding", None)
    d["retrievals"] = conn.execute("SELECT COUNT(*) FROM retrievals WHERE path=?", (args.path,)).fetchone()[0]
    print(json.dumps(d, indent=2))
    return 0


# -------------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault", default=".", help="vault root (default: cwd)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("reindex", help="build or refresh .index/brain.sqlite3")
    r.set_defaults(func=cmd_reindex)
    k = sub.add_parser("rank", help="score notes for a query: relevance × recency × activation")
    k.add_argument("query")
    k.add_argument("--k", type=int, default=10)
    k.add_argument("--profile", choices=["auto", *sorted(PROFILE_MULT)], default="auto",
                   help="intent profile; auto classifies from trigger phrases (Part 3), default current")
    k.add_argument("--types", help="comma-separated note types to include, e.g. area,person or meeting,day")
    k.add_argument("--no-embeddings", action="store_true", help="grep-only even if the index has vectors")
    k.add_argument("--json", action="store_true")
    k.set_defaults(func=cmd_rank)
    b = sub.add_parser("bump", help="record that notes were read to answer, or newly linked to")
    b.add_argument("paths", nargs="*", help="vault-relative note paths")
    b.add_argument("--links-of", metavar="NOTE", help="bump every note this note wikilinks to (kind wikilink)")
    b.add_argument("--kind", choices=["ask", "thread", "prep", "brief", "wikilink"], required=True)
    b.add_argument("--weight", type=float, help="override the row weight (wikilink default from CLAUDE.md retrieval.wikilink_weight)")
    b.set_defaults(func=cmd_bump)
    c = sub.add_parser("classify", help="which intent profile a question gets, and why")
    c.add_argument("question")
    c.set_defaults(func=lambda a: print(json.dumps(dict(zip(("profile", "trigger"), classify(a.question))))) or 0)
    u = sub.add_parser("undistilled", help="event-shaped notes updated recently that have no distilled_to")
    u.add_argument("--since", type=int, default=7, help="days")
    u.add_argument("--json", action="store_true")
    u.set_defaults(func=cmd_undistilled)
    d = sub.add_parser("distill", help="write distilled_to / distilled_on into a note's frontmatter")
    d.add_argument("note")
    d.add_argument("--to", action="append", required=True, help="'[[Areas/Pricing]]' or 'bd:cab-31'; repeatable; 'none' = reviewed, nothing durable")
    d.add_argument("--date", help="override distilled_on (YYYY-MM-DD)")
    d.set_defaults(func=cmd_distill)
    co = sub.add_parser("cooling", help="retrieved-once notes whose activation fell below the threshold, with nothing distilled")
    co.add_argument("--since", type=int, help="only notes that crossed the threshold within N days")
    co.add_argument("--threshold", type=float, default=0.6)
    co.add_argument("--limit", type=int, default=10)
    co.add_argument("--json", action="store_true")
    co.set_defaults(func=cmd_cooling)
    dc = sub.add_parser("distilled-check", help="distilled_to targets that don't exist")
    dc.add_argument("--json", action="store_true")
    dc.set_defaults(func=cmd_distilled_check)
    s = sub.add_parser("show", help="dump one note's index row")
    s.add_argument("path")
    s.set_defaults(func=cmd_show)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
