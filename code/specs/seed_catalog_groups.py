"""Seed Manon's catalog groups: a few base specs of every new catalog category
plus version variants of each ("all versions we can make of each").
Appends to the hot file; run split_volumes.py afterwards.
Usage: python3 seed_catalog_groups.py"""
import json
import os
import sys

import generate_specs as g
from catalog_groups import iter_group_cats

BASES = 3
VARIANTS = 2
SUFFIXES = ["Pro", "Lite", "Max", "Portable", "Ultra", "Mini",
            "Enterprise", "Turbo", "Plus", "Nano"]


def main():
    st = g.load_state()
    used = set(st["used_titles"])
    idx = st["next_index"]
    cats = {}
    for _grp, cn, k, cpc, devs in iter_group_cats():
        if cn in g.EXISTING_NAMES:
            continue  # already covered by the original 122 categories
        cats.setdefault(cn, []).append((cn, k, cpc, devs))
    print(f"seeding {len(cats)} new categories", flush=True)
    os.makedirs(os.path.dirname(g.DATA), exist_ok=True)
    made = 0
    with open(g.DATA, "a", encoding="utf-8") as fh:
        for n, cn in enumerate(sorted(cats)):
            variants = cats[cn]
            for b in range(BASES):
                cat = variants[b % len(variants)]
                spec, tkey = g.make_spec(idx, used,
                                         seed=f"JAH-GRP-{cn}-{b}",
                                         category=cat)
                used.add(tkey)
                st["used_titles"].append(tkey)
                spec["line"] = g.line_for_category(cn, cat[1])
                pid = spec["spec_id"]
                fh.write(json.dumps(spec, separators=(",", ":"),
                                    ensure_ascii=True) + "\n")
                idx += 1
                made += 1
                for v in range(VARIANTS):
                    sfx = SUFFIXES[(b * VARIANTS + v) % len(SUFFIXES)]
                    vcat = variants[(b + v) % len(variants)]
                    vspec, vtkey = g.make_spec(
                        idx, used, seed=f"JAH-VAR-{pid}-{sfx}",
                        category=vcat)
                    used.add(vtkey)
                    st["used_titles"].append(vtkey)
                    vspec["title"] = spec["title"] + " " + sfx
                    vspec["line"] = g.line_for_category(cn, vcat[1])
                    vspec["line_note"] = (
                        f"Variant '{sfx}' of {pid} - all versions of "
                        "this catalog entry.")
                    vspec["mix_from"] = [pid, "VARIANT"]
                    fh.write(json.dumps(vspec, separators=(",", ":"),
                                        ensure_ascii=True) + "\n")
                    idx += 1
                    made += 1
            if (n + 1) % 40 == 0:
                print(f"  ...{n + 1}/{len(cats)} categories", flush=True)
    st["next_index"] = idx
    g.save_state(st)
    print(f"done: +{made} new group seeds, next_index={idx}")


if __name__ == "__main__":
    main()
