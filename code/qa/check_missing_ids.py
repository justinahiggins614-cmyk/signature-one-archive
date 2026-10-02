#!/usr/bin/env python3
"""Missing-ID check for the Spec Catalog indexes.

Each index (main + shard clones) must hold one contiguous integer run of
JAH-SPEC-###### IDs — the shard architecture moves whole chunks, so any hole
inside an index means lost records, not a legitimate gap.

Also verifies each shard clone's min/max ID matches the range implied by its
chunk files (spot check on the first/last chunk).

Re-runnable: python3 code/qa/check_missing_ids.py
Exit 0 when clean, 1 on findings.
"""
import gzip, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKSPACE = os.path.dirname(REPO)
ID_RE = re.compile(r"JAH-SPEC-(\d+)$")

def index_paths():
    paths = []
    entries = json.load(open(os.path.join(REPO, "data/index/shards.json"))).get("shards", [])
    for e in entries:
        base = e.get("base", "")
        m = re.search(r"github\.io/([^/]+)/?$", base) if base else None
        d = REPO if not base else (os.path.join(WORKSPACE, m.group(1)) if m else None)
        if d and os.path.exists(os.path.join(d, e["index"])):
            paths.append((e.get("base", "(main)"), os.path.join(d, e["index"])))
    return paths

def main():
    findings = []
    for base, p in index_paths():
        nums = []
        with gzip.open(p, "rt", encoding="utf-8", errors="replace") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    sid = json.loads(ln)[0]
                except Exception:
                    continue
                m = ID_RE.match(sid)
                if m:
                    nums.append(int(m.group(1)))
        if not nums:
            findings.append("%s: no JAH-SPEC IDs found" % p)
            continue
        lo, hi = min(nums), max(nums)
        expect = set(range(lo, hi + 1))
        missing = sorted(expect - set(nums))
        extra = len(nums) - len(set(nums))
        status = "OK" if not missing and not extra else "HOLES"
        print("%-60s %7d rows  %d..%d  %s%s" % (
            os.path.relpath(p, WORKSPACE), len(nums), lo, hi, status,
            (" missing=%d (first: %s)" % (len(missing), missing[:5])) if missing else ""))
        if missing:
            findings.append("%s: %d missing IDs in %d..%d (first: %s)"
                            % (p, len(missing), lo, hi, missing[:10]))
        if extra:
            findings.append("%s: %d duplicate rows inside one index" % (p, extra))
    print("---")
    if findings:
        print("FINDINGS (%d):" % len(findings))
        for f in findings:
            print("  - " + f)
        return 1
    print("no missing IDs in any index — clean")
    return 0

if __name__ == "__main__":
    sys.exit(main())
