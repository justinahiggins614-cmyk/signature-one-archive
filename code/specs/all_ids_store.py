"""Sharded store for the all_ids index: {spec_id: [category, line, title]}.

The old monolithic code/specs/all_ids.json grew past 70MB toward GitHub's
100MB single-file hard limit. The index is now split into per-ID-range part
files under code/specs/all_ids.d/ (50,000 IDs per part, ~6MB each).

All readers/writers go through this module:
  load_all_ids()  -> merged dict of every part, in numeric ID order
  save_all_ids(ids) -> rewrite the whole store from a full dict (migration,
                       or rebuild-from-volumes after a repair wipe)
  add_new_ids(entries) -> merge {spec_id: [...]} into the store, rewriting
                       only the affected part files; returns count added
Parts are written atomically (temp file + os.replace).
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
STORE_DIR = os.path.join(HERE, "all_ids.d")
LEGACY = os.path.join(HERE, "all_ids.json")  # removed; kept as a breadcrumb
PART = 50000


def _num(sid):
    m = re.search(r"(\d+)$", sid or "")
    return int(m.group(1)) if m else 0


def _part_bounds(n):
    n0 = ((n - 1) // PART) * PART + 1
    return n0, n0 + PART - 1


def part_path_for(n):
    n0, n1 = _part_bounds(n)
    return os.path.join(STORE_DIR, "all_ids-%06d-%06d.json" % (n0, n1))


def _list_parts():
    if not os.path.isdir(STORE_DIR):
        return []
    out = []
    for fn in os.listdir(STORE_DIR):
        m = re.match(r"all_ids-(\d+)-(\d+)\.json$", fn)
        if m:
            out.append((int(m.group(1)), os.path.join(STORE_DIR, fn)))
    return [p for _, p in sorted(out)]


def _atomic_write(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, separators=(",", ":"))
    os.replace(tmp, path)


def load_all_ids():
    """Merged {spec_id: [category, line, title]} across all part files."""
    ids = {}
    for p in _list_parts():
        with open(p, encoding="utf-8") as fh:
            ids.update(json.load(fh))
    return ids


def save_all_ids(ids):
    """Rewrite the whole store from a full dict. Removes stale parts."""
    os.makedirs(STORE_DIR, exist_ok=True)
    buckets = {}
    for sid, v in ids.items():
        n0, _ = _part_bounds(_num(sid))
        buckets.setdefault(n0, {})[sid] = v
    wanted = set()
    for n0 in sorted(buckets):
        path = part_path_for(n0)
        wanted.add(path)
        _atomic_write(path, buckets[n0])
    for p in _list_parts():
        if p not in wanted:
            os.remove(p)


def add_new_ids(entries):
    """Merge new {spec_id: [...]} entries, rewriting only affected parts.

    Returns the number of entries actually added (existing IDs untouched).
    """
    by_part = {}
    for sid, v in entries.items():
        n0, _ = _part_bounds(_num(sid))
        by_part.setdefault(n0, {})[sid] = v
    os.makedirs(STORE_DIR, exist_ok=True)
    added = 0
    for n0 in sorted(by_part):
        path = part_path_for(n0)
        cur = {}
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                cur = json.load(fh)
        changed = False
        for sid, v in by_part[n0].items():
            if sid not in cur:
                cur[sid] = v
                added += 1
                changed = True
        if changed:
            _atomic_write(path, cur)
    return added


def store_size_bytes():
    total = 0
    for p in _list_parts():
        total += os.path.getsize(p)
    return total
