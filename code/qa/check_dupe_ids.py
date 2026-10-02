#!/usr/bin/env python3
"""Duplicate-ID check for the Spec Catalog indexes.

Scans the main specs index and every shard clone present locally for
duplicate spec IDs. The catalog rule: an ID is the record's name forever —
never reused, never silently changed. A duplicate ID means a bug (e.g. a
stale state.json re-IDing an appended block); report it, do not delete data.

Re-runnable: python3 code/qa/check_dupe_ids.py [--fast]
  --fast scans the main index only (shards are frozen storage).
Exit 0 when clean, 1 when duplicates found.
"""
import gzip, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKSPACE = os.path.dirname(REPO)

def index_paths(fast):
    paths = [os.path.join(REPO, "data/index/specs.idx.json.gz")]
    if fast:
        return paths
    entries = json.load(open(os.path.join(REPO, "data/index/shards.json"))).get("shards", [])
    for e in entries:
        base = e.get("base", "")
        m = re.search(r"github\.io/([^/]+)/?$", base) if base else None
        d = REPO if not base else (os.path.join(WORKSPACE, m.group(1)) if m else None)
        if d and os.path.exists(os.path.join(d, e["index"])):
            p = os.path.join(d, e["index"])
            if p not in paths:
                paths.append(p)
    return paths

def main():
    fast = "--fast" in sys.argv
    dupes = {}
    total = 0
    for p in index_paths(fast):
        seen = set()
        with gzip.open(p, "rt", encoding="utf-8", errors="replace") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    sid = json.loads(ln)[0]
                except Exception:
                    continue
                total += 1
                if sid in seen:
                    dupes.setdefault(p, []).append(sid)
                else:
                    seen.add(sid)
        print("scanned %s (%s mode)" % (os.path.relpath(p, WORKSPACE), "fast" if fast else "full"))
    print("---")
    print("rows scanned: %d" % total)
    if dupes:
        n = sum(len(v) for v in dupes.values())
        print("FINDINGS: %d duplicate ID occurrences" % n)
        for p, ids in dupes.items():
            print("  %s: %s%s" % (os.path.relpath(p, WORKSPACE), ", ".join(ids[:10]),
                                  "..." if len(ids) > 10 else ""))
        return 1
    print("no duplicate IDs — clean")
    return 0

if __name__ == "__main__":
    sys.exit(main())
