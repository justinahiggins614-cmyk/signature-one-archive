#!/usr/bin/env python3
"""Re-stamp the static (no-JS) count fallbacks in specs.html from the real data.

Reads the true totals from code/specs/state.json (specs) and
code/wordspecs/state.json (word-spec records), cross-checks against
data/index/az/manifest.json, and rewrites the five static spots in
specs.html with the real numbers + Manon's date (America/New_York).

All on-page counters are JS-live at load; this only keeps the raw-HTML
fallbacks (what crawlers and no-JS readers see) honest between drips.

WIRING: add this to the jah-spec-drip-fill body, AFTER build_search_index.py
(which rebuilds the A-Z the archCount live counter reads):
    python3 code/stamp_counts.py
"""
import datetime
import json
import os
import re
import sys
import zoneinfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDT = zoneinfo.ZoneInfo("America/New_York")


def main():
    specs_state = json.load(open(os.path.join(ROOT, "code/specs/state.json")))
    specs = int(specs_state["next_index"]) - 1
    # words: count the real index rows (IDs start at 0, so next_index - 1
    # would undercount by one)
    import gzip
    words = sum(1 for _ in gzip.open(
        os.path.join(ROOT, "data/index/words.idx.json.gz"), "rt"))
    total = specs + words

    # cross-check against the A-Z manifest the live archCount reads
    man_path = os.path.join(ROOT, "data/index/az/manifest.json")
    if os.path.exists(man_path):
        mtotal = json.load(open(man_path)).get("total")
        if mtotal != total:
            print("WARN: az/manifest.json total %s != specs+words %s — "
                  "manifest may lag the last drip; stamping anyway" % (mtotal, total),
                  file=sys.stderr)

    date = datetime.datetime.now(EDT).date().isoformat()
    specs_s = format(specs, ",")
    total_s = format(total, ",")

    p = os.path.join(ROOT, "specs.html")
    html = open(p, encoding="utf-8").read()

    subs = [
        # JSON-LD description (specs only)
        (r'"description": "[\d,]+ original draft invention specifications \(as of \d{4}-\d{2}-\d{2}\)',
         '"description": "%s original draft invention specifications (as of %s)' % (specs_s, date)),
        # hero chip (specs only; JS sets it live from the catalog index)
        (r'<b id="statCount">[\d,]+</b> draft specs',
         '<b id="statCount">%s</b> draft specs' % specs_s),
        # static crawlable paragraph (specs only)
        (r'<p class="staticcount">[\d,]+ original draft specifications published in this catalog \(as of \d{4}-\d{2}-\d{2}\)',
         '<p class="staticcount">%s original draft specifications published in this catalog (as of %s)' % (specs_s, date)),
        # hub status line (specs only; JS sets it live)
        (r'<b id="statNodes">[\d,]+</b> NODES SYNCED',
         '<b id="statNodes">%s</b> NODES SYNCED' % specs_s),
        # A-Z archive count: the live JS fills this from the A-Z manifest,
        # which covers JAH-SPEC *and* JAH-WORD records, so the fallback and
        # its label must describe both ("draft records", not "draft specs").
        (r'<b id="archCount">[\d,]+</b> draft (?:specs|records)',
         '<b id="archCount">%s</b> draft records' % total_s),
    ]
    changed = 0
    for pat, new in subs:
        html, n = re.subn(pat, new, html, count=1)
        if n != 1:
            raise SystemExit("stamp_counts: pattern matched %d times (expected 1): %s" % (n, pat[:60]))
        changed += 1

    open(p, "w", encoding="utf-8").write(html)
    print("stamped specs.html: %s specs, %s word-records, %s total (as of %s)"
          % (specs_s, format(words, ","), total_s, date))


if __name__ == "__main__":
    main()
