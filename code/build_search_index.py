#!/usr/bin/env python3
"""Build compact search indexes for light clients (JAH Wiki search).

The wiki used to download every shard's full specs.idx.json.gz (21 files,
~31MB gz, ~300MB of JSON parsed on the main thread) just to search titles.
On phones that blows the 25s load budget and search never works.

This builder writes two small files instead:
  data/index/specs.search.json.gz  - one compact row per spec:
      [spec_id, title, chunk_file, shard_n, category]
  data/index/specs.sigline.json.gz - [pub, spec_id, title] for Signature-line
      specs only (lets the wiki link a patent to its Signature-line version
      without scanning the full index)

Shard repos are frozen storage, so per-shard compact rows are cached in
~/workspace/hidden_files/spec-search-cache/<slug>.jsonl.gz and reused;
only the main repo's own index is re-read every run. Run this after every
drip (build_index.py) and after every shard move, then commit + push.

Row layout contract with jah-wiki/index.html loadDB():
  search row: [0]=spec_id, [1]=title, [2]=chunk path (data/volumes/...),
              [3]=shard_n (position in data/index/shards.json "shards"
              array), [4]=category
"""
import gzip
import io
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)  # repo root (code/ lives directly under it)
INDEXDIR = os.path.join(REPO, "data", "index")
CACHEDIR = os.path.expanduser("~/workspace/hidden_files/spec-search-cache")
PUB_RE = re.compile(r"patent record ([A-Z]{2}[A-Z0-9]+)")


def read_idx_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def fetch_idx(url):
    req = urllib.request.Request(url, headers={"User-Agent": "JAH-search-index-builder/1.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return gzip.decompress(r.read()).decode("utf-8").splitlines()


def slug_of(base):
    return base.rstrip("/").rsplit("/", 1)[-1] or "main"


def compact_rows(idx_lines):
    """Yield (search_row, sigline_row_or_None) for each full index row."""
    for line in idx_lines:
        line = line.strip() if isinstance(line, str) else line
        if not line:
            continue
        r = json.loads(line) if isinstance(line, str) else line
        if len(r) < 21:
            continue
        spec_id, title, chunk, category = r[0], r[1], r[20], r[3]
        yield [spec_id, title, chunk, category], r


def main():
    os.makedirs(CACHEDIR, exist_ok=True)
    with open(os.path.join(INDEXDIR, "shards.json"), encoding="utf-8") as f:
        doc = json.load(f)
    shards = doc["shards"] if isinstance(doc, dict) else doc

    search_rows = []
    sigline = []
    seen_sig = set()

    for n, entry in enumerate(shards):
        base = (entry.get("base") or "").rstrip("/")
        index = entry.get("index") or "data/index/specs.idx.json.gz"
        if not base:
            # main repo: read the freshly rebuilt local index
            local = os.path.join(REPO, index)
            lines = list(read_idx_gz(local))
            for (srow, full) in compact_rows(lines):
                srow.insert(3, n)
                search_rows.append(srow)
                lin = full[13] if len(full) > 13 else ""
                if lin and "Signature-line" in str(lin):
                    m = PUB_RE.search(str(lin))
                    if m and m.group(1) not in seen_sig:
                        seen_sig.add(m.group(1))
                        sigline.append([m.group(1), full[0], full[1]])
            print(f"main (shard_n={n}): {len(lines)} rows", flush=True)
            continue
        # frozen shard: use cache, else download once
        slug = slug_of(base)
        cache = os.path.join(CACHEDIR, slug + ".jsonl.gz")
        if os.path.exists(cache):
            lines = list(read_idx_gz(cache))
            cached = True
        else:
            url = base + "/" + index
            print(f"downloading {url} ...", flush=True)
            raw_lines = fetch_idx(url)
            buf = io.StringIO()
            for (srow, _full) in compact_rows(raw_lines):
                buf.write(json.dumps(srow, separators=(",", ":")) + "\n")
            with gzip.open(cache, "wt", encoding="utf-8") as cf:
                cf.write(buf.getvalue())
            lines = list(read_idx_gz(cache))
            cached = False
        for srow in lines:  # cached rows are [id,title,chunk,category]
            search_rows.append([srow[0], srow[1], srow[2], n, srow[3]])
        # sigline rows for this shard (own cache file, rebuilt if missing)
        sig_cache = os.path.join(CACHEDIR, slug + ".sigline.json.gz")
        if os.path.exists(sig_cache):
            with gzip.open(sig_cache, "rt", encoding="utf-8") as sf:
                for s in json.load(sf):
                    if s[0] not in seen_sig:
                        seen_sig.add(s[0])
                        sigline.append(s)
            print(f"{slug}: sigline [{os.path.getsize(sig_cache)//1024}KB cache]", flush=True)
        else:
            if cached:
                # search rows were cached but sigline cache is missing (e.g.
                # regex change): re-derive from the shard index download
                url = base + "/" + index
                print(f"re-downloading {url} for sigline ...", flush=True)
                raw_lines = fetch_idx(url)
            shard_sig = []
            for line in raw_lines:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                lin = r[13] if len(r) > 13 else ""
                if lin and "Signature-line" in str(lin):
                    m = PUB_RE.search(str(lin))
                    if m:
                        shard_sig.append([m.group(1), r[0], r[1]])
                        if m.group(1) not in seen_sig:
                            seen_sig.add(m.group(1))
                            sigline.append([m.group(1), r[0], r[1]])
            with gzip.open(sig_cache, "wt", encoding="utf-8") as sf:
                json.dump(shard_sig, sf)
            print(f"{slug}: sigline [{len(shard_sig)} rows rebuilt]", flush=True)
        print(f"{slug} (shard_n={n}): {len(lines)} rows {'[cache]' if cached else '[downloaded]'}", flush=True)

    search_rows.sort(key=lambda r: r[0])
    out_search = os.path.join(INDEXDIR, "specs.search.json.gz")
    with gzip.open(out_search, "wt", encoding="utf-8") as f:
        for r in search_rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
    out_sig = os.path.join(INDEXDIR, "specs.sigline.json.gz")
    with gzip.open(out_sig, "wt", encoding="utf-8") as f:
        json.dump(sigline, f, separators=(",", ":"))

    # sanity: IDs unique and contiguous-ish
    ids = [r[0] for r in search_rows]
    dupes = len(ids) - len(set(ids))
    print(f"WROTE {out_search}: {len(search_rows)} rows, {os.path.getsize(out_search)/1e6:.1f}MB gz, dupes={dupes}")
    print(f"WROTE {out_sig}: {len(sigline)} sigline rows, {os.path.getsize(out_sig)/1e3:.0f}KB gz")
    if dupes:
        print("ERROR: duplicate spec IDs in search index", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
