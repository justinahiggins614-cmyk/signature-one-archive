# JAH-SPEC Autoread Schema v1.0

The machine-readable identity + governance block carried by every
Signature Spec Catalog record (`autoread_block`).

## What it is

A newline- (or `|`-) separated list of `KEY=VALUE` (or `KEY: VALUE`) pairs.
It is the **machine-readable identity** of a spec — deterministic,
legal-ID coded, content-hashed. The `JAH-SPEC-######` ID + the official
stamp + the content hash IS Manon's own patent governance (the **JAH
Signature-One Patent Authority**): each record is legal-ID coded and
provably made, every boundless product points to its ID, and the system's
own track record is its own confirmation. This is his own patent
authority — **not the USPTO, not a government system.**

## Fields

| Field | Required? | Meaning |
|---|---|---|
| `SCHEMA` | recommended | `JAH-SPEC-SCHEMA 1.0` |
| `SPEC_ID` (`SPEC=` accepted, aliased) | **required** | Canonical ID, `JAH-SPEC-######` (or `JAH-WORD-######`) |
| `VERSION` | recommended | Spec version/revision, e.g. `1 rev 0` |
| `OBJECT` | recommended | The thing being specified |
| `DOMAIN` | recommended | Product category / domain |
| `DOCUMENT_TYPE` | recommended | `DRAFT_PATENT_SPECIFICATION` |
| `PATENT_STATUS` | recommended | `NOT_GRANTED` — not a granted patent |
| `SOURCE` | recommended | `JAH_ORIGINAL` — authored by Justin Addam Higgins |
| `USPTO_AFFILIATION` | recommended | `NONE` |
| `GOVERNANCE` | recommended | JAH Signature-One Patent Authority statement |
| `TITLE` | recommended | Spec title |
| `INVENTOR` | recommended | Justin Addam Higgins |
| `CATEGORY` / `CPC` / `ERA` | recommended | Classification triple (CATEGORY line may carry `| CPC= | ERA=`) |
| `DIMENSIONS` | recommended | Physical or data dimensions |
| `MATERIAL` | recommended | Material(s) |
| `PROCESS` | recommended | Manufacturing / build process |
| `SIGNATURE_TOOLS` | recommended | The six Signature tools used |
| `PARAMETERS` | recommended | Key parameters (also inline `KEY=value` lines) |
| `ASSUMPTIONS` | recommended | Stated assumptions / scope limits |
| `VALIDATION_STATUS` | recommended | Separate from `STATUS` (see below) |
| `STATUS` | **required** | `SIGNATURE-1 VALID` |
| `HASH` | recommended | Canonical content hash (SHA-256 of canonical text) |

Unknown fields are kept (not dropped) by the parser.

## What `STATUS=SIGNATURE-1 VALID` means

**SIGNATURE-1 VALID = the block passes Signature-One schema validation.**
It is a **data/specification status** — the record is complete, parsed, and
schema-valid. It is **NOT** physical, prototype, or manufacturing
validation. Those are separate, honest statuses:

- `SPECIFICATION_COMPLETE` — schema validation (what SIGNATURE-1 VALID asserts)
- `ENGINEERING_VALIDATED` — engineering review (default: not yet validated)
- `PROTOTYPE_TESTED` — tested against a physical prototype (default: NOT_TESTED)
- `MANUFACTURING_VALIDATED` — manufacturing review (default: not validated)

Compliance wording (FDA, BPA-free, food-safe, …) is **CLAIMED, not verified**,
unless a verification source is attached. Manufacturing parameters are
labeled `REQUIRED` / `TARGET` / `RECOMMENDED` / `VALIDATED`.

## Parser rules (tolerant, never invents defaults)

Implemented in `code/specs/autoread.py` (Python) and mirrored in `specs.html`
(`jahParseAutoread`, JS). Rules:

- Split on newlines or `|`; separator `=` or `:` (first occurrence).
- Keys upper-cased; whitespace trimmed; unknown keys kept.
- Duplicate keys: **last wins**, with a warning.
- `SPEC=` aliases to `SPEC_ID`.
- Missing `SPEC_ID` or `STATUS` → `valid=False`; **no defaults are invented**.
- Lines that are not `KEY=VALUE` produce warnings, not failures.

## Canonical text + content hash

Hash the **canonical text**, never the page HTML:

1. `SCHEMA=JAH-SPEC-SCHEMA <version>`
2. `SPEC_ID=`, `TITLE=`, `INVENTOR=Justin Addam Higgins`, `PREPARED=`
3. All other fields, **sorted by key**, `KEY=value`, one per line

`content_hash()` = SHA-256 hex of that text. Deterministic: the same record
always hashes the same, regardless of field order or `|` vs newline layout.

## Generating new blocks

All drip generators route through `build_autoread()` in
`code/specs/generate_specs.py`, which delegates to
`autoread.make_autoread()` — every new spec emits the identity/governance
fields automatically. Legacy (pre-schema) blocks still parse as valid
because only `SPEC_ID` and `STATUS` are required.

## Conventions worth knowing

- Bounding-box axes are fixed catalog-wide: `L×W×H` (length × width × height),
  suffixed on the value, e.g. `BOUNDING_BOX=3.5x4.5x10.0in_LxWxH`.
- Wall taper (where given) is the wall-to-vertical angle implied by the
  listed dimensions, e.g. `arctan(((D_RIM−D_BASE)/2)/H)`.
- Rib depth is a single value per record (`RIB_DEPTH=0.03in`).
- The AI explainer is a **generated interpretation** of the spec, not the
  spec itself. SPECIFICATION = source of record.
- Demos are simulations: `DEMO_STATUS=NOT_TESTED` unless a physical test
  result is attached (`PASS` / `FAIL` / `PARTIAL`).
- Runnable programs carry environment metadata: `LANGUAGE`, `DEPENDENCIES`,
  `OS`, `CPU/GPU`, `NETWORK_REQUIRED`, `INPUT`, `OUTPUT`.
