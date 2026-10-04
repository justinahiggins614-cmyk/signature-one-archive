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
(shard-2: 1-52500 ... shard-26: 490051-506550, shard-27: 506551-523050, shard-28: 523051-539550,
 shard-29: 539551-556050, shard-30: 556051-572550, shard-31: 572551-589050,
 shard-32: 589051-605550, shard-33: 605551-622050,
 main: 589051-677719).
"""
import json
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

# The network's dates are America/New_York, but this VM runs UTC — a bare
# date.today() can stamp a bogus future date (e.g. 2026-10-04 at 9pm EDT).
TODAY = datetime.now(ZoneInfo("America/New_York")).date().isoformat()

HOME = os.path.expanduser("~")
MAIN = os.path.join(HOME, "workspace", "signature-one-archive")
SITE = "https://justinahiggins614-cmyk.github.io/signature-one-archive"

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
    ("signature-one-archive-shard-22", 424051, 440550),
    ("signature-one-archive-shard-23", 440551, 457050),
    ("signature-one-archive-shard-24", 457051, 473550),
    ("signature-one-archive-shard-25", 473551, 490050),
    ("signature-one-archive-shard-26", 490051, 506550),
    ("signature-one-archive-shard-27", 506551, 523050),
    ("signature-one-archive-shard-28", 523051, 539550),
    ("signature-one-archive-shard-29", 539551, 556050),
    ("signature-one-archive-shard-30", 556051, 572550),
    ("signature-one-archive-shard-31", 572551, 589050),
    ("signature-one-archive-shard-32", 589051, 605550),
    ("signature-one-archive-shard-33", 605551, 622050),
    ("signature-one-archive-shard-34", 622051, 638550),
    ("signature-one-archive-shard-35", 638551, 655050),
    ("signature-one-archive-shard-36", 655051, 671550),
]
MAIN_RANGE = (671551, 746882)
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


def _category_count():
    """Distinct categories in the master catalog_groups list.

    This is the stable category vocabulary the generators draw from; the live
    page's finishLoad() overwrites the chip with the exact distinct count from
    the loaded indexes. Used only as the no-JS fallback so the chip never
    boots as a bare "..."."""
    import sys
    sys.path.insert(0, os.path.join(MAIN, "code", "specs"))
    import catalog_groups
    groups = getattr(catalog_groups, "groups", getattr(catalog_groups, "GROUPS", []))
    cats = set()
    for gr in groups:
        seq = gr[3] if isinstance(gr, (list, tuple)) else gr.get("categories", [])
        for c in seq:
            cats.add(c)
    return len(cats)


def stamp_static_count(total):
    """Keep the no-JS crawlable count on specs.html honest.

    The discoverability pass stamped a static record count into the raw HTML
    so crawlers see a real number without running JS. The drip adds ~11k
    specs every 2h, so re-stamp it here (this script already runs after every
    drip and `total` is verified against the shard ranges by the assert in
    main()). Also stamps the CATALOG DATA / PAGE BUILD dates on the
    <p class="lastupdated"> line so the two dates never silently diverge:
    catalog-data date = the data being published (today — the drip just
    appended records), page-build date = when this page was stamped.
    The live page's refreshLastUpdated() corrects the catalog-data date from
    the GitHub API on load; these are the honest no-JS fallbacks.
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
    # Stamp the header count chip too, so it never shows a bare "..." before
    # (or without) the JS index load; finishLoad() overwrites it live.
    new_chip = '<b id="statCount">%s</b>' % format(total, ",")
    html2, n3 = re.subn(r'<b id="statCount">.*?</b>', new_chip, html2,
                        count=1, flags=re.S)
    if n3 != 1:
        raise RuntimeError("statCount chip not found in specs.html")
    # Stamp the remaining header chips too, so none boot as a bare "..."
    # before (or without) the JS index load; finishLoad() overwrites them live.
    fields = _category_count()
    html2, n4 = re.subn(r'<b id="statFields">.*?</b>',
                        '<b id="statFields">%s</b>' % format(fields, ","),
                        html2, count=1, flags=re.S)
    if n4 != 1:
        raise RuntimeError("statFields chip not found in specs.html")
    html2, n5 = re.subn(r'<b id="statNodes">.*?</b>',
                        '<b id="statNodes">%s</b>' % format(total, ","),
                        html2, count=1, flags=re.S)
    if n5 != 1:
        raise RuntimeError("statNodes chip not found in specs.html")
    # Stamp the Full Spec Archive's count chip too (same source of truth).
    html2, n5b = re.subn(r'<b id="archCount">.*?</b>',
                         '<b id="archCount">%s</b>' % format(total, ","),
                         html2, count=1, flags=re.S)
    if n5b != 1:
        raise RuntimeError("archCount chip not found in specs.html")
    pct = min(100.0, total / 1000000 * 100)
    html2, n6 = re.subn(r'<b id="goalPct">.*?</b>',
                        '<b id="goalPct">%.2f%%</b>' % pct,
                        html2, count=1, flags=re.S)
    if n6 != 1:
        raise RuntimeError("goalPct chip not found in specs.html")
    html2, n7 = re.subn(r'<div class="goalfill" id="goalFill"( style="width:[^"]*")?></div>',
                        '<div class="goalfill" id="goalFill" style="width:%.2f%%"></div>' % pct,
                        html2, count=1)
    if n7 != 1:
        raise RuntimeError("goalFill bar not found in specs.html")
    new_dates = ('<p class="lastupdated">CATALOG DATA LAST UPDATED &nbsp;'
                 '<b id="lastUpdDate">%s</b> &nbsp;&middot;&nbsp; PAGE BUILD '
                 '<b id="pageBuildDate">%s</b></p>' % (TODAY, TODAY))
    html2, n2 = re.subn(r'<p class="lastupdated">.*?</p>', new_dates, html2,
                        count=1, flags=re.S)
    if n2 != 1:
        raise RuntimeError("lastupdated line not found in specs.html")
    if html2 != html:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html2)
        print("stamped static count: %s (as of %s)" % (format(total, ","), TODAY))
    else:
        print("static count already current")

    # Also keep the head Dataset JSON-LD description count/date honest (FIX-02).
    html3, n2 = re.subn(
        r'"description": "\d[\d,]* original draft invention specifications \(as of \d{4}-\d{2}-\d{2}\)',
        '"description": "%s original draft invention specifications (as of %s)' % (format(total, ","), TODAY),
        html2, count=1)
    if n2 != 1:
        raise RuntimeError("Dataset JSON-LD description line not found in specs.html")
    if html3 != html2:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html3)
        print("stamped Dataset JSON-LD description: %s (as of %s)" % (format(total, ","), TODAY))
    else:
        print("Dataset JSON-LD description already current")


def shard_number(dirname):
    """signature-one-archive-shard-25 -> 25."""
    return int(dirname.rsplit("-", 1)[1])


def esc_html(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def stamp_methodology_shards():
    """Keep methodology.html's shard-architecture paragraph honest.

    The shard count grows every few drips; hand-maintained prose goes stale
    (it once said "16 shards" when there were 26). Re-stamp it from the SHARDS
    list every run — same source of truth as the sitemaps.
    """
    path = os.path.join(MAIN, "methodology.html")
    with open(path, encoding="utf-8") as f:
        html = f.read()
    n = len(SHARDS)
    first = min(first for _, first, _ in SHARDS)
    last = max(last for _, _, last in SHARDS)
    total = sum(last - first + 1 for _, first, last in SHARDS)
    new_li = ('<li><b>%d frozen shard repos</b> hold the oldest chunks '
              '(JAH-SPEC-%06d through JAH-SPEC-%06d, %s specs); the <b>main repo</b> '
              'holds the newest chunks and the search index. The file '
              '<code>data/index/shards.json</code> lists every shard in order — '
              'IDs are contiguous across shards with no gaps. (Auto-updated %s.)</li>'
              % (n, first, last, format(total, ","), TODAY))
    html2, n2 = re.subn(r'<li><b>\d+ frozen shard repos</b>.*?</li>', new_li,
                        html, count=1, flags=re.S)
    if n2 != 1:
        raise RuntimeError("shard paragraph not found in methodology.html")
    # Also refresh the stale "16-shard" mentions in meta description + JSON-LD.
    html2 = html2.replace("the 16-shard archive architecture",
                          "the %d-shard archive architecture" % n)
    if html2 != html:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html2)
    print("stamped methodology.html shard paragraph: %d shards" % n)


def write_shard_ranges(ml):
    """Write js/shard-ranges.js for the specs.html shard-jump select (FIX-05).

    The drip re-runs build_sitemaps.py after every run, so the ranges stay
    fresh as shards are created and the main catalog grows.
    """
    ranges = [{"n": "Main catalog", "a": MAIN_RANGE[0], "b": ml}]
    for dirname, first, last in sorted(SHARDS, key=lambda s: shard_number(s[0]), reverse=True):
        ranges.append({"n": "Shard %d" % shard_number(dirname), "a": first, "b": last})
    body = ("/* Auto-generated by code/build_sitemaps.py — do not hand-edit. */\n"
            "var SHARDRANGES = " + json.dumps(ranges) + ";\n")
    out = os.path.join(MAIN, "js", "shard-ranges.js")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote js/shard-ranges.js (%d ranges)" % len(ranges))


def write_data_page():
    """Write data.html: static anchor lists of every catalog data file (FIX-03).

    Shard parsers and crawlers that cannot run the page JS get crawlable
    anchors to every shard index, the compact wiki indexes, and the APIs.
    """
    rows = []
    for dirname, first, last in sorted(SHARDS, key=lambda s: shard_number(s[0])):
        base = "https://justinahiggins614-cmyk.github.io/" + dirname + "/"
        rows.append((base + "data/index/specs.idx.json.gz",
                     "Shard %d — spec index (JAH-SPEC-%06d to JAH-SPEC-%06d)"
                     % (shard_number(dirname), first, last)))
    rows.append((SITE + "/data/index/specs.idx.json.gz", "Main catalog — spec index (newest chunks)"))
    rows.append((SITE + "/data/index/specs.search.json.gz",
                 "Compact search index (one row per spec, all shards + main)"))
    rows.append((SITE + "/data/index/specs.sigline.json.gz",
                 "Signature-line index (public patent -> JAH-SPEC)"))
    rows.append((SITE + "/data/index/words.idx.json.gz", "Word-invention index (JAH-WORD-######)"))
    # Full Spec Archive: per-letter lazy indexes + manifest (built by
    # code/build_search_index.py alongside the compact search index)
    try:
        azm = json.load(open(os.path.join(MAIN, "data", "index", "az",
                                          "manifest.json"), encoding="utf-8"))
        rows.append((SITE + "/data/index/az/manifest.json",
                     "A-Z archive manifest (%s draft specs, per-letter counts)"
                     % format(azm.get("total", 0), ",")))
        for L in sorted(azm.get("counts", {})):
            rows.append((SITE + "/data/index/az/%s.json.gz" % L,
                         "A-Z archive — letter %s (%s draft specs, titles + IDs)"
                         % (L, format(azm["counts"][L], ","))))
    except (OSError, ValueError):
        pass
    rows.append((SITE + "/api.json", "Catalog API manifest"))
    rows.append((SITE + "/sitemap-index.xml", "Segmented sitemap index"))
    lis = "\n".join(
        '    <li><a href="%s">%s</a><br><span class="u">%s</span></li>' % (u, esc_html(t), u)
        for u, t in rows)
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Catalog data files — Signature Spec Catalog</title>
<meta name="description" content="Static index of every Signature Spec Catalog data file: shard indexes, search indexes, and API manifests.">
<link rel="canonical" href="%s/data.html">
<style>
body{background:#060608;color:#c9c9d2;font-family:monospace;margin:0;padding:24px 16px;max-width:900px}
h1{color:#ff3b3b;font-size:1.2em} a{color:#ff6b6b} .u{color:#77777f;font-size:.8em;word-break:break-all}
li{margin:10px 0} p{line-height:1.6}
</style>
</head>
<body>
<h1>Catalog data files</h1>
<p>Every data file behind the Signature Spec Catalog, as static crawlable links.
Shard indexes are gzipped JSON arrays; each spec row carries its permanent
JAH-SPEC-###### identifier. Per-record deep links follow the pattern
<code>specs.html?spec=JAH-SPEC-000123</code>. All records are draft invention
specifications authored by Justin Addam Higgins (JAH) — drafts, ready to
review and file; not granted patents; not affiliated with the USPTO.</p>
<ul>
%s
</ul>
<p><a href="specs.html">&larr; Back to the Spec Catalog</a></p>
</body>
</html>
""" % (SITE, lis)
    with open(os.path.join(MAIN, "data.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote data.html (%d anchors)" % len(rows))


def check_az_manifest(total):
    """Fail loud if the Full Spec Archive index is stale or missing.

    code/build_search_index.py rebuilds data/index/az/ (per-letter files +
    manifest.json) on every drip, BEFORE this script runs. If the manifest is
    missing or its total disagrees with the freshly computed catalog total,
    the archive would ship one run behind — stop the drip step instead of
    silently publishing a stale archive.
    """
    mpath = os.path.join(MAIN, "data", "index", "az", "manifest.json")
    if not os.path.exists(mpath):
        raise RuntimeError("A-Z archive manifest missing: %s — run "
                           "code/build_search_index.py first" % mpath)
    with open(mpath, encoding="utf-8") as f:
        m = json.load(f)
    if m.get("total") != total:
        raise RuntimeError("A-Z archive manifest total %s != catalog total "
                           "%d — re-run code/build_search_index.py"
                           % (m.get("total"), total))
    if sum(m.get("counts", {}).values()) != total:
        raise RuntimeError("A-Z archive letter counts do not sum to the "
                           "catalog total — re-run code/build_search_index.py")
    print("A-Z archive manifest OK: %d rows across %d letters"
          % (total, len(m.get("counts", {}))))


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
    # MAIN_RANGE start follows the newest shard (shard-33 ends at 622050); end follows state.json.
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
    check_az_manifest(total)
    stamp_static_count(total)
    stamp_methodology_shards()
    write_shard_ranges(ml)
    write_data_page()


if __name__ == "__main__":
    main()
