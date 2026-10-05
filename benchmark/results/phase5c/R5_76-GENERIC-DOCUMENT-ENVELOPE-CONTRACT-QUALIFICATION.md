# R5.76 — Generic document-envelope contract investigation and qualification

## Primary result

**`R5_76_DOCUMENT_ENVELOPE_GAP`**.

No authoritative generic opened-resource → behavioral-contract envelope definition
was identified in the inspected generic protocols. They specify component formats
and consumer arguments, not a versioned document-role, container, reference or
whole-contract assembly protocol. Consequently a schema-aware generic extractor
cannot be independently justified in this round. No generic adapter was installed
and generic qualification is **not complete**. A synthetic container invented here
would not establish what existing benchmark documents generically permit.

Bounded positive evidence: **19/19 diagnostic tests** and four fresh, independently
committed synthetic lifecycles pass. Explicit non-task synthetic inputs reach all
existing static consumers; coherent support PASS, known support failure, malformed
fixture and incomplete fixture outcomes are distinguishable. These results qualify
the explicit fixture path only, not arbitrary benchmark document envelopes.

## Inherited boundary and permanent historical status

R5.75 remains **`R5_75_OBSERVATION_INDETERMINATE`**. Record permanently:

- **`B02_EXPOSED_IN_R5_75`**;
- **`B02_STATIC_RESULT_INDETERMINATE`**.

Its authorization/reservation/opening/dispatch counts remain **1/1/1/1**, protected
attempts/reads **11/11**, completions **0**, and generation/execution/frozen
acceptance/repair **0/0/0/0**. Its incomplete ledger is not reset, completed or
replayed. B02 is no longer unseen or pristine. These historical facts are inherited
from the starting state, not reconstructed by reading captured B02 documents.

R5.76 performs **zero actual-benchmark authorizations, openings or observations**.
Neither B02 protected resources nor R5.75's captured document artifact are read.
No actual ledger is opened or modified. B03 and other untouched requests are not
used as inputs, fixtures, test targets or sources of envelope rules.

## A — Generic authority investigation

Inspected sources, all outside protected B02/B03 contents:

| Source | Actual authority established | What it does not establish |
| --- | --- | --- |
| `benchmark/README.md`, `benchmark/requirements/README.md`, `benchmark/harness/README.md` | Frozen observable requests, cumulative acceptance, external subprocess oracle and provenance discipline | A JSON opened-document envelope schema |
| R5.72 simplified-runner protocol, `phase5_runner_v2.py` | Exact sealed resource-set opening, commitment verification, controller-bound callbacks, one-shot ledger, state/health binding | JSON document roles, payload extraction or complete requirement inventory |
| `docs/nullable-readiness-r5.38.md`, `readiness_r5_41.py` | Whole-application static inspection; explicit externally supplied boundary obligation list; unknown kinds fail closed | How that list is serialized in a benchmark resource |
| `docs/boundary-profile-admission-r5.40.md`, `profile_audit_r5_40.py` | Closed `transport/state/launch` configuration structure, complete input mapping, traceability and contamination checks | Multi-resource contract assembly or obligation-document envelopes |
| `application_boundary_r5_41.py`, `current_pipeline.py` | Application `id/state/operations`, CheckedPlans, current R5.41 compatibility/admission policy, core count 30 | Document schema versions or application supersession between resources |
| `benchmark/semantic/README.md`, `format.py` | Separate prospective scenario formats v1/v2, ordered steps, IDs, origins and applicability | An integrated frozen static-envelope contract; scenario records cannot be substituted for static boundary obligations |
| `operation_contract.py`, `contracts.py`, `operation-contract-fixtures.json` | Explicit extraction of an older combined synthetic fixture's `operation/schema/checks`; separate case evidence | General-purpose nested `payload` handling or a universal `obligations` key |
| `test_optional_support_r5_41.py`, `boundary_study_r5_39.py`, `test_whole_readiness_r5_38.py` | Independent measurement/seed-bank examples and directly supplied obligation lists | A protocol-defined distributed/referenced obligation document format |

The canonical v0.3 application-model JSON schema governs the compiler model; it
does not define benchmark resource envelopes. Existing evidence seals provide
canonical identities and persistence checks, not semantic document roles.

**Known component interface:** one application, one complete configuration with
`transport`, `state`, `launch`, and an explicit list of boundary obligations. The
current readiness consumer recognizes `public_state_alternatives` (public route
names) and `durable_content_constraints` (state-alternative constraint references).
Operation relations reside in the semantic application, not in that supplemental
boundary list. No conventional source/code structure is introduced.

**Unspecified at the opened-document boundary:** required/optional envelope fields,
role registry, top-level versus nested container locations, multi-document inventory,
obligation IDs and duplicate/conflict rules, reference resolution, document ordering,
supersession, schema/version dispatch, and authoritative contract provenance/completeness.
The frozen resource set alone does not resolve these questions. In particular, an
empty list cannot be inferred to mean that no required external obligations exist.

This is an absence of identified authority in these sources, not a claim to have
inspected every historical record. Protected records were deliberately excluded.

## B — Exact R5.75 assumption, from source only

`benchmark/results/phase5c/r5_75_experiment.py:172–175` selects an experiment-specific
resource and evaluates:

```python
obligation_document = documents['obligation-fixture-r540']
obligations = (obligation_document['obligations']
               if isinstance(obligation_document, dict)
               else obligation_document)
```

Expected shape: every dictionary is a top-level `obligations` container; a
non-dictionary is treated as the obligation list. The subsequent list check cannot
catch a missing dictionary key because indexing fails first. No envelope version,
role, required-content, reference or assembly validation precedes it.

The generic consumer requires an **explicit list**, but does not prescribe that
document layout. A dictionary is therefore insufficient evidence for that key.
The source also selects an application using an `r540` resource-name heuristic
(lines 158–167). Neither convention is a generic protocol. No observation of the
actual value causing R5.75's failure is used here; its shape remains uninspected.
The historical callback and runner are preserved byte-for-byte.

## C–F — Reproduction and extraction/error boundary

`benchmark/evaluation/test_document_envelope_r5_76.py` parses only the historical
assignment AST and evaluates that expression against fresh synthetic values. It
never imports or executes the R5.75 controller. Demonstrations:

- top-level obligations and bare-list examples succeed;
- optional metadata leaves that expression unchanged;
- a synthetic nested `payload` counterexample raises exactly `KeyError: 'obligations'`;
- a missing-key example also raises that incidental exception;
- unknown versions/roles, unresolved references and conflicting obligation IDs
  are accepted by the expression without validation.

**Nested and multi-document counterexamples are not asserted to be valid protocol
envelopes.** No source authorizes that assertion. Treating them as valid merely
because a new adapter accepts them would be circular qualification.

The test-local diagnostic consumer accepts only its explicit, predetermined
`application/configuration/obligations` fixture. It rejects unknown containers as
`DOCUMENT_ENVELOPE_GAP`, malformed JSON as `SYNTHETIC_FIXTURE_MALFORMED`, an incomplete
fixture resource set as `SYNTHETIC_FIXTURE_INCOMPLETE`, and incidental downstream
failures as `SYNTHETIC_STATIC_INTERFACE_FAILURE`. These are **diagnostic labels**,
not a newly installed benchmark protocol. Malformed/incomplete demonstrations
assert that no CheckedPlan consumer runs. No obligation content is invented.

Protocol-native classifications such as `MISSING_REQUIRED_CONTRACT_CONTENT`,
`UNSUPPORTED_ENVELOPE_VERSION`, `INVALID_DOCUMENT_ROLE`, `AMBIGUOUS_CONTRACT`, and
unresolved-reference failures still require a versioned generic contract defining
what is required, supported, valid and ambiguous. They are **not qualified** here.

## D, G–H — Examples, assembly and static interface

Real existing examples are the already-public independent measurement and seed-bank
constructors, plus the older combined operation fixture. No new held-out material
is exposed. B01 need not be reread to establish the component interface; no B02
or B03 example is used.

For the direct synthetic fixture, its constructor explicitly supplies the complete
application, all three configuration components and two known boundary obligations.
Canonical serialization round-trips and deterministic consumer output are tested.
The contract identity is the SHA-256 of that explicit fixture's canonical JSON.
This is not an identity for an assembled multi-document benchmark contract.

The bounded static call boundary is:

`explicit application + configuration + obligation list`
→ `current_pipeline.checked`
→ `readiness_r5_41.inspect`
→ `profile_audit_r5_41.inspect`
→ `application_boundary_r5_41.aggregate`
→ `application_boundary_r5_41.support_report`
→ conjunction of READY / SUPPORTED / ADMITTED / SUPPORTED.

Consumers receive their existing typed arguments, never nested raw envelopes.
Readiness also forms its own CheckedPlans internally; no analysis authority is
replaced. This shows the existing consumers compose on known inputs. It does not
define the missing stable **generic BehavioralContract assembly interface**.
Required-document coverage, distributed ordering, duplicate/conflict checks and
cross-document references remain **NOT_QUALIFIED**. Partial assemblies are never
evaluated as complete.

## I–J — Full bounded synthetic pipeline

The diagnostic driver freezes synthetic commitment bytes before authorization,
binds real freshly run generic health, and uses the existing unmodified runner.
Each of four fake experiments has its own durable ledger and exactly these events:

`AUTHORIZED → OPENING_RESERVED → OPENING_CONSUMED → DISPATCHED → COMPLETED`.

The opened bytes verify against their commitment before callback dispatch. JSON
parsing and explicit fixture extraction precede all static calls. Each result
persists and each immediate post-check passes. Replay/second authorization and
intentional synthetic repair invalidation are tested separately in disposable
ledgers; published demonstrations are neither replayed nor repaired.

| Evidence | Classification | Static views | Completion / post-check |
| --- | --- | --- | --- |
| [supported.json](R5_76-evidence/supported.json) | `SYNTHETIC_STATIC_PASS` | CheckedPlan `store`; READY, SUPPORTED audit, ADMITTED, SUPPORTED compatibility | 1 / PASS |
| [unsupported.json](R5_76-evidence/unsupported.json) | `SYNTHETIC_STATIC_UNSUPPORTED` | Known nullable Boolean/raw-text boundary limit; NOT_READY, UNSUPPORTED audit, REJECTED admission, UNSUPPORTED compatibility | 1 / PASS |
| [malformed.json](R5_76-evidence/malformed.json) | `SYNTHETIC_FIXTURE_MALFORMED` | No static evaluation | 1 / PASS |
| [incomplete.json](R5_76-evidence/incomplete.json) | `SYNTHETIC_FIXTURE_INCOMPLETE` | No static evaluation | 1 / PASS |

Infrastructure-failure observation completion means that a structured failure was
recorded; it is not support PASS. Incomplete resource-set diagnostics do not prove
generic distributed-contract completeness. **The full generic envelope/assembly
pipeline demanded by R5.76 remains unqualified.** No language capability issue is
newly discovered; the unsupported example is an existing generic support limit.

## Required-test disposition

The 19 passing tests are diagnostics, not a claim that all 22 requested generic
qualification conditions passed. The following explicitly records that boundary:

| # | Required condition | R5.76 disposition |
| --- | --- | --- |
| 1 | Valid top-level envelope | Explicit synthetic example passes; generic validity unspecified |
| 2 | Valid protocol-defined nested envelope | NOT_QUALIFIED; no identified nesting authority; counterexample reproduces failure |
| 3 | Valid multi-document contract | NOT_QUALIFIED; no identified assembly authority |
| 4 | Optional metadata | Historical expression tolerates synthetic metadata; generic optional-field policy unspecified |
| 5 | Missing obligation structured rejection | Explicit fixture rejects unknown/missing shape before static evaluation; generic required-content rule unspecified |
| 6 | Unsupported schema version | Historical lack of validation demonstrated; unknown diagnostic container rejects; no generic version registry |
| 7 | Invalid document role | Historical lack of validation demonstrated; no generic role registry |
| 8 | Duplicate/conflicting obligations | Historical lack of validation demonstrated; generic conflict rejection NOT_QUALIFIED |
| 9 | Unresolved references | Historical lack of validation demonstrated; generic resolver NOT_QUALIFIED |
| 10 | Deterministic assembly | Explicit fixture/result deterministic; multi-document assembly NOT_QUALIFIED |
| 11 | Canonical round trip | Explicit fixture PASS; generic BehavioralContract round trip NOT_QUALIFIED |
| 12 | Stable static-consumer interface | Existing direct typed-input interface PASS; generic assembled interface NOT_QUALIFIED |
| 13 | Synthetic supported whole-contract PASS | PASS for explicitly complete non-task fixture |
| 14 | Unsupported requirement classification | PASS for known generic Boolean/text limit |
| 15 | Malformed-envelope classification | PASS for diagnostic fixture JSON; generic protocol classification NOT_QUALIFIED |
| 16 | Incomplete-contract classification | PASS for diagnostic fixture resource set; generic multi-document assembly NOT_QUALIFIED |
| 17 | Exactly-one lifecycle | PASS for each fresh fake lifecycle |
| 18 | Replay rejection | PASS before opener/evaluator |
| 19 | Repair invalidation | PASS in disposable synthetic test ledger |
| 20 | B02 access prohibited | Fake denied-file control PASS; real protected attempts/reads zero |
| 21 | B03 access prohibited | Fake denied-file control PASS; no real B03 access or fixtures |
| 22 | AI-independent extraction | Deterministic offline explicit-fixture path PASS; no inferred malformed structure |

## Health, publication and evidence

Fresh scoped checks use the simplified runner's eight bounded worker selections,
not broad harness discovery or the retired production framework:

| Check | Fresh result |
| --- | --- |
| Runner | **74/74 PASS** |
| Document diagnostics | **19/19 PASS** |
| Compiler/application | **31/31 PASS** |
| Current generic semantic/support | **157/157 PASS**, 36 metadata-only prohibited skips |
| Coherence | **16 profiles / 84 rows PASS** |
| Profile schema and traceability | Valid; **99/99 leaves** |
| Contamination | Clean current generic support implementations |
| Validation / safety | PASS under current canonical model |
| AI independence | Offline, site-disabled generic validation/lowering/read-only execution; authoring mutation invariant; deterministic fixture parsing |
| Safe held-out exclusion | **14 ordinary tests PASS / 36 pre-import prohibited skips** |
| Secret-safe publication | Canonical sealed evidence passes runner guard; deliberate synthetic marked-value rejection succeeds; read-only audit checks evidence and report |
| State integrity | Immediate per-stage/per-observation checks plus separate read-only audit; core **30** |
| Whitespace | `git diff --check` and audit of newly added source/report files PASS |

Commands run from the repository root with `PYTHONPATH=src`:

```powershell
python -B -S -m benchmark.evaluation.test_document_envelope_r5_76
python -B -S benchmark/results/phase5c/r5_76_investigation.py
python -B -S benchmark/results/phase5c/r5_76_audit.py
git diff --check
```

Preserved development failure: the first diagnostic command failed in
`test_unknown_envelope_is_gap_not_invented_obligations` because a patched
CheckedPlan sentinel also blocked construction of the generic seed fixture.
Fixture construction was moved before that sentinel; the second command passes
19/19. This occurred before the fresh evidence run and is not an observation
failure, ledger repair or hidden retry. No completed evidence run is repeated.

[summary.json](R5_76-evidence/summary.json), [health.json](R5_76-evidence/health.json),
[state.json](R5_76-evidence/state.json), [document-diagnostics.json](R5_76-evidence/document-diagnostics.json)
and [audit.json](R5_76-evidence/audit.json) retain machine-readable evidence.
Health workers bind their original CurrentState; an enclosing state additionally
pins the diagnostic source and driver. These two scopes are explicit, not conflated.

## Simplicity, semantics and next step

The two runner modules, authority layer, six artifact types and five normal
transitions are unchanged. There is no B02/B03 parser, resource-name heuristic
or additional production framework. Test-local explicit fixture code is not
installed as a generic adapter. Core semantics remain **30**, with no #31 and
no language/compiler/schema/runtime changes. AI services are not involved in
parsing or extraction. Behavioral relations remain separate from conventional
implementation structure.

**Next prerequisite:** separately define/authorize one versioned generic document
contract from non-held-out component formats. It must explicitly specify roles,
containers, obligation inventory, references, duplicate/conflict rules, ordering,
identity/provenance, versions and completeness; then independently qualify one
simple adapter and the entire synthetic opening-to-static-result path. Do not
use B02 to fill those specification gaps.

Only after that qualification should a separately authorized pristine held-out
experiment select B03 or the next still-unexposed eligible benchmark, with the
qualified full synthetic path checked first. **R5.76 does not recommend immediate
held-out exposure.** Future B02 use may be `POST_EXPOSURE_DIAGNOSTIC` or
`REGRESSION_BENCHMARK`, never first-exposure or held-out transfer evidence. No such
run occurs here. Phase 5C remains paused. R5.76 stops at this documented generic
envelope-contract gap.
