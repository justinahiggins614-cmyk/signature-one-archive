# SIGNATURE RECORD STANDARD — v1.0

The common record law underneath all nine Signature sites. One deterministic,
self-auditing identity and provenance system: every important object on every
site is traceable as

```
PRODUCT → PRODUCT_ID → SPEC_ID → CANONICAL_RECORD → SIGNATURE_HASH
  → VERSION → BUILD/ARTIFACT → TEST/VALIDATION → PUBLIC RECORD
```

This standard does not change how any site looks. It is invisible plumbing:
machine-readable fields every site's records carry, so the whole ecosystem
behaves as one governed system instead of nine separate websites.

Canonical machine-readable schema: `signature-record-standard.json`
(in this directory). That JSON file is authoritative; this document explains it.

## The 15 core fields

Every governed record, on every site, carries:

| # | Field | Meaning |
|---|-------|---------|
| 1 | `id` | Permanent deterministic identity, never reused, never silently changed. Format is per-site (see below); the ID is the record's name forever. |
| 2 | `type` | Record class, e.g. `SPEC`, `PATENT_RECORD`, `WORD`, `WIKI_ARTICLE`, `DOSSIER`, `AI`, `PC_SYSTEM`, `CALCULATION`, `LLAMA_MODEL`. |
| 3 | `title` | Human-readable name. |
| 4 | `status` | Lifecycle state, e.g. `DRAFT`, `VERIFIED`, `PUBLISHED`, `SUPERSEDED`. |
| 5 | `version` | Integer version. A changed record bumps `version`; the `id` stays the same. Old versions are never silently overwritten. |
| 6 | `date` | Creation date (ISO 8601). |
| 7 | `source` | Where the record came from: which site, which generator, which run. |
| 8 | `parent` | The record this was derived from (`null` for originals). Hybrids, editions, blends, and generated objects always name their parent(s). |
| 9 | `canonical_data` | The exact canonical content the hash is computed over. |
| 10 | `hash` | SHA-256 of the canonical data (hex). Any consumer can recompute and verify. |
| 11 | `governance_status` | Standing inside the Signature system: `SIGNATURE_VERIFIED`, `SIGNATURE_DRAFT`, `INTERNAL_SIMULATION`, etc. This is Manon's own patent-making authority — never a government grant, never USPTO. |
| 12 | `public_status` | Standing in the outside world, kept strictly separate from field 11: `PUBLIC_RECORD` (real harvested patent), `NOT_FILED` (his original draft — not filed, not granted), `HISTORICAL` (documented history), `FOLKLORE_UNVERIFIED`, `THEORETICAL`, `CREATIVE_SIMULATION`. |
| 13 | `build_status` | For buildable artifacts: `NOT_BUILT`, `BUILDABLE`, `BUILT`, `SIMULATED_ONLY`. |
| 14 | `test_status` | Validation standing: `UNTESTED`, `SELF_TEST_PASS`, `QA_PASS`, `HUMAN_REVIEW_REQUIRED`. |
| 15 | `related_records` | IDs of linked records on any of the nine sites (cross-site traceability). |

## The two statuses that must never blur

`governance_status` (field 11) answers: **what does the Signature system itself
say about this record?** `public_status` (field 12) answers: **what is this in
the outside world?** A Signature draft spec is `SIGNATURE_VERIFIED` /
`NOT_FILED`. A harvested patent is `CATALOGED` / `PUBLIC_RECORD`. A JAH-N
dossier simulation is `INTERNAL_SIMULATION` / `CREATIVE_SIMULATION`. No AI on
any site may present one as the other.

## Per-site ID formats (already live)

| Site | Record | ID format |
|------|--------|-----------|
| Spec Catalog | specification | `JAH-SPEC-######` |
| Spec Catalog | word patent | `JAH-WORD-######` |
| Patent Catalog | catalog entry | `JAH-PAT-######` |
| Dictionary | word entry | `JAH-DICT-W-######` |
| JAH Wiki | article | `JAH-WIKI-######` |
| JAH-N Wiki | dossier | `JAHN-<CLASS>-######` |
| Telephone Book | AI | `JAH-AI-<WING>-###` / `JAH-AI-MIX-######` |
| Calculator | equation/solve record | `JAH-EQ-########` |
| PC Depository | computer system | `JAH-PC-########` |
| Signature Llama | model release | `SIGLLAMA-V#` |
| Backend | operator file record | `JAH-AI-OP-######` |

## Per-site specializations

Each site extends the 15 core fields with its own fields; the core 15 are never
dropped or renamed:

- **Dictionary** adds `deterministic_definition`, `definition_version`,
  `word_program_hash`.
- **Specs** add `document_type`, `inventor`, `created`/`modified`,
  `product_relationships`, full JAH-SPEC-SCHEMA 1.0 block.
- **JAH-N dossiers** add `dossier_type`, `source_status`, `simulation_status`,
  `public_records`, `jah_analysis`.
- **PC systems** add `system_type` (`HISTORICAL` / `SIGNATURE_ORIGINAL` /
  `GENERATED` / `PREDICTED`), `generator_version`, `seed`.
- **Calculator** adds `input`, `units`, `mode`, `method`, `precision` so every
  saved calculation is reproducible.
- **Telephone Book** adds `ai_type`, `parent_model`, `genome`, `voice`,
  `capabilities`, `engine`, `model_version`.
- **Llama** adds `engine`, `weights_hash`, `training_corpus_version`,
  `tool_permissions`.
- **Wiki** adds `article_type`, `source_records`, `source_dates`,
  `signature_status`.

## Determinism rule

Any generated object (hybrid AI, mixed spec, generated PC, forged genome) is
reproducible from `id + generator_version + seed/parameters + canonical spec`.
If it cannot be regenerated bit-for-bit from those, it is not a governed
record yet.

## Verification rule

Any consumer — human, browser, or AI — can verify a record by recomputing the
SHA-256 in field 10 over the canonical data in field 9. Downloads ship the
record's `id`, `version`, and `hash` so the file is verifiable offline.

## Version history

- **1.0** (2026-10-01): initial standard, ratified from the nine-site
  consolidated review. Canonical schema in `signature-record-standard.json`.
