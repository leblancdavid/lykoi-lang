# R5.105 — Typed value and input profile closure

**Final classification: `R5_105_TYPED_VALUE_INPUT_PROFILE_CLOSED`.**

The bounded input/value family traverses the normal source → captured typed FRC
→ source inventory/reconciliation → synthetic owner seal → structural coverage
→ BDI/adequacy → faithful normal V1 → restricted author → deterministic normal
compiler → external application behavior path. **348/348 current tests pass**,
plus canonical model validation/safety. Four public synthetic domains publish
**132 external invocations**. Frozen twenty-case transfer has **8 behavioral
successes / 9 structural / 1 BDI / 2 clarification**, with **178 external
invocations** across successful local cases.

R5.104 remains the preserved baseline. Its generic evidence, transfer results,
historical records and B03's immutable first result are unchanged. B01–B20 are
exposed development/regression data: these are requirement-local successes,
not cumulative Phase 5C achievement or held-out generalization.

## Deliverables and reproduction

| Deliverable | Implementation/evidence |
| --- | --- |
| Typed input/value closure, literals, stages, presence, parameters, binding and missing behavior | [Versioned specification](../../../docs/typed-input-values-v1.md) |
| Literal collection creation and explicit stage/condition validation | `src/air_compiler/mutable_values.py` |
| Semantic parameter/type/presence and separate external binding checks | `src/air_compiler/input_values.py` |
| Closed normal typed FRC producer vocabulary | `src/lykoi_workspace/mutable_schema.py`, normal formalizer guidance |
| Reconciliation, structural facets/coverage, BDI/adequacy and faithful V1 | `src/lykoi_pipeline/mutable_profile.py`, existing workspace/contracts engines |
| Deterministic lowering, declared missing-input translation, atomic persistence | Normal compiler dispatcher and `src/air_compiler/mutable_runtime.py` |
| Public article/contact/product/profile source captures and preauthor external plans | `src/lykoi_workspace/input_corpus.py` |
| Literal/input/default, authority, stage/presence, binding, V1, persistence and external challenges | `tests/test_input_values.py` (8 tests, multiple material subcases per test), existing 340 regressions |
| Passing final generic checks | `R5_105-GENERIC-FINAL-VERIFICATION.json` |
| Full public-domain normal pipeline/external audit | `R5_105-SYNTHETIC-FINAL-EVIDENCE.json` |
| Final pre-transfer implementation/spec/test/history lock | `R5_105-GENERIC-LOCK-2.json` |
| Fixed twenty captures and plans | `R5_105-B01-CANDIDATE.json` through `R5_105-B20-CANDIDATE.json`, `R5_105-CORPUS-LOCK.json` |
| Full native-stage/external transfer evidence | `R5_105-TRANSFER-EVIDENCE.json` |
| Baseline blockers, newly reached stages and actual behavioral results | [Matrix](R5_105-CAPABILITY-MATRIX.md), `R5_105-COMPARISON.json` |
| Final preservation/whitespace/scope audit | `R5_105-FINAL-AUDIT.json` |

Scripts publish exclusively and refuse overwriting evidence. From PowerShell:

```powershell
$env:PYTHONPATH='src;.'
python benchmark/results/phase5c/R5_105-verify.py RECHECK
```

Generic and transfer publication require unused output names/a disposable output
location. The transfer script checks final lock 2 before and after execution and
fixes every capture/plan before the first outcome. Every source bundle is freshly
read from frozen sources; unchanged demand shapes retain their still-current typed
interpretation rather than invent support for excluded families. This is captured
current-system evaluation, not a fresh live language-model English parsing study.

## General semantics implemented

* **Literals:** scalar constants retain existing semantics. Collections now have
  explicit literal source/value, including empty/nonempty typed ordered arrays,
  independently of input and omission defaults. Literal creation adds no invented
  input flag. Nonempty duplicate-permitted literals retain duplicates/order;
  unique-policy invalid literals refuse.
* **Required collection input:** a separate source=input creation declaration
  requires supplied typed data and has no omission default. Supplied `[]` is
  accepted as a value; omission triggers the declared error.
* **Stages:** RAW preserves the adapter-decoded original input; TRANSFORMED
  observes the pipeline point; PERSISTED observes the final proposed value before
  atomic commit, with no later transformations. Append pipelines observe incoming
  elements, not a fabricated persisted collection; full candidate typing remains
  checked before commit.
* **Conditions:** one explicit presence/empty/nonempty/whitespace predicate with
  a declared observation stage activates validation. Raw whitespace is not raw
  empty. No trimming or arbitrary boolean programming is inferred.
* **Presence:** input-map membership distinguishes omitted, empty string,
  whitespace, empty collection and existing permitted timestamp API null. Omitted
  optional writes skip pipelines; an all-omitted update avoids writing bytes.
* **Parameters/bindings:** operation identity, logical parameter, exact type and
  required/optional presence are distinct from flag/encoding. Explicit destinations
  bind different flag spellings faithfully. Every creation/mutation input needs
  exactly one declaration; constants cannot be substituted as parameters.
* **Missing behavior:** declared application_error emits its exact JSON error,
  exit 1, empty stdout. Declared cli_rejection explicitly emits exit 2 and the
  versioned adapter diagnostic, without inferring an application error identity
  or relying on parser required defaults. CLI-only required mutation rejection
  carries null missing_error; API omission raises MissingExternalInput.

The current external adapter is CLI flags with text/JSON/repeated encodings, not
a new CLI syntax primitive in the core value algebra. Historical scalar model,
legacy generator/runtime/schema and canonical generated files remain preserved.

## Authority and integration challenges

Reconciliation rejects independently changed candidate facts for invented
literal contents, trim, required parameter, missing error, RAW observation and
wrong binding. Same-agent source-side inventory interpretations remain the
evidence boundary; exact typed agreement alone does not prove authority truth.

Closed structural validation rejects missing bindings, nonexistent/wrong
parameter identities, duplicate/conflicting bindings, wrong type/encoding,
constant substitution, optional→required changes, absent required missing behavior,
implicit stage and transformations after PERSISTED observation. Missing selected
input_contracts fails complete coverage. Full source relations and derived
CreationValueSource, SemanticParameters, ExternalBinding, MissingInputBehavior,
InputValueStages and existing mutation/pipeline/validation/effect facets survive
projection; removing facets fails coverage recomputation.

Generic BDI decisions cover value source, presence, missing behavior and binding,
retaining full ordered stage/condition pipeline decisions. Removing determined
authority makes adequacy IMPLEMENTATION_UNDERSPECIFIED. Faithful V1 corruption
tests detect literal contents, literal/default source, stage, condition, required
status, external binding and missing error changes. No structured relation bypasses
reconciliation or grants implementation permission.

## Synthetic and external behavior

| Domain | Published external invocations | Distinct creation behavior |
| --- | ---: | --- |
| Article labels | 34 | Literal empty collection, no creation label input |
| Contact aliases | 35 | Required JSON aliases through separately named --alias-data; missing_aliases on omission |
| Product keywords | 32 | Literal ordered `['Seed','A','Seed']`, duplicate preservation and later exact membership query |
| Profile interests | 31 | Literal empty collection, optional scalar presence updates |
| **Total** | **132** | All four execute the complete normal pipeline |

Every domain also has literal enum category=public (not a default), required
nickname with declared application error, optional description creation default,
RAW-empty-before-trim versus trim-before-TRANSFORMED-empty updates, supplied/omitted
optional nickname, conditional RAW-nonempty validation, PERSISTED typed check,
atomic multi-field updates, separate-process reload and same-store query/lifecycle
composition. Additional process/API tests cover required supplied empty arrays,
wrong/null input, incorrect external flags, explicit CLI-only rejection, RAW
observation after trim, whitespace predicates, existing nullable timestamp and
later-field/persistence failure preserving prior bytes and temporary-file cleanup.
These supplemental tests are in the 348-test denominator, not extra published
CLI invocations in the 132-domain total.

### Development corrections and lock chronology

An initial focused run exceeded its 120-second shell allowance; the rerun with a
larger command timeout completed and caught a mistaken test expectation: whitespace
predicate activation does not make raw whitespace fail nonempty validation unless
validation observes the trimmed value. The oracle was corrected before verification.
This was test development, not benchmark-driven implementation.

Initial complete generic verification and 132-invocation audit produced lock 1.
A **pre-transfer binding audit**, before any transfer execution/outcome, identified
the distinction between CLI-only rejection and application missing-error identity.
The generic null missing_error / MissingExternalInput path was added and challenged
on public inputs. Full verification again passed 348 tests, then a new full public
audit and **lock 2** superseded lock 1 prospectively. Initial verification/audit/lock
remain preserved. Only lock 2 governs transfer. No implementation, specification or
test change followed any transfer outcome.

## Frozen exposed transfer

| First result | Preserved R5.104 | R5.105 |
| --- | ---: | ---: |
| Behavioral success | 6 | **8** |
| Structural | 11 | **9** |
| BDI | 1 | **1** |
| Formalization/clarification | 2 | **2** |

Successes: **B01/B02/B03/B04/B05/B06/B07/B10**. B06 and B07 newly pass structure
and reach BDI, adequacy, representation, authoring, compilation, runtime and
external behavioral verification. Their **28 and 29** external invocations add
57 to the preserved six-case 121, yielding **178** transfer invocations.

* **B06 succeeds:** omission and supplied raw empty produce empty category;
  supplied nonempty values trim; raw whitespace/tab reject invalid_category
  unchanged. Exact case-sensitive category selection, including empty and
  completed records, baseline operations and migrations pass.
* **B07 succeeds:** literal notes=[] on creation with no create-notes parameter;
  explicit old-record migration; required text CLI binding without invented
  application missing-text error; trim/blank validation; ordered repeated appends,
  lookup failure, rejection bytes, reload and independent lifecycle all pass.

Remaining structural cases: **B08/B09/B11/B12/B13/B14/B15/B16/B19**. Their
writable-boolean/archive, compound/range/in-set predicates, relationships,
multi-entity existence and atomic successor/effect/arithmetic demands remain
unsupported. **B18** remains UNSUPPORTED_BDI_SCOPE for its external-effect channel.
**B17/B20** remain DISPUTED at clarification; no old-user migration role or missing
member error is invented. Downstream unexecuted stages remain NOT_REACHED.

## Limits, recommendation and stop

Normal integration is implemented **within this bounded profile**. Source capture,
inventory, source review and literal oracles share the active agent; ModelAdapter
replays them and owners/reviewers are synthetic. External processes verify software
behavior, not independent cognition, live formalization accuracy or broad generality.
Only existing timestamp nullability and single-record/store atomic writes are claimed.

The next highest-leverage major project is **typed predicate/guard composition**,
with the remaining writable-boolean/archive prerequisite explicitly accounted for.
It addresses the early B08/B09/B11/B12/B13 cluster before persistent relationships
and atomic effects. This is a recommendation only. No new predicate family,
relationships/graph/events/successors/arithmetic/joins/aggregates/pagination,
runtime/tool/model/firewall infrastructure, or benchmark-specific product behavior
was introduced. **Stop after R5.105 closure and corpus transfer.**

## Completion answers

1. Yes: literal empty/nonempty collections differ from omission, defaults and input.
2. Yes: RAW, TRANSFORMED and PERSISTED are explicit as specified above.
3. Yes: validation targets the stated stage, including preserved RAW after trim.
4. Yes: bounded input-state predicates conditionally activate validation.
5. Yes: semantic parameters/types/presence are distinct from external flag bindings.
6. Yes: application errors and CLI-only rejection are declared, not parser defaults.
7. Yes: candidate writes remain atomic; rejection/persistence failure preserves bytes.
8. Yes: persistence/reload and subsequent unchanged CollectionQuery behavior pass.
9. **Eight** local exposed cases succeed behaviorally.
10. **B06 succeeds**, newly reaching all downstream stages.
11. **B07 succeeds**, newly reaching all downstream stages.
12. **8 success / 9 structural / 1 BDI / 2 clarification**, no other first blockers.
13. Typed predicate/guard composition, with writable-boolean/archive prerequisites.
14. Yes: B17/B20 remain ambiguous and clarification-blocked.
15. No benchmark identifiers, application-specific dispatch or benchmark-specific
    behavior were added to product semantics/runtime.
16. Infrastructure work was avoided.
