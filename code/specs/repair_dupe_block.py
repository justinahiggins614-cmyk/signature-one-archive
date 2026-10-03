"""Repair the 2026-09-30 spec-drip duplicate-ID collision.

Root cause: the cron worker ran the six generators concurrently; each read
code/specs/state.json next_index while the others were still writing, so the
signature-line / mix / versions / revisions / product-lines generators all
wrote into the same ID block JAH-SPEC-177841..180840 (3000 IDs, 5500 extra
writes, multiplicity up to 4x).

Repair policy (Manon's standing rule: NEVER delete data, repair by re-IDing):
- Every duplicate write is a DISTINCT spec (verified: 0 identical copies), so
  each keeps its record and gets a fresh unique ID.
- First occurrence of each spec_id keeps its ID; 2nd+ occurrences are re-ID'd
  from (max_id + 1) upward, with all self-references inside the record updated.
- Tracking files that point at re-ID'd records are remapped by title match:
  revision_coverage values [n, latest_spec_id, title] and product_lines
  latest_id (matched via line name inside the member title).
- revision_coverage KEYS stay: the generators' hot-scan was first-wins, so
  keys already mean the first occurrence.
- all_ids.d sharded index / software_ids.json gain every post-repair ID.
- state.json next_index = max_id + 1.
"""
import json, re, os, gzip, glob, sys
from collections import defaultdict

import all_ids_store

REPO = os.path.expanduser('~/workspace/signature-one-archive')
HOT = os.path.join(REPO, 'data/specs.jsonl')
SPEC_RE = re.compile(r'JAH-SPEC-(\d+)')

def spec_num(sid):
    m = SPEC_RE.fullmatch(str(sid))
    return int(m.group(1)) if m else None

# ---- 1. max ID across sealed volumes -------------------------------------
vol_max = 0
for f in sorted(glob.glob(os.path.join(REPO, 'data/volumes', 'specs-*.jsonl.gz'))):
    with gzip.open(f, 'rt', encoding='utf-8') as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            n = spec_num(json.loads(ln)['spec_id'])
            if n and n > vol_max:
                vol_max = n
print('sealed volumes max:', vol_max)

with open(HOT, encoding='utf-8') as fh:
    hot_lines = [ln for ln in fh if ln.strip()]
hot_max = max(spec_num(json.loads(ln)['spec_id']) for ln in hot_lines)
print('hot records:', len(hot_lines), 'hot max:', hot_max)

next_new = max(vol_max, hot_max) + 1
print('new IDs start at:', next_new)

# ---- 2. re-ID duplicate occurrences --------------------------------------
occurrences = defaultdict(list)   # old_id -> [{line, title, new?}]
out = []
reided = 0
for idx, ln in enumerate(hot_lines):
    r = json.loads(ln)
    old = r['spec_id']
    occ_no = len(occurrences[old])
    occurrences[old].append({'line': idx, 'title': r.get('title', ''), 'old': old})
    if occ_no == 0:
        out.append(ln if ln.endswith('\n') else ln + '\n')
    else:
        new = 'JAH-SPEC-%06d' % next_new
        next_new += 1
        s = json.dumps(r, separators=(',', ':'), ensure_ascii=True)
        assert old in s, old
        s = s.replace(old, new)
        r2 = json.loads(s)
        assert r2['spec_id'] == new
        out.append(s + '\n')
        occurrences[old][-1]['new'] = new
        reided += 1
print('re-IDd duplicate writes:', reided)

tmp = HOT + '.repair_tmp'
with open(tmp, 'w', encoding='utf-8') as fh:
    fh.writelines(out)
os.replace(tmp, HOT)   # atomic; never delete-then-read
print('hot file rewritten atomically')

# ---- 3. sanity: no cross-record ID refs, all unique -----------------------
def refs_of(rec):
    return set(SPEC_RE.findall(json.dumps(rec, ensure_ascii=True)))

bad_refs = 0
seen_ids = set()
with open(HOT, encoding='utf-8') as fh:
    for ln in fh:
        ln = ln.strip()
        if not ln:
            continue
        r = json.loads(ln)
        sid = r['spec_id']
        assert sid not in seen_ids, 'STILL DUPLICATE: ' + sid
        seen_ids.add(sid)
        for m in SPEC_RE.finditer(json.dumps(r, ensure_ascii=True)):
            if m.group(0) != sid:
                bad_refs += 1
                if bad_refs <= 5:
                    print('  cross-ref:', sid, '->', m.group(0))
print('cross-record ID references in hot:', bad_refs)
final_max = max(spec_num(s) for s in seen_ids)
print('final hot max:', final_max, 'unique:', len(seen_ids))

# ---- 4. remap tracking files ----------------------------------------------
def find_occ(old_id, title):
    return [o for o in occurrences.get(old_id, []) if o['title'] == title]

# 4a. revision_coverage values [n, latest_spec_id, title, cat, line]
rc_path = os.path.join(REPO, 'code/specs/revision_coverage.json')
rc = json.load(open(rc_path))
n_rc = 0
amb_rc = []
for k, v in rc.items():
    if isinstance(v, list) and len(v) > 2 and isinstance(v[1], str) and v[1].startswith('JAH-SPEC-'):
        sid, title = v[1], v[2]
        cands = find_occ(sid, title)
        if len(cands) == 1 and 'new' in cands[0]:
            v[1] = cands[0]['new']
            n_rc += 1
        elif len(cands) != 1:
            amb_rc.append((k, sid, title, len(cands)))
with open(rc_path, 'w', encoding='utf-8') as fh:
    json.dump(rc, fh, separators=(',', ':'))
print('revision_coverage values remapped:', n_rc, '| ambiguous:', len(amb_rc))
for a in amb_rc[:10]:
    print('  AMBIG RC:', a)

# 4b. product_lines latest_id (member title contains the line name)
pl_path = os.path.join(REPO, 'code/specs/product_lines.json')
pl = json.load(open(pl_path))
n_pl = 0
amb_pl = []
for lid, le in pl.items():
    sid = le.get('latest_id', '')
    occs = occurrences.get(sid, [])
    if len(occs) > 1:
        name = le.get('name', '')
        cands = [o for o in occs if name and name in o['title']]
        if len(cands) == 1 and 'new' in cands[0]:
            le['latest_id'] = cands[0]['new']
            n_pl += 1
        elif len(cands) == 1:
            pass  # generator's own record was the first occurrence; already correct
        else:
            amb_pl.append((lid, sid, name, len(cands)))
with open(pl_path, 'w', encoding='utf-8') as fh:
    json.dump(pl, fh, separators=(',', ':'))
print('product_lines latest_id remapped:', n_pl, '| ambiguous:', len(amb_pl))
for a in amb_pl[:10]:
    print('  AMBIG PL:', a)

# ---- 5. derived indexes: add every post-repair ID --------------------------
ai = all_ids_store.load_all_ids()
n_ai = 0
new_entries = {}
with open(HOT, encoding='utf-8') as fh:
    for ln in fh:
        ln = ln.strip()
        if not ln:
            continue
        r = json.loads(ln)
        sid = r['spec_id']
        if sid not in ai:
            new_entries[sid] = [r.get('category', ''), r.get('line') or '',
                                r.get('title', '')]
            ai[sid] = new_entries[sid]
            n_ai += 1
all_ids_store.add_new_ids(new_entries)
print('all_ids store: +', n_ai, 'total', len(ai))

sys.path.insert(0, os.path.join(REPO, 'code/specs'))
try:
    from generate_versions import CAT2KIND
except Exception as e:
    print('CAT2KIND import failed:', e)
    CAT2KIND = {}
sp_path = os.path.join(REPO, 'code/specs/software_ids.json')
sp = json.load(open(sp_path))
n_sp = 0
with open(HOT, encoding='utf-8') as fh:
    for ln in fh:
        ln = ln.strip()
        if not ln:
            continue
        r = json.loads(ln)
        if CAT2KIND.get(r.get('category', '')) == 'software':
            sid = r['spec_id']
            if sid not in sp:
                sp[sid] = [r.get('category', ''), r.get('line') or '']
                n_sp += 1
with open(sp_path, 'w', encoding='utf-8') as fh:
    json.dump(sp, fh, separators=(',', ':'))
print('software_ids.json: +', n_sp, 'total', len(sp))

# ---- 6. state.json ----------------------------------------------------------
st_path = os.path.join(REPO, 'code/specs/state.json')
st = json.load(open(st_path))
st['next_index'] = final_max + 1
with open(st_path, 'w', encoding='utf-8') as fh:
    json.dump(st, fh, separators=(',', ':'))
print('state.json next_index =', st['next_index'])

print('REPAIR DONE: +0 lost,', reided, 're-IDd,', len(seen_ids), 'unique hot records')
