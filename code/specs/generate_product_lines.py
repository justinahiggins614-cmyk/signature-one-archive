#!/usr/bin/env python3
"""Product lines for Manon's iteration graph (2026-09-29):
COMPOUND/SPEC -> PRODUCT LINE -> V1 -> V2 -> V3 ...

A product line is founded on any existing spec (spec, hybrid compound,
revision...). Members are full draft specs titled "<LineName> V<n>",
each parented from the previous member (mix_from=[prev_id, "PRODUCTLINE"]).

Lines tracked in product_lines.json:
  line_id -> {name, founder, latest, latest_id, cat, line}

Usage: python3 generate_product_lines.py [max_new]
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
LINES = os.path.join(HERE, "product_lines.json")

CATMAP = {cat: (cat, kind, cpc, devs) for (cat, kind, cpc, devs) in g.ALLCATS}

SERIES = ["X-Series", "Pro Line", "Ultra Series", "Prime Line", "Nova Series",
          "Apex Line", "Core Series", "Edge Line", "Titan Series", "Flux Line",
          "Vector Series", "Pulse Line"]

# share the id index with generate_revisions
sys.path.insert(0, HERE)
import generate_revisions as revmod
import all_ids_store


def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return default


def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)


def dev_of_title(title):
    t = title[10:] if title.startswith("Signature ") else title
    d = t.split(" for ")[0].strip()
    return d[:48] or "Unit"


def main():
    max_new = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    st = g.load_state()
    used = set(st.get("used_titles", []))
    idx = st.get("next_index", 1)

    ids = all_ids_store.load_all_ids()
    if not ids:
        print("building full spec id index from volumes...", flush=True)
        ids = revmod.scan_all_ids()
        all_ids_store.save_all_ids(ids)
        print(f"  {len(ids)} specs indexed", flush=True)
    before = set(ids)
    added = revmod.scan_hot_ids(ids)
    if added:
        all_ids_store.add_new_ids({k: v for k, v in ids.items()
                                   if k not in before})

    lines = load_json(LINES, {})
    # guard: skip malformed all_ids store entries (see note in
    # generate_revisions.py — 2026-10-04 a backfill wrote 1000 bare [] entries)
    founders = []
    for pid, v in ids.items():
        if not isinstance(v, (list, tuple)) or len(v) != 3:
            continue
        cat, _ln, title = v
        if title and cat in CATMAP \
                and not re.search(r" (Rev \d+|V\d+)$", title):
            founders.append(pid)
    rr = random.Random()
    rr.shuffle(founders)
    line_ids = list(lines.keys())
    rr.shuffle(line_ids)

    made = 0
    fi = 0
    os.makedirs(os.path.dirname(g.DATA), exist_ok=True)
    with open(g.DATA, "a", encoding="utf-8") as fh:
        while made < max_new:
            # ~1 in 6 actions founds a brand-new line, the rest extend lines
            if line_ids and (made % 6 != 0 or fi >= len(founders)):
                lid = line_ids[made % len(line_ids)]
                L = lines[lid]
                ver = L["latest"] + 1
                parent_id = L["latest_id"]
                name, cat, line = L["name"], L["cat"], L["line"]
                seed = f"JAH-PLINE-{lid}-V{ver}"
                note = (f"V{ver} of the {name} product line "
                        f"(founded on {L['founder']}).")
            else:
                if fi >= len(founders):
                    break
                founder = founders[fi]
                fi += 1
                cat, line, title = ids[founder]
                lid = f"PL-{idx:06d}"
                ver, parent_id = 1, founder
                seed = f"JAH-PLINE-{lid}-V1"
                name = None  # derived from the V1 product after generation
                note = None
            cat_tuple = CATMAP.get(cat)
            if cat_tuple is None:
                continue
            pspec, ptkey = g.make_spec(idx, used, seed=seed, category=cat_tuple)
            if ver == 1:
                # name the line after the actual V1 product, not the founder
                name = f"{dev_of_title(pspec['title'])} {rr.choice(SERIES)}"
                lid = f"PL-{idx:06d}"
                note = (f"V1 of the {name} product line "
                        f"(founded on {founder}).")
            pspec["title"] = pspec["title"] + f" \u2014 {name} V{ver}"
            tk = pspec["title"].lower()
            if tk in used:
                # make_spec already uniquified the base; the suffix keeps it unique
                pass
            used.add(tk)
            st.setdefault("used_titles", []).append(tk)
            pspec["line"] = line or g.line_for_category(cat, cat_tuple[1])
            pspec["line_note"] = note + " All versions of this product line."
            pspec["mix_from"] = [parent_id, "PRODUCTLINE"]
            fh.write(json.dumps(pspec, separators=(",", ":"),
                                ensure_ascii=True) + "\n")
            founder_id = parent_id if ver == 1 else L["founder"]
            lines[lid] = {"name": name, "founder": founder_id,
                          "latest": ver, "latest_id": pspec["spec_id"],
                          "cat": cat, "line": pspec["line"]}
            if ver == 1:
                line_ids.append(lid)
            idx += 1
            made += 1
            if made % 500 == 0:
                print(f"  ...{made}/{max_new}", flush=True)

    st["next_index"] = idx
    g.save_state(st)
    # ids is unchanged since load (hot-file additions were merged above),
    # so no index rewrite is needed here.
    save_json(LINES, lines)
    print(f"done: +{made} product-line members across {len(lines)} lines, next_index={idx}")


if __name__ == "__main__":
    main()
