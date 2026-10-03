# code/qa — re-runnable checkers for the Spec Catalog page code

These checkers are additive QA tooling. They never write to `data/`,
`code/specs/state.json`, or any drip-owned file — they only read.

## The checkers

| Script | What it verifies |
|---|---|
| `check_links.py` | Every `href` in `specs.html` + `standard.html`: relative hrefs resolve to a real repo file; absolute URLs return HTTP 200; deep-link targets (`?spec=`, `?word=`, `?dossier=`, `?w=`) resolve live with real IDs |
| `check_counts.py` | Every `shards.json` entry resolves locally; spec-ID ranges contiguous (no gaps/overlaps); total count; all chunk files referenced by the main index exist; words/word-AI index counts |
| `check_dupe_ids.py` | No duplicate spec IDs across the main index + all shard clones (default); `--fast` scans the main index only. A duplicate means a generator bug — report it, never delete data |
| `check_missing_ids.py` | Each index holds one contiguous integer run of `JAH-SPEC-######` IDs — any hole inside an index means lost records |
| `check_prose_machine.py` | Sampled prose-vs-machine agreement: 40 seeded records per index (main + every shard clone) verified that index rows (id/title/category/cpc/era/prepared) match the actual chunk records |

Run all four:

```bash
cd ~/workspace/signature-one-archive
python3 code/qa/check_links.py
python3 code/qa/check_counts.py
python3 code/qa/check_dupe_ids.py
python3 code/qa/check_missing_ids.py
python3 code/qa/check_prose_machine.py
```

Exit 0 = clean. Exit 1 = findings printed; fix them or explicitly mark them dead.

## Generator/seed stamping — READY TO IMPLEMENT (not applied)

**Decision: not applied in this pass.** The spec drip owns the generators and runs
every 2h; editing the emit path mid-run risks a race with `state.json` (the
2026-09-29 incident: a stale state read re-ID'd 1,010 specs). Per the standing
rule — never invent or backfill seed/version info for old records — stamping is
**forward-only for new records** and is left as this exact patch for the drip
owner to apply between runs:

In `code/specs/generate_specs.py`, `make_spec()` — the returned record dict
currently ends with:

```python
        "measurements": measurements,
        "ai_explainer": ai_explainer,
    }, title.lower()
```

Add two fields to that dict (exact insertion):

```python
        "measurements": measurements,
        "ai_explainer": ai_explainer,
        "record_version": "1.0",
        "generator": {
            "script": "generate_specs.py",
            "seed": seed if seed is not None else f"JAH-{SEED}-{i}",
            "schema": "JAH-SPEC-SCHEMA 1.0",
        },
    }, title.lower()
```

Same pattern applies to the sibling emitters (`generate_signature_line.py`,
`generate_mix.py`, `generate_versions.py`, `generate_revisions.py`,
`generate_product_lines.py`, and the word-spec emitter) — each stamps its own
`script` name and the seed it used. Safe window: apply only when no drip run is
in progress (`code/specs/drip.log` shows no active run), and never touch
`code/specs/state.json`. The page already reads nothing from these fields, so
adding them changes no rendering; a future checker can assert their presence on
new records. **Never backfill**: records published without these fields keep
`Record version: v1.0 (baseline)` with "no revisions recorded" — no invented history.
