# R6.72 — Demonstration coverage and curriculum alternatives

## Ten unchanged R6.63 demonstrations

[Inventory](TRAINING-COVERAGE-INVENTORY.json) reads the existing sources, scopes and
expert actions without rescoring historical outputs. No new training examples were
created, admitted or trained in this round. Counts: add4, le3, eq3; this modest
imbalance alone does not explain observed errors.

|Demo|Operation/binding|What it teaches|Missing matched distinction|
|---|---|---|---|
|D01|add(arrivals,reserve)|two integer refs, Boolean distractor|same scope comparison/equality; same-type distractor|
|D02|add(1,count)|literal first, integer distractor, extra literal|same operands as bound/equality; literal-right twin|
|D03|add(batch,batch)|repeated ref, one unique dependency|negative duplicate dependency and replacement-by-decoy|
|D04|add(subtotal,adjustment)|prior result, indirect deps excluded, unused mirror|negative source/alias/indirect closure choices|
|D05|le(load,5)|inclusive upper bound, same-type distractor|same-scope reversed comparison plus add/eq alternatives|
|D06|le(5,stock)|inclusive lower bound, literal first|matched reversal with D05's exact scope|
|D07|le(requested,available)|ordered two-ref comparison|swapped operands with asymmetric behavior; negated wording|
|D08|eq(recorded,reference)|integer equality, same-type distractor|same scope le/add and unequal values in both orientations|
|D09|eq(first,second)|Bool equality, integer distractor|invalid mixed-type operand counterexample|
|D10|eq(enabled,true)|Boolean literal, Boolean distractor|false-versus-zero; literal-first equality; wrong-kind rejection|

The expert choices are valid positive supervision. Their source acceptance fixtures
include overflow, malformed arguments and exact Bool/Int64 controls; however,
those fixture observations and rejected alternative actions are **not assistant
training targets**. Positive complete-action supervision does not explicitly teach
why a nearby wrong choice fails. The system skill states types, direct dependencies
and order; a rule in a prompt is not evidence that a model learned it.

### Adequacy by decision

- **Operation:** all three operations appear, with understandable prose. Different
  operations generally use different domain names/scopes; no matched same-scope
  operation-switch triples decouple relation choice from incidental vocabulary.
- **Order:** both literal positions occur for le; add literal-first and reference
  patterns occur. No matched ordered-comparison reversal within one exact scope.
  Add/eq order is largely a representation convention rather than observable math.
- **Relevant operands:** several distractors exist, including same-type ones. Scope
  order permutations and equivalent wording pairs are absent from the ten sources.
- **Literal/reference:** integer and Boolean literals appear, but no all-literal
  selected action, false-versus-zero contrast, or kind-switch negative target.
- **Dependencies:** repeated refs and one prior subtotal teach unique direct closure.
  No labeled missing/extra/indirect/duplicate dependency contrasts, two-prior-result
  selected comparison, or reflexive prior Bool equality.
- **Types:** Int64 add/le and Int64/Bool eq are covered. Invalid input fixtures
  check runtime behavior; they are not training examples rejecting incompatible
  action bindings. Type-sensitive selection is stated, not contrastively taught.

Thus the dataset covers basic positive mechanics but lacks several contrastive
binding distinctions. This is a static coverage finding, not proof that a missing
example caused a particular output. Ten examples/20 training updates cannot establish
adequate semantic learning. R6.72's interrupted paired evaluation cannot determine
adapter improvement. The unchanged representation itself is sufficient for all12
gold tasks; supplied result type and repeated structural boilerplate may simplify
some decisions while leaving others difficult. No representation deficiency is proved.

## Alternatives

|Criterion|A: complete incremental action|B: compact semantic selection|C: contrastive semantic decisions|
|---|---|---|---|
|Supervision|positive native action, directly executable after validation|operation, two explicit tagged operands, type and dependency choice|matched positive and negative decisions with authoritative feedback|
|Output complexity|full id/type/deps/node/op/expr envelopes; repeated mechanical tokens|smaller fixed tuple/list, still all true semantic choices|classification/feedback plus corrected semantic tuple; multiple records per source|
|Data feasibility|existing assembler/scorer qualify each target|requires a versioned lossless renderer and exact identity encoding|requires single-factor mutations, typed rejection labels and functional counterexamples|
|Validation|unchanged structural check then scope/type/dependency/behavior|validate compact target, render native action, run same authority|reject malformed/incompatible negatives; execute valid-but-wrong alternatives against source fixtures|
|Superficial-pattern risk|JSON/key/type copying, vocabulary correlation|memorized indices/positions, supplied type copying|negative label imbalance, feedback-code copying, recognizing mutation artifacts|
|Deterministic reconstruction|already native|fixed envelope; preserve two slots, tags and exact refs; do not infer choices|use accepted positive selection as renderer input; no LLM at execution|

**Recommendation: C using B's explicit compact selection as the construction
target.** Contrastive supervision directly targets the missing distinctions; compact
rendering removes boilerplate without discarding operation/identity/order choices.
It is a hypothesis to test. A shorter target does not guarantee better learning,
and more records/feedback can change effective supervision and cost.

Dependencies should remain an explicit choice in the teaching target and be checked
against expression refs. Computing them silently would conceal dependency learning.
Rendering may sort/serialize an explicitly chosen dependency set, but must reject
missing/extra/duplicate choices and report raw-choice accuracy before normalization.
Result type should be predicted and checked; disclose if input scope still supplies it.
Never collapse Bool false and Int64 zero, or treat raw/source aliases as acceptable
when the requirement asks for a prior identity. Invalid action rejection feedback
is a training decision task, not a new execution primitive.

## Tradeoff and current boundary

The timing wrapper is experiment-local and output-preserving on neutral controls;
synchronization introduces measurement overhead. The decoder's unchanged prefix
admission plus terminal validation can encounter a dead end, as S11 did. Preserve
that first failure; separately authorized completion qualification should precede
a new training experiment. No decoder repair is part of this round.

Focused contrastive training is **justified as a falsifiable proposal**, not justified
for immediate execution or established as beneficial. Static coverage gaps plus
base binding/ordering errors warrant testing it once the infrastructure gate is
qualified. No paired R6.72 adapter claim is possible.
