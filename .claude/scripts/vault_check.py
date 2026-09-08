#!/usr/bin/env python3
"""Check the invariants the README claims are load-bearing.

Four of them, and only four. Each corresponds to a promise made in
CLAUDE.md, README.md, or /install; a check that doesn't defend a stated
promise doesn't belong here.

  1. No unrendered `{{date:...}}` outside Templates/. CLAUDE.md is explicit
     that Claude is Templater here — a literal directive in a note means a
     command wrote one and nobody noticed.
  2. Every [[wikilink]] resolves. They're grep anchors today and real links
     under Obsidian later; a dangling one is invisible in both.
  3. Every note's YAML frontmatter parses. "Every note gets frontmatter" is
     worth nothing if it's malformed.
  4. No seed content shadows an example. A bead or memory that duplicates an
     `example-` one without the marker outlives /install's cleanup, and the
     user inherits a fabricated fact about people who exist nowhere in their
     vault. This happened twice before it was caught.

Exit 1 on any violation. Run with --fix-list to print paths only.
"""
import json, os, re, sys

# Archive/ stays in scope: notes get archived, links to them don't stop
# mattering, and an archived note is still a note somebody will read.
SKIP_DIRS = {'.git', '.beads', '.index', 'node_modules', 'docs', '.github'}
TEMPLATE_DIR = 'Templates'

def notes(root='.'):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        for f in filenames:
            if f.endswith('.md'):
                yield os.path.relpath(os.path.join(dirpath, f), root)

def strip_code(text):
    """Blank out fenced blocks and inline code, preserving line numbers.

    Every one of these checks is about what a note *asserts*. Documentation
    that quotes the syntax — "maintain `[[wikilinks]]`", "`{{date:...}}` is a
    directive" — asserts nothing and must not trip anything, or the check
    cries wolf on its own README and gets ignored, which is the only real
    failure mode a linter has.
    """
    text = re.sub(r'```.*?```', lambda m: re.sub(r'[^\n]', ' ', m.group(0)), text, flags=re.S)
    text = re.sub(r'`[^`\n]*`', lambda m: ' ' * len(m.group(0)), text)
    return text


def parse_frontmatter(text):
    """Minimal YAML-ish frontmatter validation, no dependency.

    Only checks structural shape: a closing delimiter, and that every
    top-level line is a `key: value`, a list item, or a continuation.
    Deliberately not a YAML parser — this runs on every push and a false
    positive is worse than a missed exotic edge case.
    """
    if not text.startswith('---\n'):
        return None                      # no frontmatter is a separate concern
    end = text.find('\n---', 3)
    if end == -1:
        return 'frontmatter opened with --- but never closed'
    for i, line in enumerate(text[4:end].split('\n'), start=2):
        if not line.strip() or line.startswith((' ', '\t', '-', '#')):
            continue
        if ':' not in line:
            return f'line {i}: not a key: value pair -> {line.strip()[:60]!r}'
    return None

def check_seed_shadows(root):
    """Flag unmarked twins of example content in the beads seed.

    /install clears the seed by judgment — "bd list to find them" — not by
    keying on the example- marker, so there is no general way to ask whether a
    given bead is disposable. What *is* mechanical is the failure that actually
    shipped twice: something that duplicates an example without carrying the
    marker, and therefore survives a cleanup that removes its twin. Checking
    only that costs no false positives, which is the whole budget a check like
    this gets.
    """
    path = os.path.join(root, '.beads', 'issues.jsonl')
    if not os.path.exists(path):
        return []

    memories, issues, fails = {}, [], []
    for i, line in enumerate(open(path, encoding='utf-8'), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError as e:
            fails.append(('.beads/issues.jsonl', i, f'unparseable JSON: {e}'))
            continue
        if d.get('_type') == 'memory':
            memories[d.get('key', '')] = i
        elif d.get('id'):
            issues.append((i, d))

    for key, line in memories.items():
        if key.startswith('example-') and key[len('example-'):] in memories:
            bare = key[len('example-'):]
            fails.append(('.beads/issues.jsonl', memories[bare],
                          f'memory {bare!r} shadows {key!r} without the example- marker — '
                          f'it survives /install and is auto-injected into every session'))

    seeded = {}
    for line, d in issues:
        if 'example-seed' in (d.get('labels') or []):
            seeded.setdefault((d.get('title') or '').strip().lower(), d.get('id'))
    for line, d in issues:
        title = (d.get('title') or '').strip().lower()
        if title in seeded and 'example-seed' not in (d.get('labels') or []) \
                and d.get('status') != 'closed':
            fails.append(('.beads/issues.jsonl', line,
                          f'issue {d.get("id")} duplicates seeded {seeded[title]} without the '
                          f'example-seed label — it outlives the seed it refers to'))
    return fails


def main():
    root = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else '.'
    all_notes = sorted(notes(root))
    stems = {os.path.splitext(p)[0] for p in all_notes}
    stems |= {os.path.splitext(os.path.basename(p))[0] for p in all_notes}

    fails = []
    for rel in all_notes:
        raw = open(os.path.join(root, rel), encoding='utf-8', errors='replace').read()
        text = strip_code(raw)
        in_templates = rel.startswith(TEMPLATE_DIR + os.sep)

        if not in_templates and '{{date:' in text:
            n = text[:text.index('{{date:')].count('\n') + 1
            fails.append((rel, n, 'unrendered {{date:...}} directive — a command wrote a template literal'))

        # Templates are placeholders by design: [[Areas/Parent Area]] is an
        # instruction to the filler, not a link that should resolve.
        for m in (() if in_templates else re.finditer(r'\[\[([^\]|#^]+)', text)):
            target = m.group(1).strip()
            if not target or target.startswith(('http', '/')):
                continue
            if target not in stems and os.path.splitext(target)[0] not in stems:
                n = text[:m.start()].count('\n') + 1
                fails.append((rel, n, f'dangling wikilink [[{target}]]'))

        err = parse_frontmatter(raw)
        if err:
            fails.append((rel, 1, f'frontmatter: {err}'))

    fails += check_seed_shadows(root)

    for rel, line, msg in fails:
        print(f'{rel}:{line}: {msg}')
    print(f'\n{len(all_notes)} notes checked, {len(fails)} problem(s).', file=sys.stderr)
    return 1 if fails else 0

if __name__ == '__main__':
    sys.exit(main())
