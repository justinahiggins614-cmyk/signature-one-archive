#!/usr/bin/env python3
"""Pack staged JAH-WORD records into data/volumes/words-cNNNNN.jsonl.gz
(150 records per chunk) and update the word indexes.

- data/index/words.idx.json.gz    -> cumulative [word_lower, spec_id, chunkFile, lineIdx]
- data/index/words.search.json.gz -> cumulative 21-element search rows (specs.idx shape)
Both are re-gzipped after each pack run (multi-run safe: rebuild from jsonl).

Usage: python3 pack.py
"""
import json, os, gzip, glob

ROOT = os.path.expanduser("~/workspace/signature-one-archive")
WS = os.path.join(ROOT, "code", "wordspecs")
STATE = os.path.join(WS, "state.json")
STAGE = os.path.join(WS, "staging", "wordspec_staging.jsonl")
VOLDIR = os.path.join(ROOT, "data", "volumes")
IDXDIR = os.path.join(ROOT, "data", "index")
CHUNK = 150

def letter_of(title):
    for ch in str(title or "").strip().upper():
        if "A" <= ch <= "Z":
            return ch
        if "0" <= ch <= "9":
            return "#"
    return "#"

def search_row(rec, chunk_file):
    return [rec["spec_id"], rec["title"], rec["abstract"], rec["category"],
            rec["cpc"], rec["era"], rec["prepared_date"],
            None, None, None, None, letter_of(rec["title"]),
            rec["line"], rec.get("line_note", ""),
            None, None, None, None, None, None, chunk_file]

def main():
    if not os.path.exists(STAGE) or os.path.getsize(STAGE) == 0:
        print("nothing staged")
        return
    staged = []
    with open(STAGE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                staged.append(json.loads(line))
    if not staged:
        print("nothing staged")
        return
    st = json.load(open(STATE)) if os.path.exists(STATE) else {"next_index": 0, "next_id": 1, "chunks": 0}
    os.makedirs(VOLDIR, exist_ok=True)
    os.makedirs(IDXDIR, exist_ok=True)
    # continue chunk numbering from highest existing words-cNNNNN
    nums = []
    for n in os.listdir(VOLDIR):
        if n.startswith("words-c") and n.endswith(".jsonl.gz"):
            try:
                nums.append(int(n[7:12]))
            except ValueError:
                pass
    cn = max(nums) if nums else 0
    idx_jsonl = os.path.join(IDXDIR, "words.idx.jsonl")       # working file (removed after gzip)
    sch_jsonl = os.path.join(IDXDIR, "words.search.jsonl")    # working file (removed after gzip)
    idx_gz = os.path.join(IDXDIR, "words.idx.json.gz")        # served to the site
    sch_gz = os.path.join(IDXDIR, "words.search.json.gz")     # served to the site
    # restore cumulative working files from the served .gz (they are not stored)
    for wj, gz in ((idx_jsonl, idx_gz), (sch_jsonl, sch_gz)):
        if not os.path.exists(wj) and os.path.exists(gz):
            with gzip.open(gz, "rb") as f_in, open(wj, "wb") as f_out:
                f_out.write(f_in.read())
    n_new_chunks = 0
    with open(idx_jsonl, "a", encoding="utf-8") as fi, open(sch_jsonl, "a", encoding="utf-8") as fs:
        buf = []
        def flush():
            nonlocal cn, n_new_chunks
            if not buf:
                return
            cn += 1
            cname = "words-c%05d.jsonl.gz" % cn
            with gzip.open(os.path.join(VOLDIR, cname), "wt", encoding="utf-8") as gz:
                for li, rec in enumerate(buf):
                    gz.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    fi.write(json.dumps([rec["word"].lower(), rec["spec_id"],
                                         "volumes/" + cname, li]) + "\n")
                    fs.write(json.dumps(search_row(rec, "volumes/" + cname),
                                        ensure_ascii=False) + "\n")
            n_new_chunks += 1
            buf.clear()
        for rec in staged:
            buf.append(rec)
            if len(buf) >= CHUNK:
                flush()
        flush()
    st["chunks"] = cn
    json.dump(st, open(STATE, "w"), indent=1)
    # re-gzip the cumulative indexes to their served names; drop working files
    for src, gz in ((idx_jsonl, idx_gz), (sch_jsonl, sch_gz)):
        with open(src, "rb") as f_in, gzip.open(gz, "wb") as f_out:
            f_out.write(f_in.read())
        os.remove(src)
    open(STAGE, "w").close()  # clear staging
    # verify chunk integrity
    total = 0
    for n in sorted(os.listdir(VOLDIR)):
        if n.startswith("words-c") and n.endswith(".jsonl.gz"):
            with gzip.open(os.path.join(VOLDIR, n), "rt", encoding="utf-8") as gz:
                for line in gz:
                    json.loads(line)
                    total += 1
    print("packed %d records into %d new chunks (%d total chunks, %d total word records)" % (
        len(staged), n_new_chunks, cn, total))

if __name__ == "__main__":
    main()
