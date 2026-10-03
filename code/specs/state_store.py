"""Sharded store for code/specs/state.json's bulky used_titles list.

The old monolithic code/specs/state.json grew past 50MB toward GitHub's
100MB single-file hard limit (the used_titles dedup list: 600k+ title
strings, appended by every drip run). The list is now sharded into
per-position part files under code/specs/state.d/ (50,000 titles per part,
~4MB each), mirroring the all_ids.d / all_ids_store.py pattern.

state.json itself keeps only the scalar counters: seed, next_index, catset.

All readers/writers go through this module (normally via
generate_specs.load_state() / generate_specs.save_state(), the central seam
used by generate_mix.py, generate_signature_line.py, generate_versions.py,
generate_revisions.py, generate_product_lines.py and seed_catalog_groups.py):
  load_scalars()          -> {"seed","next_index","catset"} from state.json
  save_scalars(d)         -> atomic write of the slim state.json
  load_used_titles()      -> full title list, in original append order
  append_used_titles(ts)  -> append titles (the normal generator path);
                             rewrites only the tail part(s); returns count
  save_used_titles(ts)    -> full rewrite from a list (repair path);
                             removes stale parts
  used_titles_count()     -> stored title count without a full load
  check_prefix(ts, n)     -> True if the first n stored titles equal ts[:n]
                             (cheap divergence tripwire: reads only the
                             parts covering the first n positions)

Parts are written atomically (temp file + os.replace).
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_JSON = os.path.join(HERE, "state.json")
STORE_DIR = os.path.join(HERE, "state.d")
PART = 50000
SCALAR_KEYS = ("seed", "next_index", "catset")


def _part_name(lo):
    return "titles-%06d-%06d.json" % (lo, lo + PART - 1)


def _list_parts():
    if not os.path.isdir(STORE_DIR):
        return []
    out = []
    for fn in os.listdir(STORE_DIR):
        m = re.match(r"titles-(\d+)-(\d+)\.json$", fn)
        if m:
            out.append((int(m.group(1)), os.path.join(STORE_DIR, fn)))
    return [p for _, p in sorted(out)]


def _atomic_write(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, separators=(",", ":"))
    os.replace(tmp, path)


def load_scalars():
    """Scalar counters from the slim state.json."""
    with open(STATE_JSON, encoding="utf-8") as fh:
        st = json.load(fh)
    return {k: st[k] for k in SCALAR_KEYS if k in st}


def save_scalars(d):
    """Atomic write of the slim state.json (scalars only)."""
    slim = {k: d[k] for k in SCALAR_KEYS if k in d}
    _atomic_write(STATE_JSON, slim)


def load_used_titles():
    """Full used_titles list, in original append order."""
    titles = []
    for p in _list_parts():
        with open(p, encoding="utf-8") as fh:
            titles.extend(json.load(fh))
    return titles


def used_titles_count():
    """Stored title count without loading every title."""
    total = 0
    for p in _list_parts():
        with open(p, encoding="utf-8") as fh:
            total += len(json.load(fh))
    return total


def check_prefix(titles, n):
    """True if the first n stored titles equal titles[:n].

    Reads only the parts covering positions 1..n. Used by
    generate_specs.save_state() as a cheap divergence tripwire before
    appending: if another writer changed the store underneath us, we fall
    back to a full rewrite instead of appending onto a moved base.
    """
    if n <= 0:
        return True
    want = titles[:n]
    got = []
    for p in _list_parts():
        with open(p, encoding="utf-8") as fh:
            got.extend(json.load(fh))
        if len(got) >= n:
            break
    return got[:n] == want


def append_used_titles(new_titles):
    """Append titles to the store, rewriting only the tail part(s).

    Returns the number of titles appended. Parts hold PART titles each;
    the tail part is topped up first, then new parts are created.
    """
    new_titles = list(new_titles)
    if not new_titles:
        return 0
    os.makedirs(STORE_DIR, exist_ok=True)
    parts = _list_parts()
    idx = 0
    if parts:
        tail = parts[-1]
        with open(tail, encoding="utf-8") as fh:
            cur = json.load(fh)
        room = PART - len(cur)
        if room > 0:
            take = new_titles[:room]
            cur.extend(take)
            _atomic_write(tail, cur)
            idx = room
    while idx < len(new_titles):
        lo = (used_titles_count() // PART) * PART + 1
        # lo from the on-disk count keeps numbering stable even if the
        # tail part above was just topped up.
        chunk = new_titles[idx:idx + PART]
        _atomic_write(os.path.join(STORE_DIR, _part_name(lo)), chunk)
        idx += len(chunk)
    return len(new_titles)


def save_used_titles(titles):
    """Full rewrite of the title store from a list (repair path).

    Removes stale parts. Preserves order exactly.
    """
    titles = list(titles)
    os.makedirs(STORE_DIR, exist_ok=True)
    wanted = set()
    for lo in range(1, len(titles) + 1, PART):
        path = os.path.join(STORE_DIR, _part_name(lo))
        wanted.add(path)
        _atomic_write(path, titles[lo - 1:lo - 1 + PART])
    for p in _list_parts():
        if p not in wanted:
            os.remove(p)


def store_size_bytes():
    total = 0
    for p in _list_parts():
        total += os.path.getsize(p)
    return total
