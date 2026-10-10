# R6.40 requirement-authority audit

## Source hierarchy and exact wording

Frozen [E3 requirement](../r6_40/EVALUATION-TASKS.json) says:
“Next check 13<=u (FIRST_LOW at u), 13<=v (SECOND_LOW at v), u+v<=245
(TOTAL_HIGH at v). Return (u+v)+1. Preserve this order.”

Frozen E4 says: “Let t=((x+y)+y)+6. Check 200<=t (RANGE_LOW at t), then t<=403
(RANGE_HIGH at t). Return t+5.” Both read x then y and check input end before
computation. No sentence defines the source span of a composed derived result.

[Protocol](../../../../experiments/adaptive_discovery_r6_40/PROTOCOL.md)
lines38–49 defines X as expanded bodies without pins and requires exact success
spans/rejection sites plus work controls. It does not define a caller-versus-callee
input-span correspondence or authorize flattening as full-envelope equivalence.

The [participant guide](../r6_37/GUIDE.txt) lines5–13 explains `site`, compose,
types/order/pins and admission. R6.40 visible dispatch repeats task wording and
inlining instructions. It does not present an explicit derived-span propagation
contract. This is an observation about visible supplied guidance, not an attestation
of excluded hidden context or participant ignorance.

[Scorer source](../../../../experiments/adaptive_discovery_r6_40/tasks.py)
lines19–48 calls offsets “requirement-defined input-source” and assigns
TOTAL_HIGH(v)=1, RANGE_LOW/HIGH(t)=0. Frozen E3/E4 EXPECTATIONS fix those values
before authoring. Lines79–99 score values/types/bytes/consumed/root provenance,
or error code/stage/offset and membership of error.node in the expansion map.
They do not require a particular symbolic node, complete operand lineage, or exact
cross-condition work. Budget controls only require WORK_LIMIT and matching budget.

## Explicitness audit

| Question |Frozen task prose |Scoring artifacts |Existing semantic contract |
| --- | --- | --- | --- |
| Coordinate system |Named sites x/y/u/v/t; bytes and read order; no explicit zero-based propagation rule |Numeric0/1 expectations fix tested sites |Input Cell spans, node IDs and definition/local maps distinct |
| Expansion boundaries |Not specified |Oracle assumes input-origin offsets regardless of derived region returns |Compose emits seq; returned span is region-relative cursor |
| Caller vs definition relative |Not specified |Scalar input offset, not authored definition/caller coordinate |Node path and definition/local separately encode caller and definition |
| Required observable provenance |“at” identifies a value/site; ordered checks explicit |Exact offset/stage/code; node must exist in map; root span on success |Raw VM envelopes/work; no rebasing/hiding by wrapper |
| Compact vs expanded equivalence |No task-level equivalence judgment |Conditions share finite numeric expectations |Exact boundary-preserving expansion normative; not arbitrary flat-template equivalence |

The frozen expectations unambiguously determine **historical scoring**. They were
same-coordinator-created and not human-reviewed/external; candidate-independent
and pre-result is not independent authority. The report already retains this
ambiguity. These facts do not authorize R6.41 to invalidate or rescore the oracle.

R6.18's explicit semantics determine **implemented composition behavior**. The
result is consistent with that contract, including the earlier nested-offset3
witness. A/X matching the frozen numeric oracle does not prove compact compositions
ought to preserve input origins, nor that compact artifacts satisfy intended tasks.
This is a mismatch between an underspecified task interpretation and existing
well-specified mechanics, not evidence of nondeterministic errors or a hidden new
operation. Whether the task requires origin-preserving implementations remains open.

## Clarification questions

Human requirement authority should answer, prospectively and without rewriting
R6.40 outcomes:

1. For these derived values, does “at v/t” mean the returned Cell's existing span,
   an original input contributor, an authored expression coordinate, or a separate
   blame field? Name the coordinate system, indexing and allowed zero-width sites.
2. If an original input is required, why y for E3 v and x for E4 t? Is this the
   VM's left-operand rule, all contributing inputs, an explicit selected operand,
   or another rule? What happens with reversed operands, constants and nested calls?
3. Does a composition return expose its seq span, transparently preserve its
   result expression's span, or retain both? Are internal-check and post-return
   check sites intentionally different? Decide before new artifacts are authored.
4. Must executable node/definition/local/caller path be runtime observables or may
   they reside in a pinned debugging sidecar? Are authored text coordinates required?
5. What equivalence is required: exact boundary-preserving expanded envelope, or
   functional equivalence with explicitly paired representation-relative nodes/spans?
   Are work/depth cutoffs and node identity compared exactly or separately qualified?
6. Who independently approves and freezes those expectations before exposure, and
   what is the disposition if fixed semantics cannot meet an input-origin contract?

No answers or maintainer intent are fabricated. Clarifying the existing runtime
mechanics does not resolve these task-authority questions by itself.
