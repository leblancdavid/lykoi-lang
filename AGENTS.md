# Agent guidance for Lykoi

The project is **Lykoi**, not Axiom. Keep historical `axiom`/`air` paths,
serialized keys and pinned records for compatibility; use Lykoi in new prose.
Check `git status` before editing. Read `docs/project-overview.md` for the
current research boundary and `docs/agent-workflow.md` for scope-specific rules.

## Model and verification

- R5.96 current policy: `docs/research-workflow-r5.96.md`. Use compatible current
  tooling and the available AI model; machine/model/OpenCode/runtime/transport
  qualification and protected activation/access grants are not research gates.
  Preserve historical evidence and useful Lykoi architecture. B03 was exposed in
  R5.97: first result DECISION_DISCOVERY_UNSUPPORTED / STRUCTURAL_COVERAGE_FAILURE;
  no authoring or behavioral evaluation reached. Preserve its immutable result;
  later B03 work is post-exposure research. For future held-out access record a
  fresh snapshot; no informed Lykoi changes before the first terminal result.
- `air/task_manager.json` is canonical; `src/air_compiler/` validates and
  generates the Python backend. Never hand-edit `generated/`. Current model
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
