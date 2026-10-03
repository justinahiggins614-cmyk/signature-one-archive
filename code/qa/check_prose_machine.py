#!/usr/bin/env python3
"""Sampled prose-vs-machine agreement check (Site #7 fix list BQ).

Verifies that the machine-readable index rows agree with the actual chunk
records they point to: spec_id, title, category, era, prepared_date.
A mismatch means the index and the published record disagree about the same
spec — the kind of drift this checker exists to catch.

Samples deterministically (seeded) across the main index + every shard clone
in ~/workspace/signature-one-archive-shard-*/data/index/specs.idx.json.gz.
Read-only: never writes to data/ or any drip-owned file.

Exit 0 = clean. Exit 1 = mismatches printed.
"""
import gzip
import json
import os
import random
import sys

HOME = os.path.expanduser("~")
MAIN = os.path.join(HOME, "workspace", "signature-one-archive")
SAMPLES_PER_INDEX = 40
SEED = 20261003

# index row layout (code/specs/build_index.py):
# [spec_id, title, abstract, category, cpc, era, prepared_date, ..., chunk_file]
I_ID, I_TITLE, I_CAT, I_CPC, I_ERA, I_PREP, I_CHUNK = 0, 1, 3, 4, 5, 6, -1


def norm(s):
    return " ".join(str(s or "").split())


def load_rows(path):
    rows = []
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    return rows


def check_index(name, idx_path, vol_dir):
    rows = load_rows(idx_path)
    if not rows:
        print("SKIP %s: empty index" % name)
        return []
    rng = random.Random("%s-%d" % (SEED, hash(name) % 10 ** 8))
    sample = rng.sample(rows, min(SAMPLES_PER_INDEX, len(rows)))
    bad = []
    for r in sample:
        chunk = os.path.join(vol_dir, os.path.basename(r[I_CHUNK]))
        rec = None
        try:
            with gzip.open(chunk, "rt", encoding="utf-8") as fh:
                for ln in fh:
                    try:
                        d = json.loads(ln)
                    except Exception:
                        continue
                    if d.get("spec_id") == r[I_ID]:
                        rec = d
                        break
        except Exception as e:
            bad.append((r[I_ID], "chunk unreadable: %s" % e))
            continue
        if rec is None:
            bad.append((r[I_ID], "record missing from chunk %s" % r[I_CHUNK]))
            continue
        for label, idxv, recv in (("title", r[I_TITLE], rec.get("title")),
                                  ("category", r[I_CAT], rec.get("category")),
                                  ("cpc", r[I_CPC], rec.get("cpc")),
                                  ("era", r[I_ERA], rec.get("era")),
                                  ("prepared", r[I_PREP],
                                   rec.get("prepared_date") or rec.get("prepared"))):
            if norm(idxv) != norm(recv):
                bad.append((r[I_ID], "%s mismatch: index=%r chunk=%r"
                            % (label, idxv, recv)))
    print("%-42s sampled %3d  mismatches %d"
          % (name, len(sample), len(bad)))
    return bad


def main():
    all_bad = []
    main_idx = os.path.join(MAIN, "data", "index", "specs.idx.json.gz")
    all_bad += check_index("main", main_idx,
                           os.path.join(MAIN, "data", "volumes"))
    shards_doc = json.load(open(os.path.join(
        MAIN, "data", "index", "shards.json"), encoding="utf-8"))
    for entry in shards_doc.get("shards", []):
        base = entry.get("base") or ""
        if not base:
            continue
        repo = base.rstrip("/").rsplit("/", 1)[-1]
        clone = os.path.join(HOME, "workspace", repo)
        idx = os.path.join(clone, entry.get("index",
                                            "data/index/specs.idx.json.gz"))
        if not os.path.exists(idx):
            print("SKIP %s: no local clone index" % repo)
            continue
        all_bad += check_index(repo, idx, os.path.join(clone, "data", "volumes"))
    if all_bad:
        print("---\n%d mismatches:" % len(all_bad))
        for sid, why in all_bad[:20]:
            print(" ", sid, "-", why)
        sys.exit(1)
    print("---\nprose-vs-machine agreement: clean")


if __name__ == "__main__":
    main()
