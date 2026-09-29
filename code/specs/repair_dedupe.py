#!/usr/bin/env python3
"""One-time repair (2026-09-29): dedupe spec records by spec_id.

A drip run appended ~1000 specs whose ids collided with the next_index
sequence, so the hot file contains duplicate spec_ids (the page renders
every line, so dupes would show as double cards). This script:

  1. reads all sealed volumes (in order) + the hot file
  2. keeps the FIRST occurrence of each spec_id
  3. repartitions everything into fresh .jsonl.gz volumes (45MB raw cap)
  4. clears the hot file, rewrites the manifest
  5. resets state.json: next_index = max numeric id + 1,
     used_titles rebuilt from surviving records
  6. removes derived indexes (all_ids, revision_coverage, product_lines)
     so generators rebuild them cleanly

Run from the repo root: python3 code/specs/repair_dedupe.py
"""
import glob
import gzip
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "data")
HOT = os.path.join(DATA, "specs.jsonl")
VOLDIR = os.path.join(DATA, "volumes")
TMPDIR = VOLDIR + ".tmp-repair"
MANIFEST = os.path.join(VOLDIR, "manifest.json")
STATE = os.path.join(HERE, "state.json")
VOL_MAX_BYTES = 45 * 1024 * 1024


def read_lines(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as fh:
        return [ln for ln in fh if ln.strip()]


def main():
    files = sorted(glob.glob(os.path.join(VOLDIR, "specs-*.jsonl*")))
    if os.path.exists(HOT) and os.path.getsize(HOT):
        files.append(HOT)
    print(f"reading {len(files)} files...", flush=True)

    seen = set()
    dupes = 0
    maxidx = 0
    titles = []

    # repartition into a TEMP dir first, streaming, so the live volumes
    # stay untouched until the very end (never delete-then-read)
    shutil.rmtree(TMPDIR, ignore_errors=True)
    os.makedirs(TMPDIR, exist_ok=True)
    names = []
    vol_n = 1
    vol_fh = None
    vol_size = 0

    def open_vol():
        global vol_fh, vol_size, vol_n
        p = os.path.join(TMPDIR, f"specs-v{vol_n:03d}.jsonl.gz")
        vol_fh = gzip.open(p, "wt", encoding="utf-8")
        names.append(f"volumes/specs-v{vol_n:03d}.jsonl.gz")
        vol_size = 0
        vol_n += 1

    def emit(ln):
        global vol_fh, vol_size
        if vol_fh is None:
            open_vol()
        b = ln.encode("utf-8")
        if vol_size and vol_size + len(b) > VOL_MAX_BYTES:
            vol_fh.close()
            open_vol()
        vol_fh.write(ln)
        vol_size += len(b)

    kept = 0
    for f in files:
        for ln in read_lines(f):
            try:
                d = json.loads(ln)
            except Exception:
                continue
            sid = d.get("spec_id")
            if not sid or sid in seen:
                dupes += 1
                continue
            seen.add(sid)
            emit(ln if ln.endswith("\n") else ln + "\n")
            kept += 1
            m = re.search(r"(\d+)$", sid)
            if m:
                v = int(m.group(1))
                if v > maxidx:
                    maxidx = v
            if d.get("title"):
                titles.append(d["title"].lower())
    if vol_fh is not None:
        vol_fh.close()
    print(f"kept {kept} unique, dropped {dupes} duplicates", flush=True)
    print(f"wrote {len(names)} volumes to temp dir", flush=True)
    with open(os.path.join(TMPDIR, "manifest.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"files": names}, fh)

    # atomic-ish swap: only now replace the live volumes
    shutil.rmtree(VOLDIR, ignore_errors=True)
    os.replace(TMPDIR, VOLDIR)
    print("volumes swapped in", flush=True)

    # clear hot file
    open(HOT, "w").close()

    # reset state
    st = {}
    if os.path.exists(STATE):
        st = json.load(open(STATE, encoding="utf-8"))
    st["next_index"] = maxidx + 1
    st["used_titles"] = titles
    json.dump(st, open(STATE, "w", encoding="utf-8"))
    print(f"state reset: next_index={maxidx + 1}, {len(titles)} titles", flush=True)

    # drop derived indexes - generators rebuild them
    for name in ("all_ids.json", "revision_coverage.json",
                 "product_lines.json", "software_ids.json",
                 "version_coverage.json"):
        p = os.path.join(HERE, name)
        if os.path.exists(p):
            os.remove(p)
            print(f"  removed {name}", flush=True)
    print("repair complete")


if __name__ == "__main__":
    main()
