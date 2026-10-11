# Minimal supervision records v1

Schemas: [common](common-1.schema.json), [A](A-1.schema.json),
[B](B-1.schema.json), [C](C-1.schema.json). Register the four URNs locally;
never fetch a remote schema. These define qualified-record envelopes, not admission
or typed execution by themselves. Zero new training records are exported here.

Requirement identity contains exact source/FRC references, episode, nominal family
and connected ancestry component. Profile pins the versioned semantic contract and
execution foundation. Context preserves exact model messages, the pre-action state
(null only for A) and interface contract/tool inventory. Metadata/evidence/provenance
stay outside model input unless the frozen interface explicitly declares them.
Targets preserve exact assistant text; B also pins the expected resulting state,
C the selected tool, arguments, schema, actual response and resulting state.
Evidence binds target origin, validation, frozen behavioral acceptance, observations
and admission. Provenance never invents hidden reasoning. Partitions include a
ledger reference and fail-closed export designation. Evaluation-only rows cannot
have training export enabled, including derivatives.

## Canonical serialization and semantic gates

For new qualified records: UTF-8, LF, sorted keys, compact comma/colon separators,
no BOM/NaN/duplicate keys, one JSON object per line. Hash each artifact's original
bytes, including any terminal newline. Existing minified targets retain their exact
historical assistant text; do not normalize them and call the result the same record.
Record envelope canonicalization and supervised-target bytes are separate identities.
Targets supervise content plus native end-of-turn; prompts, final newline and padding
are masked. Freeze token IDs/masks and reject overflow rather than truncate targets.

An external qualifier must resolve references beneath an approved source root,
check hashes, load profile-specific target/argument schemas, and perform native
typing, exact dependency, order and bounded-resource validation. A string `text`
is deliberately opaque to the envelope validator; JSON Schema does not certify it.
For C, `text` must equal canonical `{"arguments":...,"tool":...}` for the selected
schema-valid call. Reject unknown tools, extra fields and schema/provider flattening
that changes meaning. B's `text` must match its pinned update schema and replay
from `context.state` to `target.after`. No permissive patch language or Python payload.
Reject if semantic validation or correct frozen behavior is missing, failed or
NOT_REACHED. `status=QUALIFIED` is a checked assertion, never self-certification.

B/C trace references require captured before/after states and explicit ordinal
with exact invocation ordering, not a guessed chronology from final AST order.
Expert traces must say deterministic expert demonstration; actual AI traces require
original model-visible messages, selected call/edit, response and uncertainty about
hidden context. Raw unsuccessful trajectories may be retained for analysis but
are not positive qualified records. A successful single declaration in a failed
program is insufficient under the complete-behavior gate.

## Quality and leakage controls

1. Source/FRC determines target meaning before construction; freeze acceptance
   independently of candidate output. Keep known synthetic same-author limitations.
2. Verify exact target serialization, typed literals/arguments, closed operations,
   resolvable earlier references, exact deps, acyclic composition and pinned identities.
3. Validate every admissible partial update; incomplete state is not a complete
   program pass. Freeze explicit completion obligations and validate assembled endpoint.
4. Replay frozen positive, invalid/type/boundary, simultaneous-failure/error-precedence
   and applicable state/restart observations. Correctness is finite/scoped.
5. Mutation controls: well-typed wrong operator, swapped refs, omitted dep,
   reordered checks, wrong result and hidden callback must not be admitted.
6. Deterministic assembler may copy static envelope and compute hashes; it cannot
   choose a missing operator, synthesize a guard, repair refs or execute host shortcuts.
7. Ancestry joins predecessors/successors, shared definitions, oracle/scaffold and
   all objective views. Split components before conversion; never row-split steps.
8. Evaluation-only or unqualified sources and public R6.50 sibling sketches remain
   excluded. R6.48 quarantined F5/F6 and E09–E12 are not promoted. P6-A05 inaccessible.
9. Expert versus observed AI provenance is mandatory. No chain-of-thought field;
   token accounting is not reasoning text. Reject missing correctness/provenance.
10. A future exporter needs positive/negative fixtures and roundtrip/hash/partition
    tests. This round validates envelope schemas, not a implemented exporter.

These controls also cover B/C data synthesized later from endpoints: derivation is
new expert evidence requiring authorization, deterministic replay and new admission;
an existing endpoint's Tier T status does not automatically admit its step views.
