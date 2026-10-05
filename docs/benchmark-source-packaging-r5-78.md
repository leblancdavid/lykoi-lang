# R5.78 generic source-to-V1 rule

This prospective mechanical rule is defined before protected B03 access. It
does not authorize observation or reinterpret historical requirements.

## Source boundary

Two explicitly selected source interfaces are recognized; filenames and request
numbers never select a mapping:

* `explicit-components`: a UTF-8 JSON object containing exactly `application`,
  `configuration`, `obligations`. These are the already-qualified V1 component
  interfaces, not prose or regression expectations. Identified obligations must
  already exist. No synthesis, default empty obligations, meaning normalization,
  obligation ID invention, recursive search or distributed merge is allowed.
* `frozen-request-bundle`: exactly three UTF-8 byte resources, `request`,
  `profile`, `capability`, from the historical frozen benchmark protocol.
  Request is nonblank prose; profile and capability are JSON objects. That
  protocol declares observable requirements and regression expectations, not a
  complete semantic application/configuration/identified-obligation interface.
  A structurally readable bundle therefore rejects `UNREPRESENTABLE_SOURCE`.
  It is never converted to descriptive metadata or given invented behavior.

The latter is a generic protocol limitation established from README and generic
composer authority, not from B02 layout or B03 contents. Even a parseable source
is not mechanically representable merely because some regression data exists.

## Transformation

For explicit components, validate the closed V1 payload without semantic-support
calls. Preserve application/configuration and requirement objects unchanged;
sort identified obligations by ID as V1 requires. Make exactly one behavioral
document, schema `BenchmarkDocumentContractV1`, with ID `behavioral-` followed by
SHA-256 of the canonical normalized payload. No metadata documents or optional
metadata are emitted: arbitrary source metadata and undeclared keys reject.
There are no document references. This intentionally conservative metadata
treatment cannot publish acceptance answers as descriptions.

Canonicalization is V1 sorted-key compact UTF-8 JSON, unescaped Unicode, finite
numbers, Python numeric representation. Package bytes are the canonical array
of the single document. Package commitment is SHA-256 of those exact bytes;
document commitment is SHA-256 of the canonical document. Behavioral commitment
is SHA-256 of canonical `{schema_version: BehavioralContractV1, application,
configuration, obligations}`. Source provenance is a SHA-256 commitment over
canonical interface name and the named raw-byte SHA-256 commitments. Hashes
do not attest behavioral coverage against prose.

## Boundary and gate

The pure packager accepts bytes; it performs no I/O, evaluation, runner issuance,
opening, AI interpretation, generation or execution. Only structural validation
and commitments occur. Publication is a closed, content-free receipt; errors
publish only `MALFORMED_SOURCE`, `UNREPRESENTABLE_SOURCE`,
`UNSUPPORTED_SOURCE_INTERFACE` or `INVALID_V1_STRUCTURE`, never paths, keys,
values, source lengths or exception text. A future trusted controller must provide
protected I/O, immutable sealing and provenance authority independently.

Freeze this document, implementation, V1 adapter and schema by content commitment
before qualification. Qualification uses synthetic and public components plus
public B01 historical source. If the applicable frozen source interface cannot
produce a complete V1 package, the pre-B03 gate fails: record
`R5_78_B03_PACKAGING_GAP`, do not access B03, and stop protected processing.
No controller or B03-specific workaround is installed in that case.
