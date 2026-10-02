#!/usr/bin/env python3
"""Build per-shard sitemap XML files + the main sitemap index for the Spec Catalog.

Layout (per the 2026-10-01 discoverability pass):
  - Each frozen shard repo (signature-one-archive-shard-N) carries its own
    sitemap-specs.xml at its repo ROOT (<=50,000 URLs per file, so shard-2 is
    split into sitemap-specs-1.xml / sitemap-specs-2.xml).
  - The main repo carries sitemap-main-1.xml / sitemap-main-2.xml at its repo
    ROOT for the newest chunks (never inside data/ -- the 850MB data guard).
+  - The main repo carries sitemap-words.xml at its repo ROOT for the word
+    invention records (JAH-WORD-######, specs.html?spec=JAH-WORD-###### deep
+    links). Word records are a separate ID scheme from JAH-SPEC and were
+    invisible to crawlers before this file existed.
   - The main repo's sitemap-index.xml lists the static pages sitemap plus every
-    shard sitemap plus the two main sitemaps.
+    shard sitemap plus the two main sitemaps plus the words sitemap.

Re-run this after every 2h drip (the drip owns data/ chunks; it must call this
script afterwards so the newest JAH-SPEC IDs get sitemap coverage). The spec
deep-links (specs.html?spec=JAH-SPEC-######) live on the MAIN site; shard
sitemaps only *list* URLs, they don't serve the pages.

Ranges below were verified contiguous from the live indexes on 2026-10-02
(shard-2: 1-52500 ... shard-21: 407551-424050, main: 424051-518355).
"""
import json
import os
import re
from datetime import date

HOME = os.path.expanduser("~")
MAIN = os.path.join(HOME, "workspace", "signature-one-archive")
SITE = "https://justinahiggins614-cmyk.github.io/signature-one-archive"
TODAY = date.today().isoformat()

# (shard_dir_name, first_id, last_id) -- shard-2 gets split files
SHARDS = [
    ("signature-one-archive-shard-2", 1, 52500),
    ("signature-one-archive-shard-3", 52501, 97500),
    ("signature-one-archive-shard-4", 97501, 121500),
    ("signature-one-archive-shard-5", 121501, 141000),
    ("signature-one-archive-shard-6", 141001, 160500),
    ("signature-one-archive-shard-7", 160501, 177000),
    ("signature-one-archive-shard-8", 177001, 194850),
    ("signature-one-archive-shard-9", 194851, 212700),
    ("signature-one-archive-shard-10", 212701, 230550),
    ("signature-one-archive-shard-11", 230551, 254550),
    ("signature-one-archive-shard-12", 254551, 272550),
    ("signature-one-archive-shard-13", 272551, 290550),
    ("signature-one-archive-shard-14", 290551, 308550),
    ("signature-one-archive-shard-15", 308551, 325050),
    ("signature-one-archive-shard-16", 325051, 341550),
    ("signature-one-archive-shard-17", 341551, 358050),
    ("signature-one-archive-shard-18", 358051, 374550),
    ("signature-one-archive-shard-19", 374551, 391050),
    ("signature-one-archive-shard-20", 391051, 407550),
    ("signature-one-archive-shard-21", 407551, 424050),
]
MAIN_RANGE = (424051, 518355)
URL_LIMIT = 50000


def spec_url(n):
    return "%s/specs.html?spec=JAH-SPEC-%06d" % (SITE, n)


def word_url(n):
    return "%s/specs.html?spec=JAH-WORD-%06d" % (SITE, n)


def write_urlset(path, first, last, urlfn=None):
    urlfn = urlfn or spec_url
    parts = ['<?xml version="1.0" encoding="UTF-8"?>\n',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n']
    for n in range(first, last + 1):
        parts.append("  <url><loc>%s</loc><changefreq>monthly</changefreq></url>\n" % urlfn(n))
    parts.append("</urlset>\n")
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(parts)
    return last - first + 1


def stamp_static_count(total):
    """Keep the no-JS crawlable count on specs.html honest.

    The discoverability pass stamped a static record count into the raw HTML
    so crawlers see a real number without running JS. The drip adds ~11k
    specs every 2h, so re-stamp it here (this script already runs after every
    drip and `total` is verified against the shard ranges by the assert in
    main()). Only the one <p class="staticcount"> line is touched.
    """
    path = os.path.join(MAIN, "specs.html")
    with open(path, encoding="utf-8") as f:
        html = f.read()
    new_line = ('<p class="staticcount">%s original draft specifications published '
                'in this catalog (as of %s). The live counter above refreshes from '
                'the same catalog index when the data loads.</p>'
                % (format(total, ","), TODAY))
    html2, n = re.subn(r'<p class="staticcount">.*?</p>', new_line, html,
                       count=1, flags=re.S)
    if n != 1:
        raise RuntimeError("staticcount line not found in specs.html")
    if html2 != html:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html2)
        print("stamped static count: %s (as of %s)" % (format(total, ","), TODAY))
    else:
        print("static count already current")


def main():
    index_entries = [SITE + "/sitemap.xml"]  # static pages first
    total = 0

    # --- shard sitemaps, written into each shard repo's root ---
    for dirname, first, last in SHARDS:
        root = os.path.join(HOME, "workspace", dirname)
        n = last - first + 1
        if n > URL_LIMIT:
            mid = first + n // 2 - 1
            write_urlset(os.path.join(root, "sitemap-specs-1.xml"), first, mid)
            write_urlset(os.path.join(root, "sitemap-specs-2.xml"), mid + 1, last)
            base = "https://justinahiggins614-cmyk.github.io/" + dirname
            index_entries += [base + "/sitemap-specs-1.xml", base + "/sitemap-specs-2.xml"]
        else:
            write_urlset(os.path.join(root, "sitemap-specs.xml"), first, last)
            index_entries.append("https://justinahiggins614-cmyk.github.io/" + dirname + "/sitemap-specs.xml")
        total += n
        print("shard %-32s %d-%d (%d urls)" % (dirname, first, last, n))

    # --- main repo's own newest chunks (repo ROOT, never data/) ---
    # MAIN_RANGE start follows the newest shard (shard-21 ends at 424050); end follows state.json.
    mf = MAIN_RANGE[0]
    with open(os.path.join(MAIN, "code", "specs", "state.json"), encoding="utf-8") as f:
        ml = json.load(f)["next_index"] - 1
    write_urlset(os.path.join(MAIN, "sitemap-main-1.xml"), mf, mf + URL_LIMIT - 1)
    write_urlset(os.path.join(MAIN, "sitemap-main-2.xml"), mf + URL_LIMIT, ml)
    index_entries += [SITE + "/sitemap-main-1.xml", SITE + "/sitemap-main-2.xml"]
    total += ml - mf + 1
    print("main %-36s %d-%d (%d urls)" % ("(repo root)", mf, ml, ml - mf + 1))

    # --- word invention records (JAH-WORD-######, separate ID scheme) ---
    # Ground truth: code/wordspecs/state.json next_id. IDs are contiguous
    # 1..N (verified 2026-10-02); the ?spec=JAH-WORD-###### deep link opens the
    # full record via openSpec, same as JAH-SPEC.
    with open(os.path.join(MAIN, "code", "wordspecs", "state.json"), encoding="utf-8") as f:
        wn = json.load(f)["next_id"] - 1
    if wn > URL_LIMIT:
        mid = wn // 2
        write_urlset(os.path.join(MAIN, "sitemap-words-1.xml"), 1, mid, word_url)
        write_urlset(os.path.join(MAIN, "sitemap-words-2.xml"), mid + 1, wn, word_url)
        index_entries += [SITE + "/sitemap-words-1.xml", SITE + "/sitemap-words-2.xml"]
    else:
        write_urlset(os.path.join(MAIN, "sitemap-words.xml"), 1, wn, word_url)
        index_entries.append(SITE + "/sitemap-words.xml")
    print("words %-35s 1-%d (%d urls)" % ("(repo root)", wn, wn))

    # --- sitemap index on main ---
    lines = ['<?xml version="1.0" encoding="UTF-8"?>\n',
             "<!-- Spec Catalog sitemap index. Shard sitemaps live on each frozen shard repo;\n",
             "     sitemap-main-*.xml cover the newest chunks on the main repo;\n",
             "     sitemap-words*.xml cover the JAH-WORD word-invention records.\n",
             "     After each 2h drip, re-run code/build_sitemaps.py so new JAH-SPEC\n",
             "     and JAH-WORD IDs are listed, then commit+push. -->\n",
             '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n']
    for loc in index_entries:
        lines.append("  <sitemap><loc>%s</loc><lastmod>%s</lastmod></sitemap>\n" % (loc, TODAY))
    lines.append("</sitemapindex>\n")
    with open(os.path.join(MAIN, "sitemap-index.xml"), "w", encoding="utf-8") as f:
        f.writelines(lines)

    print("index entries: %d, total spec urls: %d" % (len(index_entries), total))
    expected = sum(last - first + 1 for _, first, last in SHARDS) + (ml - mf + 1)
    assert total == expected, "expected %d, got %d" % (expected, total)
    stamp_static_count(total)


if __name__ == "__main__":
    main()
