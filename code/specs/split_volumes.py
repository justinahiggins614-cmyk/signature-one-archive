#!/usr/bin/env python3
"""Split the hot specs file into sealed volumes so no single data file
approaches GitHub's 100MB cap. Idempotent and incremental.

Layout:
    data/specs.jsonl                  hot file the generators append to
    data/volumes/specs-v001.jsonl ... sealed volumes, each <= VOL_MAX_BYTES
    data/volumes/manifest.json        {"files": [...]} in load order

The page loads the manifest, then each file in order.
"""
import gzip
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "data")
HOT = os.path.join(DATA, "specs.jsonl")
VOLDIR = os.path.join(DATA, "volumes")
MANIFEST = os.path.join(VOLDIR, "manifest.json")
VOL_MAX_BYTES = 45 * 1024 * 1024  # raw bytes per volume, well under GitHub's 100MB file cap


def load_manifest():
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as fh:
            return json.load(fh).get("files", [])
    return []


def save_manifest(files):
    os.makedirs(VOLDIR, exist_ok=True)
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        json.dump({"files": files}, fh)


def vol_path(n):
    return os.path.join(VOLDIR, f"specs-v{n:03d}.jsonl.gz")


def vol_name(n):
    return f"volumes/specs-v{n:03d}.jsonl.gz"


def read_vol_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return fh.readlines()


def write_vol_gz(path, lines):
    with gzip.open(path, "wb", compresslevel=6) as fh:
        for ln in lines:
            fh.write(ln.encode("utf-8"))


def main():
    os.makedirs(VOLDIR, exist_ok=True)
    files = load_manifest()
    vols = [f for f in files if f.startswith("volumes/")]
    n_vol = len(vols)

    if not os.path.exists(HOT):
        open(HOT, "a").close()
    hot_size = os.path.getsize(HOT)
    if hot_size <= VOL_MAX_BYTES and n_vol == 0:
        # Nothing sealed yet and hot is small: single-file mode.
        save_manifest(["specs.jsonl"])
        print(f"single-file mode, hot={hot_size / 1048576:.1f}MB")
        return

    # Move hot lines into volumes (volumes are gzip-compressed).
    with open(HOT, encoding="utf-8") as fh:
        lines = fh.readlines()

    # Top up the last volume first if it has room (decompress, append, recompress).
    idx = 0
    if vols:
        last = os.path.join(DATA, vols[-1])
        if last.endswith(".gz") and os.path.exists(last):
            existing = read_vol_gz(last)
            used = sum(len(ln.encode("utf-8")) for ln in existing)
            room = VOL_MAX_BYTES - used
            if room > 0:
                while idx < len(lines):
                    b = len(lines[idx].encode("utf-8"))
                    if b > room:
                        break
                    existing.append(lines[idx])
                    room -= b
                    idx += 1
                write_vol_gz(last, existing)

    # Seal remaining lines into new volumes.
    while idx < len(lines):
        n_vol += 1
        vp = vol_path(n_vol)
        chunk = []
        used = 0
        while idx < len(lines):
            b = len(lines[idx].encode("utf-8"))
            if used + b > VOL_MAX_BYTES and used > 0:
                break
            chunk.append(lines[idx])
            used += b
            idx += 1
        write_vol_gz(vp, chunk)
        vols.append(vol_name(n_vol))

    # Hot file is now drained (generators keep appending to it).
    open(HOT, "w").close()
    save_manifest(vols + ["specs.jsonl"])
    print(f"volumes={len(vols)} hot=drained")
    for v in vols:
        p = os.path.join(DATA, v)
        print(f"  {v}: {os.path.getsize(p) / 1048576:.1f}MB gz")


if __name__ == "__main__":
    main()
