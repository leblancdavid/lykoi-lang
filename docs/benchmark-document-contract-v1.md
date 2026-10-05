# BenchmarkDocumentContractV1 (prospective R5.77)

## Authority and scope

This is new evaluation-infrastructure authority, authorized by R5.77 for future
packages. It is not a historical interpretation of B01/B02/B03, an acceptance
oracle, a requirement-meaning language, or a Lykoi semantic. Incompatible changes
require a new version; there is no legacy fallback or structure inference.

Sources: benchmark README and external-oracle protocol; R5.72/R5.74 exact sealed
resource-set opening; R5.38/R5.41 readiness's explicit obligations argument;
R5.40 profile structure and R5.41 application admission; public seed-bank R5.39
and independent optional-boundary study R5.41. These establish component inputs
and static-only intent. They did not select document roles, multiplicity,
obligation IDs or assembly rules. The following choices are prospective.

## Envelope and roles

Every opened resource is exactly one UTF-8 JSON document (duplicate JSON keys,
nonfinite numbers and non-JSON objects reject). Four required top-level fields:
`schema_version` (literal `BenchmarkDocumentContractV1`), nonblank `document_id`,
`role`, and object `payload`. One optional field: object `metadata`. All other
envelope fields reject. Document IDs are exact case-sensitive strings.

There are **two roles**:

* `behavioral`: exactly one; owns the entire static contract.
* `metadata`: zero or more; payload is descriptive JSON, excluded from consumers
  and behavioral identity. It must not contain private acceptance answers or
  generation/execution instructions disguised as metadata.

No request/intent, fixture/data, acceptance or auxiliary role is needed by these
static interfaces. Such material belongs in separately committed, separately
authorized packages that are never opened by the static runner. Request meaning
must already be expressed in the declared semantic application/obligations by
the independent benchmark authority. The adapter does not interpret prose.

## Payload and obligations

The behavioral payload has exactly `application`, `configuration`, `obligations`.
Application is the existing `id/state/operations` interface: nonblank ID,
nonempty state versions and operation map. Configuration is the existing closed
R5.40 structural profile (`transport/state/launch`), audited independently of
support. Semantic validity/support remain existing consumers' responsibility.
The envelope schema intentionally does not duplicate the semantic language.

Obligations are a required explicit array of `{id, requirement}` objects, with
no optional entry fields. IDs are nonblank exact strings, unique within the
contract. `requirement` is a JSON object with nonblank string `kind`; it is
passed unchanged to readiness. Known current component forms are:

* `public_state_alternatives`: exactly `kind/public`, where public is an array
  of unique nonblank route strings.
* `durable_content_constraints`: exactly `kind/requirements`, mapping nonblank
  state-version names to arrays of constraint objects.

Other kinds remain explicit opaque JSON requirement objects: they are not
silently dropped or transformed, and current readiness rejects unsupported
kinds. Adding infrastructure validation for new component shapes is versioned
prospectively; this protocol does not define their behavioral meaning.
Array order is not obligation priority; normalize by ascending ID. Inner arrays
retain order because their component semantics may depend on it. Identical
duplicate IDs reject `DUPLICATE_OBLIGATION`; differing requirements with the
same ID reject `CONFLICTING_OBLIGATIONS`. Logical inconsistency across distinct
IDs is a consumer concern, not guessed by the adapter. An explicit empty array
means the benchmark authority declares no supplemental boundary obligations;
it does not remove the application's behavioral relations. Absence is incomplete.

## Assembly, completeness and identity

The external sealed resource inventory defines the complete document set;
the unmodified runner verifies exact inventory and commitments before dispatch.
The adapter validates every document, sorts by document ID, rejects duplicate
IDs even when content is identical, requires exactly one behavioral document,
and ignores metadata roles for behavioral normalization. More than one
behavioral document is ambiguous; no precedence, merge or supersession exists.
Multi-document packages therefore mean one behavioral plus metadata documents,
not distributed obligation fragments. This deliberate bound avoids an inventory
manifest, ownership graph and partial-merge rules. Adapter completeness is
syntactic; truth/completeness relative to a prose request is benchmark authority's
responsibility, independently reviewed before sealing.

**References are omitted.** No reference field, pointer, resolver, target
component, unresolved-reference outcome or cycle traversal exists. Envelope
references reject as undeclared fields; a `ref`-only obligation is malformed.
Component-internal semantic references retain existing semantics and are not
document links. Reference resolution tests are consequently not applicable.

`BehavioralContractV1` has `schema_version`, `application`, `configuration`,
sorted `obligations` and `identity`. The identity is SHA-256 of the other four
fields in UTF-8 JSON: sorted object keys, compact separators, Unicode unescaped,
finite numbers only. Document identity hashes its complete validated envelope,
including metadata; behavioral identity excludes all document IDs and metadata.
Python's JSON numeric representation is the V1 canonicalization rule (integers
and floats are not conflated); no timestamp, filesystem order or machine ID is
used. Existing consumer arguments are projected from this normalized contract;
obligation IDs remain in the contract but readiness receives their requirements.
Consumers never receive document envelopes.

## Structured failures

`DocumentError.record()` is `{code, path}` and never includes rejected values.
Codes: `UNSUPPORTED_SCHEMA_VERSION`, `UNKNOWN_REQUIRED_ROLE`,
`MISSING_REQUIRED_ROLE`, `DUPLICATE_DOCUMENT_ID`, `MALFORMED_DOCUMENT`,
`MALFORMED_DOCUMENT_SET`, `MALFORMED_PAYLOAD`, `MALFORMED_OBLIGATION`,
`DUPLICATE_OBLIGATION`, `CONFLICTING_OBLIGATIONS`, `AMBIGUOUS_ASSEMBLY`,
`INCOMPLETE_CONTRACT`, `MALFORMED_CONTRACT`. Missing payload components are
incomplete; invalid/extra components are malformed. No partial static call
follows a document error. Multiple invalid inputs need not have a canonical
first error; valid-set normalized identity is canonical. Downstream interface
failure is infrastructure failure, distinct from a support gap.

Machine-readable envelope shape: `schema/benchmark-document-contract-v1.schema.json`.
The single adapter module `benchmark/evaluation/benchmark_documents_v1.py`
additionally enforces uniqueness, component structure and assembly. No I/O,
filename dispatch, AI inference, support decisions or benchmark-specific adapter.

## Future pristine packaging process

A trusted independent benchmark authority, outside Lykoi development, authors
or packages a pristine benchmark as V1 **before exposure**. It independently
reviews full behavioral coverage, role separation and explicit empty sets,
validates V1, and seals/commits immutable V1 bytes and an exact static resource
inventory. Private execution/acceptance packages get separate commitments and
authority. Publish only version, static inventory/roles, byte commitments,
authority provenance and packaging-review attestation to development; no
payload or content-derived hints. Freeze the qualified adapter, consumers and
state against those commitments before any separately authorized opening.

If a pristine historical benchmark needs conversion, only that independent
authority sees its contents. It records conversion provenance and keeps the
development firewall intact. Requalification or corrections happen before
opening; after opening there is no repair/retry masquerading as first exposure.
B03 is not opened, converted, inspected or validated here. This process is
specified, not executed or attested for B03. B02 history is not reinterpreted.
