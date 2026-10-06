# Sealed authoring and independent verification — R5.88

`src/lykoi_pipeline/` implements **sealed-pipeline-1**, a prospective extension of
the unchanged R5.86 controller. The R5.87 workspace uses its existing API to seal
WHAT. The new service consumes that exact seal, including its approval, source,
clarification and policy dependency closure. It never recovers authority from a
transcript, filename or author assumption. Requirements-recovery provenance remains
compatible; this round implements no recovery.

## Interfaces and authority

- `PipelineController(path, principals, verification_fixtures=..., author_fixture=...)`:
  trusted service configuration. Fixture registries are canonical, content-pinned
  and immutable across SQLite restart. They are never author inputs or author APIs.
- `Pipeline.prepare(seal, run, review_rationale=...)`: structural adapter, item
  coverage, separate reviewer evidence, unchanged R5.82 BDI, unchanged R5.81
  adequacy, faithful unchanged-V1 adapter, verifier-role plan production, item/case
  coverage, separate review, controller plan seal, exact manifest and grant.
- `Pipeline.execute(prepared)`: exact grant applicability, single-use author
  reservation, fixed restricted worker, registered Lykoi model, existing compiler
  validation/generation, registered exact target, external processes and bound result.
- `Pipeline.audit_run(run)`: find a completed or halted run using persistent
  controller records alone. `audit(result)` returns exact envelopes and journal
  evidence for all used stages, inputs, observations and dispositions.

Native stage validation recomputes the adapters and analysis. `ADEQUATE`, `READY`
or `projection_complete` strings cannot authorize a run. `identity-closure` and
synthetic producer receipts cannot validate native pipeline evidence. Project/role,
dependency coherence, human WHAT approval and dependency invalidation remain R5.86
mechanics. The requirements-only structural disposition retained in R5.87 approval
is historical WHAT evidence; it cannot substitute for the new authoring projection.
Its explicit UNSUPPORTED authoring status is superseded *for this new stage only*
by a separately reviewed projection. Dispute/rejection still blocks applicability.

Structural rows retain every obligation and exact relation, scope, origins,
unsupported items and exclusions. Complete source-selected component context, when
present, is retained as an additional `@component-context` row and exact normative
relation. It is not independently rediscovered by BDI. BDI remains its supported
15-rule inventory, finite reachability and observation limitations; declared unsupported
observations halt. Coverage review is bounded evidence, not a semantic completeness
proof. Zero discovered supported choices use an explicit INTERNAL inventory record
with unchanged R5.81 relevance semantics, rather than a new decision family.

The V1 adapter has R5.80's existing positive domain: complete explicitly authorized
component context plus `public_state_alternatives` / `durable_content_constraints`.
It assembles current V1 and checks exact recovered relations/context. Other relations
halt `UNREPRESENTABLE_SOURCE / NO_QUALIFIED_COMPLETE_MAPPING`; this is a conservative
adapter representation gap, not proof that V1 is intrinsically incapable.

## Verification preparation and coverage

`plans.produce` is a fixed WHAT-side deterministic fixture producer. It receives
sealed relations, never author output. The verifier role registers the plan; a
separate reviewer commits coverage evidence and verification authority seals it.
Plan dependencies bind exact WHAT, structural receipt, BDI, adequacy, V1 and
component freeze. Missing obligations, unexecutable capability, false exclusions,
missing case references, changed case hashes and false traceability halt.

Separately authored local fixtures may be provisioned by the trusted service,
indexed by exact FRC commitment. This supports deterministic engineering tests
without pretending a general plan generator exists. Registry identity is frozen
before authoring; changes require a new controller database/configuration identity.
An author principal cannot produce, review or seal a plan, or bind verification
authority, even if provisioned with an additional corresponding role.

Plans describe commands, states, expected outputs/absence, return codes, transitions,
invariants, rejection scope and contractual durable-file observations where applicable.
Invariant/rejection descriptions alone are not executed assertions. Actual checks are
the explicit command expectations and optional allowlisted JSON-file observations;
reviewers must assess their adequacy. The calibration engineering fixture has one
positive store/persistence sample; it is not exhaustive context equivalence evidence.
The default producer visibly refuses complete component context it cannot verify.

## Executable two-part freeze

The immutable `freeze` artifact pins controller/adapters, analysis/V1 versions,
compiler/semantic versions, schemas, interpreter executable and available embeddable
runtime libraries, ordinary transitive implementation-import closure and fixture
registry. Hashes use physical bytes: this freeze does not rewrite historical pins.

The run manifest is the immutable `bundle.content.manifest`, with
[`sealed-pipeline-v1.schema.json`](../schema/sealed-pipeline-v1.schema.json).
It binds exact FRC/seal, reviewed projection/receipt, BDI, adequacy, V1, plan seal,
component freeze, run and author-fixture identities. Thus the plan can depend on
already-frozen components, and a later exact manifest can bind its seal without a
cyclic artifact identity. The grant binds this exact bundle and component freeze.
Native validation enforces schema shape and stronger referential/native checks.

Current pins and native dependencies are rechecked before grant, reservation,
author completion, target registration/validation and verification/binding. Manifest,
tool, adapter, fixture, target and plan substitutions cannot keep authorization.
Upstream supersession/invalidation makes old grants inapplicable. Reusing an issued
run ID for another bundle is refused. A changed acceptance plan has a new identity;
it cannot occupy the old manifest or original run's plan-seal dependency.

## Visibility and execution isolation

The author receives exactly `version`, `run`, normalized authorized `v1`, minimal
`toolchain`, and a frozen public author fixture/seed when applicable. It receives no
original human prose, transcript, expected outputs, case selection, reviewer rationale,
rejected interpretation or controller credentials. The current fixture author needs
no prose. Future AI author/provider/prompt identities must be added and frozen before
that adapter can qualify; no AI author runs in R5.88.

The author subprocess has a fresh temporary working directory, empty environment,
isolated CPython flags, fixed entry point and explicit stdin allowlist. Stdout is the
sole output channel; the trusted parent stores the model in the controller's exact
output artifact. A Python audit hook denies normal file, process, network and ctypes
APIs during fixture execution. The hidden-plan file-access challenge is denied.
The author fixture can preserve/reorder the existing model or deliberately produce
wrong/malformed output; it is not a general V1-to-Lykoi synthesizer.

**Isolation class:** local process/role-separated deterministic fixtures with Python
API denial; **no OS sandbox, hostile-native-code containment or model/provider
independence**. Service administrators and SQLite storage remain trusted. Generated
target subprocesses are also not OS sandboxed. These limits are material rehearsal
blockers, not grounds for silently granting wider access.

The verifier receives an exact target, sealed plan and fresh permitted state. It
executes each command in a separate application process, retaining persistence only
within each case. It observes stdout/stderr, exit status and explicitly contractual
allowlisted durable files, never imports internal implementation state. Results bind
target, plan, executed case identities, observations, pass/fail, unexecutable cases
and verifier version. Source identity binds execution, but is never an acceptance
expectation. Failed behavior remains failed even when compilation succeeds.

## Outcomes and public invocation

Distinct outcomes include `STRUCTURAL_COVERAGE_FAILURE`, `UNSUPPORTED_BDI_SCOPE`,
`IMPLEMENTATION_UNDERSPECIFIED`, `UNREPRESENTABLE_SOURCE` (V1 representation gap),
`VERIFICATION_PLAN_COVERAGE_GAP`, `FREEZE_FAILURE`, `GRANT_DENIAL`,
`LYKOI_CAPABILITY_GAP`, `AUTHOR_RESOURCE_DENIED`, `AUTHORING_FAILURE`,
`COMPILATION_FAILURE`, `RUNTIME_FAILURE`, `BEHAVIORAL_VERIFICATION_FAILURE` and
`BEHAVIORALLY_VERIFIED` (executed-plan scope only). Controller-native denial details
are retained, including role, dependency, replay and stale-authority failures.

With Python 3.10+ and repository root / `src` on `sys.path`:

```powershell
$env:PYTHONPATH='src'
python -m lykoi_pipeline.example
python -m unittest discover -s tests -p test_sealed_pipeline.py -v
```

The public R5.87 wizard completes exact WHAT approval/sealing, structural coverage,
BDI and adequacy, then stops at the unchanged V1 mapping boundary. It receives no
grant and performs no authoring. Public calibration fixtures separately exercise
sealed plan → grant → author → build → external failure → persistent bound result.
Two different existing-model declaration forms independently pass the same wizard
behavior plan in a lower-level external-verifier experiment; neither is presented as
an authorized full wizard run through the absent V1 mapping.
