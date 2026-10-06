# Lykoi

Lykoi is an AI-native semantic representation for software. This experimental
software-development system is designed around AI authorship: an AI maintains a
semantic model of a software system, validates its relationships and contracts,
and generates disposable implementation artifacts. The model, not Python, is
the source of truth. Python is the first backend, not the definition of Lykoi.

Lykoi (pronounced “lie-KOY”) is named after the Lykoi cat breed. Its central
question is: what should software look like when AI, rather than humans, is the
primary programmer? Human intent leads to an AI-authored Lykoi semantic model,
then validation, lowering and generation, and finally an executable system.

For the work to date, current research boundary and long-term goal, see
[`docs/project-overview.md`](docs/project-overview.md). The project is **Lykoi,
not Axiom**; historical `axiom` names are retained only for compatibility and
reproducible research records.

Contributors and AI agents should start with [`AGENTS.md`](AGENTS.md) and the
[agent workflow](docs/agent-workflow.md) before changing the model, compiler or
benchmark.

The [R5.87 requirements workspace](docs/requirements-workspace-r5.87.md) implements
a public synthetic human-intent → clarification → independent source review → exact
approval → controller-sealed requirements lifecycle. With `PYTHONPATH=src`, run
`python -m lykoi_workspace.example` for the wizard transcript or add `--audit` for
exact artifact bindings. This is requirements engineering, not production AI
qualification or an implementation grant.

The [R5.88 sealed authoring/verification pipeline](docs/sealed-authoring-verification-r5.88.md)
adds native analysis/coverage checks, independently presealed acceptance plans,
executable component/run freezes, exact grants, restricted fixture authorship,
deterministic builds and external behavioral verification with restart audit.
`python -m lykoi_pipeline.example` attempts the public wizard's back half and halts
at the existing faithful-V1 adapter gap before authoring. Local fixture isolation
is not an OS sandbox or production AI qualification.

The [R5.89 public rehearsal profile](docs/public-rehearsal-capability-r5.89.md) adds
closed task-title/default mappings, structured HTTPS AI interfaces, independent
WHAT-derived acceptance planning, trusted-target containment and a machine-verifiable
inactive public freeze. `python -m lykoi_rehearsal.freeze check` reports infrastructure
eligibility without inspecting a future requirement. Current status is
`R5_89_PUBLIC_REHEARSAL_BLOCKED_REAL_AI_QUALIFICATION`: live models/calibration and
separate public activation remain. The exact R5.87 wizard still halts before authoring.

The [R5.90 live worker qualification preflight](benchmark/results/phase5c/R5_90-LIVE-AI-WORKER-QUALIFICATION.md)
stops **`R5_90_LIVE_AI_WORKERS_BLOCKED_CREDENTIAL_UNAVAILABLE`**: no service credential
is available and all role models remain unconfigured. Live runs and qualified roles
are zero; infrastructure remains ineligible before future requirement selection.

The [R5.91 live integration](benchmark/results/phase5c/R5_91-LIVE-AI-INTEGRATION-AND-PUBLIC-REHEARSAL-FREEZE.md)
ends **`R5_91_PUBLIC_REHEARSAL_FROZEN`**. Existing OpenCode/GitHub Copilot OAuth now
executes `claude-sonnet-4.6` for all four restricted roles; real smoke evidence is
preserved. **R5.91-PUBLIC-REHEARSAL-2** is active, with mechanical freeze-before-
requirements admission. Model identity is frozen provenance, not semantic authority;
general model qualification is deferred. The [next-round protocol](docs/public-rehearsal-protocol-r5.91.md)
is frozen. No future requirement was selected and no rehearsal was run. R5.90's
historical blocked result, the R5.89 envelope and B03 protection remain intact.

The [R5.94 protected evaluation repair](docs/protected-evaluation-r5.94.md) adds generic
protected provenance, exact opaque-source/run authorization, durable admission and
role-specific access accounting around the existing semantic pipeline. Synthetic
supported/invariance/unsupported challenges pass. A [new generic candidate](benchmark/results/phase5c/r5_94/protected-freeze-candidate.json)
is frozen inactive; no B03 authorization or access occurred. Historical R5.91 machinery
and evidence remain intact. See the [engineering report](benchmark/results/phase5c/R5_94-GENERIC-PROTECTED-EVALUATION-ADMISSION-REPAIR.md)
for checks and trusted-local containment limits.

The [R5.94A runtime contract](docs/python-runtime-contract-v1.md) qualifies Python
behavior independently of exact installation bytes while recording actual runtime
provenance. With `PYTHONPATH=src`, run the chosen interpreter with
`-X utf8 -m lykoi_runtime.verify verify --current`; no global `python` command is
required. CPython 3.14.3 passes. The [engineering report](benchmark/results/phase5c/R5_94A-PORTABLE-RUNTIME-CONTRACT-REPAIR.md)
records an inactive new candidate blocked by inherited file-byte/OpenCode pins,
not Python incompatibility. No protected authorization follows.

The [R5.94B portable freeze](docs/freeze-dependency-classes-v1.md) pins exact canonical
content, qualifies Python/OpenCode through behavioral contracts and records physical
bytes/paths as provenance. **R5.94B-GENERIC-PROTECTED-CANDIDATE-2** initially passed
Python 3.14.3/OpenCode 1.18.32 first/restart and relocated LF/CRLF checks. Later live
OpenCode CLI failures block current machine eligibility; content pins and Python pass.
The configured worker model remains frozen independently. See the
[report and preflight command](benchmark/results/phase5c/R5_94B-CROSS-MACHINE-FREEZE-PORTABILITY.md).
The candidate is inactive; no B03 activation, authorization or access follows.

The [R5.94C worker transport contract](docs/ai-worker-transport-contract-v1.md) makes
OpenCode an optional implementation of a provider-neutral isolated-worker interface.
With `PYTHONPATH=src`, `python -X utf8 -m lykoi_transport.verify verify --implementation
opencode --executable <selected executable>` performs bounded public/synthetic checks.
The frozen Copilot/Sonnet model and all 137 inherited content pins remain unchanged.
Current status is **`R5_94C_BLOCKED_NO_FUNCTIONING_TRANSPORT_FOR_FROZEN_MODEL`**:
all eight first/fresh-process role attempts fail explicitly; final nontransport checks
pass, but no successor freeze or B03 authority is created. See the
[engineering report](benchmark/results/phase5c/R5_94C-PROVIDER-NEUTRAL-AI-WORKER-TRANSPORT.md).

The task application lives in [`air/task_manager.json`](air/task_manager.json)
(the `air/` path and `air_compiler` import path are retained for compatibility).
The current v0.3 model is documented in [`docs/axiom-v0.3.md`](docs/axiom-v0.3.md),
its JSON envelope in [`schema/axiom-v0.3.schema.json`](schema/axiom-v0.3.schema.json),
and the experiment in [`docs/research-log.md`](docs/research-log.md).
The historical v0.1 semantics are preserved in [`docs/air-v0.1.md`](docs/air-v0.1.md).
Existing `air/`, `air_compiler`, `axiom_version`, and schema paths remain stable
compatibility interfaces for saved models and research artifacts.

Phase 5's comparative-maintenance setup, conventional Python baseline,
external behavioral oracle, twenty sequential requests and execution records
are in [`benchmark/`](benchmark/README.md). The benchmark is in progress:
post-B16 histories have been revalidated against the corrected oracle, while
R5.3 acceptance reconstruction remains unfrozen and B17 is unexposed.

Python 3.10+; no third-party dependencies. In PowerShell from the repository root:

```powershell
$env:PYTHONPATH='src'
python -m air_compiler.cli validate air/task_manager.json
python -m air_compiler.cli generate air/task_manager.json generated/task_manager.py
python -m air_compiler.cli inspect air/task_manager.json field_priority
python -m air_compiler.cli diff experiments/task_manager-v0.2-before-priority.json air/task_manager.json
python -m air_compiler.cli impact air/task_manager.json field_due_date --manifest generated/task_manager.manifest.json
python -m air_compiler.cli safety air/task_manager.json
python -m air_compiler.cli plan experiments/phase3-due-dates.plan.json
python -m unittest discover -s tests -v
```

The Phase 3 experiment plan is pinned to the **pre-change** model. After it has
been applied, its baseline hash deliberately prevents reapplication; consult
`experiments/phase3-prechange-impact.json` and
`experiments/phase3-impact-comparison.json` for the saved predictions and
outcome. On a matching baseline, `python -m air_compiler.cli apply PLAN` stages
the model and generated artifact, verifies them and rolls back on failure.

Run the application from a separate working directory: it stores `tasks.json`
in that directory. The generated artifact offers `create --title T --description
D [--priority LOW|NORMAL|HIGH] [--due-date UTC_TIMESTAMP]`, `list`, `list-high`,
`list-overdue`, `complete --id ID`,
`delete --id ID`, and `migrate`. Omitted priority defaults to `NORMAL`. An old
task file must be upgraded with `migrate` before other commands will read it;
this is an explicit, atomic schema migration. Overdue means pending with a
non-null due date strictly before the current UTC time.

**Never edit files under `generated/` directly.** Change the Lykoi model,
validate, regenerate, and verify the behavior. `generated/task_manager.manifest.json`
records provenance and the artifact hash. Changing Lykoi's semantic vocabulary
requires a compiler/backend change, a documented capability gap, and tests.

**Intent may be probabilistic. Program semantics should not be.**

**If the system knows an operation is invalid, it should be impossible for an AI-generated change to silently introduce it. Behaviors should possess the minimum authority necessary to perform their declared semantics.**
