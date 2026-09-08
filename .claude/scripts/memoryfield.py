#!/usr/bin/env python3
"""Memoryfield export / import for a Claude-as-Brain vault.

Implements Memoryfield Improvements Spec §7 against Cal Paterson's memoryfield
format (SPEC.md v0.1, 2026-08). Markdown stays the source of truth; this only
maps frontmatter and packages files.

    python3 .claude/scripts/memoryfield.py export [FOLDER ...] [--out NAME.memoryfield.zip]
    python3 .claude/scripts/memoryfield.py import ZIP [--into DIR] [--sha256 HEX]

Export
  - Default folders: Resources/ Areas/ (folder README.md files are skipped).
  - Frontmatter mapping: title, created, updated, summary, uuid. A missing uuid
    is generated (v4) and WRITTEN BACK to the source note so it is stable
    across exports. Nothing else in the source note changes.
  - Notes over 8192 bytes are split at `## ` headings into "<title> (i of N)"
    pages, each with its own uuid. Split is export-only.
  - Vault-specific keys (source, confidence, distilled_to, distilled_on) move
    under an `x-cab` mapping instead of being dropped. The vault-relative path
    goes there too so a re-import can find its way home.
  - No vector index is produced (no local embeddings yet). The spec makes the
    index optional.

Import
  - Verifies the zip's sha256 against --sha256, or warns loudly if none given.
    Never auto-trusts.
  - Pages land in Resources/Imported/<name>/ with source: external,
    confidence: low, tag #imported, imported_from and imported_on.
  - The import folder is appended to `retrieval.quarantine` in CLAUDE.md so
    /ask labels citations from it (imported, unverified).
  - Vector index files in the zip are ignored; run /reindex instead.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import os
import re
import subprocess
import sys
import unicodedata
import uuid
import zipfile
from pathlib import Path

import yaml

PAGE_LIMIT = 8192
CAB_KEYS = ("source", "confidence", "distilled_to", "distilled_on")
DEBRIS = (".DS_Store", "desktop.ini", "Thumbs.db")
TYPE_TAGS = ("#area", "#project", "#meeting", "#person", "#moc", "#todos", "#index", "#changelog")
FM_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?", re.S)
SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")


# ----------------------------------------------------------------- helpers

def split_frontmatter(text: str) -> tuple[dict, str, str | None]:
    """Return (frontmatter dict, body, raw frontmatter text or None)."""
    m = FM_RE.match(text)
    if not m:
        return {}, text, None
    raw = m.group(1)
    try:
        data = yaml.safe_load(raw) or {}
        if not isinstance(data, dict):
            data = {}
    except yaml.YAMLError:
        data = {}
    return data, text[m.end():], raw


def iso(value) -> str | None:
    """Coerce a frontmatter date/datetime/str to a quoted ISO 8601 string."""
    if value is None or value == "":
        return None
    if isinstance(value, dt.datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=dt.timezone.utc)
        return value.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(value, dt.date):
        return value.strftime("%Y-%m-%dT00:00:00Z")
    s = str(value).strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s + "T00:00:00Z"
    return s


def slugify(text: str) -> str:
    s = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    return s or "page"


def git_dates(vault: Path, rel_paths: list[str]) -> dict[str, tuple[str, str]]:
    """Map rel path -> (first committer date, last committer date), from git."""
    out: dict[str, tuple[str, str]] = {}
    try:
        res = subprocess.run(
            ["git", "log", "--format=%x00%cI", "--name-only", "--", *rel_paths],
            cwd=vault, capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return out
    current = None
    for line in res.stdout.splitlines():
        if line.startswith("\x00"):
            current = line[1:].strip()
            continue
        p = line.strip()
        if not p or current is None:
            continue
        p = p.replace("\\", "/")
        first, last = out.get(p, (None, None))
        # log is newest-first: first sighting is the latest commit
        out[p] = (current, last or current)
    return {k: (iso(dt.datetime.fromisoformat(v[0])), iso(dt.datetime.fromisoformat(v[1])))
            for k, v in out.items()}


def mtime_iso(path: Path) -> str:
    return dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def dump_frontmatter(data: dict) -> str:
    text = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=None, width=1000)
    return f"---\n{text}---\n"


def write_back_uuid(path: Path, text: str, raw_fm: str | None, new_uuid: str) -> str:
    """Insert `uuid:` into an existing frontmatter block, or create a minimal one."""
    if raw_fm is None:
        new_text = f"---\nuuid: {new_uuid}\n---\n\n{text.lstrip()}" if text.strip() else f"---\nuuid: {new_uuid}\n---\n"
    else:
        m = FM_RE.match(text)
        head = text[:m.start(1) + len(raw_fm)]
        new_text = head.rstrip("\n") + f"\nuuid: {new_uuid}\n" + text[m.start(1) + len(raw_fm):].lstrip("\n")
        # keep the closing --- on its own line
        if not new_text.startswith(head.rstrip("\n") + f"\nuuid: {new_uuid}\n---"):
            new_text = text[:m.start(1) + len(raw_fm)] + f"\nuuid: {new_uuid}" + text[m.start(1) + len(raw_fm):]
    path.write_text(new_text, encoding="utf-8")
    return new_text


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------ export

def split_body(body: str, limit: int) -> list[str]:
    """Split a body into chunks under `limit` bytes, preferring ## boundaries."""
    if len(body.encode("utf-8")) <= limit:
        return [body]
    sections = re.split(r"(?m)^(?=## )", body)
    chunks: list[str] = []
    current = ""
    for sec in sections:
        if len(sec.encode("utf-8")) > limit:
            # oversize section: flush what we have, then split on paragraphs
            if current.strip():
                chunks.append(current)
                current = ""
            para_buf = ""
            for para in re.split(r"\n\n+", sec):
                cand = (para_buf + "\n\n" + para) if para_buf else para
                if len(cand.encode("utf-8")) > limit and para_buf:
                    chunks.append(para_buf)
                    para_buf = para
                else:
                    para_buf = cand
            if para_buf.strip():
                current = para_buf
            continue
        cand = current + sec
        if len(cand.encode("utf-8")) > limit and current.strip():
            chunks.append(current)
            current = sec
        else:
            current = cand
    if current.strip():
        chunks.append(current)
    return chunks or [body]


def build_vector_index(pages: list[tuple[str, str]]) -> Path | None:
    """Write <model>.sqlite3 in the spec's suggested schema if a local embedder is available.

    The spec says the embedding input MUST be the complete page file (frontmatter
    included), so pages are embedded here as exported, not copied from the
    vault's own index. Returns None, silently, when there is no embedder.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from brain_index import Embedder, pack
    except ImportError:
        return None
    embedder = Embedder.detect()
    if not embedder:
        return None
    import json as _json
    import sqlite3
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="memoryfield-")) / f"{embedder.name}.sqlite3"
    conn = sqlite3.connect(tmp)
    conn.executescript(
        "CREATE TABLE pages (filename TEXT PRIMARY KEY, frontmatter JSON NOT NULL, last_modified DATETIME NOT NULL,"
        " sha256_hash BLOB NOT NULL, embedding BLOB NOT NULL);"
    )
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for fname, content in pages:
        fm, _, _ = split_frontmatter(content)
        try:
            vec = embedder.embed("search_document: " + content[:PAGE_LIMIT])
        except Exception as e:  # noqa: BLE001
            print(f"warning: embedding failed for {fname}: {e}; omitting vector index", file=sys.stderr)
            conn.close()
            tmp.unlink(missing_ok=True)
            return None
        conn.execute("INSERT INTO pages VALUES (?, ?, ?, ?, ?)",
                     (fname, _json.dumps(fm, default=str), now, hashlib.sha256(content.encode("utf-8")).digest(), pack(vec)))
    conn.commit()
    conn.close()
    return tmp


def collect_notes(vault: Path, folders: list[str]) -> list[Path]:
    notes: list[Path] = []
    for folder in folders:
        base = vault / folder
        if not base.is_dir():
            print(f"warning: {folder}/ does not exist, skipping", file=sys.stderr)
            continue
        for p in sorted(base.rglob("*.md")):
            if p.name == "README.md" or p.name.startswith(".") or any(part.startswith(".") for part in p.relative_to(vault).parts):
                continue
            notes.append(p)
    return notes


def cmd_export(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    folders = args.folders or ["Resources", "Areas"]
    notes = collect_notes(vault, folders)
    if not notes:
        print("nothing to export", file=sys.stderr)
        return 1

    rels = [str(p.relative_to(vault)).replace("\\", "/") for p in notes]
    gdates = git_dates(vault, rels)
    vault_name = slugify(vault.name)
    out = Path(args.out) if args.out else vault / f"{vault_name}.memoryfield.zip"
    if out.suffix != ".zip":
        out = out.with_name(out.name + ".memoryfield.zip")

    pages: list[tuple[str, str]] = []  # (filename, content)
    listing: list[tuple[str, str, str]] = []  # (filename, title, source path)
    used: set[str] = set()
    written_back = 0
    split_count = 0

    def unique(slug: str) -> str:
        cand, n = slug, 2
        while cand in used or cand in ("index", "listing"):
            cand = f"{slug}-{n}"
            n += 1
        used.add(cand)
        return cand

    for path, rel in zip(notes, rels):
        text = path.read_text(encoding="utf-8")
        fm, body, raw_fm = split_frontmatter(text)
        note_uuid = str(fm.get("uuid") or "").strip()
        if not note_uuid:
            note_uuid = str(uuid.uuid4())
            write_back_uuid(path, text, raw_fm, note_uuid)
            written_back += 1
        title = str(fm.get("title") or path.stem)
        first, last = gdates.get(rel, (None, None))
        created = iso(fm.get("created")) or iso(fm.get("date")) or first or mtime_iso(path)
        updated = iso(fm.get("updated")) or last or mtime_iso(path)

        xcab = {"path": rel}
        extras = {}
        for k, v in fm.items():
            if k in ("title", "uuid", "summary", "created", "updated"):
                continue
            if k in CAB_KEYS:
                xcab[k] = v
            elif k == "x-cab" and isinstance(v, dict):
                xcab.update({kk: vv for kk, vv in v.items() if kk != "path"})
            else:
                extras[k] = v if not isinstance(v, (dt.date, dt.datetime)) else iso(v)

        base_slug = unique(slugify(rel[:-3] if rel.endswith(".md") else rel))
        chunks = split_body(body, PAGE_LIMIT - 600)  # headroom for frontmatter
        n = len(chunks)
        if n > 1:
            split_count += 1
        for i, chunk in enumerate(chunks, 1):
            page_fm: dict = {"title": title if n == 1 else f"{title} ({i} of {n})"}
            page_fm["uuid"] = note_uuid if n == 1 else str(uuid.uuid4())
            if fm.get("summary"):
                page_fm["summary"] = str(fm["summary"])
            page_fm["created"] = created
            page_fm["updated"] = updated
            page_fm.update(extras)
            x = dict(xcab)
            if n > 1:
                x.update({"part": i, "of": n, "parent_uuid": note_uuid})
            page_fm["x-cab"] = x
            fname = f"{base_slug}.md" if n == 1 else f"{base_slug}-{i}-of-{n}.md"
            assert SLUG_RE.match(fname[:-3]), fname
            pages.append((fname, dump_frontmatter(page_fm) + "\n" + chunk.lstrip("\n")))
            listing.append((fname, page_fm["title"], rel))

    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    index_md = (
        f"---\ntitle: {vault.name} memoryfield\ncreated: '{today}'\nupdated: '{today}'\n---\n\n"
        f"# {vault.name}\n\n"
        f"Notes exported from a Claude-as-Brain vault ({', '.join(f + '/' for f in folders)}) on {today[:10]}. "
        "Each page is one note: prose with YAML frontmatter. Keys under `x-cab` carry the vault's own metadata "
        "(provenance `source`, `confidence`, `distilled_to`, and the original path). Wikilinks in `[[double brackets]]` "
        "refer to notes in the source vault and may not resolve here.\n\n"
        "No vector index is included; build one locally if you need semantic search. "
        "`listing.md` catalogues the pages.\n"
    )
    listing_md = "# Listing\n\n| Page | Title | Source note |\n|---|---|---|\n" + "".join(
        f"| `{f}` | {t} | `{s}` |\n" for f, t, s in listing
    )

    out.parent.mkdir(parents=True, exist_ok=True)
    vec_file = build_vector_index(pages)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("index.md", index_md)
        zf.writestr("listing.md", listing_md)
        for fname, content in pages:
            zf.writestr(fname, content)
        if vec_file:
            zf.write(vec_file, vec_file.name)
            vec_file.unlink()

    digest = sha256_file(out)
    print(f"exported {len(pages)} page(s) from {len(notes)} note(s) in {', '.join(folders)}")
    if split_count:
        print(f"  split {split_count} note(s) over {PAGE_LIMIT} bytes into numbered pages")
    if written_back:
        print(f"  wrote a new uuid back into {written_back} source note(s)")
    print(f"  vector index: {vec_file.name}" if vec_file else "  no vector index (no local embeddings)")
    print(f"  {out}")
    print(f"  sha256  {digest}")
    return 0


# ------------------------------------------------------------------ import

def update_quarantine(vault: Path, folder: str) -> bool:
    """Append `folder` to retrieval.quarantine in CLAUDE.md. Returns True if changed."""
    claude_md = vault / "CLAUDE.md"
    if not claude_md.exists():
        return False
    text = claude_md.read_text(encoding="utf-8")
    block_re = re.compile(r"```yaml\n(retrieval:\n.*?)```", re.S)
    m = block_re.search(text)
    if not m:
        new_block = f"\n## Retrieval Config\n\n```yaml\nretrieval:\n  quarantine:\n    - {folder}\n```\n"
        anchor = "## Structure"
        text = text.replace(anchor, new_block.lstrip("\n") + "\n---\n\n" + anchor, 1) if anchor in text else text + new_block
        claude_md.write_text(text, encoding="utf-8")
        return True
    data = yaml.safe_load(m.group(1)) or {}
    cfg = data.setdefault("retrieval", {}) or {}
    q = cfg.get("quarantine") or []
    if folder in q:
        return False
    q.append(folder)
    cfg["quarantine"] = q
    data["retrieval"] = cfg
    dumped = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)
    text = text[:m.start(1)] + dumped + text[m.end(1):]
    claude_md.write_text(text, encoding="utf-8")
    return True


def safe_title_filename(title: str, used: set[str]) -> str:
    name = re.sub(r'[\\/:*?"<>|]+', " ", title).strip()
    name = re.sub(r"\s+", " ", name)[:120] or "Untitled page"
    cand, n = name, 2
    while cand.lower() in used:
        cand = f"{name} ({n})"
        n += 1
    used.add(cand.lower())
    return cand + ".md"


def cmd_import(args: argparse.Namespace) -> int:
    vault = Path(args.vault).resolve()
    zpath = Path(args.zip).resolve()
    if not zpath.is_file():
        print(f"error: {zpath} not found", file=sys.stderr)
        return 1
    digest = sha256_file(zpath)
    if args.sha256:
        if digest.lower() != args.sha256.strip().lower():
            print("error: sha256 mismatch — refusing to import", file=sys.stderr)
            print(f"  expected {args.sha256.strip().lower()}\n  actual   {digest}", file=sys.stderr)
            return 2
        print(f"sha256 verified: {digest}")
    else:
        print("WARNING: no --sha256 given. The archive's integrity is UNVERIFIED.", file=sys.stderr)
        print(f"         actual sha256: {digest}", file=sys.stderr)
        print("         Imported pages are quarantined as (imported, unverified) regardless.", file=sys.stderr)

    name = zpath.name
    for suffix in (".memoryfield.zip", ".zip"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    into = Path(args.into) if args.into else Path("Resources") / "Imported" / name
    into_abs = (vault / into).resolve() if not into.is_absolute() else into
    try:
        rel_into = str(into_abs.relative_to(vault)).replace("\\", "/")
    except ValueError:
        rel_into = str(into_abs)
    today = dt.date.today().isoformat()

    used: set[str] = set()
    imported = 0
    skipped: list[str] = []
    with zipfile.ZipFile(zpath) as zf:
        members = [i for i in zf.infolist() if not i.is_dir()]
        into_abs.mkdir(parents=True, exist_ok=True)
        for info in members:
            fname = info.filename
            base = os.path.basename(fname)
            if "/" in fname.strip("/"):
                skipped.append(fname)  # sub-directories are never pages
                continue
            if base in DEBRIS or base.endswith("~") or ".sync-conflict-" in base:
                continue
            if not base.endswith(".md"):
                skipped.append(fname)  # vector indexes, media: not pages
                continue
            raw = zf.read(info).decode("utf-8", errors="replace")
            if base == "listing.md":
                continue
            if base == "index.md":
                fm, body, _ = split_frontmatter(raw)
                (into_abs / "README.md").write_text(
                    f"---\ndate: {today}\ntags: [\"#resource\", \"#imported\"]\nsource: external\nconfidence: low\n"
                    f"imported_from: {zpath.name}\nimported_on: {today}\n---\n\n"
                    f"<!-- index.md of the imported memoryfield. Untrusted until reviewed. -->\n\n{body.lstrip()}",
                    encoding="utf-8",
                )
                continue
            fm, body, _ = split_frontmatter(raw)
            title = str(fm.get("title") or base[:-3].replace("-", " ").title())
            tags = fm.get("tags") or []
            if isinstance(tags, str):
                tags = [tags]
            tags = [t if str(t).startswith("#") else f"#{t}" for t in tags]
            # The page is a resource now, whatever it was at home.
            tags = [t for t in tags if t not in TYPE_TAGS]
            for t in ("#resource", "#imported"):
                if t not in tags:
                    tags.append(t)
            created = iso(fm.get("created"))
            new_fm: dict = {
                "date": (created or today)[:10],
                "title": title,
                "tags": tags,
                "source": "external",
                "confidence": "low",
                "imported_from": zpath.name,
                "imported_on": today,
                "imported_filename": base,
            }
            for k in ("uuid", "summary", "created", "updated"):
                if fm.get(k) not in (None, ""):
                    new_fm[k] = iso(fm[k]) if k in ("created", "updated") else fm[k]
            for k, v in fm.items():
                if k not in new_fm and k not in ("tags", "source", "confidence"):
                    new_fm[k] = v if not isinstance(v, (dt.date, dt.datetime)) else iso(v)
            if fm.get("source") or fm.get("confidence"):
                x = new_fm.get("x-cab") if isinstance(new_fm.get("x-cab"), dict) else {}
                x = dict(x)
                x.setdefault("original_source", fm.get("source"))
                x.setdefault("original_confidence", fm.get("confidence"))
                new_fm["x-cab"] = {k: v for k, v in x.items() if v is not None}
            out_name = safe_title_filename(title, used)
            (into_abs / out_name).write_text(dump_frontmatter(new_fm) + "\n" + body.lstrip("\n"), encoding="utf-8")
            imported += 1

    changed = update_quarantine(vault, rel_into)
    print(f"imported {imported} page(s) into {rel_into}/")
    if skipped:
        print(f"  skipped {len(skipped)} non-page file(s): {', '.join(skipped[:5])}{' …' if len(skipped) > 5 else ''}")
    print(f"  CLAUDE.md retrieval.quarantine {'updated' if changed else 'already lists this folder'}: {rel_into}")
    print("  pages are tagged #imported with source: external, confidence: low")
    print("  next: run /reindex so the local index sees them (no embeddings are imported)")
    return 0


# -------------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault", default=".", help="vault root (default: cwd)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ex = sub.add_parser("export", help="export folders to a .memoryfield.zip")
    ex.add_argument("folders", nargs="*", help="vault folders (default: Resources Areas)")
    ex.add_argument("--out", help="output zip path (default: <vault>.memoryfield.zip)")
    ex.set_defaults(func=cmd_export)
    im = sub.add_parser("import", help="import a .memoryfield.zip into the vault")
    im.add_argument("zip")
    im.add_argument("--into", help="target folder (default: Resources/Imported/<name>/)")
    im.add_argument("--sha256", help="expected sha256 of the zip; import refuses on mismatch")
    im.set_defaults(func=cmd_import)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
