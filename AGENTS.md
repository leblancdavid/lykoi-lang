# Agent guidance for Lykoi

The project is **Lykoi**, not Axiom. Keep historical `axiom`/`air` paths,
serialized keys and pinned records for compatibility; use Lykoi in new prose.
Check `git status` before editing. Read `docs/project-overview.md` for the
current research boundary and `docs/agent-workflow.md` for scope-specific rules.

## Model and verification

- Current bounded reference policy is R5.109:
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
