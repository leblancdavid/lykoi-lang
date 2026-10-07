# R5.109 — Persistent references and cross-entity integrity

**Final classification: `R5_109_PERSISTENT_RELATIONSHIPS_IMPLEMENTED_KERNEL_EXTENDED`.**

The bounded persistent-reference family executes through the normal requirements
and compiler pipeline. Typed references, existence, restrictive deletion and
related-record quantification compose existing meanings. Cycle rejection supplies
the evidence for **one explicitly admitted core candidate: finite nonempty-path
reachability**. The proposed architectural kernel grows **22 → 23**; this is not
a proof of minimality or a claim that every conceptual kernel member has a fully
general shared implementation.

Generic verification passes **372/372 tests** and canonical model validation/safety.
Six synthetic domains publish **182 external CLI invocations**. The frozen exposed
transfer verifies **16/20 requirement-local cases, B01–B16**, across **447 external
invocations**. **B14/B15/B16 newly succeed**, with every downstream stage reached.
B17/B20 remain disputed, B18 halts at external-effect BDI discovery and B19 remains
structurally unsupported. B01–B20 are exposed development/regression data: these
results establish neither held-out generalization nor cumulative historical
benchmark achievement.

## Deliverables

| Deliverable | Location |
| --- | --- |
| Persistent-reference specification and exact pre-round kernel | `docs/persistent-references-v1.md` |
| Typed reference/value model; nominal identity and field binding | `src/air_compiler/references.py` |
| Inspectable existence and reverse restriction lowering | `references.py`: `compose`, typed selection/cardinality checks |
| Related-state guards / explicit namespaces | `references.py`: `validate_condition`, `flat_types` |
| Quantification and finite-domain analyses | Specification: EXISTS/NONE/ALL and finite-domain scope |
| Cycle/composition failure and reachability admission | Specification: cycle pressure and explicit reachability candidate |
| Typed FRC schema / native recursive closed-node validation | `src/lykoi_workspace/reference_schema.py`, `mutable_schema.py` |
| Reconciliation integration | Existing typed relation reconciliation; adversarial `test_references.py` |
| Structural coverage and facet integration | `src/lykoi_pipeline/mutable_profile.py` |
| BDI/adequacy integration | Reference material-choice decisions plus existing adequacy engine |
| Normal V1/profile integration and faithful recovery | Existing normal mutable profile; full reference facts retained |
| Normal compiler/store support | `src/air_compiler/profiles.py`, `reference_runtime.py` |
| Synthetic multi-domain corpus and literal plans | `src/lykoi_workspace/reference_corpus.py` |
| Generic reference, authority, quantification and backend tests | `tests/test_references.py` (11 test methods, multiple adversarial partitions) |
| Published external generic evidence | `R5_109-SYNTHETIC-EVIDENCE.json` |
| Updated kernel accounting | `R5_109-KERNEL-ACCOUNTING.json` |
| Pre-transfer implementation/spec/test lock | `R5_109-GENERIC-LOCK.json` |
| Fixed twenty source captures/plans and corpus lock | `R5_109-Bxx-CANDIDATE.json`, `R5_109-CORPUS-LOCK.json` |
| Individual outcomes and transfer matrix | `R5_109-Bxx-RESULT.json`, `R5_109-TRANSFER-EVIDENCE.json`, `R5_109-COMPARISON.json`, [matrix](R5_109-CAPABILITY-MATRIX.md) |
| Verification and final scope/history/whitespace audit | `R5_109-GENERIC-VERIFICATION.json`, individual `R5_109-CHECK-*`, `R5_109-FINAL-AUDIT.json` |
| Current direction, observations and tradeoffs | Project overview, decisions, research log, workflow, README and AGENTS |

## Composition-first findings

### Identity and persistent reference fields

Reuse the existing identifier domain, adding nominal target metadata under its
typed schema. `User.id` cannot replace `Project.id` in a typed reference input,
comparison, lookup or write. Target authority persists in FRC, structural facts,
normal V1 and generated semantic SPEC while the store carries IDs. Single and
collection references retain existing order/duplicate/equality semantics.

The primary historical adapter retains its qualified scalar/collection backend;
the new reference facet refines its reference fields explicitly. Existing owner
filters retain their source-authorized stored-string query adapter; new reference
write/guard operands use nominal types. A CLI string is interpreted within its
declared parameter domain, not magically distinguished by physical UUID spelling.
Arbitrary caller provenance for an untagged wire string is not claimed.

### Existence, deletion and commit

The compiler publishes `count(select(target.id == candidate_identity)) == 1`
for pointwise reference validation. Reverse restriction publishes selection
equality/membership with count zero. Runtime executes those typed conditions.
Creation, replacement, append/add-unique and stable removal produce a private
candidate; touched references, including same-value replacement, are checked
before one commit. Restrictive deletion sees all remaining referring records;
archived records do not disappear from the reference domain.

Explicit permit is tested separately. It may leave old dangling values after
authorized deletion, but a subsequent source write still must satisfy required
existence. No cascade/cleanup is inferred. A source without target deletion
authority can declare deletion unavailable only when no target-delete effect is
exposed; this does not guess either restrict or permit for a hypothetical command.

The store binds primary and related collections to one coherent file. Cooperating
CLI invocations take one exclusive reservation covering read/check/one-record
mutation/atomic replacement. Reservation refusal and injected replacement failure
preserve bytes. This refines existing atomic commit, not database-level
serializability, distributed atomicity, arbitrary multi-record mutation or crash
recovery. Writers bypassing the adapter and abandoned reservations are outside
the evidence boundary. Related migration uses explicit empty/missing-value repair,
checks every target and preserves nonempty IDs; rejection/create-target/retry passes.

### Quantification and domain scope

EXISTS is cardinality ≥ 1; NONE is cardinality = 0; ALL is NONE of a counterexample
over the declared related domain. Exact N uses the same bounded cardinality
relation. Tests distinguish all empty/mixed/positive domains, ANY versus ALL,
ALL versus NONE, and unrelated records outside membership scope.

The named finite entity source and explicit predicate define the exact domain.
**Finite-domain scope remains a mandatory composition/profile facet, not core #24.**
Selection completeness and reference existence remain distinct obligations.

### The one kernel extension

The inherited kernel has no recursive/fixpoint/transitive-path meaning. A finite
syntactic unroll to depth k cannot reject a cycle through a longer finite chain.
An imposed depth limit changes the contract; a backend-only traversal conceals
the gap; a recursive fold would admit a broader new semantic foundation.

**K23: `reachable(entity, field, source, target, paths: nonempty)`** has exact nominal
endpoints and a declared self-reference projection over finite committed state.
It means existence of a path of at least one edge. Missing endpoints are false;
visited traversal terminates even on cyclic input. Cycle rejection composes
self-equality and reverse reachability before insertion.

Project prerequisite and category parent domains demonstrate the same semantic
operator, including an 81-record chain and cyclic termination. The kernel decision
is supported by explicit multi-domain behavior and the precise absent transitive
relation; it is not fitted to B14 text. No Relationship, ForeignKey, Graph,
Quantifier, join or unrestricted recursive-query primitive is admitted.

## Authority, coverage and normal-path preservation

FRC producer schemas and native validators retain exact target, policies, errors,
bindings, domains, predicates and nonempty-path policy. The recursive producer
validator visits each closed node rather than expanding a recursive schema
exponentially. Reconciliation disputes wrong targets, dropped existence, restrictive
deletion changed to permit, ALL/ANY count changes, altered state predicates,
wrong domains and omitted cycle guards.

Coverage recomputes full IR and typed-field/selection-cardinality/atomic-effect
facets. Normal V1 embeds source contract and facts; recovery detects losses.
Reference BDI decisions and existing tree decisions retain complete material
authority; deleting determined decision authority makes adequacy underspecified.
Missing observable errors and unauthorized cascade refuse instead of receiving
conventional behavior.

The evidence uses same-agent captured source interpretations, inventory and
literal oracles with synthetic owner approvals. External processes verify generated
behavior; they do not establish independent cognition or general live English
formalization accuracy. Correlated source/inventory omissions remain possible.

## Generic evidence and chronology

| Synthetic domain | Published invocations | Representative composition |
| --- | ---: | --- |
| Orders / Customers | 30 | Existing-customer creation and owner replacement |
| Projects / Users | 30 | Ordered unique membership and prerequisite cycles |
| Documents / Owners | 30 | Missing-owner update rejection / reload |
| Departments / Employees / Employment | 32 | Cross-entity reverse restriction |
| Teams / Members | 30 | ALL over explicit member domain |
| Categories / Parent Categories | 30 | Self-reference/cycle composition |
| **Total** | **182** | All six full normal pipelines verified |

The public fixtures also exercise unrelated-field preservation, failed checks,
stale/deleted targets, unique duplicate rejection, idempotent add-unique, stable
removal, empty related scope and independent lifecycle guards. Generic tests add
duplicate-allow collection order, migration/retry, explicit permit, same-value
stale replacement, nominal substitution, authority/coverage/V1 losses, exact
cardinality, long paths and commit/reservation failures.

Two broad verification attempts hit the inherited per-suite 420-second timeout
without producing an aggregate record. The final evidence runner preserves
individual completed receipts bound to the exact source/test-tree digest and
allows longer ordinary test execution; **372 complete passing tests** are counted
once. The earlier partial stdout is not added to that denominator. A focused
migration test initially exposed the absent migrate dispatcher; it was repaired
before the final generic verification. Same-value stale validation and a compact
closed-node schema were also completed before lock. No runtime/model/tool/firewall
infrastructure was changed.

`R5_109-GENERIC-LOCK.json` was published after passing generic tests, six-domain
behavior and kernel accounting and before any transfer outcome. It pins all source,
tests, canonical model, specification and evidence runners, plus historical
results/requirements/generated artifacts. The frozen spec and implementation
remained exact throughout transfer.

The transfer capture builder had two pre-corpus syntax/type-construction failures
(temporary required-input construction and an incomplete audit FRC envelope).
Only the capture builder changed, before any R5.109 terminal result or corpus lock.
The first transfer process hit its shell timeout after preserving B01–B13 receipts;
the unchanged driver resumed exact fixed candidates and completed B14–B20. No
saved candidate, oracle, implementation or test was repaired after an outcome.

## Frozen exposed transfer

| Outcome | R5.107 | R5.109 |
| --- | ---: | ---: |
| Local behavioral success | 13 | **16** |
| Structural halt | 4 | **1** |
| BDI halt | 1 | **1** |
| Clarification/dispute | 2 | **2** |

* **B14:** ordered dependency references, existence including archived targets,
  duplicate/self/cycle rejection, restrictive deletion, migration and unchanged
  rejection execute normally. Prior archive/completion/note/delete guards remain.
* **B15:** dependency membership domain plus NONE of incomplete state implements
  ALL-completed; mixed, empty and archived-completed cases verify. No dependencies
  are rewritten by completion.
* **B16:** nominal users, built-in system, case-sensitive unique/nonblank IDs,
  required existing owner, preserved owner filtering, explicit unowned migration,
  nonempty unknown-owner rejection/create-user/retry and reload verify.

All three pass structural coverage and newly reach BDI, adequacy, V1, restricted
authoring, compilation, runtime and external verification. **No new downstream
failure occurs in these progressed cases.** Remaining downstream capability gaps
are broader atomic effects/durable audit/sequence authority and arithmetic/successor
semantics. Neither family was implemented. B17/B20 still lack migration-role and
unknown-member-error authority; no answer was inferred.

Captures use freshly read frozen source bundles and requirement-local disposable
schema-4 realizations against canonical schema 3. They do not reconstruct the
entire historical migration sequence or claim cumulative B01–B16 achievement.
B16's retry example isolates the pre-reference schema-4 owner-value boundary;
canonical schema-3 additive migration is verified in a separate case. Creating
related records while an arbitrary primary schema is still unreadable remains
outside the currently verified profile, as do broader cross-version entity changes.

## Final answers and stop

1. **Yes.** Typed references compose typed fields, existing identities and target types.
2. **Yes.** Existence uses exact selection/cardinality and precommit validation.
3. **Yes.** Restriction uses reverse equality/membership selection and cardinality zero.
4. **Yes.** EXISTS/NONE/ALL derive from selection, cardinality, predicates and NOT.
5. **No new core needed.** Explicit source and selection predicate define finite scope.
6. **Yes within this kernel.** Unbounded finite-path cycle rejection needs transitive reachability meaning.
7. **Yes.** One proposed core candidate, finite nonempty-path reachability, was admitted.
8. **23**, preserving the exact inherited 22 plus K23.
9. **Yes.** Normal source/FRC/coverage/BDI/adequacy/V1/compiler/backend handles writes, reload and checks.
10. **16/20**, B01–B16, as exposed requirement-local behavioral evidence.
11. **B14/B15/B16 all newly succeed** and reach every downstream stage.
12. **No new progressed-case failures.** Broader atomic effects, audit sequence authority and arithmetic remain gaps; cross-version related-record access is an unqualified store seam.
13. **Yes.** B17/B20 remain disputed with their original unanswered authority.
14. **Yes.** B18 external-effect BDI and B19 arithmetic/successor boundaries remain intact.
15. Recommend **bounded atomic effect composition and durable audit history**, composition-first, with sequence/ordering authority investigated explicitly and recurrence arithmetic deferred. This is a recommendation only.
16. **No benchmark-specific primitive.** Product dispatch is by typed facets/operations.
17. **Yes.** Infrastructure work was avoided.

**Stop after R5.109.** No event/arithmetic implementation or R5.110 work began.
Final whitespace/scope details are recorded separately in `R5_109-FINAL-AUDIT.json`:
introduced-line and new-file whitespace checks pass; one inherited frozen guidance
trailing space remains in the full modified-file scan.
