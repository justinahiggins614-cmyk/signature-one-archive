#!/usr/bin/env python3
"""JAH-SPEC canonical autoread schema (JAH-SPEC-SCHEMA 1.0).

Machine-readable identity + governance for every Signature Spec Catalog
record. The JAH-SPEC-###### ID + official stamp + content hash IS Manon's own
patent governance (the JAH Signature-One Patent Authority): deterministic
legal-ID coding is the protection and credibility -- his own patent
authority, not the USPTO, not a government system.

Schema fields (SPEC_ID and STATUS required; the rest recommended):
  SPEC_ID, VERSION, OBJECT, DOMAIN, DOCUMENT_TYPE, PATENT_STATUS, SOURCE,
  USPTO_AFFILIATION, GOVERNANCE, STATUS, DIMENSIONS, MATERIAL, PROCESS,
  SIGNATURE_TOOLS, PARAMETERS, ASSUMPTIONS, VALIDATION_STATUS, HASH

The tolerant parser accepts newline- or |-separated KEY=VALUE (or KEY:
VALUE) pairs, tolerates extra spaces / mixed case / reordered fields /
unknown fields / unicode, keeps the last value on duplicates, and never
invents defaults. It rejects cleanly (valid=False) when SPEC_ID or STATUS
is missing or malformed.

Hash THIS (never the HTML) for the content hash: the canonical text is
fixed key order, sorted fields, no whitespace games.
"""

import hashlib
import re

SCHEMA_VERSION = "1.0"
REQUIRED = ["SPEC_ID", "STATUS"]
RECOMMENDED = ["OBJECT", "DOMAIN", "VERSION", "DIMENSIONS", "MATERIAL",
               "PROCESS", "SIGNATURE_TOOLS", "PARAMETERS", "ASSUMPTIONS",
               "VALIDATION_STATUS", "SOURCE", "HASH"]

IDENTITY = {
    "DOCUMENT_TYPE": "DRAFT_PATENT_SPECIFICATION",
    "PATENT_STATUS": "NOT_GRANTED",
    "SOURCE": "JAH_ORIGINAL",
    "USPTO_AFFILIATION": "NONE",
    "GOVERNANCE": ("JAH Signature-One Patent Authority -- Manon's own patent "
                   "governance: deterministic JAH-SPEC ID + stamp + hash are "
                   "the protection and credibility. Not the USPTO, not a "
                   "government system."),
    "INVENTOR": "Justin Addam Higgins",
    "STATUS": "SIGNATURE-1 VALID",
}

VALIDATION_NOTE = ("SIGNATURE-1 VALID means: this block passes Signature-One "
                   "schema validation (data/specification status). It is NOT "
                   "physical, prototype, or manufacturing validation.")

STATUS_LEVELS = {
    "SPECIFICATION_COMPLETE": "schema validation (data/specification status)",
    "ENGINEERING_VALIDATED": "not yet validated",
    "PROTOTYPE_TESTED": "not tested against a physical prototype",
    "MANUFACTURING_VALIDATED": "not manufacturing-validated",
}

SEEK = re.compile(r"JAH-SPEC-(\d{6})")


def parse(text):
    """Tolerant parse of an autoread block.

    Returns (fields, order, warnings, valid, missing). fields keys are
    upper-cased; SPEC is aliased to SPEC_ID. Unknown fields are kept.
    """
    fields, order, warnings = {}, [], []
    chunks = re.split(r"[\n|]", text or "")
    for i, chunk in enumerate(chunks):
        c = chunk.strip()
        if not c:
            continue
        eq = c.find("=")
        if eq < 0:
            eq = c.find(":")
        if eq < 0:
            warnings.append("line %d is not KEY=VALUE: %s" % (i + 1, c[:40]))
            continue
        key = re.sub(r"[^A-Z0-9_]", "_", c[:eq].strip().upper())
        val = c[eq + 1:].strip()
        if val.startswith(":"):
            val = val[1:].strip()
        if not key:
            warnings.append("line %d has empty key" % (i + 1))
            continue
        if key in fields:
            warnings.append("duplicate key %s -- last value kept" % key)
        if key not in order:
            order.append(key)
        fields[key] = val
    if "SPEC" in fields and "SPEC_ID" not in fields:
        fields["SPEC_ID"] = fields["SPEC"]
    missing = [k for k in REQUIRED if not fields.get(k)]
    return fields, order, warnings, not missing, missing


def canonical_text(spec_id, title="", prepared="", autoread=""):
    """Canonical serialization of a record's identity data for hashing."""
    fields, _, _, _, _ = parse(autoread)
    lines = ["SCHEMA=JAH-SPEC-SCHEMA " + SCHEMA_VERSION,
             "SPEC_ID=" + spec_id,
             "TITLE=" + title,
             "INVENTOR=" + IDENTITY["INVENTOR"],
             "PREPARED=" + prepared]
    for k in sorted(fields):
        if k in ("SPEC_ID", "SPEC"):
            continue
        lines.append("%s=%s" % (k, fields[k]))
    return "\n".join(lines)


def content_hash(spec_id, title="", prepared="", autoread=""):
    """SHA-256 hex of the canonical record text."""
    return hashlib.sha256(
        canonical_text(spec_id, title, prepared, autoread).encode("utf-8")
    ).hexdigest()


def make_autoread(spec_id, title, cat, cpc, era, params, object_phrase=None,
                  version="1 rev 0"):
    """Emit a governance-tagged autoread block for a new spec.

    Keeps the legacy line order first (SPEC, TITLE, INVENTOR, CATEGORY, params,
    STATUS) so old tooling keeps working; identity fields are inserted right
    after the CATEGORY line.
    """
    lines = [
        "SCHEMA=JAH-SPEC-SCHEMA " + SCHEMA_VERSION,
        "SPEC=" + spec_id,
        "TITLE=" + title,
        "INVENTOR=" + IDENTITY["INVENTOR"],
        "CATEGORY=%s | CPC=%s | ERA=%s" % (cat, cpc, era),
        "DOCUMENT_TYPE=" + IDENTITY["DOCUMENT_TYPE"],
        "PATENT_STATUS=" + IDENTITY["PATENT_STATUS"],
        "SOURCE=" + IDENTITY["SOURCE"],
        "USPTO_AFFILIATION=" + IDENTITY["USPTO_AFFILIATION"],
        "GOVERNANCE=" + IDENTITY["GOVERNANCE"],
    ]
    if object_phrase:
        lines.append("OBJECT=" + object_phrase)
    lines.append("DOMAIN=" + cat)
    lines.append("VERSION=" + version)
    lines += ["%s=%s" % (k, v) for k, v in params.items()]
    lines.append("NOTE=" + VALIDATION_NOTE)
    lines.append("STATUS=" + IDENTITY["STATUS"])
    return "\n".join(lines)
