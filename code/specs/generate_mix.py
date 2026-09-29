#!/usr/bin/env python3
"""Mix-and-match hybrid specs: combine two existing specs into new ones.

Picks random pairs from the sealed volumes (reservoir-sampled so it scales),
blends their parameters and tool mappings, and emits brand-new hybrid specs
with full filing packages (patent draft, manufacture, demo, measurements,
AI explainer). Lineage is recorded in `mix_from` and shown with a MIX badge.

Usage: python3 code/specs/generate_mix.py <count>
Appends to data/specs.jsonl and advances code/specs/state.json.
"""
import json
import gzip
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_specs as g

DATA = os.path.join(HERE, "..", "..", "data")
VOLDIR = os.path.join(DATA, "volumes")
MANIFEST = os.path.join(VOLDIR, "manifest.json")
HOT = os.path.join(DATA, "specs.jsonl")
STATE = os.path.join(HERE, "state.json")
POOL_SAMPLE = 5000

CATKIND = {n: k for n, k, _, _ in g.ALLCATS}


def sample_pool():
    """Reservoir-sample candidate parents from all sealed volumes + hot file."""
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    pool = []
    n = 0
    for f in manifest["files"]:
        p = os.path.join(DATA, f)
        if not os.path.exists(p):
            continue
        opener = gzip.open if p.endswith(".gz") else open
        with opener(p, "rt", encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    d = json.loads(ln)
                except Exception:
                    continue
                n += 1
                cand = (d["spec_id"], d["title"], d["category"],
                        d.get("key_parameters", {}), d.get("signature_tool_mapping", {}))
                if len(pool) < POOL_SAMPLE:
                    pool.append(cand)
                else:
                    j = random.randrange(n)
                    if j < POOL_SAMPLE:
                        pool[j] = cand
    return pool


def make_mix_spec(idx, used, pool, seed):
    r = random.Random(seed)
    (idA, titleA, catA, paramsA, toolA), (idB, titleB, catB, paramsB, toolB) = r.sample(pool, 2)
    kind = CATKIND.get(catA, "hardware")
    cat, kind, cpc, devs = next(c for c in g.ALLCATS if c[0] == catA)
    devA = g._dev_of(titleA)
    devB = g._dev_of(titleB)
    fn = r.choice(g.SW_FUNCS if kind == "software" else g.HW_FUNCS)
    mech = r.choice(g.SW_MECHS if kind == "software" else g.HW_MECHS)
    title = f"{devA}-{devB} hybrid for {fn} using {mech}"
    rev = 2
    base = title
    while title.lower() in used and rev < 50:
        title = f"{base} (Rev {rev})"
        rev += 1
    spec_id = f"JAH-SPEC-{idx:06d}"
    era = r.choices(["Past", "Current", "Future"], weights=[25, 45, 30])[0]

    # Blend parameters: half from A, half from B, topped up fresh.
    ka = list(paramsA.items())
    kb = list(paramsB.items())
    r.shuffle(ka)
    r.shuffle(kb)
    blended = dict(ka[:3] + kb[:3])
    fresh = g.build_params(r, kind)
    for k, v in fresh.items():
        if k not in blended:
            blended[k] = v
    params = dict(list(blended.items())[:10])

    # Blend tool mapping: A's geometry, one tool remapped through B.
    toolmap = dict(toolA) if toolA else g.build_toolmap(kind, devA)
    if toolB:
        swap_tool = r.choice(list(toolmap.keys()))
        toolmap[swap_tool] = f"{toolB.get(swap_tool, toolmap[swap_tool])} fused with {devB}"

    dev = f"{devA}-{devB} hybrid"
    steps = g.build_steps(dev, fn)
    prepared = g.random_date(r)
    autoread = g.build_autoread(spec_id, title, cat, cpc, era, params)
    abstract = g.build_abstract(r, kind, dev, fn, mech)
    manufacture = g.build_manufacture(r, kind, title, cat, params)
    demo = g.build_demo(r, kind, title, cat)
    measurements = g.build_measurements(r, kind, title, cat)
    ai_explainer = g.build_ai_explainer(r, kind, title, cat, params, toolmap, steps)
    patent_draft = g.build_patent_draft(r, kind, title, cat, params, toolmap, extra={
        "spec_id": spec_id, "cpc": cpc, "era": era, "prepared": prepared,
        "steps": steps, "measurements": measurements, "manufacture": manufacture,
        "demo": demo, "ai_explainer": ai_explainer, "line": g.line_for_category(cat, kind),
        "mix_from": [idA, idB], "abstract_text": abstract,
    })
    return {
        "spec_id": spec_id,
        "title": title,
        "abstract": abstract,
        "category": cat,
        "cpc": cpc,
        "era": era,
        "prepared_date": prepared,
        "inventor": g.INVENTOR,
        "owner": g.INVENTOR,
        "status": g.STATUS,
        "signature_tool_mapping": toolmap,
        "key_parameters": params,
        "autoread_block": autoread,
        "algorithm_steps": steps,
        "patent_draft": patent_draft,
        "manufacture": manufacture,
        "demo": demo,
        "measurements": measurements,
        "ai_explainer": ai_explainer,
        "mix_from": [idA, idB],
        "line": g.line_for_category(cat, kind),
        "line_note": "Mix-and-match hybrid of " + idA + " and " + idB + ".",
    }, title.lower()


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    pool = sample_pool()
    if len(pool) < 2:
        print("not enough parents to mix")
        return
    st = g.load_state()
    used = set(t.lower() for t in st.get("used_titles", []))
    idx = st.get("next_index", 1)
    new_titles = []
    with open(HOT, "a", encoding="utf-8") as out:
        for n in range(count):
            spec, tkey = make_mix_spec(idx, used, pool, f"JAH-MIX-{idx}")
            used.add(tkey)
            new_titles.append(spec["title"])
            out.write(json.dumps(spec, separators=(",", ":"), ensure_ascii=True) + "\n")
            idx += 1
    st["used_titles"] = st.get("used_titles", []) + new_titles
    st["next_index"] = idx
    with open(STATE, "w", encoding="utf-8") as fh:
        json.dump(st, fh)
    print(f"mixed {count} hybrids, next_index={idx}")


if __name__ == "__main__":
    main()
