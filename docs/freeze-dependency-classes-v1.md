# Portable protected freeze dependency classes v1 — R5.94B

This prospective format does not amend any historical freeze. Every dependency
declares its type, class, reason, identity procedure and exact creation provenance.
Unknown classes, undeclared text types and ambiguous inherited representations
fail closed. No implicit byte-pin default exists.

* `CANONICAL_CONTENT_PIN`: authoritative UTF-8 text/code/data, exact SHA-256 of
  `UTF8_CRLF_TO_LF_V1`. Decode strictly; reject NUL. Replace CRLF with LF only.
  Preserve lone CR, final newline presence/count, BOM, Unicode code points,
  whitespace, indentation, comments, JSON ordering/serialization and wording.
  BOM addition/removal and NFC/NFD changes therefore invalidate identity.
  The already-defined CJ-1 canonical serializer additionally pins the two embedded
  structured values (semantic envelope and model/access configuration), without
  extending JSON ordering normalization to physical JSON files. Their physical
  container identity is recorded with the published candidate's evidence hash.
* `EXACT_BINARY_PIN`: deliberately byte-identical binary artifact, SHA-256 of
  physical bytes. Never text-canonicalize it. The audited current set contains
  no artifact requiring this class; the verifier supports and tests the class.
* `COMPATIBILITY_CONTRACT`: Python/runtime/platform/containment under the unchanged
  `PYTHON_RUNTIME_CONTRACT_V1`, and OpenCode transport under the separately pinned
  `OPENCODE_ADAPTER_CONTRACT_V1`. A label/version alone never qualifies machinery.
* `PROVENANCE_ONLY`: actual runtime/tool/version/hash/path/OS, machine locations,
  historical installation facts and physical representation. Recorded but not
  eligibility predicates. Historical records themselves remain content-pinned
  evidence; facts inside them do not become current-machine requirements.

The candidate identity is CJ-1/SHA-256 of its complete semantic body, including
the dependency manifest with each entry's `provenance` omitted. A separate
provenance digest binds all creation physical hashes. Preflight takes an external
expected candidate identity; resealing changed content cannot satisfy it.
Verification does not build a replacement freeze from the current files.

## Inherited pins and representation evidence

For each inherited file, construction must match its historical byte hash in
one of exactly three representations: physical bytes, declared canonical LF,
or uniform CRLF reconstructed from those LF bytes. Otherwise construction halts
`INHERITED_CONTENT_DRIFT_OR_AMBIGUOUS_CLASSIFICATION`. This establishes canonical
content continuity without rereading protected targets or rewriting old files.
New implementation/procedure/docs/tests are pinned prospectively. All compiler,
controller, workspace, pipeline, FRC/structural schemas, mappings, BDI/adequacy,
profile, prompts, verification, access policy and failure taxonomy stay exact.

## Configuration and machine boundary

The intended provider/model, timeout, temperature, independence statement and
policy are frozen separately from transport. Only `executable` and `cli_version`
are removed from current role eligibility configuration; their original values
remain in the inherited evidence and machine provenance. `LYKOI_OPENCODE` or an
explicit argument selects the machine's artifact, without rewriting a model pin.
The old configuration file remains content-pinned historical evidence.

Absolute repository/temp/auth locations and usernames do not confer eligibility.
The inherited `src/lykoi_controller/Controller.py` entry is a case-only alias of
the tracked `controller.py`, with identical inherited pins. Its manifest explicitly
uses that tracked locator; no global path case-folding rule is introduced.
Fresh empty role working directories, isolated configuration, argv/pipes/timeouts,
SQLite durability, Unicode/space paths and existing trusted-local process/API
containment must mechanically work. Supported platform scope remains CPython
3.10+, 64-bit Windows/Linux/macOS; POSIX requires resource limits. This is not an
OS sandbox against hostile native code. Credentials are used by the installed
OAuth transport, never extracted or recorded by Lykoi.

Every machine preflight reruns both contracts. A process-local execution guard
records actual Python/OpenCode/OS before each controller dispatch and AI call;
changed implementations requalify before proceeding. Qualification never grants
protected authorization. Stop after inactive generic freeze verification.
