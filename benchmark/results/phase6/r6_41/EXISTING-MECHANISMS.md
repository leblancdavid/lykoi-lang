# Existing-mechanism feasibility assessment

Read-only sources: [R6.18 semantics](../../../../experiments/typed_composition_r6_18/SEMANTICS-1.md),
[expander](../../../../experiments/typed_composition_r6_18/composition.py),
[VM](../../../../experiments/semantic_interpreter/interpreter.py),
[R6.32 identity specification](../../../../experiments/lifecycle_r6_32/SPEC-1.md),
[R6.25 transport boundary](../r6_25/ENVELOPE-1.md) and R6.40 preserved packages/maps.

| Capability |Existing support |Missing interface/semantics |Conclusion |
| --- | --- | --- | --- |
| Error semantic origin |error.node identifies active primitive; map links it to definition/local; check carries code/test/site |No independent expression-occurrence ID; error.node is active node rather than every inner expression |Bounded primitive-node origin supported |
| Value semantic origin |Plan binds a generated name to producing operation; original package and expansion permit static reconstruction |Cell has value/span/origins, not producer node or arithmetic operand ancestry |Static node producer supported; complete runtime value lineage absent |
| Authoring origin |Map definition hash/local ID; package result/steps/args; immutable registry closure |No authored text line/column ranges; map does not separately label each substituted expression leaf/parameter use |Node-level origin supported; full expression/text origin absent |
| Expansion path |Path embeds root hash, each call-local/target hash and primitive local; repeated calls get distinct bindings/sites |No standalone typed chain schema; need decode/validation conventions for consumers |Bounded ordered chain reconstructible from existing path/package |
| Stable correspondence |Exact program/plan hashes/maps reproduce on reload; registry pins never redirect |No compact-to-arbitrary-flat relation; IDs change on edits/resealing; hashing is not equivalence |Stable exact-content anchors supported, representation-independent mapping unqualified |
| Deterministic error site |check evaluates declared site and uses start; seq returns region span; ordered absorbing failure |Task-level choice between returned span and input contributor unresolved |Current runtime sites deterministic; alternative attribution not supplied |

## What can be represented without implementation

The original expansion artifact already separates `plan` and `map`. A consumer can
retain both along with the exact package/closure and distinguish:

- active operation: existing node.id/op;
- definition-local authoring location: map[node].definition/local;
- occurrence chain: generated node path plus caller steps;
- runtime input location: recorded error.offset or successful Cell provenance.

This is sufficient for the recommended bounded node-level C sidecar approach.
It requires a prospective reporting/correspondence contract, not a new executable
operation. R6.41's extraction illustrates the records using existing data only;
it does not implement a new public API or add runtime fields.

A returned integer's lost inner-expression span is not stored as a second integer
origin by the VM. With the exact small package one can analyze which expression
supplied its value, but that is not a general runtime lineage trace, and multiple
operands/constant use complicate a canonical blame rule. The char-origin tuple
cannot simply be reinterpreted as an integer ancestry field. The wrapper's closed
schema has no option to request transparent compose-return start provenance.

The VM's existing span_end/rebase_errors do not fill this gap and are not emitted
by the wrapper. A caller can independently author a different `site` using an
available original Cell, but that would change its task artifact and provenance
choice; it is not proof that the current compact submissions preserve v/t sites.
No such repair is performed here.

## Identity and transport constraints

R6.32 SPEC-1 lines9–29: immutable generations, exact R6.18 content identity,
explicit pins, deep-copy retrieval, no name-to-latest redirection. Those guarantees
are useful provenance anchors but do not authorize merging origins across successor
versions. Caller migration/resealing explicitly changes identities and paths.

R6.23 remains a construction adapter into unchanged R6.18; R6.25 ENVELOPE-1
lines20–34 keeps provider metadata quarantined and forwards semantic arguments
unchanged. Provider call IDs/turn positions are authoring-request provenance, not
executable node, input-byte or symbolic expansion coordinates. No host/LLM callback
may determine runtime error sites. Production generated manifests are artifact-level
provenance and do not provide this experimental expression correspondence.

## Qualified answer

Existing semantics support exact expanded-node reporting and bounded separate
symbolic origins/paths in retained artifacts. They do not fully support an adopted
representation-independent expression/input-lineage contract. Missing interfaces
are a typed observation/correspondence specification, expression-level origin model
if required, and independently frozen authority for derived-site behavior. None
is implemented or silently promoted to current semantics in this round.
