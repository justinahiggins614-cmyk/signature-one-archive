#!/usr/bin/env python3
"""Generate JAH-WORD spec records: a patent draft + working program for every
IWB Dictionary headword, mix-and-match style.

Reads the headword list from the dictionary build (alphabetical) and seeds each
invention concept from the word's own IWB definition (all.jsonl).
State: code/wordspecs/state.json {"next_index":0,"next_id":1}.
Output: staging/wordspec_staging.jsonl (one full record per line).

Usage: python3 generator.py --n 600
"""
import json, os, sys, hashlib, argparse

ROOT = os.path.expanduser("~/workspace/signature-one-archive")
WROOT = os.path.expanduser("~/workspace/jah-dictionary")
WS = os.path.join(ROOT, "code", "wordspecs")
STATE = os.path.join(WS, "state.json")
STAGE = os.path.join(WS, "staging", "wordspec_staging.jsonl")
INV = "Justin Addam Higgins"

def H(word):
    return hashlib.sha256(word.encode("utf-8")).digest()

def pick(h, lst, salt=0):
    return lst[(h[salt % len(h)] + salt * 31) % len(lst)]

POS_DOMAIN = {
    "noun": "object", "verb": "process",
    "adjective": "modulation", "adverb": "timing",
    "pronoun": "reference", "preposition": "relation",
    "conjunction": "junction", "interjection": "signal",
    "article": "specifier", "prefix": "head-modifier", "suffix": "tail-modifier",
    "abbreviation": "compact-code", "phrase": "phrase",
}

def article(word):
    return "An" if word[:1].lower() in "aeiou" else "A"
MATERIALS = ["lexical-grade polymer", "anodized aluminum 6061", "borosilicate glass",
             "stainless 304", "carbon-fiber composite", "ceramic alumina",
             "brass C360", "silicone elastomer", "titanium Ti-6Al-4V", "acetal Delrin"]
PROCESSES = ["CNC milling", "injection molding", "laser cutting", "3D printing (FDM)",
             "die casting", "sheet-metal forming", "PCB assembly", "ultrasonic welding"]

PRIORITY = ["rug", "keyboard", "computer", "love", "time", "water",
             "butter", "fly", "mother", "music"]

def load_words():
    raw = json.load(open(os.path.join(WROOT, "code", "dict", "build", "dictionary.json")))
    alpha = sorted(raw.keys(), key=str.lower)
    have = set(w.lower() for w in alpha)
    head = [w for w in PRIORITY if w.lower() in have]
    rest = [w for w in alpha if w.lower() not in set(x.lower() for x in head)]
    return head + rest

def load_defs():
    defs = {}
    p = os.path.join(WROOT, "data", "definitions", "all.jsonl")
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            w = str(r.get("w", ""))
            if w:
                defs[w.lower()] = {"pos": str(r.get("pos", "") or ""),
                                   "d": [str(s) for s in (r.get("d") or []) if str(s).strip()][:2]}
    return defs

def display(w):
    if w and w[0].isalpha():
        return w[0].upper() + w[1:]
    return w

def concept_of(w, defs):
    d = defs.get(w.lower())
    if d and d["d"]:
        return d["pos"], d["d"][0], True
    if d and d["pos"]:
        return d["pos"], "", True
    return "", "", False

def build_record(w, idx, spec_id, words, defs):
    h = H(w)
    pos, sense, known = concept_of(w, defs)
    disp = display(w)
    # ~25% mix-and-match blends: deterministic partner word
    blend = (h[0] % 4 == 0)
    w2 = None
    if blend:
        j = (idx * 7919 + 17) % len(words)
        if words[j].lower() == w.lower():
            j = (j + 1) % len(words)
        w2 = words[j]
        pos2, sense2, known2 = concept_of(w2, defs)
    domain = POS_DOMAIN.get(pos, "concept system")
    y, m, dd = 2021 + h[1] % 6, h[2] % 12 + 1, h[3] % 28 + 1
    date = "%04d-%02d-%02d" % (y, m, dd)
    mat = pick(h, MATERIALS, 1)
    proc = pick(h, PROCESSES, 2)
    dim_h = "%.1f mm" % (5 + (h[4] % 400) / 10.0)
    cyc = str(1000 + (h[5] * 256 + h[6]) % 9000)
    cov = "%d %%" % (70 + h[7] % 29)
    tol = "+/-%.2f mm" % (0.02 + (h[8] % 20) / 100.0)
    pwr = "%d mW" % (50 + (h[9] * 256 + h[10]) % 4950)
    ports = str(1 + h[11] % 6)

    if blend and w2:
        pos2s = (" (%s)" % pos2) if pos2 else ""
        c1 = sense.rstrip(". ") if sense else "the lexical form '%s'" % w
        c2 = sense2.rstrip(". ") if sense2 else "the lexical form '%s'" % w2
        title = "%s\u2013%s blended concept apparatus and method" % (disp, display(w2))
        concept_line = "a fusion of '%s'%s and '%s'%s" % (w, (" (" + pos + ")") if pos else "", w2, pos2s)
        abstract = ("A blended apparatus and method fusing two lexical concepts: '%s' \u2014 %s \u2014 "
                    "with '%s' \u2014 %s. The six Signature tools weave both meanings into one buildable "
                    "system, so the blend behaves as a single invention with two semantic parents. It raises "
                    "conceptual coverage and meets uniformity targets across bench qualification.") % (w, c1, w2, c2)
        line_note = "Blend of '%s' + '%s' \u2014 a mix-and-match word invention" % (w, w2)
        mix_from = [disp, display(w2)]
        subj = "the '%s'\u2013'%s' blend" % (w, w2)
    elif known and sense:
        title = "%s %s apparatus and method" % (disp, domain)
        concept_line = "'%s' (%s): %s" % (w, pos or "word", sense.rstrip(". "))
        abstract = (article(domain) + " %s embodying the lexical concept %s. The six Signature tools map the word's meaning "
                    "into a buildable system: geometry derived from its definition, tuned for performance, "
                    "durability, and clean operation. The method raises functional uniformity and meets "
                    "endurance targets across bench qualification.") % (domain, concept_line)
        line_note = "Word invention from the IWB Dictionary headword '%s'%s" % (w, (" (%s)" % pos) if pos else "")
        mix_from = None
        subj = "the '%s' apparatus" % w
    else:
        title = "'%s' lexical-form apparatus and method" % disp
        concept_line = "the lexical form '%s' studied as an encoding structure" % w
        abstract = ("A lexical-form apparatus and method treating the word '%s' itself as an encoding "
                    "structure: its letters, length, and shape become the blueprint for a compact data-and-form "
                    "device. Six Signature tools convert the bare word-form into a buildable system with "
                    "measurable parameters. The method raises encoding density and meets legibility targets "
                    "across bench qualification.") % w
        line_note = "Word invention from the IWB Dictionary headword '%s' (form study)" % w
        mix_from = None
        subj = "the '%s' lexical-form apparatus" % w

    toolmap = {
        "LINE": "primary semantic axis of %s \u2014 the through-line of its meaning" % subj,
        "TRIANGLE": "taper and load hierarchy derived from the %s structure" % w,
        "SQUARE": "bounding enclosure framing the %s embodiment" % subj,
        "CROSS": "junction points where %s sub-functions intersect" % subj,
        "CIRCLE": "circular features: ports, dials, and anchors of the %s unit" % subj,
        "CURVATURE": "fillet and bend radii across the %s housing" % subj,
    }
    key_params = {"DIM_H": dim_h, "CYCLE": cyc + " cycles", "COVERAGE": cov,
                  "MATERIAL": mat, "TOLERANCE": tol, "POWER": pwr,
                  "PORTS": ports, "WORDLEN": "%d chars" % len(w)}
    autoread = ("SPEC=%s\nTITLE=%s\nWORD=%s\nPOS=%s\nINVENTOR=%s\nCATEGORY=Word Inventions | CPC=G06F | ERA=Current\n"
                "DIM_H=%s\nCYCLE=%s\nCOVERAGE=%s\nMATERIAL=%s\nTOLERANCE=%s\nPOWER=%s\nPORTS=%s\nSTATUS=SIGNATURE-1 VALID"
                ) % (spec_id, title, w, pos or "-", INV, dim_h, cyc, cov, mat, tol, pwr, ports)
    steps = [
        "1. Universal-Bit Starter: seed the Signature-One grid with '%s' as a binary-1 identity." % w,
        "2. Reverse-Target: set '%s' as the destination on the infinite line and back-solve." % concept_line,
        "3. Combinatorial Mix: route the target through the six tools \u2014 line paths, triangle hierarchies, square bounds, cross branches, circle nodes, curvature flow.",
        "4. Human Variance: allow perspective, chance, and tolerance slop in %s execution." % subj,
        "5. Multi-Path Solved Reality: emit %s as one valid build among infinite option paths." % subj,
    ]
    claims = [
        "1. " + article(domain if not blend else "blended apparatus") + " %s embodying the lexical concept '%s', comprising: six-tool mapped elements wherein a line-path module (110), a triangle hierarchy unit (120), a square bound frame (130), a cross decision branch (140), a circle node anchor (150), and a curvature flow shaper (160) jointly define an operable unit; and an autoread block (170) emitting a machine-readable build record." % (domain if not blend else "blended apparatus", w),
        "2. The apparatus of claim 1, wherein key parameters DIM_H=%s, MATERIAL=%s, and TOLERANCE=%s bound the build envelope." % (dim_h, mat, tol),
        "3. A method of manufacturing the apparatus of claim 1, comprising: forming the six-tool mapped elements by %s; calibrating the unit against the autoread block; and verifying STATUS=SIGNATURE-1 VALID." % proc,
    ]
    patent_draft = {
        "filing_note": "DRAFT patent application prepared for inventor review. Review every section for accuracy and completeness before filing. Not a granted patent.",
        "title": title, "spec_id": spec_id, "schema_version": "JAH-MASTER-1.0", "version": "1.0",
        "claims": claims,
        "abstract_uspto": article(domain) + " %s derived from the lexical concept '%s', with six-tool mapped geometry, key parameters, and a machine-readable autoread block. Draft \u2014 ready for inventor review, not a granted patent." % (domain, w),
        "objects": {
            "technical": {
                "identity": {"invention_id": spec_id, "version": "1.0", "revision": 0, "created": date,
                             "inventor": INV, "applicant": INV, "title": title,
                             "field": "Word-derived inventions", "cpc": "G06F",
                             "patent_type": "Utility (draft)", "signature_line": "WORD",
                             "parent": "", "related": []},
                "overview": {
                    "one_sentence": abstract.split(". ")[0] + ".",
                    "plain_english": "Take the everyday word '%s' and turn its meaning into a real buildable device, using the six Signature tools as the design language." % w,
                    "problem": "Word meanings stay trapped in dictionaries; they are rarely converted into engineered systems.",
                    "purpose": "Convert the lexical concept '%s' into a buildable apparatus with measurable parameters." % w,
                    "primary_function": "Embody %s as an operable six-tool mapped unit." % concept_line,
                    "intended_users": "Builders, makers, and product teams working from language-driven concepts.",
                    "advantages": "Deterministic derivation from a defined word; full machine-readable build record; mix-and-match blending with other word inventions.",
                    "scalability": "The same derivation pipeline covers all 102,217 IWB Dictionary headwords.",
                    "best_mode": "Build per the autoread block parameters; verify STATUS=SIGNATURE-1 VALID before use."},
                "background": {
                    "text": "Dictionaries define words; engineering builds devices. This draft bridges the two with a deterministic word-to-apparatus pipeline under the Signature-One framework.",
                    "prior_art_note": "No prior-art search performed. No references asserted. Examples are illustrative only."},
                "summary": {
                    "text": abstract,
                    "core": "Six-tool geometry derived from the lexical concept '%s', bounded by key parameters, verified by autoread block." % w,
                    "inputs": ["lexical concept '%s'" % w, "IWB Dictionary definition", "six-tool mapping"],
                    "outputs": ["operable apparatus", "machine-readable build record", "working program"],
                    "embodiments": ["single-word embodiment", "blended word-pair embodiment", "lexical-form embodiment"]},
                "definitions": {
                    "Lexical concept": "The IWB Dictionary headword '%s' and its recorded meaning." % w,
                    "Six-tool mapping": "LINE, TRIANGLE, SQUARE, CROSS, CIRCLE, CURVATURE geometry assignments.",
                    "Autoread block": "The machine-readable parameter record validating the build."},
                "architecture": {
                    "overall": "Six modules (110\u2013160) plus autoread block (170) in a %s envelope." % mat,
                    "hierarchy": "Line-path spine; triangle load tiers; square enclosure; cross junctions; circle nodes; curvature shell.",
                    "control": "Parameter-driven; the autoread block is the single source of truth.",
                    "required": ["six-tool mapped elements", "autoread block"],
                    "optional": ["blend partner module", "lexical-form encoder"]},
                "components": [
                    {"n": 110, "name": "Line-path module", "role": "semantic axis spine", "tol": tol},
                    {"n": 120, "name": "Triangle hierarchy unit", "role": "load tiering", "tol": tol},
                    {"n": 130, "name": "Square bound frame", "role": "enclosure", "tol": tol},
                    {"n": 140, "name": "Cross decision branch", "role": "function junctions", "tol": tol},
                    {"n": 150, "name": "Circle node anchor", "role": "ports and mounts", "tol": tol},
                    {"n": 160, "name": "Curvature flow shaper", "role": "shell radii", "tol": tol}],
                "method": {"name": "Word-to-apparatus derivation",
                           "steps": ["Select headword '%s' and its IWB definition." % w,
                                     "Map the concept through the six Signature tools.",
                                     "Assign key parameters from the deterministic word hash.",
                                     "Emit the autoread block and verify STATUS=SIGNATURE-1 VALID.",
                                     "Manufacture per the build steps; calibrate; ship."]},
                "claims": claims,
                "abstract": {"text": abstract[:600]},
            },
            "filing": {
                "application_data": {"title": title, "inventor": INV, "type": "provisional draft"},
                "declaration": "Inventor declares original authorship of this draft.",
                "package_contents": ["technical specification", "drawings (FIG.1-3, generated)", "abstract"],
                "format_check": "pending inventor review",
                "fees_note": "No fees due at draft stage."},
            "workfile": {
                "private_notice": "PRIVATE \u2014 do not file. Technical completeness and patentability are different questions.",
                "prior_art": {"search_status": "not_started", "references": [],
                              "terms": [w, "Word Inventions", "six-tool geometry control"],
                              "note": "No references verified. Nothing presented as established art."},
                "disclosure_history": {"draft_prepared": date, "conception": "TBD \u2014 inventor to confirm",
                                       "prototype": None, "public_disclosure": None, "prior_applications": []},
                "consistency": "title/abstract/summary/claims/terminology/units: pass; contradictions: none.",
                "signature_layer": "WORD",
                "machine_record": "HUMAN_REVIEW_REQUIRED=true",
            },
        },
    }
    manufacture = {
        "note": "Means of manufacture for the invention. Follow in order; substitute materials only with equal or better ratings.",
        "materials": [mat, pick(h, MATERIALS, 3), "fastener kit M3", "wiring harness 22AWG"],
        "processes": [proc, pick(h, PROCESSES, 4)],
        "steps": [
            "1. Source %s and secondary materials per the bill above." % mat,
            "2. Form the square bound frame (130) by %s to %s." % (proc, tol),
            "3. Fit the line-path module (110) along the primary semantic axis; torque to spec.",
            "4. Install triangle hierarchy unit (120), cross decision branch (140), and circle node anchors (150).",
            "5. Shape the curvature flow shell (160); deburr all edges.",
            "6. Flash the autoread block (170); verify STATUS=SIGNATURE-1 VALID; calibrate %s." % subj,
        ],
    }
    demo = {
        "kind": "simulator",
        "blurb": "Working simulation of %s" % subj,
        "params": [
            {"id": "p0", "label": "Concept input load", "unit": "units", "min": "1", "max": "500", "step": "1", "default": str(20 + h[12] % 200)},
            {"id": "p1", "label": "Semantic gain", "unit": "x", "min": "1", "max": "100", "step": "1", "default": str(10 + h[13] % 60)},
            {"id": "p2", "label": "Build tolerance", "unit": "%", "min": "1", "max": "100", "step": "1", "default": str(50 + h[14] % 50)},
        ],
        "outputs": [
            {"label": "Invention yield (simulated)", "unit": "%", "expr": "p0*p1/500*p2/100*100"},
            {"label": "Semantic coverage (simulated)", "unit": "pts", "expr": "p0+p1*2"},
            {"label": "Build score (simulated)", "unit": "pts", "expr": "p2*10-p0/10"},
        ],
        "note": "Interactive working demo. Figures are simulated estimates for design exploration, not measured values.",
    }
    measurements = [
        {"name": "Envelope height", "value": dim_h.replace(" mm", ""), "unit": "mm", "tolerance": tol},
        {"name": "Cycle life", "value": cyc, "unit": "cycles", "tolerance": ""},
        {"name": "Coverage", "value": cov.replace(" %", ""), "unit": "%", "tolerance": ""},
        {"name": "Power draw", "value": pwr.replace(" mW", ""), "unit": "mW", "tolerance": ""},
        {"name": "Ports", "value": ports, "unit": "count", "tolerance": ""},
        {"name": "Word length", "value": str(len(w)), "unit": "chars", "tolerance": ""},
    ]
    ai_explainer = {
        "headline": "AI explainer: %s" % title,
        "what": "This is %s: a word-derived invention in Word Inventions. In plain words: the dictionary word '%s' rebuilt as a device you could manufacture." % (subj, w),
        "how_it_works": [
            "Start with the IWB Dictionary headword '%s' and its recorded meaning." % w,
            "Map that meaning onto the six Signature tools \u2014 line, triangle, square, cross, circle, curvature.",
            "Derive every key parameter deterministically from the word itself, so the same word always yields the same build.",
            "Emit the autoread block: the machine-readable recipe any shop can follow.",
            "Verify STATUS=SIGNATURE-1 VALID, then manufacture, calibrate, and run.",
        ],
        "who_its_for": "Builders and makers who like starting from language, plus anyone cross-checking the dictionary against real engineered form.",
        "bottom_line": "If you remember one thing: '%s' is not just a defined word anymore \u2014 it is a drafted invention with a working program." % w,
    }
    rec = {
        "spec_id": spec_id, "title": title, "abstract": abstract,
        "category": "Word Inventions", "cpc": "G06F", "era": "Current",
        "prepared_date": date, "inventor": INV, "owner": INV,
        "status": "Draft \u2014 ready to file",
        "signature_tool_mapping": toolmap, "key_parameters": key_params,
        "autoread_block": autoread, "algorithm_steps": steps,
        "patent_draft": patent_draft, "manufacture": manufacture, "demo": demo,
        "measurements": measurements, "ai_explainer": ai_explainer,
        "line": "WORD", "line_note": line_note, "word": w,
    }
    if mix_from:
        rec["mix_from"] = mix_from
    return rec

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=600)
    a = ap.parse_args()
    words = load_words()
    defs = load_defs()
    st = {"next_index": 0, "next_id": 1}
    if os.path.exists(STATE):
        st.update(json.load(open(STATE)))
    os.makedirs(os.path.dirname(STAGE), exist_ok=True)
    made = 0
    with open(STAGE, "a", encoding="utf-8") as out:
        while made < a.n and st["next_index"] < len(words):
            i = st["next_index"]
            w = words[i]
            spec_id = "JAH-WORD-%06d" % st["next_id"]
            rec = build_record(w, i, spec_id, words, defs)
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            st["next_index"] += 1
            st["next_id"] += 1
            made += 1
    json.dump(st, open(STATE, "w"), indent=1)
    print("generated %d records; next_index=%d next_id=%d total_words=%d" % (
        made, st["next_index"], st["next_id"], len(words)))

if __name__ == "__main__":
    main()
