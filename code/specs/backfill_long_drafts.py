#!/usr/bin/env python3
"""Backfill LONG-form patent drafts for every existing spec (2026-09-28).

Regenerates row['patent_draft'] deterministically (seed JAH-DRAFT-<spec_id>),
leaving every other field untouched, then repartitions into fresh 45MB
volumes and rewrites the manifest. Hot file is drained.
"""
import json
import os
import random
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_specs as g

DATA = os.path.join(HERE, "..", "..", "data")
VOLDIR = os.path.join(DATA, "volumes")
HOT = os.path.join(DATA, "specs.jsonl")
MANIFEST = os.path.join(VOLDIR, "manifest.json")
VOL_MAX = 45 * 1024 * 1024

CATKIND = {n: k for n, k, _, _ in g.ALLCATS}


def load_rows():
    rows = []
    with open(MANIFEST, encoding="utf-8") as fh:
        files = json.load(fh)["files"]
    for f in files:
        p = os.path.join(DATA, f)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    return rows


def main():
    rows = load_rows()
    print(f"loaded {len(rows)} rows", flush=True)
    done = 0
    for row in rows:
        kind = CATKIND[row["category"]]
        r = random.Random(f"JAH-DRAFT-{row['spec_id']}")
        row["patent_draft"] = g.build_patent_draft(
            r, kind, row["title"], row["category"],
            row["key_parameters"], row["signature_tool_mapping"])
        done += 1
        if done % 3000 == 0:
            print(f"  ...{done}/{len(rows)}", flush=True)

    # Repartition fresh at 45MB cap.
    shutil.rmtree(VOLDIR)
    os.makedirs(VOLDIR, exist_ok=True)
    files, n, cur = [], 1, 0
    fh = open(os.path.join(VOLDIR, f"specs-v{n:03d}.jsonl"), "w", encoding="utf-8")
    for row in rows:
        line = json.dumps(row, separators=(",", ":"), ensure_ascii=True) + "\n"
        b = len(line.encode("utf-8"))
        if cur + b > VOL_MAX and cur > 0:
            fh.close()
            n += 1
            cur = 0
            fh = open(os.path.join(VOLDIR, f"specs-v{n:03d}.jsonl"), "w", encoding="utf-8")
        fh.write(line)
        cur += b
    fh.close()
    files = [f"volumes/specs-v{i:03d}.jsonl" for i in range(1, n + 1)]
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump({"files": files}, fh)
    open(HOT, "w").close()  # drained; sealed into volumes
    total_mb = sum(os.path.getsize(os.path.join(VOLDIR, os.path.basename(f))) for f in files) / 1048576
    print(f"done: {len(rows)} drafts regenerated, {n} volumes, {total_mb:.1f}MB total", flush=True)


if __name__ == "__main__":
    main()
