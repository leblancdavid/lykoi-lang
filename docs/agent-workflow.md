# Working on Lykoi: agent guide

This guide is project governance for agents working in the repository. Start
with [the project overview](project-overview.md); it describes the research
goal and the current boundary. `AGENTS.md` is the short entry point. For an
experiment, its frozen protocol and evidence govern that experiment; this guide
does not retroactively amend them or authorize a new run.

## Orient before editing

**Current historical-state/verification policy is R5.114:
`R5_114_HISTORICAL_STATE_TRUSTED_VERIFICATION_CLOSED`.** Read the
[versioned interface](historical-state-trusted-verification-v1.md) and
[report](../benchmark/results/phase5c/R5_114-REPORT.md) before extension. Related
enum/role, nominal reference/collection and nullable/computed fields migrate only
with explicit historical sources; creation defaults never authorize history.
Version chains, rejected bytes, idempotence and restart use ordinary one-store
composition. The sealed verifier owns host contexts and external classification;
host actor assertion is not authentication, and CLI flags cannot establish it.
Kernel remains 26; 397 tests, validation/safety and 133 synthetic invocations precede
the generic lock. Fresh transfer retains 16 successes, 447 invocations; B17–B20
remain disputed, B18/B19 downstream NOT_REACHED. Preserve history and all locks;
**stop after R5.114**, no next evaluation or infrastructure begun.

**Preserved authorization/effect policy is R5.113:
`R5_113_AUTHORIZATION_CONDITIONAL_EFFECT_COMPOSITION_PARTIAL`.** Read the
[prewrite/conditional specification](prewrite-conditional-composition-v1.md) and
[report](../benchmark/results/phase5c/R5_113-REPORT.md) before extension. Role/owner/set
guards, trusted controlled-host binding, conditional updates/creations and dependent
created images compose; actors supplied on CLI remain selectors, not authenticated
principals. Exact elapsed-day duration conversion justifies K26, kernel 25 -> 26.
393 tests and 144 synthetic external invocations precede the generic lock. Fresh
transfer retains 16 successes, 447 invocations; B17/B20 disputes remain and B18/B19
now halt on inherited historical-role authority at formalization, no new downstream
stages. Never infer migration roles from creation defaults. Related historical-field
migration and sealed trusted-host-success verification remain seams. Preserve all
earlier records; **stop after R5.113**, with R5.114 only recommended.

**Current prospective research policy is [R5.96](research-workflow-r5.96.md).**
Historical frozen experiments retain their protocols; their infrastructure gates
do not govern ordinary research or the next held-out benchmark. **R5.101 treats
B01–B20 as an exposed development/transfer/regression corpus, freely inspectable
for diagnosis and regression. Their performance cannot establish held-out
generalization; new generalization needs a new development-unexposed source.**
**Preserved primary interface policy is R5.112:
`R5_112_PRIMARY_INTERFACE_COMPOSITION_PARTIAL`.** Read
[primary value interfaces](primary-value-interfaces-v1.md) and its
[report](../benchmark/results/phase5c/R5_112-REPORT.md) before extension. Signed-64/
nullable primary fields, explicit supplied actor context, cardinality history and
unconditional same-primary successors compose through the normal path. Absolute
UTC-day midnight representation is separate from unsupported runtime N-day scaling.
Kernel remains 25; final generic lock stays exact through transfer: 16 successes,
B17/B20 disputes, B18 prewrite authorization and B19 conditional duration/effect/image
bindings structural. No new downstream stages. Stop after R5.112; R5.113 is a
recommendation only. No new infrastructure or unrestricted/calendar arithmetic.

**Preserved bounded computation policy is R5.111:
`R5_111_TYPED_COMPUTATION_IMPLEMENTED_KERNEL_EXTENDED`.** Read
[typed computation](typed-computation-v1.md) and its
[report](../benchmark/results/phase5c/R5_111-REPORT.md) before extension.
Signed-64 integers, cardinality value bindings, checked addition and dimensioned
fixed-second UTC displacement use explicit graphs with at most 16 nodes. Computed
values feed related mutations/predicates/creations under inherited atomicity.
Proposed kernel 23 → 25; successor/history remain compositions. Generic lock is
unchanged through fresh transfer: 16 successes B01–B16, B17/B20 disputes, B18
primary-history/actor and B19 primary numeric/day/successor/actor integration
structural. Stop after R5.111; further primary-interface closure is a recommendation.
No unrestricted expressions, broad calendar recurrence or infrastructure work.

**Preserved bounded atomic-state policy is R5.110:
`R5_110_ATOMIC_DURABLE_HISTORY_IMPLEMENTED_BY_COMPOSITION`.** Read
[atomic durable history](atomic-durable-history-v1.md) and its
[report](../benchmark/results/phase5c/R5_110-REPORT.md) before extension.
Existing primary writes plus 1..8 ordinary typed related creations share one local
atomic frame; explicit occurrence/key order, clock/ID binding and append-only
operation restriction compose existing concepts. Proposed kernel stays exactly 23.
Generic lock is unchanged through fresh exposed transfer: 16 successes B01–B16,
B17/B20 disputed, B18 structural numeric-history/primary-actor binding, B19 structural.
No numeric generation, temporal successor, distributed effects or infrastructure work.
Stop after R5.110; future numeric/cardinality and actor closure work is a recommendation.

**Preserved bounded reference policy is R5.109:
`R5_109_PERSISTENT_RELATIONSHIPS_IMPLEMENTED_KERNEL_EXTENDED`.** Read
[persistent references](persistent-references-v1.md) and its
[report](../benchmark/results/phase5c/R5_109-REPORT.md) before extending the bridge.
Exact R5.108 kernel 22 is preserved; one finite nonempty-path reachability candidate
makes 23. References/existence/restriction/EXISTS/NONE/ALL compose existing meanings.
Generic implementation/spec/tests stay locked through transfer: 16 exposed local
successes B01–B16, B17/B20 disputes, B18 BDI, B19 structural. No arbitrary
multi-record effects, cascade, unrestricted recursive query or infrastructure work.
Stop after R5.109; atomic effect/durable audit work is only a recommendation.

R5.102's bounded existing-scalar profile is **partial**, not full language-path
closure. Its [versioned semantics](existing-scalar-normal-path-v1.md) and
[report](../benchmark/results/phase5c/R5_102-NORMAL-PATH-REPORT.md) distinguish
fresh typed source capture, old-capture regression, existing write algebra,
read-only types and unclosed normal integration seams. Do not infer writable
booleans/integers, arbitrary guards or mixed-profile composition from passing
scalar examples. R5.101 remains the pre-development baseline.

**R5.103's fresh typed baseline supersedes stale-capture measurement, not historical
results.** Read its [report](../benchmark/results/phase5c/R5_103-REPORT.md) and
[bounded composition rules](existing-semantic-composition-v1.md) for current
guard/clock/provider/scalar-query integration. All twenty cases are freshly
evaluated; B01/B04/B05 are local behavioral successes. Writable arrays/booleans,
write transformations, OR/ranges/in-set, relationships and atomic effects remain
gaps. One-state read-only composition is qualified; arbitrary profile union is
not. B17/B20 still require clarification. R5.104's mutable-values recommendation
is prospective, not implemented or authorized by that report.

R5.104's [typed mutable-value profile](typed-mutable-values-v1.md) executes
ordered collections, presence-aware staged transforms and atomic record writes
through the normal path. Read its [report](../benchmark/results/phase5c/R5_104-REPORT.md)
before extension: verified generic content was locked before twenty exposed
attempts; six local successes, eleven structural, B18 BDI and B17/B20 clarification.
Literal collection creation, required CLI binding and raw-empty-sensitive validation
remain profile seams. R5.103 stays the pre-R5.104 baseline; R5.105 is prospective.

R5.105's [input/value closure](typed-input-values-v1.md) and
[report](../benchmark/results/phase5c/R5_105-REPORT.md) supersede the remaining
R5.104 profile seams prospectively: literals, explicit stages/conditions and
semantic parameters separate from CLI bindings now traverse the normal path.
Final generic lock 2 remained fixed throughout transfer: eight local successes
(B01–B07/B10), nine structural, B18 BDI and B17/B20 clarification. Preserve R5.104
evidence and both R5.105 pre-transfer lock histories; stop after R5.105. No new
predicate/relationship/effect family is authorized by that recommendation.

R5.106 is now the explicitly instructed bounded predicate family:
`R5_106_TYPED_PREDICATE_GUARD_COMPOSITION_IMPLEMENTED`. Read
[typed conditions](typed-predicates-v1.md) and its
[report](../benchmark/results/phase5c/R5_106-REPORT.md) before extension. Boolean
storage/migration, typed query trees, prewrite guards and local staged validation
share the pure interpreter. Generic lock and candidate bytes remain fixed through
transfer. Eight local successes remain; eight structural, B18 BDI, B17/B20
clarification and B12 invalid typed clock-reference candidate at formalization.
No newly reached request stage. Preserve R5.105 and interrupted-driver evidence.
Normal predicate/value interface closure is a recommendation, not permission to
begin R5.107. Stop after R5.106.

R5.107's [interface closure](predicate-value-interfaces-v1.md) is now implemented:
`R5_107_PREDICATE_VALUE_INTERFACE_CLOSED`. Read its
[report](../benchmark/results/phase5c/R5_107-REPORT.md) before extension. Literal
replacement, exact-base selection amendments (including existing clock listings),
distinct query validation/preconditions/errors and declared UTC resource operands
compose through the normal path. Final generic lock 3 remains unchanged through
transfer: 13 local successes B01–B13, four structural, B18 external-effect BDI and
B17/B20 disputes. Preserve all three pre-transfer locks and R5.106 evidence. A
single guidance trailing space is a recorded frozen formatting defect. Persistent
relationships/cross-entity integrity is a recommendation only; stop after R5.107.

B03 was exposed in
R5.97 and its first structural-coverage result is immutable; later B03 work is
post-exposure research and requires separate instructions. Never read held-out requirements
merely to orient, select retained architecture or run broad historical tests.

1. Read `AGENTS.md`, `README.md` and `docs/project-overview.md`. Check
   `git status` and inspect relevant local changes before editing; do not
   overwrite another person's in-progress work.
2. Identify the task's scope: application model, language/compiler, research
   documentation, benchmark preparation, frozen track execution, or prospective
   protocol work. Do not carry a change from one scope into another implicitly.
3. Read the governing sources for that scope. Use `docs/axiom-v0.3.md` and
   `schema/axiom-v0.3.schema.json` for current model semantics; earlier versioned
   docs are historical. Use `benchmark/README.md`, the applicable frozen
   requirement, and the relevant `benchmark/results/` protocol and checkpoint
   for benchmark work. An overview cannot replace a versioned freeze record.
4. State whether a claim is implemented behavior, an observation, a design
   proposal or an unverified hypothesis. Keep evidence and denominators with
   empirical claims. Passing validation or tests does not prove generality,
   safety, semantic equivalence or a comparative advantage.

## Repository map and normal development

| Location | Role |
| --- | --- |
| `air/task_manager.json` | Canonical Lykoi task-manager model; `air` is a compatibility path. |
| `schema/`, `src/air_compiler/` | Serialized shapes, validator, semantic tooling and current Python backend. Changing semantic vocabulary requires general semantics, validation, backend work, documentation and relevant tests. |
| `generated/` | Disposable generated implementation and manifest. Regenerate from the model; never hand-edit. |
| `tests/` | Language/compiler and application tests. |
| `docs/` and `experiments/` | Versioned semantics, decisions, research observations and pinned earlier experiments. Do not reapply a stale hash-pinned plan to a newer model. |
| `benchmark/requirements/`, `benchmark/harness/`, `benchmark/results/` | Frozen requests, external oracle/tooling, and versioned protocols, checkpoints and evidence. Do not treat the root model as a benchmark track's live workspace. |

From the repository root, for **ordinary non-frozen** model/compiler work with
Python 3.10+ (PowerShell):

```powershell
$env:PYTHONPATH='src'
python -m air_compiler.cli validate air/task_manager.json
python -m air_compiler.cli safety air/task_manager.json
python -m unittest discover -s tests -p test_compiler.py -v
python -m unittest discover -s tests -p test_application.py -v
python -m unittest discover -s benchmark/harness -p test_baseline.py -v
```

Use `inspect`, `diff` and `impact` to trace semantic IDs before editing. If the
model is intentionally changed, regenerate normally and verify the generated
artifact and manifest; use a temporary copy when checking a proposed change
that should not modify the repository. Run checks relevant to the change, and
record what actually ran. The commands above are development checks, **not**
the checkpoint restore, external-suite and freeze gates of a benchmark
amendment. Do not run `apply` on an old experiment plan: its pinned baseline is
expected to reject reapplication.

## Language design and research discipline

The research question is whether a small general-purpose semantic vocabulary
can compose complex software reliably. Prefer typed, explicit, reusable
primitives and their composition to a new operation for each application
feature. Before proposing an extension, identify the precise expressiveness
gap, examples beyond the triggering requirement, interactions with existing
semantics, validator/runtime obligations, migration/compatibility costs, and a
way to challenge generality with unseen problems. Do not imitate a host
language's syntax simply to make authoring familiar. A bounded current
implementation does not establish that the eventual language is general.

Move correctness into language semantics, constraints, compiler/runtime
guarantees and validated external-capability adapters where feasible. Keep the
core semantic model separate from integration details such as storage, clocks,
IDs and other external services. Additional adapters are a direction to
investigate, not a claim that today's backend enforces isolation or provides
formal proof. Tests are essential for the language, compiler/runtime,
adapters, intent interpretation and independent evaluation; they are not the
semantic target for generated application behavior.

## Benchmark firewall

For new research, use the R5.96 first-result protocol: current compatible tooling
and available model; fresh commit/tree/tests/core/V1/model/time/held-out snapshot;
mark first access as exposure; formalize and attempt existing-capability authoring
and independent verification; record the first terminal result before any informed
Lykoi development. No infrastructure qualification or protected activation is
required. Product controller handoffs remain useful, not benchmark-access authority.
The Phase 5C instructions below retain their historical comparative-run scope.

Phase 5C compares Conventional source maintenance with a **frozen** Lykoi
capability set on cumulative B01–B20 requests. Observable satisfaction of the
frozen requirement is the criterion, not identical code, names, algorithms or
representation. Derive implementation from the requirement and permitted
context; independently verify with external acceptance tests. Do not use
hidden oracle details to drive implementation unless the governing protocol
explicitly allows them. Do not rewrite a requirement, test, frozen tool,
checkpoint or old classification to improve an outcome.

During a frozen track run, do not extend Lykoi's compiler, schema or runtime to
pass a newly encountered request. Record an evidenced capability gap when the
frozen semantic vocabulary cannot express it (historical records call this
`AXIOM_CAPABILITY_GAP`; newer conventions may say `LYKOI_CAPABILITY_GAP`).
Distinguish this from a failed implementation within the existing vocabulary.
Use `BLOCKED_BY_GAP` only when the later request actually depends on the
missing prerequisite; an earlier gap alone does not block every later task.
Preserve the achieved history and report applicable external checks, skips and
regressions separately. Protocol defects are not language capability defects.
Benchmark agents must follow the frozen track instructions and isolation
rules; this repository-wide context is not permission to disclose the other
track's solution or hidden acceptance details inside an isolated run.

The authoritative corrected post-B16 acceptance boundary is R5.2.2. Exhaustive
R5.3 reconstruction has stopped as the gate for B17–B20; its unfinished evidence
is preserved, not a frozen equivalence proof. The R5.4 bounded-bridge decision
authorizes prototype work, not B17 exposure or an acceptance freeze. Follow
the current boundary in
`docs/project-overview.md` and the versioned records under
`benchmark/results/phase5c/` before touching this area. Preserve frozen
inputs and historical results. Record corrections as prospective, separately
versioned evidence, with provenance and independent checks before any claimed
freeze. Governance edits do not advance the benchmark.
The prospective B17 dependency adjudication retains request-level
classification through B20: when B16 is missing and B17 completion needs it,
use `BLOCKED_BY_GAP -> B16`. Independently observed B17 clauses belong in
separate disposable-state diagnostics, never in achieved history or acceptance
composition; Conventional must satisfy the whole B17 request.

## After a benchmark and keeping this guide current

Once a frozen suite actually completes, collect gaps, group them by semantic
cause, propose the smallest abstractions that address multiple gaps, evolve a
new version separately, rerun the original suite under a controlled protocol
and evaluate on new unseen domains. B01–B20 can remain a stable diagnostic
suite, but repeated success on the same task manager cannot establish
generality. The prospective semantic-requirement prototype is not today's
oracle; B17–B20 semantic-first records need independent verification and a
separately authorized freeze before activation.

Update `AGENTS.md` when entry-point rules change, this guide when work
procedures change, and `docs/project-overview.md` when direction, milestones or
current boundary changes. Put observations and limitations in
`docs/research-log.md`, design tradeoffs in `docs/decisions.md`, and language
semantics in the relevant versioned doc. Benchmark-specific findings belong
beside their evidence under `benchmark/results/`, without editing frozen
history. Check README links and status claims in the same change. A future
agent should be able to tell *what is known, what is proposed, and what remains
unverified* from these documents without assuming passing tests imply proof.
