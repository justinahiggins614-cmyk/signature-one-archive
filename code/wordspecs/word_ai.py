#!/usr/bin/env python3
"""Generate JAH-AI-WORD records: one telephone-book AI for every dictionary
word, tied to its JAH-WORD patent draft + its word program + its dictionary
entry. Everything derives from Manon's own IWB definitions and word-spec
records — nothing copied from outside sources.

Reads packed JAH-WORD volumes (data/volumes/words-c*.jsonl.gz) in id order and
emits word-AI records for every id >= state next_id. Packs 150/chunk into
data/ai/wordai-cNNNNN.jsonl.gz (uniform chunks, sequential ids, so the phone
book can derive chunk/line from the id) and rebuilds the cumulative index
data/index/wordai.idx.json.gz as [[word_lower, id_num], ...].

State: code/wordspecs/word_ai_state.json {"next_id":1,"chunks":0}.

Usage: python3 word_ai.py   (processes everything new since the last run)
"""
import json, os, gzip, glob, re

ROOT = os.path.expanduser("~/workspace/signature-one-archive")
WROOT = os.path.expanduser("~/workspace/jah-dictionary")
WS = os.path.join(ROOT, "code", "wordspecs")
STATE = os.path.join(WS, "word_ai_state.json")
VOLDIR = os.path.join(ROOT, "data", "volumes")
AIDIR = os.path.join(ROOT, "data", "ai")
IDXDIR = os.path.join(ROOT, "data", "index")
CHUNK = 150
INV = "Justin Addam Higgins"
DICT_BASE = "https://justinahiggins614-cmyk.github.io/jah-dictionary/"
SPEC_BASE = "https://justinahiggins614-cmyk.github.io/signature-one-archive/specs.html"

STOPWORDS = set("""a an the and or but of to in on for with as at by from is are was were
be been being it its this that these those they them their he she we you your our
one two used use often very can may might must shall will would could should do
does did done have has had having not no nor so such than then there here when
where which who whom whose what how why into over under again once such more most
other some any each every both few many much own same too also just about between
through during before after above below up down out off only own same than too very
can will just don should now""".split())

def load_defs():
    defs = {}
    p = os.path.join(WROOT, "data", "definitions", "all.jsonl")
    if not os.path.exists(p):
        return defs
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
                defs[w.lower()] = {
                    "pos": str(r.get("pos", "") or ""),
                    "d": [str(s) for s in (r.get("d") or []) if str(s).strip()][:2],
                }
    return defs

def display(w):
    if w and w[0].isalpha():
        return w[0].upper() + w[1:]
    return w

def key_terms(definition, word, n=6):
    out = []
    wl = word.lower()
    for tok in re.findall(r"[A-Za-z][A-Za-z\-']*", definition.lower()):
        t = tok.strip("-'")
        if len(t) >= 5 and t not in STOPWORDS and t != wl and t not in out:
            out.append(t)
        if len(out) >= n:
            break
    return out

def demo_sentences(w, pos):
    wl = w.lower()
    if w.startswith("-"):
        kind = "suffix" if pos == "suffix" else ("prefix" if pos == "prefix" else "affix")
        return [
            "As a %s, '%s' does its work inside other words \u2014 watch for it and you will see it everywhere." % (kind, w),
            "Build with '%s': take a root word, add the %s, and a brand-new word is born." % (w, kind),
            "'%s' is small but mighty \u2014 whole families of words carry it." % w,
        ]
    if pos == "noun":
        return [
            "The %s sat exactly where it belonged, doing its quiet work." % wl,
            "She reached for the %s without even looking \u2014 habit knows the way." % wl,
            "Every home has a %s with a story; this one had three." % wl,
        ]
    if pos == "verb":
        return [
            "Every morning, they %s without even thinking about it." % wl,
            "Learn to %s once, and you will %s for the rest of your life." % (wl, wl),
            "She decided she would %s, and nothing talked her out of it." % wl,
        ]
    if pos == "adjective":
        return [
            "It was a %s morning, the kind you remember for years." % wl,
            "The %s idea won because it was simply true." % wl,
            "He gave a %s answer and everyone nodded." % wl,
        ]
    if pos == "adverb":
        return [
            "She spoke %s, and the room understood." % wl,
            "He finished %s, ahead of everyone else." % wl,
            "They worked %s until the job was done right." % wl,
        ]
    return [
        "Here is '%s' at work: the %s shows exactly what the word means." % (w, wl),
        "Say it with me: '%s' \u2014 now use it before the day is out." % w,
        "'%s' earns its place: one word, doing real work in a real sentence." % w,
    ]

def build_word_ai(num, word, spec_id, defs):
    ai_id = "JAH-AI-WORD-%06d" % num
    d = defs.get(word.lower(), {})
    pos = d.get("pos", "")
    senses = d.get("d", [])
    known = bool(senses)
    definition = senses[0] if senses else ""
    name = display(word) + " AI"
    pos_label = pos or "word"

    if known:
        mentality = ("I am the '%s' AI \u2014 a true expert on the word '%s'. %s "
                     "Ask me to define it, use it in sentences, teach it like a tutor, "
                     "or walk you through its word patent and its working program.") % (word, word, definition)
    else:
        mentality = ("I am the '%s' AI \u2014 keeper of the word-form '%s' itself. The editors "
                     "are still writing its full definition, but I already hold its word patent draft %s "
                     "and its working program, and I will teach you everything the record holds.") % (word, word, spec_id)

    abilities = [
        "Define '%s' in plain words" % word,
        "Use '%s' in real sentences" % word,
        "Teach '%s' like a personal tutor" % word,
        "Show the word patent %s" % spec_id,
        "Run the '%s' word program" % word,
    ]
    params = [
        ["word", word],
        ["part of speech", pos_label],
        ["word patent", spec_id],
        ["dictionary", "The Signature Dictionary \u2014 ?w=" + word],
    ]

    rules = []
    if known:
        rules.append({
            "k": ["define", "definition", "meaning", "mean", "what is"],
            "r": ["'%s' means: %s" % (word, definition),
                  "The definition of '%s': %s" % (word, definition)],
        })
    rules.append({
        "k": ["sentence", "example", "use it", "use the word"],
        "r": ["Here is '%s' in a sentence: %s" % (word, demo_sentences(word, pos)[0]),
              "Try this one: %s" % demo_sentences(word, pos)[1]],
    })
    rules.append({
        "k": ["patent"],
        "r": ["The word patent for '%s' is %s \u2014 a full draft patent specification turning the word into a buildable invention. Find it in the Signature Spec Catalog under Word Inventions." % (word, spec_id),
              "%s covers '%s' as an invention: six-tool mapped geometry, key parameters, claims, and a working program. It is a draft \u2014 ready to file, not a granted patent." % (spec_id, word)],
    })
    rules.append({
        "k": ["program", "code", "python", "run"],
        "r": ["The '%s' word program is a working Python script built from the word \u2014 download it from my file and run it anywhere Python lives." % word,
              "My program prints the definition of '%s' and shows it working in a sentence. Grab the .py from my file tools."],
    })
    rules.append({
        "k": ["spell", "spelling", "letters"],
        "r": ["'%s' is spelled: %s \u2014 %d characters." % (word, " - ".join(list(word.upper())), len(word)),
              "Letter by letter: %s." % ", ".join(list(word))],
    })
    if known:
        for term in key_terms(definition, word, 4):
            rules.append({
                "k": [term],
                "r": ["'%s' is a key part of '%s': %s" % (term, word, definition),
                      "Think of '%s' through '%s' \u2014 %s" % (word, term, definition)],
            })

    if known:
        fallback = [
            "As the '%s' AI, I start from its meaning: %s What would you like \u2014 define, use, learn, patent, or program?" % (word, definition),
            "Everything I know about '%s' grows from one root: %s Ask me for a sentence, a lesson, or its patent." % (word, definition),
            "I am the expert on '%s' \u2014 %s Try asking me to define it, spell it, or show its program." % (word, definition),
            "'%s': %s That is my home ground. Shall we take it to the classroom, the patent office, or the code bench?" % (word, definition),
        ]
        greeting = "Hello \u2014 I am the '%s' AI, your expert on the word '%s'. %s Ask me anything about it." % (display(word), word, definition)
    else:
        fallback = [
            "As the '%s' AI, I hold its word patent %s and its working program even while the full definition is being written. Ask me about either." % (word, spec_id),
            "The editors are still writing the full definition of '%s' \u2014 but its patent draft and program are ready. Which shall we open?" % word,
            "I am the keeper of '%s'. Its file carries the patent %s and a runnable program; the definition arrives soon." % (word, spec_id),
            "Ask me to show the word patent for '%s', or run its program \u2014 both are ready now." % word,
        ]
        greeting = "Hello \u2014 I am the '%s' AI, keeper of the word '%s'. Its full definition is still being written, but its patent and program are ready. What shall we open?" % (display(word), word)

    sentences = demo_sentences(word, pos)

    py_lines = [
        "# %s %s (word AI)" % (ai_id, name),
        "# Signature-made by %s \u2014 the AI Telephone Book" % INV,
        "# Word patent: %s | Dictionary: ?w=%s" % (spec_id, word),
        "WORD = " + json.dumps(word, ensure_ascii=False),
        "POS = " + json.dumps(pos_label, ensure_ascii=False),
        "DEFINITION = " + json.dumps(definition or "Definition still being written by the editors.", ensure_ascii=False),
        "SENTENCE = " + json.dumps(sentences[0], ensure_ascii=False),
        'print("%s online \u2014 expert on the word %s." %% WORD)' % (name, json.dumps(word, ensure_ascii=False)),
        'print("Definition: " + DEFINITION)',
        'print("In a sentence: " + SENTENCE)',
        'print("Word patent: %s (Signature Spec Catalog \u2014 draft, ready to file).")' % spec_id,
    ]

    return {
        "ai_id": ai_id,
        "word": word,
        "word_spec": spec_id,
        "name": name,
        "stamp": ai_id,
        "kind": "word",
        "mentality": mentality,
        "abilities": abilities,
        "params": params,
        "rules": rules,
        "fallback": fallback,
        "greeting": greeting,
        "demoKind": "word",
        "definition": definition,
        "sentences": sentences,
        "links": {
            "dictionary": DICT_BASE + "?w=" + word,
            "wordPatent": SPEC_BASE + "?word=" + word,
        },
        "py": "\n".join(py_lines),
    }

def load_word_records():
    recs = []
    for f in sorted(glob.glob(os.path.join(VOLDIR, "words-c*.jsonl.gz"))):
        with gzip.open(f, "rt", encoding="utf-8") as gz:
            for line in gz:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    recs.append(r)
    recs.sort(key=lambda r: int(r["spec_id"].split("-")[2]))
    return recs

def main():
    os.makedirs(AIDIR, exist_ok=True)
    os.makedirs(IDXDIR, exist_ok=True)
    st = {"next_id": 1, "chunks": 0}
    if os.path.exists(STATE):
        st.update(json.load(open(STATE)))
    defs = load_defs()
    recs = load_word_records()
    new_recs = []
    for r in recs:
        num = int(r["spec_id"].split("-")[2])
        if num < st["next_id"]:
            continue
        new_recs.append(build_word_ai(num, r["word"], r["spec_id"], defs))
    if not new_recs:
        print("word-ai: nothing new (next_id=%d)" % st["next_id"])
        return
    # continue chunk numbering
    nums = []
    for n in os.listdir(AIDIR):
        if n.startswith("wordai-c") and n.endswith(".jsonl.gz"):
            try:
                nums.append(int(n[8:13]))
            except ValueError:
                pass
    cn = max(nums) if nums else 0
    idx_gz = os.path.join(IDXDIR, "wordai.idx.json.gz")
    idx_rows = []
    if os.path.exists(idx_gz):
        with gzip.open(idx_gz, "rt", encoding="utf-8") as gz:
            idx_rows = json.load(gz)
    n_new_chunks = 0
    buf = []
    def flush():
        nonlocal cn, n_new_chunks
        if not buf:
            return
        cn += 1
        cname = "wordai-c%05d.jsonl.gz" % cn
        with gzip.open(os.path.join(AIDIR, cname), "wt", encoding="utf-8") as gz:
            for rec in buf:
                gz.write(json.dumps(rec, ensure_ascii=False) + "\n")
                idx_rows.append([rec["word"].lower(), int(rec["ai_id"].split("-")[3])])
        n_new_chunks += 1
        buf.clear()
    for rec in new_recs:
        buf.append(rec)
        if len(buf) >= CHUNK:
            flush()
    flush()
    with gzip.open(idx_gz, "wt", encoding="utf-8") as gz:
        json.dump(idx_rows, gz, ensure_ascii=False)
    st["next_id"] = int(new_recs[-1]["ai_id"].split("-")[3]) + 1
    st["chunks"] = cn
    json.dump(st, open(STATE, "w"), indent=1)
    print("word-ai: +%d records in %d new chunks (%d total chunks, %d total word-AIs, next_id=%d)" % (
        len(new_recs), n_new_chunks, cn, len(idx_rows), st["next_id"]))

if __name__ == "__main__":
    main()
