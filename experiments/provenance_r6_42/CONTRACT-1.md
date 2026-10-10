# R6.42 prospective provenance contract (research only)

The owner's R6.42 authorization adopts the R6.41 recommended observation-level
clarification for this bounded, model-free, unscored experiment. Production and
historical scoring contracts are unaffected. No new execution meaning is defined.

## Normative coordinates and correspondence

1. R6.18 SEMANTICS-1 and the unchanged R6.10 VM remain executable authority.
   Preserve every executable seq boundary, returned Cell span, raw error stage,
   node, offset, logical charge, and deterministic output. Never rebase errors.
2. Compact execution means deterministic lowering followed by that VM. Its exact
   expansion is independently constructed, preserving IDs, bindings, regions and
   expressions. Require byte-identical canonical plans and exact entire envelopes,
   node-entry/return traces and charge traces on every tested input/budget.
3. Map entries identify **definition content pin** and **definition-local node**.
   Region entries use local `region`; they do not invent a compose-step entry.
   Expansion paths are ordered call-local/pin pairs following the R6.18 path rule.
   Check consumer path and returned-value producer region are separate coordinates.
4. A flat node corresponds only to the explicit executable-node pair frozen in
   CORRESPONDENCE.json. Region returns removed by flattening have no flat node.
   Functional comparison requires status, typed value, bytes, consumption, error
   classification/stage and first-check label at default budgets. Raw node IDs,
   input offsets, intermediate spans, work, output-span IDs and cutoff outcomes
   remain representation-dependent observations, never overwritten or normalized.
5. The flat sidecar's paired symbolic origin is a **comparison annotation**, not
   an assertion that the flat author used that definition or retained its regions.
   No cross-representation equal-work or equal-budget-outcome requirement applies.
6. Unsupported claims reject: offset equals authored-text coordinate; returned
   seq span equals operand ancestry; wrong call path/definition/local identity;
   flattening preserves full envelope; empty integer `origins` contains byte lineage.
   Authored line/column, expression-occurrence identity, and dynamic arithmetic
   producer ancestry are unavailable. Do not fabricate them.

## Independently specified behavior and three forms

Read two UInt8 values x/y, then end-check before computation. Guarded(x) checks
x<=3 (`INNER`, site x), computes x+1, returns it. Nested(x) calls Guarded(x) and
returns its result. Entry calls Nested(x) as left then Nested(y) as right; checks
3<=left (`POST_LOW`, site left), then left+right<=6 (`POST_HIGH`, site right);
computes/returns left+right and emits UInt16BE. All checks are absorbing and ordered.
Both siblings run even if a subsequent caller check would fail. Calls are pinned.

The independent exact expansion contains root plus four zero-byte nested seq
regions, with result-ref evaluations intact. The flat counterpart contains root,
the two ordered primitive guard/add pairs, caller checks, total and encoder.
No optimizer or new opcode is used. Domain: x,y in 0..5 (36 unique pairs), plus
empty, one-byte and three-byte inputs. Two deterministic passes; all budgets
0 through the independently expected unbounded work plus one for every input/form.

## Pre-execution expectations and logical work derivation

EXPECTATIONS.json is computed without executing/expanding candidates or reading
their bodies. Its specification schedule explicitly charges node entry once,
each expression occurrence once, each input byte once plus UInt8 conversion once,
each seq result ref once, encoder ref once and two emitted bytes once each.
These rules come from interpreter.py Machine.charge/expr/run/execute and R6.18
SEMANTICS-1 lines25–36,38–60,88–103. The oracle records every charge, returned
Cell (exact type/span/origins), ordered entry/return and full envelope, including
budget exhaustion before a charge. It is same-coordinator specification-derived,
not an independent human audit or cognitive separation claim.

Hand-derived full work: success compact/exact51, flat43; first INNER15/13,
second INNER27/21; POST_LOW37/29; POST_HIGH43/35. Internal guard offsets0/1;
caller guard offsets compact/exact2, flat0/1. Successful root span[0,2), arithmetic
origins empty; nested regions return[2,2). Truncation/trailing precede all guards.
Work cutoff uses current cursor unless a byte/conversion charge explicitly sites
an input byte, including conversion cutoff after cursor advancement. Charge and
trace records retain partial execution, not hypothetical completion.

## Protocol and stop

`python experiments/provenance_r6_42/prepare.py` verifies inherited hashes and
publishes immutable baseline/forms/expectations/maps/controls and FREEZE.json.
`python experiments/provenance_r6_42/run.py` first verifies that freeze, then
executes observations and adversarial controls. No candidate/oracle repair after
freeze; retain discrepancies and classify partial/gap/halt as appropriate.
Run existing R6.18 and R6.32 regression suites, preservation and publication
verification plus git diff --check. Only additive R6.42 paths may change.
Publication verifier excludes itself and verification receipts from recursive
self-hashing, and separately binds the publication manifest in VERIFICATION.json.
Stop after publication and await explicit authorization for another experiment.
