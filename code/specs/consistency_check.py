#!/usr/bin/env python3
"""Nightly consistency check for the Signature Spec Catalog (script only).

Verifies, on a bounded sample plus the newest chunk in full:
  1. spec_id uniqueness (no duplicate IDs in the scanned records)
  2. autoread blocks parse clean under the JAH-SPEC-SCHEMA 1.0 tolerant parser
     (SPEC_ID present and matching the record, STATUS present)
  3. canonical content hashes: format + determinism (recompute twice)
  4. generator determinism: make_spec with a fixed seed emits byte-identical
     autoread blocks on repeat runs
  5. geometry honesty: any record carrying TAPER=...deg plus H/D_RIM/D_BASE
     dims must satisfy taper ~= arctan(((D_RIM-D_BASE)/2)/H)
  6. rib-depth consistency: RIB_DEPTH must be a single value per record

Streams JSONL.GZ chunks; does not load the whole catalog. Prints a JSON
report to stdout; exits non-zero on any failure. Wire into a cron separately.
Usage: python3 code/specs/consistency_check.py [--sample N] [--out FILE]
"""

import argparse
import gzip
import json
import math
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import autoread as ja

REPO = os.path.dirname(os.path.dirname(HERE))
VOLDIR = os.path.join(REPO, "data", "volumes")
ID_RE = re.compile(r"^JAH-(SPEC|WORD)-\d{6}$")
NUM_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)")


def num(s):
    m = NUM_RE.search(str(s or ""))
    return float(m.group(1)) if m else None


def chunk_files():
    files = sorted(f for f in os.listdir(VOLDIR)
                   if f.endswith(".jsonl.gz"))
    return [os.path.join(VOLDIR, f) for f in files]


def stream_records(paths):
    for p in paths:
        with gzip.open(p, "rt", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except Exception:
                        yield {"__bad_line__": p}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5000)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    files = chunk_files()
    if not files:
        print(json.dumps({"ok": False, "error": "no volume chunks found"}))
        return 1

    newest = files[-1]
    rng = random.Random(20260930)
    sampled = [newest] + rng.sample(files[:-1], min(len(files) - 1, 12))

    report = {"files_scanned": len(sampled), "checks": {}}
    seen_ids = set()
    dupes, bad_parse, id_mismatch, missing_status = [], [], [], []
    taper_fail, rib_fail, bad_id_fmt = [], [], []
    hash_rows = []
    n = 0

    def take(records, limit):
        c = 0
        for r in records:
            if c >= limit:
                break
            yield r
            c += 1

    # newest chunk in full; others contribute to the sample budget
    budget = args.sample
    for idx, path in enumerate(sampled):
        limit = 10 ** 9 if idx == 0 else max(1, budget // max(1, len(sampled) - 1))
        for rec in take(stream_records([path]), limit):
            n += 1
            sid = rec.get("spec_id", "")
            if "__bad_line__" in rec:
                bad_parse.append(rec["__bad_line__"] + ":unparseable-json-line")
                continue
            if sid in seen_ids:
                dupes.append(sid)
            seen_ids.add(sid)
            if not ID_RE.match(sid or ""):
                bad_id_fmt.append(sid)
            block = rec.get("autoread_block", "")
            fields, _, warnings, valid, missing = ja.parse(block)
            if not valid:
                bad_parse.append("%s:missing=%s" % (sid, ",".join(missing)))
            else:
                if fields.get("SPEC_ID") != sid:
                    id_mismatch.append(sid)
                if "STATUS" not in fields:
                    missing_status.append(sid)
            # geometry honesty: taper must match the dims that imply it
            t = num(fields.get("TAPER"))
            h = num(fields.get("H"))
            dr = num(fields.get("D_RIM"))
            db = num(fields.get("D_BASE"))
            if t is not None and h and dr is not None and db is not None and h > 0:
                expect = math.degrees(math.atan(((dr - db) / 2) / h))
                if abs(t - expect) > 0.05:
                    taper_fail.append("%s:taper=%s,expected~%.2f" % (sid, t, expect))
            # rib depth single value per record
            rd = fields.get("RIB_DEPTH")
            if rd and len(set(re.findall(r"[0-9.]+", rd))) > 1:
                rib_fail.append(sid)
            # hash spot-check on a few
            if len(hash_rows) < 8 and n % 997 == 1:
                hh1 = ja.content_hash(sid, rec.get("title", ""),
                                      rec.get("prepared_date", ""), block)
                hh2 = ja.content_hash(sid, rec.get("title", ""),
                                      rec.get("prepared_date", ""), block)
                hash_rows.append({"id": sid, "hash": hh1,
                                  "deterministic": hh1 == hh2,
                                  "format_ok": bool(re.match(r"^[0-9a-f]{64}$", hh1))})

    # generator determinism: same seed -> identical autoread
    try:
        import generate_specs as g
        r1, _ = g.make_spec(1, set(), seed="JAH-DET-CHECK")
        r2, _ = g.make_spec(1, set(), seed="JAH-DET-CHECK")
        det_ok = (r1["autoread_block"] == r2["autoread_block"]
                  and r1["spec_id"] == r2["spec_id"])
        det_new = ja.parse(r1["autoread_block"])[3]
    except Exception as e:  # never let the harness die silently
        det_ok, det_new = False, "generator-error:" + str(e)[:80]

    report["records_scanned"] = n
    report["checks"] = {
        "id_uniqueness": {"pass": not dupes, "duplicates": dupes[:20]},
        "id_format": {"pass": not bad_id_fmt, "bad": bad_id_fmt[:20]},
        "autoread_parse": {"pass": not bad_parse, "bad": bad_parse[:20]},
        "spec_id_match": {"pass": not id_mismatch, "bad": id_mismatch[:20]},
        "status_present": {"pass": not missing_status, "bad": missing_status[:20]},
        "taper_math": {"pass": not taper_fail, "bad": taper_fail[:20]},
        "rib_depth_consistent": {"pass": not rib_fail, "bad": rib_fail[:20]},
        "hash_spot_check": {"pass": all(r["deterministic"] and r["format_ok"]
                                        for r in hash_rows) and bool(hash_rows),
                            "rows": hash_rows},
        "generator_deterministic": {"pass": bool(det_ok)},
        "new_block_parses": {"pass": bool(det_new)},
    }
    report["ok"] = all(c["pass"] for c in report["checks"].values())
    out = json.dumps(report, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(out)
    print(out)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
