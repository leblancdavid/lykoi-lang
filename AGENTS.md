# Agent guidance for Lykoi

The project is **Lykoi**, not Axiom. Keep historical `axiom`/`air` paths,
serialized keys and pinned records for compatibility; use Lykoi in new prose.
Check `git status` before editing. Read `docs/project-overview.md` for the
current research boundary and `docs/agent-workflow.md` for scope-specific rules.

## Model and verification

- Latest round R6.11: `R6_11_EXPLORATORY_COMPARISON_ONLY`.
  Read `benchmark/results/phase6/R6_11-REPORT.md` and `r6_11/PROTOCOL.md` beside it.
  Same-session Python/experimental-VM pilot: each passes four base tasks (49 cases)
  and two modifications (40 combined cases), first attempts, zero repairs/regressions.
  Production not scored; no controlled separation, independent sourcing or token/cost
  telemetry. Kernel 26, production/R6.10/history unchanged; 116 baseline methods pass.
  Stop after publication. No automatic expansion, rerun, semantic improvement or P6-A05
  access; subsequent work requires explicit owner authorization.
- Latest round R6.10: `R6_10_PROTOTYPE_PARTIAL`.
  Read `benchmark/results/phase6/R6_10-REPORT.md` and
  `experiments/semantic_interpreter/CONTRACT-1.md`. Dedicated experimental VM executes
  explicit CFG66/DSV66/BXC66 plans; 82 tests pass, including exhaustive UInt16 values
  and deterministic budget cutoffs. Full static typing, encode field paths and exact
  frozen cost/lowering correspondence remain open. Production kernel 26 and protected
  implementation/R6.3–R6.9 history preserved; no acceptance/provider/review execution.
  Stop after publication. Typed-plan/encode closure requires separate authorization;
  no production integration, independent review or P6-A05 access.
- Latest round R6.9: `R6_9_ISOLATION_CONTROL_GAP`.
  Read `benchmark/results/phase6/R6_9-REPORT.md` and
  `r6_9/INVOCATION-CONTRACT.md`. Provider-neutral package/runner/seal infrastructure
  implemented; 28 synthetic tests pass. Actual Windows runner refuses dispatch;
  unconfined negative controls demonstrate outside-file/guidance/network access.
  Linux sandbox branch unexecuted, provider hidden context unverified, input
  dependency sufficiency unreviewed. Candidate export prepared, not approved/dispatched.
  Kernel 26/language implementation/history preserved; provider and substantive-review
  calls 0. Stop after publication. Further qualification and review need explicit
  approval; no I-BOUND/C-ATOM implementation, compilation, acceptance or P6-A05 access.
- Latest round R6.8: `R6_8_INDEPENDENCE_NOT_ESTABLISHED`.
  Read `benchmark/results/phase6/R6_8-REPORT.md` and
  `r6_8/ISOLATION-EVIDENCE.md`. Pre-assignment isolation gate not established;
  source inventory/neutral prompt prepared, isolated export not released. No reviewer
  assigned, independent judgments/seal/reconciliation NOT_REACHED. Available task
  controls do not attest exclusion of inherited guidance, repository/retrieval or
  memory. No independently supported reductions or semantic verdict. Kernel 26,
  implementation and R6.3–R6.7 preserved; executions 0. Stop after publication;
  explicit authorization and auditable input control required before a later review.
  No implementation, compilation, acceptance or P6-A05 access.
- Latest round R6.7: `R6_7_INDEPENDENCE_NOT_ESTABLISHED`.
  Read `benchmark/results/phase6/R6_7-REPORT.md` and
  `r6_7/REDUCTION-MATRIX.md`. Frozen R6.6 inputs reviewed under separated nonblind
  same-platform protocol; terminal clarification confirmed inherited substantive
  R6.7 verdict/findings before review, so independence is not established. Original
  judgments/disclosures and separate correction retained. Finite escapes and UInt16BE
  decode arithmetic admit qualified subrelation
  reductions; no whole-family reduction/minimum/irreducibility proof. Exact cost,
  DSV conversion/provenance, assembly typing and round-trip domains need repair.
  All executions NOT_RUN, kernel 26/implementation/history unchanged. Stop after
  publication; prospective specification repair needs explicit authorization.
  No implementation, compilation, acceptance or P6-A05 access.
- Latest round R6.6: `R6_6_COMPOSITION_CANDIDATE_SUPPORTED`.
  Read `benchmark/results/phase6/R6_6-REPORT.md` and
  `r6_6/CANDIDATE-SEMANTICS.md`. Specification-only bounded structural
  interpretation/assembly and explicit atomic codecs compose CFG66/DSV66/BXC66.
  Two families are not two proven constructs or a minimum; adversarial outcomes
  are NOT_RUN. Typing/progress, lowering, result binding, broader Unicode/recursion,
  stronger integrity and physical effects remain open. Kernel 26/implementation/history
  unchanged; executions 0. Stop after publication; no implementation, compilation,
  acceptance or P6-A05 access. Independent specification reduction audit requires
  explicit authorization.
- Latest round R6.5: `R6_5_SEMANTIC_EXTENSION_REQUIRED`.
  Read `benchmark/results/phase6/R6_5-REPORT.md` and
  `r6_5/EXPRESSIBILITY-MATRIX.md`. Documentation-only general parsing/resource
  decomposition: decoded finite data reuse established architecturally; general
  grammar interpretation adds missing meaning under current admitted operations.
  Physical adapters/lowering/verifier work distinguished; live handles, process
  contracts and tree transactions unresolved. No minimality/impossibility or
  behavioral result. Kernel 26/implementation/history unchanged; executions 0.
  Stop after publication; no implementation, repair, compilation, acceptance or
  P6-A05 access. Next specification challenge requires explicit authorization.
- Latest round R6.4: `R6_4_LYKOI_SEMANTIC_GAP`.
  Read `benchmark/results/phase6/R6_4-REPORT.md` and
  `r6_4/CAPABILITY-INVENTORY.md`. Exact R6.3 artifact approval/source provenance
  verified; research-only receipt, static native-readiness assessment published.
  Current accepted operations lack package parsing/artifact/install semantics;
  native payload, pinned environment and observation/containment integration also
  missing. No abstract-kernel impossibility claim or measured native blocker.
  Kernel 26/implementation/history unchanged; acceptance executions 0. Stop after
  publication; no repairs, evaluation, authoring, compilation or P6-A05 access.
- Latest round R6.3: `R6_3_P6_A04_CLARIFIED_RESEARCH_CONTRACT_READY`.
  Read `benchmark/results/phase6/R6_3-REPORT.md` and `r6_3/HUMAN-REVIEW.md`.
  Exact human Q1/Q2 clarification recorded; source-faithful revision 2, pinned fixture
  and fixed four-stage acceptance expectations await subsequent exact approval.
  Native package-install execution payload remains unprepared; do not infer execution
  readiness. Kernel 26/implementation/history unchanged. Stop after publication;
  no approval, receipt, evaluation, authoring, compilation or P6-A05 access.
- Latest round R6.2: `R6_2_P6_A04_LITERAL_INPUT_CLARIFICATION_REQUIRED`.
  Read `benchmark/results/phase6/R6_2-REPORT.md` and `r6_2/HUMAN-REVIEW.md`.
  Exact preserved pip source verified; Q1/Q2 remain underdetermined by desired
  path-space behavior and failing reproduction. No revised FRC/fixed plan justified;
  R6.1 identities preserved. Kernel 26/implementation/history unchanged. Stop after
  clarification review; no approval, receipt, evaluation, tests or P6-A05 access.
- Latest round R6.1: `R6_1_P6_A04_RESEARCH_REVIEW_PREPARED`.
  Read `benchmark/results/phase6/R6_1-REPORT.md` and `r6_1/HUMAN-REVIEW.md`.
  Exact R5.116A P6-A04 pip source verified; valid unapproved FRC and conditional
  acceptance plan prepared. CLARIFY raw-space URL and wheel-filename name token;
  fixture identities unfixed. No approval/evaluation/test execution or semantic work.
  Kernel 26/model 0.3/compiler 0.3.0/history preserved. R5 numbering ends at R5.121;
  new rounds use R6.x without renumbering history. Stop after preparation; owner
  decision and separate authorization required before any later attempt. No P6-A05 access.
- Latest round R5.121: `R5_121_P6_A03_POST_FIRST_EVALUATION_COMPLETE`.
  Read `benchmark/results/phase6/R5_121-REPORT.md` and immutable
  `r5_121/P6_A03_POST_FIRST_RESULT.json`. Separately authorized linked local attempt:
  exact revision-2 approval/artifacts and receipt valid, FRC PASS, structural coverage
  `STRUCTURAL_COVERAGE_FAILURE` (six unmapped obligations). All downstream NOT_REACHED;
  no authoring/compiler/Redis acceptance, no kernel-impossibility claim. Kernel 26 and
  original first result NEEDS_CLARIFICATION / RESEARCH_APPROVER_UNAVAILABLE preserved.
  Stop after terminal publication; no repairs/retries or other-source access. General
  mapping/ordered transformation/session-scope investigation needs separate authorization.
- Latest round R5.120A: `R5_120A_LOCAL_RESEARCH_EXECUTION_READY`.
  Read `docs/local-research-execution-v1.md`,
  `docs/phase6-generalization-protocol-r5.120a.md` and
  `benchmark/results/phase6/R5_120A-REPORT.md`. Plain exact-bound human research
  receipts call existing semantic stages without controller credentials/grants/seals;
  production security unchanged. Synthetic success/native halts/wrong-compilable
  behavioral failure/isolation qualified; kernel 26/history unchanged. Stop after
  synthetic qualification. No P6-A03 evaluation/authoring/compilation or P6-A04/P6-A05
  inspection. Later P6-A03 needs separate authorization and explicit linked
  post-first-result labeling; approved executable acceptance integration still required.
- Latest round R5.120: `R5_120_P6_A03_FIRST_EVALUATION_COMPLETE`.
  Read `benchmark/results/phase6/R5_120-REPORT.md` and immutable
  `r5_120/P6_A03_FIRST_RESULT.json`: NEEDS_CLARIFICATION /
  RESEARCH_APPROVER_UNAVAILABLE at authenticated approval. Exact human statement
  and revision-2 hashes verified; no legitimate controller credentials or evaluation
  authority. All semantic stages NOT_REACHED; no Redis capability verdict. Kernel 26,
  historical results preserved. Stop; no repair/retry or other-source evaluation.
  Later linked attempt needs separate authorization and real authority provisioning.
- Latest round R5.118A: `R5_118A_RESEARCH_EVALUATION_AUTHORITY_READY`.
  Read `docs/research-evaluation-approval-v1.md`,
  `docs/phase6-generalization-protocol-r5.118a.md` and
  `benchmark/results/phase6/R5_118A-REPORT.md`. Research approval binds exact source,
  FRC, review, pre-author acceptance and evaluator; appointed research role required,
  no producer self-approval or product/deployment authority. Native semantic and
  external verification gates remain. Synthetic known-answer/same-agent evidence,
  no actual approver appointed for external sources. R5.117/R5.118 first results and
  R5.116A curation preserved; kernel 26 unchanged. Stop after methodology verification;
  no P6-A01/P6-A02 rerun or P6-A03–P6-A05 content access/evaluation authorized.
- Latest round R5.118: `R5_118_P6_A02_FIRST_EVALUATION_COMPLETE`.
  Read `benchmark/results/phase6/R5_118-REPORT.md` and preserved
  `r5_118/P6_A02_FIRST_RESULT.json`: NEEDS_CLARIFICATION at FRC review/approval,
  required approval unavailable. Exact source and bounded-change candidate verified;
  no demonstrated material ambiguity in the delta, no approved FRC or implementation
  authority. Downstream NOT_REACHED; implementation/kernel 26 unchanged. Procedurally
  selected external evidence, not blinded/held-out. Preserve R5.117. Stop; no repair or
  P6-A03–P6-A05 access. Further approval/linked attempt requires separate authorization.
- Latest round R5.117: `R5_117_P6_A01_FIRST_EVALUATION_COMPLETE`.
  Read `benchmark/results/phase6/R5_117-REPORT.md` and the preserved
  `r5_117/P6_A01_FIRST_RESULT.json`: `NEEDS_CLARIFICATION` at formalization/clarification.
  Exact P6-A01 verified; source-bound candidate envelope valid, no human approval or
  implementation authority. All downstream stages NOT_REACHED. No semantics changed,
  kernel 26; material is procedurally selected external evidence, not blinded/held-out.
  Stop after first-result publication; no repair or P6-A02–P6-A05 access/evaluation.
  Further clarification or linked post-exposure attempt requires separate authorization.
- Latest round R5.116A: `R5_116A_PROCEDURAL_OPEN_SOURCE_BATCH_CURATED`.
  Read `benchmark/results/phase6/R5_116A-REPORT.md`. Five externally authored,
  procedurally selected issues are hash-bound under precommitted policy
  `c840083469efc9f94920ebce41103a51092ac915`; no blinded/held-out claim. All five
  candidate acceptance records require clarification; this curation session saw sources.
  Implementation remains R5.114 (26 concepts, 16/20 exposed successes). Stop after
  curation; no R5.117 evaluation or semantic development authorized. R5.116 preserved.
- Preserved R5.116: `R5_116_BLOCKED_CURATOR_SEPARATION_UNAVAILABLE`.
  Read `benchmark/results/phase6/R5_116-REPORT.md`. No source selected/inspected,
  no acceptance records or batch manifests, no requirement delivery. Available
  subagents do not establish exclusion of repository guidance/access; fresh sessions
  alone are insufficient. Stop before sourcing/exposure until a genuinely separated
  curator is available. R5.117 is not ready; implementation remains R5.114.
- Current research transition is R5.115: `R5_115_PHASE6_RESEARCH_READY`.
  Read `docs/phase5-baseline-r5.115.md`, `docs/phase6-research-plan-r5.115.md`
  and `docs/phase6-generalization-protocol-r5.115.md`. This is a documentation-only
  transition; R5.114 remains the implementation baseline (26 concepts, 397 tests,
  16/20 exposed successes). B01–B20 are permanently exposed development/regression
  evidence, never held-out generalization. Future independent sources come from an
  external curator without capability tailoring, with no development semantic access
  before a fresh snapshot/evaluation. Preserve native first-blocker codes/stages and
  immutable first results; unexecuted downstream stages are NOT_REACHED. Stop after
  R5.115 planning: no source selection/generation/inspection/evaluation, semantic
  implementation, telemetry or qualification/activation infrastructure authorized.
- Current historical-state/verification policy is R5.114:
  `R5_114_HISTORICAL_STATE_TRUSTED_VERIFICATION_CLOSED`. Read
  `docs/historical-state-trusted-verification-v1.md` and
  `benchmark/results/phase5c/R5_114-REPORT.md` before extension. Explicit additive
  related role/reference/collection/nullable and checked computed migration sources
  use one-store version chains and atomic replacement. Creation defaults never
  authorize history. Normal sealed external verification includes verifier-owned
  controlled-host actor contexts; host assertion is not authentication and CLI has
  no trusted source. Kernel stays 26. 397 tests and 133 synthetic external invocations
  precede content lock; fresh transfer retains 16 successes B01–B16, 447 invocations.
  B17–B20 disputed, B18/B19 downstream NOT_REACHED. Preserve historical evidence,
  obtain actual role/error authority before further authoring. Stop after R5.114;
  no next round, new infrastructure or benchmark-specific primitives authorized.
- Preserved authorization/effect policy is R5.113:
  `R5_113_AUTHORIZATION_CONDITIONAL_EFFECT_COMPOSITION_PARTIAL`. Read
  `docs/prewrite-conditional-composition-v1.md` and `benchmark/results/phase5c/R5_113-REPORT.md`
  before extension. Prewrite role/owner/set predicates, controlled-host actor binding,
  conditional reference updates/atomic creations, acyclic created images and explicit
  nullable refinement compose. Supplied actors are selectors, not authenticated principals;
  CLI has no trusted authentication source. Exact elapsed-day conversion admits K26:
  proposed kernel 25 -> 26. Related historical-field migration and sealed trusted-host
  success verification remain seams. Generic lock stays fixed through transfer: 16
  successes B01–B16, B17/B20 disputes, B18/B19 now inherited historical-role authority
  disputes at formalization, no new downstream stages. No role migration is guessed from
  new-user defaults. Preserve all historical evidence. Stop after R5.113; R5.114 is a
  recommendation only. No new infrastructure, unrestricted arithmetic or semantic family.
- Preserved primary interface policy is R5.112:
  `R5_112_PRIMARY_INTERFACE_COMPOSITION_PARTIAL`. Read
  `docs/primary-value-interfaces-v1.md` and `benchmark/results/phase5c/R5_112-REPORT.md`
  before extension. Signed-64/nullable primary fields, explicitly supplied primary
  actor context, cardinality history and unconditional same-primary successors
  compose through the normal path. Absolute UTC-day midnight decoding is defined;
  runtime N-day duration scaling, nullable refinement, conditional atomic membership,
  secondary-created-image bindings and prewrite role/owner authorization remain gaps.
  Proposed kernel stays 25; generic lock unchanged through fresh transfer: 16 successes
  B01–B16, B17/B20 disputes, B18 authorization and B19 conditional duration/effect/image
  interfaces structural. No new downstream stages. Stop after R5.112; R5.113 remains
  a recommendation. No new infrastructure, calendar recurrence or unrestricted arithmetic.
- Preserved bounded computation policy is R5.111:
  `R5_111_TYPED_COMPUTATION_IMPLEMENTED_KERNEL_EXTENDED`. Read
  `docs/typed-computation-v1.md` and `benchmark/results/phase5c/R5_111-REPORT.md`
  before extension. Signed-64 integers/cardinality bindings, checked addition and
  typed fixed-second UTC displacement execute through normal related/atomic profiles.
  Explicit graphs have at most 16 nodes; no unrestricted expressions. Exact R5.110
  kernel 23 becomes 25: checked integer addition and fixed-duration displacement
  (`offset`). Generic successor/history/atomicity remain compositions. Generic lock
  stays unchanged through fresh transfer: 16 successes B01–B16, B17/B20 disputes,
  B18 primary-history/actor integration and B19 primary numeric/day/successor/actor
  interfaces structural. Stop after R5.111; primary-interface closure is only a
  recommendation. No distributed/calendar recurrence or infrastructure work.
- Preserved bounded atomic-state policy is R5.110:
  `R5_110_ATOMIC_DURABLE_HISTORY_IMPLEMENTED_BY_COMPOSITION`. Read
  `docs/atomic-durable-history-v1.md` and `benchmark/results/phase5c/R5_110-REPORT.md`
  before extension. Ordinary typed durable state + bounded related creations share
  one existing local atomic commit. Explicit occurrence/key query order, shared
  declared clock/ID capabilities and append-only operation restriction compose;
  exact R5.109 kernel 23 stays 23. Generic content remains locked through transfer:
  16 successes B01–B16, B17/B20 disputes, B18 structural numeric-history/primary-actor
  binding and B19 structural. Numeric sequence generation is not implemented;
  cardinality-value normal binding and arbitrary arithmetic successor are distinct.
  Stop after R5.110; no arithmetic/B19, distributed/external effects or infrastructure work.
- Preserved bounded reference policy is R5.109:
  `R5_109_PERSISTENT_RELATIONSHIPS_IMPLEMENTED_KERNEL_EXTENDED`. Read
  `docs/persistent-references-v1.md` and `benchmark/results/phase5c/R5_109-REPORT.md`
  before extending it. Exact R5.108 baseline 22 is preserved; one explicit finite
  nonempty-path reachability candidate makes 23. References, existence, restriction
  and EXISTS/NONE/ALL compose existing core meanings. Generic lock precedes all
  transfer and stays exact: 16 exposed local successes B01–B16, B17/B20 disputes,
  B18 external-effect BDI and B19 structural remain. Cooperating one-store/one-record
  commit is bounded; no arbitrary multi-record effects, cascade or unrestricted
  recursion. Atomic effect/durable audit composition is a recommendation only.
  Stop after R5.109; no event/arithmetic or infrastructure work is authorized.
- R5.96 current policy: `docs/research-workflow-r5.96.md`. Use compatible current
  tooling and the available AI model; machine/model/OpenCode/runtime/transport
  qualification and protected activation/access grants are not research gates.
  Preserve historical evidence and useful Lykoi architecture. B03 was exposed in
  R5.97: first result DECISION_DISCOVERY_UNSUPPORTED / STRUCTURAL_COVERAGE_FAILURE;
  no authoring or behavioral evaluation reached. Preserve its immutable result;
  later B03 work is post-exposure research. For future held-out access record a
  fresh snapshot; no informed Lykoi changes before the first terminal result.
- R5.101: B01–B20 are an exposed development/transfer/regression corpus and may
  be inspected freely. Their performance is not held-out generalization evidence.
  Current capability matrix/roadmap is diagnostic only; new generalization needs
  a new development-unexposed source. Preserve historical first results.
- R5.102 adds a bounded existing-scalar normal profile; final classification is
  `R5_102_EXISTING_SEMANTICS_NORMAL_PATH_PARTIAL`. Read
  `docs/existing-scalar-normal-path-v1.md` and its round report before extending
  the bridge. B04/B05 local transfer success is exposed regression evidence;
  nineteen cases replay R5.101 captures. Guard/profile/resource-testing seams remain.
- R5.103 rebaselines all twenty cases with fresh typed source captures:
  `R5_103_FRESH_TYPED_CORPUS_REBASELINED`. B01/B04/B05 locally verify; fourteen
  structural, B18 BDI and B17/B20 clarification remain. Read
  `docs/existing-semantic-composition-v1.md` for bounded guard/clock/provider and
  one-state scalar/read-only-query composition. No mutable-value, relationship or
  atomic-effect family was added. R5.104 is only a recommendation; preserve history.
- R5.104 adds `typed-mutable-values-1` through the normal compiler dispatcher,
  not historical v0.3 serialization. Read `docs/typed-mutable-values-v1.md` and
  `benchmark/results/phase5c/R5_104-REPORT.md` before extending it. Its verified
  generic lock precedes exposed transfer: six local successes B01/B02/B03/B04/
  B05/B10, eleven structural, B18 BDI and B17/B20 clarification. B06 conditional
  raw-empty validation and B07 literal collection/required-CLI-input seams remain.
  R5.103 is the preserved pre-R5.104 baseline; no held-out/cumulative claim.
  R5.105 closure is only a recommendation. Stop after R5.104.
- R5.105 closes the bounded input/value profile:
  `R5_105_TYPED_VALUE_INPUT_PROFILE_CLOSED`. Read `docs/typed-input-values-v1.md`
  and `benchmark/results/phase5c/R5_105-REPORT.md` before extension. Final generic
  lock 2 preceded all transfer outcomes and remained unchanged. Eight exposed
  local successes B01–B07/B10; nine structural, B18 BDI, B17/B20 clarification.
  R5.104 is preserved. Predicate/guard composition is only a recommendation;
  no new major family or infrastructure work is authorized. Stop after R5.105.
- `air/task_manager.json` is canonical; `src/air_compiler/` validates and
  generates the Python backend. R5.106 current bounded predicate policy is
  `R5_106_TYPED_PREDICATE_GUARD_COMPOSITION_IMPLEMENTED`; read
  `docs/typed-predicates-v1.md` and `benchmark/results/phase5c/R5_106-REPORT.md`
  before extension. Queries/guards/local staged validation share typed trees;
  boolean literal creation/input replacement/migration is integrated. Generic
  lock precedes all transfer and stays fixed. Eight exposed local successes
  B01–B07/B10 remain; eight structural, B18 BDI, B17/B20 clarification and B12
  invalid typed candidate/resource binding at formalization. No new stage progress.
  R5.105 is preserved. Literal-write/listing/query-precondition/error/clock-binding
  closure is only a recommendation for R5.107. Stop after R5.106.
- `air/task_manager.json` is canonical; `src/air_compiler/` validates and
  generates the Python backend. Never hand-edit `generated/`. Current model
  normal interface policy is `R5_107_PREDICATE_VALUE_INTERFACE_CLOSED`; read
  `docs/predicate-value-interfaces-v1.md` and `benchmark/results/phase5c/R5_107-REPORT.md`
  before extension. Final generic lock 3 predates all transfer and stays fixed:
  13 exposed local successes B01–B13, four structural, B18 external-effect BDI,
  B17/B20 disputes. Preserve R5.106 and all three pre-transfer R5.107 locks. One
  frozen guidance trailing space is a recorded formatting defect; no post-outcome
  implementation repair. Relationships/cross-entity integrity is only a recommendation.
  Stop after R5.107; no new major family or infrastructure work authorized.
  Current compatibility model
  semantics: `docs/axiom-v0.3.md` and `schema/axiom-v0.3.schema.json`; the
  validator also enforces rules beyond JSON Schema.
- Python 3.10+, no third-party dependencies. From the repo root in PowerShell:
  ```powershell
  $env:PYTHONPATH='src'
  python -m air_compiler.cli validate air/task_manager.json
  python -m air_compiler.cli safety air/task_manager.json
  python -m unittest discover -s tests -p test_compiler.py -v
  python -m unittest discover -s tests -p test_application.py -v
  python -m unittest discover -s benchmark/harness -p test_baseline.py -v
  ```
  Focus a test with `python -m unittest discover -s tests -p test_compiler.py -v`
  (or `-s benchmark/harness -p test_baseline.py`). Regenerate intentional model
  changes with `python -m air_compiler.cli generate air/task_manager.json generated/task_manager.py`;
  compiler tests compare generated output and manifest against the model.
- `inspect`, `diff`, `impact` in the CLI trace stable semantic IDs. Historical
  `experiments/` plans are hash-pinned: do not reapply them to the current model.

## Research and benchmark boundaries

- Seek general, composable semantics, not primitives fitted to a task-manager
  request or external acceptance test. A new semantic concept needs validator,
  backend, versioned language documentation and relevant tests. Validation or
  passing tests alone do not prove behavior or generality.
- `benchmark/conventional/` is the independent Python track; `benchmark/harness/`
  is an external subprocess oracle. Before benchmark work read `benchmark/README.md`,
  the applicable frozen requirement, protocol and checkpoint in
  `benchmark/results/`. Compare observable behavior, not source similarity.
  Preserve frozen compiler/runtime/schema, requirements, oracles and historical
  evidence. Record real capability gaps separately from implementation failures
  and requests actually blocked by a gap; put corrections in independently
  versioned prospective records.
- R5.2.2 is the authoritative corrected post-B16 boundary. Exhaustive R5.3
  reconstruction has stopped as a B17 gate; preserve its unfinished evidence.
  The prospective R5.4 semantic-requirement prototype does not authorize B17
  exposure or a new freeze; see the bounded-bridge decision in `benchmark/results/phase5c/`.
- Document new observations/limitations in `docs/research-log.md`, tradeoffs in
  `docs/decisions.md`, semantics in the versioned spec, and benchmark findings
  beside evidence in `benchmark/results/`. Update `docs/project-overview.md`
  when direction or boundary changes; distinguish observations from proposals.
