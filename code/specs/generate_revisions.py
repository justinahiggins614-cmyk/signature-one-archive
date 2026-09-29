#!/usr/bin/env python3
"""Revision chains for Manon's iteration graph (2026-09-29):
SPEC -> Rev 2 -> Rev 3 -> ... (true chains: each revision parents from the
previous one, titled from the root spec).

Every spec is a potential root. Coverage in revision_coverage.json maps
root_id -> [highest_rev, latest_spec_id, root_title, category, line], so runs
extend chains without duplicates.

Usage: python3 generate_revisions.py [max_new]
Appends to the hot file; run split_volumes.py afterwards.
"""
import glob
import gzip
import json
import os
import random
import re
import sys

import generate_specs as g

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "data")
ALLIDS = os.path.join(HERE, "all_ids.json")
COVERAGE = os.path.join(HERE, "revision_coverage.json")

CATMAP = {cat: (cat, kind, cpc, devs) for (cat, kind, cpc, devs) in g.ALLCATS}


def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return default


def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)


def scan_all_ids():
    """{spec_id: [category, line, title]} for every spec in sealed volumes."""
    ids = {}
    for f in sorted(glob.glob(os.path.join(DATA, "volumes", "specs-*.jsonl*"))):
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
                ids[d["spec_id"]] = [d.get("category", ""), d.get("line") or "",
                                     d.get("title", "")]
    return ids


def scan_hot_ids(ids):
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
            if d["spec_id"] not in ids:
                ids[d["spec_id"]] = [d.get("category", ""), d.get("line") or "",
                                     d.get("title", "")]
                added += 1
    return added


def main():
    max_new = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    st = g.load_state()
    used = set(st.get("used_titles", []))
    idx = st.get("next_index", 1)

    ids = load_json(ALLIDS, None)
    if ids is None:
        print("building full spec id index from volumes...", flush=True)
        ids = scan_all_ids()
        save_json(ALLIDS, ids)
        print(f"  {len(ids)} specs indexed", flush=True)
    added = scan_hot_ids(ids)
    if added:
        save_json(ALLIDS, ids)
        print(f"  +{added} new specs from hot file", flush=True)

    # coverage: root_id -> [highest_rev, latest_spec_id, root_title, cat, line]
    coverage = load_json(COVERAGE, {})

    roots = list(ids.keys())
    rr = random.Random()
    rr.shuffle(roots)

    made = 0
    os.makedirs(os.path.dirname(g.DATA), exist_ok=True)
    with open(g.DATA, "a", encoding="utf-8") as fh:
        for root in roots:
            if made >= max_new:
                break
            # never start a revision chain on a spec that is itself a revision
            # target dedup: a root already in coverage just gets extended
            if root in coverage:
                rev, latest, rtitle, cat, line = coverage[root]
            else:
                cat, line, rtitle = ids[root]
                if not rtitle or cat not in CATMAP:
                    continue
                # don't start a fresh chain on a revision or product-line
                # member - those belong to an existing chain/line
                if re.search(r" (Rev \d+|V\d+)$", rtitle):
                    continue
                rev, latest = 1, root
            nrev = rev + 1
            cat_tuple = CATMAP.get(cat)
            if cat_tuple is None:
                continue
            rspec, rtkey = g.make_spec(
                idx, used, seed=f"JAH-REV-{root}-R{nrev}",
                category=cat_tuple, title_suffix=f" Rev {nrev}")
            used.add(rtkey)
            st.setdefault("used_titles", []).append(rtkey)
            rspec["line"] = line or g.line_for_category(cat, cat_tuple[1])
            rspec["line_note"] = (
                f"Revision {nrev} of {root} - the next iteration in this "
                f"specification's revision chain.")
            rspec["mix_from"] = [latest, "REVISION"]
            fh.write(json.dumps(rspec, separators=(",", ":"),
                                ensure_ascii=True) + "\n")
            coverage[root] = [nrev, rspec["spec_id"], rtitle, cat, line]
            idx += 1
            made += 1
            if made % 500 == 0:
                print(f"  ...{made}/{max_new}", flush=True)

    st["next_index"] = idx
    g.save_state(st)
    save_json(ALLIDS, ids)
    save_json(COVERAGE, coverage)
    print(f"done: +{made} revisions, next_index={idx}")


if __name__ == "__main__":
    main()
