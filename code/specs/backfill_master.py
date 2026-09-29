#!/usr/bin/env python3
"""Backfill every spec's patent_draft with the JAH-MASTER-1.0 schema.

Regenerates ONLY patent_draft per spec, using an independent seed
JAH-MASTER-<spec_id> so published content elsewhere is untouched.
kind is derived from the spec's category via ALLCATS.
"""
import glob
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_specs as g

DATA = os.path.join(HERE, "..", "..", "data")
CAT2KIND = {cat: kind for (cat, kind, cpc, devs) in g.ALLCATS}


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(DATA, "volumes", "specs-v*.jsonl"))):
        with open(f, encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if ln:
                    rows.append(json.loads(ln))
    print(f"loaded {len(rows)} specs", flush=True)
    missing_kind = 0
    for n, d in enumerate(rows):
        cat = d.get("category", "")
        kind = CAT2KIND.get(cat)
        if kind is None:
            missing_kind += 1
            kind = "hardware"
        r = random.Random(f"JAH-MASTER-{d['spec_id']}")
        d["patent_draft"] = g.build_patent_draft(
            r, kind, d["title"], cat,
            d.get("key_parameters", {}),
            d.get("signature_tool_mapping", {}),
            extra={
                "spec_id": d["spec_id"],
                "cpc": d.get("cpc", ""),
                "era": d.get("era", ""),
                "prepared": d.get("prepared_date", ""),
                "steps": d.get("algorithm_steps", []),
                "measurements": d.get("measurements", []),
                "manufacture": d.get("manufacture", {}),
                "demo": d.get("demo", {}),
                "ai_explainer": d.get("ai_explainer", {}),
                "line": d.get("line", ""),
                "mix_from": d.get("mix_from"),
                "abstract_text": d.get("abstract", ""),
            },
        )
        if (n + 1) % 5000 == 0:
            print(f"  {n + 1}/{len(rows)}", flush=True)
    print(f"done. missing-kind categories: {missing_kind}", flush=True)

    out = os.path.join(DATA, "backfilled.jsonl")
    with open(out, "w", encoding="utf-8") as fh:
        for d in rows:
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")
    print(f"wrote {out} ({os.path.getsize(out) / 1048576:.1f}MB)", flush=True)


if __name__ == "__main__":
    main()
