#!/usr/bin/env python3
"""Build the lightweight search index for lazy page loading.

Reads every chunk in data/volumes (manifest order) and writes
data/index/specs.idx.json.gz -- one JSON array per line with the fields the
cards, filters and search need:

  [spec_id, title, abstract, category, cpc, era, prepared_date,
   null, null, null, null, letter, line, line_note,
   null, null, null, null, null, mix_from, chunk_name]

Indices match the page's row layout; heavy fields are null in the index.
The page fetches the chunk named in the last slot to get the full record.

Also writes data/index/shards.json so future shard repos can be added
behind the same page without touching it again:
  {"shards": [{"base": "", "index": "data/index/specs.idx.json.gz"}]}
"""
import gzip
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "data")
VOLDIR = os.path.join(DATA, "volumes")
MANIFEST = os.path.join(VOLDIR, "manifest.json")
INDEXDIR = os.path.join(DATA, "index")
INDEXPATH = os.path.join(INDEXDIR, "specs.idx.json.gz")
SHARDSPATH = os.path.join(INDEXDIR, "shards.json")


def letter_of(title):
    t = (title or "").strip().upper()
    for ch in t:
        if "A" <= ch <= "Z":
            return ch
        if "0" <= ch <= "9":
            return "#"
    return "#"


def chunk_files():
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as fh:
            files = json.load(fh).get("files", [])
        files = [f for f in files if f.startswith("volumes/")]
        if files:
            return files
    import glob
    return sorted("volumes/" + os.path.basename(p)
                  for p in glob.glob(os.path.join(VOLDIR, "specs-*.jsonl.gz")))


def main():
    os.makedirs(INDEXDIR, exist_ok=True)
    n = 0
    with gzip.open(INDEXPATH, "wb", compresslevel=6) as out:
        for rel in chunk_files():
            path = os.path.join(DATA, rel)
            opener = gzip.open if path.endswith(".gz") else open
            with opener(path, "rt", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if not ln:
                        continue
                    try:
                        d = json.loads(ln)
                    except Exception:
                        continue
                    row = [
                        d.get("spec_id"), d.get("title"), d.get("abstract"),
                        d.get("category"), d.get("cpc"), d.get("era"),
                        d.get("prepared_date"),
                        None, None, None, None,
                        letter_of(d.get("title")),
                        d.get("line") or "", d.get("line_note") or "",
                        None, None, None, None, None,
                        d.get("mix_from"), rel,
                    ]
                    out.write((json.dumps(row, ensure_ascii=False) + "\n").encode("utf-8"))
                    n += 1
    # Preserve any extra shard entries (shard repos) already registered;
    # the local entry always comes first.
    extra = []
    if os.path.exists(SHARDSPATH):
        try:
            with open(SHARDSPATH, encoding="utf-8") as fh:
                for s in json.load(fh).get("shards", []):
                    if isinstance(s, dict) and s.get("base"):
                        extra.append({"base": s["base"],
                                      "index": s.get("index", "data/index/specs.idx.json.gz")})
        except Exception:
            pass
    with open(SHARDSPATH, "w", encoding="utf-8") as fh:
        json.dump({"shards": [{"base": "", "index": "data/index/specs.idx.json.gz"}] + extra}, fh)
    size_mb = os.path.getsize(INDEXPATH) / 1048576
    print(f"index_lines={n} index_size={size_mb:.1f}MB gz")


if __name__ == "__main__":
    main()
