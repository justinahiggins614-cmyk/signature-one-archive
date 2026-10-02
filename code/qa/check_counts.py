#!/usr/bin/env python3
"""Count-vs-data check for the Spec Catalog.

Verifies the published indexes are complete and consistent:
  1. every shards.json entry resolves to a local index clone
  2. spec ID ranges are contiguous across main + shards (no gaps, no overlaps)
  3. total spec count across all indexes
  4. every chunk file referenced by the main index exists in data/volumes/
  5. words index + word-AI index counts (word-spec drip data)

Re-runnable: python3 code/qa/check_counts.py
Exit 0 when clean, 1 on findings.
"""
import gzip, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKSPACE = os.path.dirname(REPO)
ID_RE = re.compile(r"JAH-SPEC-(\d+)$")

def read_json_lines_gz(path):
    out = []
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln:
                out.append(json.loads(ln))
    return out

def shard_local_dir(entry):
    base = entry.get("base", "")
    if not base:
        return REPO
    m = re.search(r"github\.io/([^/]+)/?$", base)
    if not m:
        return None
    return os.path.join(WORKSPACE, m.group(1))

def main():
    findings = []
    shards_path = os.path.join(REPO, "data/index/shards.json")
    entries = json.load(open(shards_path)).get("shards", [])
    print("shard entries: %d" % len(entries))
    ranges = []
    total = 0
    for i, e in enumerate(entries):
        d = shard_local_dir(e)
        idx_path = os.path.join(d, e["index"]) if d else None
        if not d or not os.path.exists(idx_path):
            findings.append("shard entry %d: index not found locally (%s)" % (i, idx_path))
            continue
        rows = read_json_lines_gz(idx_path)
        ids = [int(ID_RE.match(r[0]).group(1)) for r in rows if ID_RE.match(r[0])]
        total += len(rows)
        first, last = (min(ids), max(ids)) if ids else (None, None)
        ranges.append((i, os.path.basename(d), len(rows), first, last))
        print("  [%2d] %-42s %7d rows  %s..%s" % (i, os.path.basename(d), len(rows), first, last))
    # contiguity: numeric ranges of the entries must not overlap
    for a in range(len(ranges)):
        for b in range(a + 1, len(ranges)):
            ia, namea, na, firsta, lasta = ranges[a]
            ib, nameb, nb, firstb, lastb = ranges[b]
            if firsta is not None and firstb is not None:
                if not (lasta < firstb or lastb < firsta):
                    findings.append("range overlap between entry %d (%s) and entry %d (%s)"
                                    % (ia, namea, ib, nameb))
    # check full ID coverage 1..max
    if ranges:
        lo = min(r[3] for r in ranges if r[3] is not None)
        hi = max(r[4] for r in ranges if r[4] is not None)
        print("overall ID span: JAH-SPEC-%06d .. JAH-SPEC-%06d" % (lo, hi))
        if lo != 1:
            findings.append("ID span does not start at 1 (starts at %d)" % lo)
        # count check: sum of rows should equal span length when no gaps
        span = hi - lo + 1
        if total != span:
            findings.append("total rows %d != ID span length %d (gap or missing chunk)" % (total, span))
    print("TOTAL spec rows across all indexes: %d" % total)

    # chunk files referenced by the main index must exist
    main_idx = os.path.join(REPO, "data/index/specs.idx.json.gz")
    missing_chunks = set()
    with gzip.open(main_idx, "rt", encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                chunk = json.loads(ln)[-1]
            except Exception:
                continue
            if chunk and not os.path.exists(os.path.join(REPO, "data", chunk)):
                missing_chunks.add(chunk)
    if missing_chunks:
        findings.append("%d referenced chunk files missing from data/volumes/ (e.g. %s)"
                        % (len(missing_chunks), sorted(missing_chunks)[0]))
    else:
        print("all chunk files referenced by the main index exist locally")

    # word-spec indexes
    for widx in ("data/index/words.idx.json.gz", "data/index/wordai.idx.json.gz"):
        p = os.path.join(REPO, widx)
        if os.path.exists(p):
            n = sum(1 for _ in gzip.open(p, "rt"))
            print("%s: %d rows" % (widx, n))
        else:
            print("%s: not present" % widx)

    print("---")
    if findings:
        print("FINDINGS (%d):" % len(findings))
        for f in findings:
            print("  - " + f)
        return 1
    print("counts clean: %d specs, contiguous, chunks present" % total)
    return 0

if __name__ == "__main__":
    sys.exit(main())
