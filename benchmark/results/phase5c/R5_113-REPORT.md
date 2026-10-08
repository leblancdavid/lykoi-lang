# R5.113 — Prewrite authorization and conditional effect composition

**Final classification: `R5_113_AUTHORIZATION_CONDITIONAL_EFFECT_COMPOSITION_PARTIAL`.**

Lykoi composes declared prewrite role/owner/permitted-set permissions, conditional
reference updates and atomic creations, and acyclic created-record image dependencies
using existing core meanings. It binds actor identity from a declared controlled-host
context without treating ordinary actor parameters as authenticated principals.
Nullable integer/instant refinement is explicit. Exact checked elapsed-day conversion
requires proposed **K26**, taking the preserved kernel **25 → 26**; no unrestricted
multiplication, recurrence command or authorization primitive is added.

The admitted CLI compositions traverse normal typed FRC → reconciliation → structural
coverage → BDI → adequacy → faithful V1 → compiler → external subprocess behavior.
Full targeted closure is not claimed: trusted-context **successful** execution is
verified by a separate generated-host subprocess probe after normal V1 lowering,
not the sealed pipeline's existing external-CLI verification artifact. Related
historical field migration is not integrated, and actual historical role authority
cannot be inferred from new-user defaults. These limits warrant partial classification.

Fresh locked exposed transfer retains **16/20 successes B01–B16**, **447 external
invocations**. B17/B20 remain disputed. B18/B19 now stop at **FORMALIZATION / DISPUTED**
on inherited unanswered non-system historical role migration, rather than retaining
R5.112's generic authorization/effect structural diagnosis. Neither gains a downstream
stage or behavioral success. Their diagnostic typed candidates are not sealed,
structurally accepted programs; no counterfactual success after clarification is claimed.

## Deliverables

| Deliverable | Specification / implementation / evidence |
| --- | --- |
| Prewrite permission specification | `docs/prewrite-conditional-composition-v1.md`, declared authority and rejection sections |
| Trusted actor-context model | Same specification; `src/air_compiler/authorization.py`, `authorization_runtime.py` |
| Conditional effects | `references.py`, `reference_runtime.py`, `atomic_state.py`, `atomic_state_runtime.py` |
| Created-image/dependency semantics | Same specification and atomic modules; exact image, entity, field, condition and dependency validation |
| Runtime duration conversion analysis | Specification's 16-node coefficient bound; `computation.py`, `computation_runtime.py` |
| Nullable refinement/presence analysis | Specification; integer/instant refinement, directional nullable-target widening and supplied-input tracking |
| FRC/reconciliation/structural/BDI/adequacy/V1 | `src/lykoi_workspace/authorization_schema.py`, `reference_schema.py`, `atomic_state_schema.py`, `computation_schema.py`, `mutable_schema.py`; `src/lykoi_pipeline/mutable_profile.py` |
| Deterministic normal compiler support | `src/air_compiler/profiles.py`, versioned normal dispatcher; generated artifacts preserved |
| Five-domain synthetic evidence | `src/lykoi_workspace/authorization_corpus.py`, `tests/test_authorization_composition.py`, `R5_113-SYNTHETIC-EVIDENCE.json` |
| Kernel accounting | `R5_113-KERNEL-ACCOUNTING.json`, exact R5.112 accounting hash retained |
| Twenty fresh captures, results, matrix | `R5_113-Bxx-CANDIDATE.json`, `R5_113-Bxx-RESULT.json`, [capability matrix](R5_113-CAPABILITY-MATRIX.md), `R5_113-COMPARISON.json` |
| Verification, content lock and final scope audit | `R5_113-GENERIC-VERIFICATION.json`, `R5_113-CHECK-*.json`, `R5_113-GENERIC-LOCK.json`, `R5_113-CORPUS-LOCK.json`, `R5_113-FINAL-AUDIT.json` |

## Implemented behavior

### Prewrite permissions and trusted context

Nominal actor, authenticated principal, current actor role, target owner, pure permission
predicate and accept/reject decision are distinct. Existing typed equality, membership,
finite selection/cardinality and boolean grouping express permissions. Optional ordered
typed checks give separate existence and permission errors. Guard evaluation observes
the committed before store; creation has explicit creation inputs and no invented target
before image. A creation input inherits a nominal reference target only from its explicit
assignment to a declared reference field. Existing missing-target error precedence remains.

An explicit actor parameter is a source-authorized selector, **not authentication**.
The trusted host adapter takes a separate execution context with an exact declared source
and nominal actor. Conflicting ordinary actor, wrong source, missing context, wrong role
or owner reject. The controlled embedding is the trust boundary; a context dictionary
is not a credential, and arbitrary host-code execution is not isolated. The current CLI
has no trustworthy authentication source and cannot establish one with `--actor`.

Authorization rejection occurs before existing writes. Commit rechecks the permission
and equality of the observed/current/commit-before snapshots. Stale host observation,
permission failure and injected persistence failure preserve durable bytes, with no
primary change, history or successor. This is the inherited cooperating one-store
reservation/replacement frame, not distributed transactions or general host-thread isolation.

Current persisted roles, historical role observations, authorized migration values and
new-entity defaults are not interchangeable. Related parameters may have independently
declared omission defaults; supplied invalid values do not trigger them. Original input
presence remains separate from default-bound values. Missing historical role fields
reject reload; a new-operator default does not repair them. No B17 migration role is guessed.

### Conditional atomic effects and images

Existing reference update assignments may have a typed pre-state `when`. Named ordinary
creations use typed `when`, complete bindings and exact dependencies. All conditions
observe the coherent operation-before store/target/inputs. Selected effects commit
together; unselected assignments preserve their fields and unselected creations do not
appear. Local creation computations execute only for selected effects. Operation-level
graphs and declared resource observations remain operation-level, not implicit branches.

Before target, proposed primary after, named newly created secondary and committed post
store are distinct. Created operands declare producer effect, entity, field and nominal
type. The dependency graph rejects wrong/missing/ambiguous images, self-reference and
cycles. A forward reference is supported: build order follows dependencies, while durable
occurrence order remains declaration order. A conditional producer must be unconditional,
have the consumer's exact condition, or provide an explicit typed literal alternative.
General predicate implication proving and arbitrary branching remain outside the profile.

Independent UUID observations use explicitly named `observation: binding` resources;
each samples once. Operation-shared resources retain one capability observation, and
clocks remain shared. This closes a binding seam for two fresh secondary identities
without relying on backend resampling or adding an identity primitive. Duplicate,
payload, graph, integrity, stale-state and persistence failures discard the candidate.

### Duration and nullable refinement

`refine_integer` and `refine_instant` require explicit null rejection or a separately
authorized typed literal fallback. Absent, null, valid value, invalid value and fallback
are distinct. No implicit null-to-zero rule or due-date invention is admitted. A
nonnull computed value may populate the identical nullable target domain; reverse
narrowing, cross-entity identity substitution and unit mismatch still reject.

`days_to_seconds` defines the exact checked relation `seconds = N × 86400` from signed-64
elapsed days to signed-64 elapsed seconds. Negative/zero values are preserved; a positive
application interval needs a separate typed guard. Overflow rejects before any durable
effect. K25 performs the UTC instant displacement with its existing canonical UTC and
year bounds. Synthetic leap-day, negative displacement, null instant and upper-year
failure cases are externally observed. No calendar month/year or arbitrary arithmetic.

Composition-first analysis does not justify claiming constant kernel size. In 16
addition nodes the coefficient of arbitrary runtime N can reach at most 65536, less
than 86400. Constants do not increase the coefficient, finite literal durations do not
cover runtime signed-64 N, and K25 requires duration dimension. Exact dimensioned scale
is newly admitted mathematical meaning, explicitly validated/lowered/documented as K26.

## Normal authority-path verification

Closed producer shapes preserve actor source, exact permission/error/observation, effect
condition, created image/dependency, conversion and null policy. Reconciliation mutation
tests detect wrong actor source, changed owner predicate, omitted guard, changed error,
changed condition, wrong image, changed scale and invented zero fallback. Structural
coverage and faithful V1 reject altered facts; exact dependency/type/cycle/unselected
checks remain mandatory. BDI retains permission, scope, selection, dependency, conversion
and refinement decisions; removing authority fails adequacy. No benchmark ID dispatch.

**393 passing tests**, canonical model validation and safety. All inherited R5.112
commands run on the final source tree. Four new tests cover full generic pipelines,
source reconciliation/structural/BDI/adequacy/V1 mutation, controlled host failures,
signed conversion boundaries, literal fallback, absence after default binding and an
explicit alternative to an unselected created image. Compiler/generated-manifest,
application, persistence/reference/history/computation/query/value, workspace/controller,
FRC/source coverage, BDI/adequacy/V1 and external-baseline regressions pass.

| Synthetic domain | Published normal external invocations |
| --- | ---: |
| Inventory | 28 |
| Document | 29 |
| Account | 30 |
| Renewal | 29 |
| Project | 28 |
| **Total** | **144** |

Partitions include primary creation wrong-role/wrong-owner rejection, current role/owner
and permitted-set scope, trusted-CLI rejection, positive/zero/negative effect selection,
two actor-attributed histories, forward successor-image reference, independent UUIDs,
null/overflow, restart, role-default/missing-historical-role distinction and UTC boundaries.
Additional generated-host probes exercise controlled trusted success, forged actor,
wrong context, wrong role/owner, stale observation and injected `os.replace` failure;
these are separate from the 144 sealed external-CLI invocations. Native tests also
cover exact positive/negative signed-64 conversion edges and authorized literal fallback.

Five domains share a schema shape. Captures, inventories and literal oracles are by
the same agent, with synthetic approval. The evidence is finite development/regression
evidence, not independent cognitive review, held-out generalization or a minimality proof.

## Chronology and preservation

The initial worktree was clean. Pre-lock diagnostics found a creation parameter type
mismatch, a literal-oracle negative-date listing order mismatch, and the controller's
safe-integer artifact range; these were corrected before final verification. The signed-64
overflow fixture uses a safe artifact integer whose scaled result overflows. A focused
test invocation and full verification invocation timed out; completed source-bound
receipts were resumed and counted once in the final verification. One PowerShell driver
invocation had invalid assignment chaining and was corrected before execution.

Final verification, 144 published synthetic invocations and kernel accounting precede
the generic content lock. Twenty fresh source captures/plans were fixed before the first
transfer outcome. All twenty transfer attempts completed. Product, specification, tests,
candidate/oracle and earlier historical bytes remained locked through transfer. Only
prospective report/status documentation and final audit records were added afterwards.
Canonical model, generated files, requirements, harness and historical results are preserved.

## Updated first blockers

| Cases | R5.112 first blocker | R5.113 first blocker | External result / stages |
| --- | --- | --- | --- |
| B01–B16 | Success | Success | All 16 reverified, 447 invocations |
| B17 | Formalization dispute | Formalization dispute | Historical non-system role unanswered |
| B18 | Structural prewrite authorization | Formalization dispute | Generic interfaces implemented; actual inherited role authority unanswered; no downstream stage |
| B19 | Structural authorization / conditional duration-effect-image composition | Formalization dispute | Typed conditional/refinement/conversion/image candidate; inherited role authority unanswered; no downstream stage |
| B20 | Formalization dispute | Formalization dispute | Unknown-member error unanswered |

B18/B19 do not resolve B17's role ambiguity merely by adding audit/recurrence requirements.
Moving their first blocker to the upstream authority gate is not downstream progress or
partial behavioral success. In particular, no source-authorized migration of existing
non-system users is derived from `create-user`'s default. Diagnostic typed candidates
have not passed structural coverage/adequacy/authoring after clarification; that path
remains unverified. The denominator is exposed requirement-local regression, not cumulative
historical Phase 5C achievement.

## Kernel accounting

The exact R5.112 baseline is 25: 23 baseline concepts plus preserved K24 addition and K25
fixed-duration displacement. One smallest typed dimensioned conversion candidate K26 is
admitted, giving **26**. Permissions, trusted binding, conditional membership, dependency
images, nonnull refinement and observation scopes are existing-core compositions/interface
closure. Private snapshots/topological candidate assembly/input presence tracking are
backend implementations of those declared meanings. No Policy, AuthenticatedActor,
Audit, Event, RecurringTask or benchmark-specific command becomes a core primitive.

## Completion answers

1. **Yes**, prewrite role/owner/permitted-set decisions compose typed predicates,
   references, finite selections/cardinality and guards with declared unchanged errors.
2. **Yes within the controlled authorized host boundary**; no authenticated principal
   or trustworthy CLI authentication is inferred from a supplied selector/context name.
3. **Yes under the supported cooperating one-store frame**, including primary creation,
   stale observations and persistence failure; byte-preserving rejection is tested.
4. **Yes**, bounded conditional reference updates and atomic creations execute correctly.
5. **Yes**, named typed created-record field/identity sources follow an exact acyclic
   graph and declared selection/alternative authority, independently of declaration order.
6. **Yes**, exact checked runtime elapsed-day-to-second conversion, not month/year arithmetic.
7. **Explicit refinement** distinguishes absence, null, valid/invalid values and an
   authorized literal fallback; no null-as-zero coercion. Defaults preserve supplied presence.
8. **No: 25 → 26**, solely for explicit K26 dimensioned day-duration conversion.
9. **B18 does not gain downstream stages or succeed**; its first blocker becomes the
   inherited formalization dispute, with diagnostic permission/history candidates retained.
10. **B19 does not gain downstream stages or succeed**; typed effect/image/duration demands
    are captured, but inherited historical role authority stops formalization.
11. **16/20**, B01–B16, 447 fresh exposed external invocations.
12. **Yes**, B17/B20 remain disputed.
13. **Remaining integration seams:** source-authorized historical related-field migration;
    sealed normal trusted-host-success verification binding; source-authorized principal/
    actor mapping if required. Source ambiguity is not a missing arithmetic/authorization
    primitive. General condition implication, arbitrary lifecycle/deletion branching,
    computed legacy creation and distributed/host-thread transaction guarantees remain
    outside the admitted bounded profile. Actual clarified B18/B19 lowering/behavior is
    unverified, so no additional corpus seam is ruled out by synthetic success.
14. **Recommend R5.114 investigate explicit historical related-state evolution and trusted
    execution verification interfaces**, composition-first. Obtain actual role authority
    before authoring B18/B19; never use a creation default as the answer. R5.114 is not begun.
15. **Yes**, benchmark-specific primitives, authentication infrastructure, policy engines,
    unrestricted arithmetic, event buses and benchmark-harness work were avoided.

**Stop after R5.113.** The central question has a bounded positive answer for authorization,
conditional effects and dependent ordinary creation by composition. Exact runtime scaling
adds one documented meaning, and full targeted normal-path closure remains partial.
