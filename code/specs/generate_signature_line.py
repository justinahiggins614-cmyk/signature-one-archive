#!/usr/bin/env python3
"""Signature-line generator: one original JAH spec per public patent record.

For each patent in the cyber-patent-catalog dataset not yet covered, this
builds an ORIGINAL draft specification by Justin Addam Higgins (JAH) in the
same product area (matched by CPC subclass) -- her own Signature-line version
of that kind of product, generated through the Signature-One framework (her
4 posts: the Math Grid, Signature-Geometry-One, Signature Math-Grid-One, and
the Reversed Universal Allowance Algorithm).

It never copies or rewords the patent's text. The patent record is only a
product-area pointer; the source record is cited in `signature_line_of` for
transparency. Every spec is as full and detailed ("hearty") as the standard
JAH forced format: abstract, key parameters, six-tool mapping, autoread
block, and the 5 reversed-allowance algorithm steps.

Usage:
    python3 code/specs/generate_signature_line.py [max_new]
        [--patents PATH] [--data PATH] [--state PATH] [--covered PATH]

Appends to data/specs.jsonl, advances state.json next_index, and records
covered publication numbers in code/specs/covered_patents.txt.
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_specs as g

PATENTS = os.path.join(os.path.expanduser("~"), "workspace", "cyber-patent-catalog",
                       "data", "patents.jsonl")
COVERED = os.path.join(HERE, "covered_patents.txt")


def parse_args(argv):
    max_new = 5000
    paths = {"patents": PATENTS, "data": g.DATA, "state": g.STATE, "covered": COVERED}
    it = iter(argv[1:])
    for a in it:
        if a == "--patents":
            paths["patents"] = next(it)
        elif a == "--data":
            paths["data"] = next(it)
        elif a == "--state":
            paths["state"] = next(it)
        elif a == "--covered":
            paths["covered"] = next(it)
        else:
            max_new = int(a)
    return max_new, paths


def load_covered(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return set(ln.strip() for ln in fh if ln.strip())
    return set()


def norm_cpc(code):
    return (code or "").upper().replace(" ", "")


def build_cpc_map():
    m = {}
    for entry in g.ALLCATS:
        m.setdefault(entry[2], []).append(entry)
    return m


def match_category(cpc_map, code, title, rr):
    code = norm_cpc(code)
    matches = None
    for cand in (code, code[:4], code[:3]):
        if cand and cand in cpc_map:
            matches = cpc_map[cand]
            break
    if not matches:
        return None
    # Prefer the candidate whose product words actually appear in the patent
    # title, so the Signature-line version lands in the closest product area.
    words = [w for w in "".join(ch if ch.isalpha() else " " for ch in
                                (title or "").lower()).split() if len(w) >= 4]
    if words and len(matches) > 1:
        scored = []
        for entry in matches:
            text = (entry[0] + " " + " ".join(entry[3])).lower()
            score = sum(1 for w in words if w in text)
            scored.append((score, entry))
        best = max(s for s, _ in scored)
        if best > 0:
            top = [e for s, e in scored if s == best]
            return rr.choice(top)
    return rr.choice(matches)


def load_patents(path):
    recs = []
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except Exception:
                continue
            pub = str(r.get("publication_number") or "").strip()
            if pub:
                recs.append(r)
    return recs


def main():
    max_new, P = parse_args(sys.argv)
    cpc_map = build_cpc_map()

    st = g.load_state() if P["state"] == g.STATE else (
        json.load(open(P["state"], encoding="utf-8"))
        if os.path.exists(P["state"]) else
        {"seed": g.SEED, "next_index": 1, "used_titles": []})
    used = set(st.get("used_titles", []))
    covered = load_covered(P["covered"])
    patents = load_patents(P["patents"])

    made = 0
    idx = st.get("next_index", 1)
    os.makedirs(os.path.dirname(P["data"]), exist_ok=True)
    with open(P["data"], "a", encoding="utf-8") as fh:
        for p in patents:
            if made >= max_new:
                break
            pub = str(p["publication_number"]).strip()
            if pub in covered:
                continue
            rr = random.Random(f"JAH-SIGLINE-{pub}")
            category = match_category(cpc_map, p.get("cpc"), p.get("title"), rr)
            spec, _tkey = g.make_spec(idx, used, seed=f"JAH-SIGLINE-{pub}",
                                      category=category)
            # Signature-line title: her own product line version.
            title = "Signature " + spec["title"]
            rev = 2
            base = title
            while title.lower() in used and rev < 60:
                title = f"{base} (Rev {rev})"
                rev += 1
            spec["title"] = title
            cat_kind = {n: k for n, k, _, _ in g.ALLCATS}.get(spec["category"],
                                                             "hardware")
            spec["line"] = g.line_for_category(spec["category"], cat_kind)
            spec["signature_line_of"] = {
                "publication_number": pub,
                "title": str(p.get("title") or "")[:200],
            }
            spec["line_note"] = (
                "Original Signature-line design by Justin Addam Higgins (JAH) "
                f"in the same product area as public patent record {pub} -- "
                "generated through the Signature-One framework. An original "
                "design, not the patented invention itself."
            )
            used.add(title.lower())
            st.setdefault("used_titles", []).append(title.lower())
            fh.write(json.dumps(spec, separators=(",", ":"), ensure_ascii=True) + "\n")
            covered.add(pub)
            idx += 1
            made += 1
            if made % 500 == 0:
                print(f"  ...{made}", flush=True)

    st["next_index"] = idx
    if P["state"] == g.STATE:
        g.save_state(st)
    else:
        with open(P["state"], "w", encoding="utf-8") as fh:
            json.dump(st, fh, separators=(",", ":"))
    with open(P["covered"], "w", encoding="utf-8") as fh:
        for pub in sorted(covered):
            fh.write(pub + "\n")
    print(f"done: +{made} signature-line specs, next_index={idx}, "
          f"{len(covered)} patents covered")


if __name__ == "__main__":
    main()
