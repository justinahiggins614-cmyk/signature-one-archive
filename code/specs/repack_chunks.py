#!/usr/bin/env python3
"""One-time repack: convert the big 45MB sealed volumes into small ~150-spec
chunks so the page can lazy-load one chunk per spec view (mobile-friendly).

Reads (in manifest order):
    data/volumes/specs-vNNN.jsonl.gz   (old sealed volumes)
    data/specs.jsonl                   (hot file, appended at the end)

Writes:
    data/chunks_new/specs-cNNNNN.jsonl.gz
    data/chunks_new/manifest.json

Does NOT touch the live data/volumes dir. The operator verifies counts and
the ID audit on chunks_new, then swaps the directories manually.

Chunk size 150 keeps each chunk ~1MB gz: fast to fetch on a phone.
"""
import gzip
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "data")
VOLDIR = os.path.join(DATA, "volumes")
HOT = os.path.join(DATA, "specs.jsonl")
OUTDIR = os.path.join(DATA, "chunks_new")
MANIFEST = os.path.join(VOLDIR, "manifest.json")
CHUNK_N = 150


def iter_old_lines():
    files = []
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as fh:
            files = json.load(fh).get("files", [])
    vols = [f for f in files if f.startswith("volumes/")]
    if not vols:
        # fall back to glob if manifest is missing
        import glob
        vols = sorted("volumes/" + os.path.basename(p)
                      for p in glob.glob(os.path.join(VOLDIR, "specs-v*.jsonl.gz")))
    for rel in vols:
        path = os.path.join(DATA, rel)
        opener = gzip.open if path.endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8") as fh:
            for ln in fh:
                if ln.strip():
                    yield ln if ln.endswith("\n") else ln + "\n"
    if os.path.exists(HOT):
        with open(HOT, encoding="utf-8") as fh:
            for ln in fh:
                if ln.strip():
                    yield ln if ln.endswith("\n") else ln + "\n"


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    files = []
    buf = []
    n_chunk = 0
    total = 0

    def flush():
        nonlocal n_chunk
        if not buf:
            return
        n_chunk += 1
        name = f"volumes/specs-c{n_chunk:05d}.jsonl.gz"
        # During the repack we stage into OUTDIR (data/chunks_new); the
        # manifest keeps the final "volumes/..." relative names so that after
        # the directory swap every reader works unchanged.
        path = os.path.join(OUTDIR, os.path.basename(name))
        with gzip.open(path, "wb", compresslevel=6) as fh:
            for ln in buf:
                fh.write(ln.encode("utf-8"))
        files.append(name)
        buf.clear()

    for ln in iter_old_lines():
        buf.append(ln)
        total += 1
        if len(buf) >= CHUNK_N:
            flush()
    flush()

    with open(os.path.join(OUTDIR, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump({"files": files}, fh)
    print(f"chunks={n_chunk} total_lines={total}")


if __name__ == "__main__":
    main()
