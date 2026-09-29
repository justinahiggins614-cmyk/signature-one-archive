#!/usr/bin/env python3
"""Seal the hot specs file into small chunks so the page can lazy-load.

Layout:
    data/specs.jsonl                  hot file the generators append to
    data/volumes/specs-cNNNNN.jsonl.gz  sealed chunks, CHUNK_N specs each
    data/volumes/manifest.json        {"files": [...]} in load order

Chunks are ~150 specs (~1MB gz): the page fetches exactly one chunk when a
visitor opens a spec, instead of downloading the whole catalog. Idempotent
and incremental: tops up the last chunk if it has room, else writes new ones.
"""
import gzip
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "data")
HOT = os.path.join(DATA, "specs.jsonl")
VOLDIR = os.path.join(DATA, "volumes")
MANIFEST = os.path.join(VOLDIR, "manifest.json")
CHUNK_N = 150


def load_manifest():
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as fh:
            return json.load(fh).get("files", [])
    return []


def save_manifest(files):
    os.makedirs(VOLDIR, exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump({"files": files}, fh)


def chunk_path(n):
    return os.path.join(VOLDIR, f"specs-c{n:05d}.jsonl.gz")


def chunk_name(n):
    return f"volumes/specs-c{n:05d}.jsonl.gz"


def read_chunk_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return [ln if ln.endswith("\n") else ln + "\n"
                for ln in fh if ln.strip()]


def write_chunk_gz(path, lines):
    with gzip.open(path, "wb", compresslevel=6) as fh:
        for ln in lines:
            fh.write(ln.encode("utf-8"))


def main():
    os.makedirs(VOLDIR, exist_ok=True)
    files = load_manifest()
    chunks = [f for f in files if f.startswith("volumes/specs-c")]
    # Pick up legacy big volumes too (pre-chunk era); they stay as-is.
    legacy = [f for f in files if f.startswith("volumes/") and f not in chunks]
    n_chunk = len(chunks)

    if not os.path.exists(HOT):
        open(HOT, "a").close()
    with open(HOT, encoding="utf-8") as fh:
        lines = [ln if ln.endswith("\n") else ln + "\n"
                 for ln in fh if ln.strip()]

    idx = 0
    # Top up the last chunk first if it has room.
    if chunks and lines:
        last = os.path.join(DATA, chunks[-1])
        if os.path.exists(last):
            existing = read_chunk_gz(last)
            room = CHUNK_N - len(existing)
            if room > 0:
                take = lines[:room]
                write_chunk_gz(last, existing + take)
                idx = len(take)

    # Seal remaining lines into new chunks.
    while idx < len(lines):
        n_chunk += 1
        take = lines[idx:idx + CHUNK_N]
        write_chunk_gz(chunk_path(n_chunk), take)
        chunks.append(chunk_name(n_chunk))
        idx += len(take)

    # Hot file is now drained (generators keep appending to it).
    open(HOT, "w").close()
    save_manifest(legacy + chunks)
    print(f"chunks={len(chunks)} legacy={len(legacy)} hot=drained")


if __name__ == "__main__":
    main()
