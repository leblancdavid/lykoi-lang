# R6.63 — Incremental symbolic construction data qualification

**Final classification: `R6_63_INCREMENTAL_DATA_QUALIFIED`.**

Ten verified incremental expert demonstrations and deterministic one-step assembly
are available. Two identical behavioral passes satisfy all48 frozen fixtures each
(96 observations);19 mutation controls and5 further adversarial test methods pass.
This qualifies bounded expert data and assembly, **not model learning, generalization
or independent evaluation custody**. Training and model inference are zero.

## 1. Baseline and frozen scope

Initial git status was clean. [Protocol](r6_63/PROTOCOL.md),
[skill specification](r6_63/SKILL-1.md), [baseline receipt](r6_63/BASELINE.json),
[source freeze](r6_63/SOURCE-FREEZE.json) and
[selection freeze](r6_63/SELECTION-FREEZE.json) precede candidate construction.
The baseline rehashes R6.62 publication and its inherited R6.61/R6.60/R6.59 chain,
all5,387 protected identities, existing environment/checkpoint/adapter artifacts,
R6.49 Tier T policy, R6.62 supervision schemas and deterministic foundation/tools.
The pinned environment's47 distribution trees are checked by the inherited audit.
Kernel26 is preserved against unchanged accounting and production implementation;
it is not newly recounted. R6.3–R6.62 classifications and evidence are preserved.

R6.59 step20 adapter weights SHA256 remains
`79843df8ce1f3e9bf87c81e0e23073c37a702695df6e52ac384b0a33f77fb7d1`;
config `642b816c81121fb0bf251550885b1ae30ca89c2cb824f4b4a2cd2c1caf657050`;
directory `d8bbe876eca1e5929a0bd570e44fb661d4eb1cdb5ebf8e857c3ee659923ab58a`.
Checkpoint weights remain
`c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8`;
tokenizer `c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539`.
Only tokenizer computation occurs; no model weights are loaded for computation.
External assets remain temporary, not made durable by these identities.

The [first baseline invocation](r6_63/BASELINE-ATTEMPT-1.json) used system Python
and failed the inherited installed-distribution equality check. No baseline/source
was written. The unchanged freeze passed under the existing pinned private Python;
no environment or historical expectation was changed.

## 2. Expert demonstrations and deterministic assembly

[Demonstration index](r6_63/DEMONSTRATIONS-2.json) links each source, frozen before/after
state and matched A/B representation. Each episode folder contains SOURCE, FRC,
BEFORE, ACCEPTANCE, ACTION, AFTER, VALIDATION, OBSERVATIONS and ADMISSION JSON.
Use **B-RECORD-2.json** as the schema-qualified B envelope; A-RECORD.json is the
matched complete-package envelope. There are ten episodes, not20 examples or96
independent tasks. All are explicitly `deterministic_expert_demonstration`.
Actual observed AI-selected semantic trajectories0; invented reasoning traces0.

[Assembler](../../../experiments/incremental_data_r6_63/assembly.py) selects no
semantics itself: it copies the submitted add/le/eq expression, validates direct
reference/literal operands through unchanged R6.18 expression typing, verifies exact
sorted distinct dependencies and required result type, appends one value step,
seals native definition/package identities and expands through unchanged helpers.
The complete prefix is validated even when unused. Rejections create no after-state.
State body, parent/action pins, prefix and parameters remain exact; serialized
reload/reassembly yields identical after-state and native validation results.

The wrapper's full program must return Int64. A mechanical HostEntry returns zero
and is **not** used as requirement acceptance. For each supplied fixture, unchanged
expansion instantiates task arguments; the generated task region is observed via
existing R6.10 `execute(..., assemble=False)` in the decode slot. Actual Int64/Bool
values, native overflow and logical work are retained. No new evaluator, operation
or UInt16 encoding claim is introduced. Argument shape/type guards enforce the
existing immutable signature before VM execution.

R6.62 B's trace field requires an artifact. The initial ten envelopes used null and
failed that field's schema check; all originals are retained. The
[schema qualification](r6_63/SCHEMA-QUALIFICATION.json) records corrected B envelopes
referencing real deterministic assembly receipts, with expert provenance. No target,
source, action, expected result or behavioral output changed. Twenty final A/B
envelopes, ten step targets and ten native package targets pass schema validation.

## 3. Acceptance and semantic diversity

Expected behavior was frozen as explicit literal fixtures before expert construction;
exact op/operand/type/dependency expectations were separately sealed before actions.
No expected value is obtained from candidate output. The acceptance artifacts and
implementation are separate, but share coordinator authorship/review; independent
human commissioning/review is not claimed.

| Demonstrations | Selection skill | Count |
| --- | --- | ---: |
| D01–D04 | add: distinct refs, literal-first, repeated ref, prior subtotal reuse |4|
| D05–D07 | le: upper/lower literal direction and ordered distinct refs |3|
| D08–D10 | eq: Int64 agreement, Bool truth pairs, Bool literal match |3|

[Diversity/leakage audit](r6_63/DIVERSITY-AND-LEAKAGE.md) distinguishes nominal
families from shared ancestry. Renamings, replay passes and A/B/C derivatives are
not independent diversity. Coverage includes distractors/unused refs, deduplicated
one/two direct dependencies and a subtotal's transitive parents. No literal-only
positive, Unit equality positive, long dependency graph or application is claimed.

- **48/48 unique fixtures per pass;96/96 two-pass observations:**38 typed-success
  fixtures,6 native OVERFLOW fixtures and4 invalid argument shape/type fixtures.
- **19/19 mutation controls:**12 static type/dependency/reference/identity/operation
  rejections;6 well-typed wrong semantic choices fail frozen behavior;1 commutative
  operand swap passes behavior but fails exact source-selection binding.
- **5/5 additional adversarial test methods:**rehashed malformed prefix/dependency,
  prefix order, identifier capture, local resource bounds and duplicate-key/float
  serialization controls. [Test output](r6_63/TEST-RESULTS.json) is retained.
- **Independent-process publication replay:**all48 original fixtures and exact
  after-state/target/schema identities are rechecked, without AI computation.

Finite acceptance is not universal equivalence. D01's plus boundaries cover both
signed ends; D03 challenges doubled-reference overflow; D04 distinguishes prior
subtotal overflow from selected-step overflow. Bool agreement covers all four pairs.
Inclusive comparison equality and swapped unequal/extreme operands are explicit.

## 4. Equivalent A/B supervision comparison

[Final measurements](r6_63/AB-MEASUREMENTS-2.json) use the unchanged pinned local
CPU tokenizer on canonical ASCII target JSON. A contains the complete sealed native
package, including prior steps and mechanical HostEntry; B contains only the selected
native step. Both represent the same source choice and assembled task behavior.

| Metric | A: complete package | B: incremental step |
| --- | ---: | ---: |
| Total target content tokens,10 tasks |4,917|354|
| Per-target content-token range |473–560|33–39|
| Total including one EOS per task |4,927|364|
| Identical serialized requirement/scope prompt tokens per task |284–366|284–366|
| New semantic choices |1 relation,2 ordered operands,result type,dependency set|same|
| Target native stored steps |2, or4 for subtotal example|1 selected step|
| Final expanded validation nodes |4, or6 for subtotal example|same assembled package|
| Median native validation across tasks |0.0635–0.0889ms|included in assembler|
| Median validation+expansion across tasks |0.1159–0.1645ms|included in assembler|
| Median B assembly incl. prefix/result validation, expansion and hashing |—|0.3907–0.5866ms|

B saves4,563 content tokens, **92.8%** in this explicit sealed-package convention.
The full skill contract adds513 context tokens; step schema422; the larger complete
package schema is measured separately. Prompt lengths alone do not include those
referenced contracts. Both need the full requirement, immutable scope, available
literals and serialization/assistance rules. B reduces output copying and delegates
identity/scaffold assembly; it does not remove semantic decisions or state context.
JSON tree-node counts, bytes, timing distributions and isolated cached package-hash
cost are recorded per episode. Target size is not a learning-benefit measurement.

Initial [measurements](r6_63/AB-MEASUREMENTS.json) are retained. Revision2 measures
the final explicit local-bound checks and removes disk-read time from the isolated
hash microtiming. Token totals are unchanged. Timings are20 sequential repetitions
on one uncontrolled host; no inference/training efficiency claim follows.

## 5. Existing C interface assessment

[C assessment](r6_63/C-INTERFACE.json) preserves the existing R6.25 advertised
`apply_operation` schema and corresponding calls. Its bounded value variant accepts:

```json
{"function":{"name":"apply_operation","arguments":{
  "definition":"Fits","alias":"selected","operation":"value","type":"Bool",
  "expression":["le","$requested","$available"],
  "dependencies":["available","requested"]}}}
```

The unchanged R6.24 dispatcher accepts all10 selected calls plus2 prefix calls,
with prior declare_input and subsequent define_result. Scripted calls and native
adapter resolution preserve all48 expected task outcomes. These are **scripted
interface qualification**, not observed AI decisions; remote MCP transport calls0.
No new MCP capability is implemented. The historical semantic tool is not exposed
as a Lykoi tool in this active harness. Its Int64-only validate_candidate finalizer
remains a full Bool endpoint gap, while Bool operation selection is expressible.

The [first C audit assertion](r6_63/INTERFACE-ATTEMPT-1.json) compared the value-only
advertised schema against a broader historical variant and failed before any C
calls. Comparing the existing value-only variant corrected the audit assertion;
historical tools/schemas and candidate semantics stayed unchanged.

## 6. Admission, withholding and smallest next step

All ten final records satisfy the conjunctive R6.49 **Tier T research-candidate**
gates for owner-authorized synthetic fixtures. Same-coordinator capability-aware
source/FRC/oracle/action review and shared ancestry are disclosed. They remain
training_development; training itself is not authorized by candidate eligibility.

At least one structurally distinct family is reserved by description:
Unit equality over two prior Unit aliases sharing an input/diamond dependency.
Completed evaluation solutions0; none exported to producer records. However,
repository/session controls do not enforce future producer exclusion or attest
provider hidden context. **Tier E0; independent evaluation qualification absent.**
The exposed reservation cannot become pristine evaluation by relabeling.

A **small B-only mechanics/fitting smoke is technically justified**, conditionally
on a new explicit authorization and frozen contexts/masks/scoring. Recommend one
fresh adapter, at most20 existing-mechanics updates, these ten corrected records,
strict source-selection/assembly/behavior diagnostics versus unchanged base, no
automatic repair or tuning. This would measure exposed fitting only. For any
generalization-qualified study, first commission a privately frozen custodian-held
structural family with auditable exclusion. The
[smallest-next-experiment recommendation](r6_63/SMALLEST-NEXT-EXPERIMENT.md) supplies
bounds; no full A/B/C comparison or C trajectory training is recommended now.

## 7. Publication integrity and stop

[Publication identities](r6_63/PUBLICATION-IDENTITIES.json) seal all R6.63 payloads;
[verification receipt](r6_63/VERIFICATION.json) binds that manifest and repeats
baseline preservation, native/schema/behavior replay, tests, additive scope,
JSON/Python/link/whitespace/credential checks and `git diff --check`. Seal/receipt
exclude themselves to avoid circular hashes. A separate invocation rechecks the seal.
[Additive research/decision/boundary supplement](../../../docs/research-log-r6.63.md)
preserves shared historical indexes.

Production kernel26; production compiler/lowerer/runtime and experimental execution
semantics unchanged; new primitives0; optimizer/scheduler updates0; additional
fine-tuning0; model downloads0; Python comparison adapter0; historical rescoring0;
P6-A04 acceptance executions0; P6-A05 access false. Execution remains AI-independent.

**Stopped after bounded qualification and publication. Await explicit authorization
before training, evaluation commissioning or further research.**
