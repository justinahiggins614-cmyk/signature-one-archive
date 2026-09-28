#!/usr/bin/env python3
"""Split the hot specs file into sealed volumes so no single data file
approaches GitHub's 100MB cap. Idempotent and incremental.

Layout:
    data/specs.jsonl                  hot file the generators append to
    data/volumes/specs-v001.jsonl ... sealed volumes, each <= VOL_MAX_BYTES
    data/volumes/manifest.json        {"files": [...]} in load order

The page loads the manifest, then each file in order.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "data")
HOT = os.path.join(DATA, "specs.jsonl")
VOLDIR = os.path.join(DATA, "volumes")
MANIFEST = os.path.join(VOLDIR, "manifest.json")
VOL_MAX_BYTES = 45 * 1024 * 1024  # well under GitHub's 100MB file cap


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
    return os.path.join(VOLDIR, f"specs-v{n:03d}.jsonl")


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

    # Move hot lines into volumes.
    with open(HOT, encoding="utf-8") as fh:
        lines = fh.readlines()

    # Top up the last volume first if it has room.
    idx = 0
    if vols:
        last = os.path.join(DATA, vols[-1])
        room = VOL_MAX_BYTES - os.path.getsize(last)
        if room > 0:
            with open(last, "a", encoding="utf-8") as out:
                while idx < len(lines):
                    b = len(lines[idx].encode("utf-8"))
                    if b > room:
                        break
                    out.write(lines[idx])
                    room -= b
                    idx += 1

    # Seal remaining lines into new volumes.
    while idx < len(lines):
        n_vol += 1
        vp = vol_path(n_vol)
        used = 0
        with open(vp, "w", encoding="utf-8") as out:
            while idx < len(lines):
                b = len(lines[idx].encode("utf-8"))
                if used + b > VOL_MAX_BYTES and used > 0:
                    break
                out.write(lines[idx])
                used += b
                idx += 1
        vols.append(f"volumes/specs-v{n_vol:03d}.jsonl")

    # Hot file is now drained (generators keep appending to it).
    open(HOT, "w").close()
    save_manifest(vols + ["specs.jsonl"])
    print(f"volumes={len(vols)} hot=drained")
    for v in vols:
        p = os.path.join(DATA, v)
        print(f"  {v}: {os.path.getsize(p) / 1048576:.1f}MB")


if __name__ == "__main__":
    main()
