# R6.31 — H1 symbolic discovery protocol 1

**Prospective only.** Question: do AI-selected reusable compositions improve
development-unseen task correctness or fully costed effort beyond fixed primitives,
human macro reuse, expanded templates and conventional construction?

## 1. Admission contract

An AI proposal contains explicit name/family, revision, typed parameters/result,
ordered body, exact referenced dependencies, purpose/domain limits and development
witness cases. Machine sealing computes identity fields only; it never fills a
missing operation, type, dependency, guard, ordering decision or expected answer.

Admission requires all of:

1. Strict bounded serialization/schema, no duplicate keys, callbacks or unknown tags.
2. Closed exact Int64/Bool/Unit type signatures, explicit data dependencies, no
   capture/shadowing, earlier-reference and result checks in unchanged machinery.
3. Immutable content identity using the existing R6.18 canonical seal convention;
   raw file SHA256 separately. A family/revision index never makes a mutable name
   an execution target. Every transitive dependency is pinned by exact identity.
4. No self/indirect symbolic cycle or data cycle; bounded hygienic expansion.
   Preserve all existing bounds; research library caps in the track document are
   additional ceilings, not raised limits.
5. Deterministic lowering to the existing allowlist, original VM validation and
   original public execution. Preserve sequence, error precedence, provenance and
   overflow; no optimization or invented execution semantics.
6. Explicit semantic definition: parameterized relation, success domain, exact
   result and ordered failure behavior. Development-only witness/property tests
   derived from that definition must pass; validity alone is insufficient.
7. Two fresh reloads reproduce identities, expansion and observations. Record
   finite evidence boundaries; no solver-equivalence or universal proof claim.

A discovery-credit entry must parameterize a multi-operation relation, not merely
rename one primitive or store a whole-task answer/acceptance lookup. Record aliases
separately; they consume caps and costs but cannot satisfy the transfer threshold.
Retain a type-valid candidate as provisional until it passes two development uses
with distinct inputs/contexts and a declared non-applicability example. Acceptance
still does not require novelty beyond ordinary macros; that is a comparator question.

Rejected proposals retain raw arguments, intended semantics, every diagnostic,
failed test, model call and expenditure. No human semantic repair to AI entries.
Revised proposals get new content identities; previous versions and rejection
records remain. Admission never consults evaluation requirements or hidden answers.
Definitions may be valid but not useful; record such accepted unused entries.

## 2. Versioned storage and retrieval

Small experiment-local filesystem store suffices: immutable canonical objects by
hash, append-only proposal/admission receipts, versioned sorted index with signatures
and declared descriptions, a manifest pinning foundation, dependency closure and
documentation. Qualify atomic new-index publication, duplicate identical insertion,
refused overwrite/tamper/stale pin and reload. Cryptographic identity establishes
bytes, not correct semantics or human authority. No database/cloud/embedding needed.

Lookup performs deterministic lexical token and exact signature filtering, with
stable identity tie-break. Return at most4 candidates and their costs/identities;
fetch returns exact pinned body and full dependency closure. Author chooses reuse
or inlining. Log queries, misses, unused retrievals and all payload tokens. Retrieval
cannot synthesize, repair or rank using hidden acceptance. The same facility is
available to LH and LX; A uses an equivalent helper index.

## 3. Development, freeze, evaluation

- Independently commission **4 development and12 evaluation tasks**, split by
  behavioral skeleton under [selection rules](TASKS-AND-CONTAMINATION.md). Evaluation
  has4 relation/domain-transfer,4 new-combination and4 stress/negative-transfer tasks.
  Do not promise applicability of any discovered composition.
- Development sees only development contracts/public examples. Separate condition
  contexts; L1 may carry accepted within-condition definitions forward. At most12
  proposals (accepted and rejected together),4 accepted library entries. Budget
  per condition:120,000 reported input+output tokens,80 model calls,120 tool calls,
  3,600s active development wall. Human LH gets3,600s logged human/tool design effort;
  any AI assistance has the same caps, is disclosed and weakens a pure-human claim.
  Count failed search, tests, documentation and all candidate versions.
- Freeze all accepted/rejected records, index, closures, machinery, control libraries,
  templates, prompts, model/configuration, selection rules, budgets and acceptance
  expectations before evaluation reveal. L1's empty vocabulary is retained. No
  later pruning, promotion, tuning or vocabulary maintenance on evaluation outcomes.
- **12 tasks ×6 conditions ×3 replicates =216 fresh author sessions.** Replicates
  use precommitted seeds if supported, otherwise repeat IDs with nondeterminism
  disclosed; not three independent task samples. No cross-task feedback/history.
- Task-local composition is permitted within the frozen grammar but cannot enter
  the reusable store or later prompts. Log learned-library use separately from
  these newly authored inline/task-local bodies.
- Seal first complete candidate before selftest feedback; preserve partial/rejected
  attempts too. Final acceptance is offline after all final submissions seal, with
  no oracle-feedback repair. Two model-free reload passes check reproducibility.

Per evaluation session:600s process wall,40 model completion calls,64 development
tool calls,64,000 input+output tokens,4,096 output/response, first candidate plus at
most2 resubmissions, at most4 selftest batches of16 author-selected inputs each.
Tools30s/call, cumulative tool CPU120s, excluding inference. Scorer30s/scenario.
The supervisor enforces identical caps; if output usage/reasoning cannot be bounded
exactly, record overshoot and cease at the first visible boundary. Unenforced caps
cannot support controlled efficiency claims. Budget infeasibility on neutral
calibration halts before task exposure; any successor budget requires a new freeze.

## 4. Transfer witness and cost outcome

A transfer witness requires an admitted development identity actually invoked by
a correct evaluation artifact in a new behavioral skeleton/context, surviving
lowering and AI-free replay. Static and dynamically entered calls are distinguished;
a never-entered branch/definition is not successful reuse. Record direct/transitive
calls and distinct successful tasks per entry; parameter renaming alone is not
novel transfer. Wrongly applied reuse is negative-transfer evidence.

[Scoring](ACCEPTANCE-AND-SCORING.md), [cost](TELEMETRY-AND-COST.md) and
[thresholds](THRESHOLDS-AND-OUTCOMES.md) govern verdicts. L1 must justify creation,
retrieval, validation, lowering and maintenance costs; fixed-symbol or human-macro
sufficiency can falsify the need for adaptive selection in this bounded scope.
No H1 result establishes stateful modification reliability.
