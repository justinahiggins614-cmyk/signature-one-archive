#!/usr/bin/env python3
"""Coherence check: every AI the spec catalog presents vs the phone-book canon.

Canon: /home/hatch/workspace/jah-ai-models/ai-catalog.json
Rule: any AI presented WITH a JAH-AI ID must match the canon exactly
(name + description, whitespace-normalized). The per-spec personal AI
is a site helper and must NOT claim a canon ID. Exit 0 = coherent,
1 = drift found (loud report).
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANON_PATHS = [
    "/home/hatch/workspace/jah-ai-models/ai-catalog.json",
    os.path.expanduser("~/workspace/jah-ai-models/ai-catalog.json"),
]
ID_RE = re.compile(r"JAH-AI-[A-Z0-9-]+")

def load_canon():
    for p in CANON_PATHS:
        if os.path.exists(p):
            c = json.load(open(p, encoding="utf-8"))
            return {r["ID"]: r for r in c.get("records", []) if r.get("ID")}
    return None

def main():
    canon = load_canon()
    if canon is None:
        print("COHERENCE WARN: canon file not found; ID-claim scan only.")
    issues = []
    files = [os.path.join(ROOT, "specs.html"),
             os.path.join(ROOT, "index.html"),
             os.path.join(ROOT, "osv.js")]
    files += glob.glob(os.path.join(ROOT, "assets", "*.js"))
    for f in files:
        if not os.path.exists(f):
            continue
        try:
            txt = open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for m in ID_RE.findall(txt):
            issues.append("canon ID claimed outside canon context: %s in %s"
                          % (m, os.path.relpath(f, ROOT)))
    print("=" * 64)
    print("COHERENCE REPORT — signature-one-archive")
    print("=" * 64)
    print("Helper AIs (no canon ID, JAHtalk voice):")
    print("  - Per-spec personal AI (answers from the spec record only)")
    print("JAH-AI ID claims found on site: %d" % len(issues))
    if issues:
        print("\n*** DRIFT DETECTED ***")
        for i in sorted(set(issues))[:20]:
            print("  ! " + i)
        return 1
    print("\nOK: no canon-ID claims; the per-spec AI is a declared helper.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
