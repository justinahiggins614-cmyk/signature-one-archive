#!/usr/bin/env python3
"""Link audit for the Spec Catalog page code (specs.html, standard.html).

Checks:
  - relative hrefs resolve to a real file in this repo
  - absolute http(s) hrefs return HTTP 200 (HEAD, fallback to GET)
  - key deep-link targets (?spec=, ?word=, ?dossier=, ?w=) resolve live

Re-runnable: python3 code/qa/check_links.py
Exit 0 when clean, 1 when findings remain. Findings are also printed so the
runner can fix or explicitly mark them dead.
"""
import os, re, sys, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAGES = ["specs.html", "standard.html"]

# Deep-link targets that are built client-side in JS (not literal hrefs).
# We probe them with real IDs known to exist in the data indexes.
DEEP_LINKS = [
    "https://justinahiggins614-cmyk.github.io/signature-one-archive/specs.html?spec=JAH-SPEC-325051",
    "https://justinahiggins614-cmyk.github.io/signature-one-archive/specs.html?word=rug",
    "https://justinahiggins614-cmyk.github.io/jah-n-wiki-leaks/?dossier=JAH-SPEC-325051",
    "https://justinahiggins614-cmyk.github.io/jah-dictionary/?w=rug",
]

# Resource-hint hrefs (preconnect): not page destinations. The real stylesheet
# URL (css2?...) is checked live; the bare domains only warm up connections.
HINT_DOMAINS = {"https://fonts.googleapis.com", "https://fonts.gstatic.com"}

HREF_RE = re.compile(r'''href\s*=\s*["']([^"'#][^"']*)["']''', re.I)

def fetch_status(url):
    req = urllib.request.Request(url, headers={"User-Agent": "jah-qa-linkcheck/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except Exception:
        pass
    try:  # some hosts reject HEAD; retry with GET
        req.get_method = lambda: "GET"
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except Exception as e:
        return "ERROR: %s" % e

def main():
    findings = []
    urls = set()
    for page in PAGES:
        path = os.path.join(REPO, page)
        if not os.path.exists(path):
            findings.append("%s: page file missing" % page)
            continue
        text = open(path, encoding="utf-8", errors="replace").read()
        for href in HREF_RE.findall(text):
            href = href.strip()
            if href.startswith(("mailto:", "tel:", "javascript:", "data:")):
                continue
            if href.startswith("#"):
                continue
            urls.add(href)
    for url in DEEP_LINKS:
        urls.add(url)
    checked = 0
    for url in sorted(urls):
        if url.rstrip("/") in HINT_DOMAINS:
            print("hint %s (preconnect — stylesheet URL checked separately)" % url)
            checked += 1
            continue
        if url.startswith("http"):
            status = fetch_status(url)
            checked += 1
            if status != 200:
                findings.append("DEAD/LIVE-CHECK: %s -> %s" % (url, status))
            else:
                print("ok   %s" % url)
        else:  # relative: must exist in repo
            target = os.path.normpath(os.path.join(REPO, url.split("?")[0]))
            checked += 1
            if not os.path.exists(target):
                findings.append("MISSING-FILE: %s (referenced as %s)" % (target, url))
            else:
                print("ok   %s" % url)
    print("---")
    print("checked %d links across %s" % (checked, ", ".join(PAGES)))
    if findings:
        print("FINDINGS (%d):" % len(findings))
        for f in findings:
            print("  - " + f)
        return 1
    print("all links live")
    return 0

if __name__ == "__main__":
    sys.exit(main())
