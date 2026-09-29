#!/usr/bin/env python3
"""Version variants for every software-kind spec (Manon's order 2026-09-28):
for each code/python/binary type patent, make all applicable versions:
Deterministic, Hybrid, Hash, Online, Offline, Phone App, PC App, Web App, CLI.

Each version is a full draft-spec record (all lenses, master schema), titled
"<parent title> (<Version> Edition)", with mix_from=[parent_id, "VARIANT"]
lineage and a VARIANT badge on the page.

Coverage is tracked in version_coverage.json so the drip keeps filling
missing versions over time without duplicates.

Usage: python3 generate_versions.py [max_new]
Appends to the hot file; run split_volumes.py afterwards.
"""
import glob
import gzip
import json
import os
import random
import sys

import generate_specs as g

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "data")
COVERAGE = os.path.join(HERE, "version_coverage.json")
SOFTIDS = os.path.join(HERE, "software_ids.json")

VERSIONS = [
    ("Deterministic", "deterministic execution - identical inputs always produce identical outputs"),
    ("Hybrid", "hybrid execution - local deterministic core combined with adaptive remote processing"),
    ("Hash", "hash-verified edition - content-addressed with integrity verification on every run"),
    ("Online", "online edition - cloud-connected, network features enabled"),
    ("Offline", "offline edition - fully self-contained, no network required"),
    ("Phone App", "phone app edition - mobile embodiment for handheld devices"),
    ("PC App", "PC app edition - desktop embodiment for personal computers"),
    ("Web App", "web app edition - runs in the browser, no install required"),
    ("CLI", "command-line edition - terminal-driven interface"),
]
VER_NAMES = [v for v, _ in VERSIONS]
VER_DESC = dict(VERSIONS)

CATMAP = {cat: (cat, kind, cpc, devs) for (cat, kind, cpc, devs) in g.ALLCATS}
CAT2KIND = {cat: kind for (cat, kind, cpc, devs) in g.ALLCATS}


def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return default


def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)


def scan_volume_ids():
    """One-time full scan: {spec_id: [category, line]} for software-kind specs."""
    ids = {}
    for f in sorted(glob.glob(os.path.join(DATA, "volumes", "specs-v*.jsonl*"))):
        opener = gzip.open if f.endswith(".gz") else open
        with opener(f, "rt", encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    d = json.loads(ln)
                except Exception:
                    continue
                if CAT2KIND.get(d.get("category", "")) == "software":
                    ids[d["spec_id"]] = [d.get("category", ""), d.get("line") or ""]
    return ids


def scan_hot_ids(ids):
    """Merge any new software specs sitting in the hot file."""
    hot = os.path.join(DATA, "specs.jsonl")
    if not os.path.exists(hot):
        return 0
    added = 0
    with open(hot, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                d = json.loads(ln)
            except Exception:
                continue
            if CAT2KIND.get(d.get("category", "")) == "software" and d["spec_id"] not in ids:
                ids[d["spec_id"]] = [d.get("category", ""), d.get("line") or ""]
                added += 1
    return added


def main():
    max_new = int(sys.argv[1]) if len(sys.argv) > 1 else 900
    st = g.load_state()
    used = set(st.get("used_titles", []))
    idx = st.get("next_index", 1)

    ids = load_json(SOFTIDS, None)
    if ids is None:
        print("building software id index from volumes...", flush=True)
        ids = scan_volume_ids()
        save_json(SOFTIDS, ids)
        print(f"  {len(ids)} software specs indexed", flush=True)
    added = scan_hot_ids(ids)
    if added:
        save_json(SOFTIDS, ids)
        print(f"  +{added} new software specs from hot file", flush=True)

    coverage = load_json(COVERAGE, {})
    # candidate parents: those missing at least one version
    cands = [pid for pid in ids if len(coverage.get(pid, [])) < len(VER_NAMES)]
    print(f"{len(ids)} software specs, {len(cands)} still missing versions", flush=True)
    if not cands:
        print("nothing to do")
        return
    rr = random.Random()
    rr.shuffle(cands)

    made = 0
    os.makedirs(os.path.dirname(g.DATA), exist_ok=True)
    with open(g.DATA, "a", encoding="utf-8") as fh:
        for pid in cands:
            if made >= max_new:
                break
            done = set(coverage.get(pid, []))
            todo = [v for v in VER_NAMES if v not in done]
            if not todo:
                continue
            ver = todo[0]
            cat, line = ids[pid]
            cat_tuple = CATMAP.get(cat)
            if cat_tuple is None:
                continue
            vspec, vtkey = g.make_spec(
                idx, used, seed=f"JAH-VER-{pid}-{ver}",
                category=cat_tuple, title_suffix=f" ({ver} Edition)")
            used.add(vtkey)
            st.setdefault("used_titles", []).append(vtkey)
            vspec["line"] = line or g.line_for_category(cat, "software")
            vspec["line_note"] = (f"Version '{ver}' of {pid} - {VER_DESC[ver]}. "
                                  f"All versions of this software entry.")
            vspec["mix_from"] = [pid, "VARIANT"]
            fh.write(json.dumps(vspec, separators=(",", ":"),
                                ensure_ascii=True) + "\n")
            done.add(ver)
            coverage[pid] = sorted(done)
            idx += 1
            made += 1
            if made % 500 == 0:
                print(f"  ...{made}/{max_new}", flush=True)

    st["next_index"] = idx
    g.save_state(st)
    save_json(SOFTIDS, ids)
    save_json(COVERAGE, coverage)
    print(f"done: +{made} version variants, next_index={idx}")


if __name__ == "__main__":
    main()
