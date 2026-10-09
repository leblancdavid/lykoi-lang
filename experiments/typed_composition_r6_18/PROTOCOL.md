# R6.18 bounded qualification protocol 1

Owner authorization: the R6.18 request in the active session authorizes this
nonproduction implementation and publication only. Initial Git status is clean.
Before wrapper implementation, `preservation.py record` verifies R6.17 publication
bytes and protected Git blobs, R6.10 publication bytes and the 26-construct ledger,
then records raw SHA256 identities. No external source/oracle content is opened.

Foundation: unchanged R6.10 `semantic-plan-1`; tiny allowlist: `seq`, `atom`
(UInt8 only), `value`, `check`, `end`, `emit` (UInt16BE only). Expressions:
`const` (signed64/Boolean/null), undotted `ref`, `add`, `le`, `eq`. Wrapper types:
Int64, Bool, Unit. No optimization, callbacks, effects, projections or coercion.

Witness: parameterized checked bounded addition, implemented as an ordered
value/add followed by check/le, returning the addition's immutable reference.
Two distinct contexts: direct byte-pair checked sum; header-guarded byte-pair
sum after nested increment. Bounds and failure behavior use existing VM meaning.
An independently constructed fully expanded twin is compared with each lowering.

Predeclared evidence: all 65,536 byte pairs in each context, three full repeated
passes; empty/truncated/trailing/wrong-header inputs, and every tightened work
cutoff through successful full work plus depth/input/output limits. Compare the
complete VM envelope, including typed values, provenance, errors/sites, output,
output spans and logical work. Identical expanded artifacts are a separate check.
Ordered entry traces come from a test-only Machine subclass and are verified
against public execute envelopes; all scored execution uses public execute.

Adversarial controls retain serialized attempts and structured diagnostics:
cycles (registry and local data), valid nested reuse, wrong types, missing symbols/
references, capture, expansion bounds, ordering, unsupported operations, malformed
JSON/shapes and identity tampering. Any implementation failure is retained before
repair; no changes to prior evidence or the VM.

Measure canonical representation/expanded bytes, node counts, wrapper validation,
expansion and public VM execution separately; report timings as host observations,
tracemalloc peak as Python allocation evidence, and work as the frozen VM metric.
No authoring/model cost inference. Stop after publication; no comparative study,
model selection, training, production integration, P6-A04 acceptance or P6-A05 access.
