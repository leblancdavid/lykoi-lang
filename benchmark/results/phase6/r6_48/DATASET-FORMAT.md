# Lykoi training episode schema 1

`dataset-episode-1.schema.json` is a draft-2020-12 machine-readable schema;
`DATASET-INDEX.json` contains twelve conforming raw research records. Each
episode also has its own `DATASET-RECORD.json` and immutable hash references.
The stdlib checker in `experiments/training_data_r6_48/dataset.py` supports
exactly the schema keywords used here; it is not a general JSON Schema engine.

Fields cover episode/family, original source and FRC, semantic profile,
symbolic/executable identity, actual tool trajectory (nullable), separate scripted
trajectory (nullable), acceptance, validation, replay, provenance, partition,
admission and technical status. Stable references contain repository-relative
path and raw-byte SHA256. Definition identities additionally use the unchanged
R6.18 canonical semantic hashing, including the frozen VM foundation.

Canonical JSON is compact, key-sorted, ASCII escaped, with a single LF terminator
and no nonfinite values. Array order is preserved. File SHA256 includes the LF;
semantic definition/plan identities hash their existing canonical form without
that file terminator. Those identities must not be confused.

This pilot's provenance classification is deliberately fixed to
SAME_COORDINATOR_EXPOSED. The schema describes these research records, not a
certification mechanism for hypothetical independently reviewed examples. A later
independent cohort requires a separately versioned provenance/admission schema.

`TRAINING-READY-EXPORT-MANIFEST.json` contains **zero entries**. No raw evidence
is labeled training-ready. E01–E08 carry primary PROVENANCE_OR_LEAKAGE_GAP and
secondary VALIDATED_LIMITED_EVIDENCE; E09/E10 carry
REQUIREMENT_CLARIFICATION_REQUIRED; E11/E12 carry CAPABILITY_GAP and separately
record their distributed-oracle acceptance gap. Unavailable artifacts and actual
AI tool traces are null, not empty invented successes. Twelve raw records are not
twelve training examples. There is no released SFT/trajectory dataset.

Actual scripted traces contain available API contract identity, sequence, selected
API, exact arguments, returned value/diagnostic and final artifact identity. Eight
traces contain 44 real calls; zero corrections were observed. They are
DETERMINISTIC_SCRIPTED_CONSTRUCTION, not model-selected semantic MCP exchanges.
R6.23 and R6.25 are preserved but were not invoked in this pilot. Hidden reasoning,
token telemetry and provider metadata are neither inferred nor serialized.

The recorded raw evidence is about 1.06 MB before final summary/publication files.
Whole-package load/validate/expand responses duplicate content in traces, so storage
per episode can exceed the direct artifact substantially. A future export can
deduplicate by stable hashes while retaining raw audit evidence. Empty exports
have negligible storage/training implications. No training memory, throughput or
useful-model data requirement has been measured by this experiment.
