# R6.29 baseline and pre-authoring capability inventory

[Baseline](BASELINE.json) verifies1,530 protected identities, the complete R6.28
publication manifest/receipt and its supported classification. R6.27 qualification
and the exact installed executable hash remain pinned. Production kernel accounting
remains26. No production, VM, wrapper, adapter, semantic dispatcher, tool definition,
transport or qualified publication annotation changes.

| Required behavior | Existing representation | Gate evidence |
| --- | --- | --- |
| Typed Boolean predicate | R6.18 Int64 `le`/same-type `eq` produce Bool; value steps store Bool | Computed predicate scripted dispatch succeeds |
| Guard evaluation | R6.18 `check` requires Bool expression and explicit site | Existing Bool-input guard scripted dispatch/expansion succeeds |
| Guard-triggered rejection | R6.10 ordered check emits declared code with absorbing failure | False guard emits WitnessDenied |
| Dependent arithmetic | Int64 immutable step refs and checked add | Two scripted dependent additions return3 |
| Ordered error precedence | Explicit region order; no topological sorting; VM seq absorbs first failure | False guard at MAX rejects before add; true guard at MAX reaches OVERFLOW |
| Tool expressibility | R6.25 exposes original R6.24 value/check/compose union | Same real Session, original schemas and normalization |
| Qualified native route | R6.27 object-root annotation and verified stdin delivery | Baseline executable identity; live four-tool list preserved |

Authoritative specifications: [R6.18 semantics](../../../../experiments/typed_composition_r6_18/SEMANTICS-1.md),
[R6.10 contract](../../../../experiments/semantic_interpreter/CONTRACT-1.md),
[R6.25 envelope](../r6_25/ENVELOPE-1.md), [dispatcher](../r6_24/tools.py),
[R6.23 adapter](../r6_23/adapter.py), [R6.27 report](../R6_27-REPORT.md).
The scripted witness is [preserved in full](CAPABILITY-WITNESS.json), including
calls, responses, artifact, typed packages, expansion, VM envelopes, traces and times.
It runs before requirement selection and makes zero model calls. Its Bool+Int64
signature differs from the subsequently selected two-Int64 requirement. The witness
is never supplied to the model as a solution.

The gate establishes expressibility, not a frozen acceptance-stage label. The
coordinator failed to copy the witness's native `validation` stage into the later
guard expectations; this distinction is disclosed in the terminal report.

Coordinator context includes earlier historical outcomes and R6.28 helpers. No
independent replication, blind task selection or hidden-context exclusion claim.
