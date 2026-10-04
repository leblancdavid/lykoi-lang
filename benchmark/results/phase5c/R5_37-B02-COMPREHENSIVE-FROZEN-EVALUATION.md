# R5.37 — Comprehensive frozen B02 evaluation

**Result: `R5_37_B02_INTEGRATION_GAP`.** The locked current pipeline rejects
the faithful overdue composition at authoritative type analysis. No complete
candidate exists; all seven applicable frozen acceptance methods are BLOCKED.
No implementation repair, reduced-slice generation or acceptance retry followed
the diagnostic. This is an evaluation finding, not a capability-development phase.

The decisive requirement was already identified in R5.23: a **nullable**
instant must become admissible to strict `before` after a non-null guard.
R5.24–R5.31 established **optional membership** refinement, which is a
different elimination rule. R5.36's readiness conclusion did not establish
this frozen-required composition. A green readiness-matrix test validates
the recorded matrix; it does not make its readiness conclusion true.

## 1. Experimental lock

Initial working tree clean at commit
`428a3409ea4d47a57a9fc9e5a94af2595d98ec43`; no commit was created. The existing
clean checkpoint pins the architecture. The recorder was the sole untracked
file when the lock was established; exact status and its SHA-256 are recorded
in [R5_37-implementation-lock.json](R5_37-implementation-lock.json).

Lock UTC time: `2026-10-04T05:04:59.476763+00:00` (local experiment date Oct 3).
Lock identity: `5bb4fa67d37259b4255f6141f3fdd06d7da5f0b02b7e8196c166d501389e34b0`.
**224 files** pinned by byte-level SHA-256, covering semantic implementations,
relations, compiler/runtime/schema, existing harness, frozen requests, generated
baseline, inventory and readiness matrix. Hashing later request bytes did not
read/expose/classify their text.

| Required identity | Locked implementation / SHA-256 |
| --- | --- |
| Candidate inventory | `R5_10-MIGRATION-COUNT-EXPRESSIVENESS.md`: `6e50891d0a343fb80f16dae17c3918906cb6fb8e9041be27518c77121a3699f4`; historical vocabulary ledger also pinned; 30 candidate core / 46 historical raw |
| Authoritative analyzer and sealed CheckedPlan | `unified_types_r5_27.py`: `ea247732670ea2a857de24898ddccd8c631e2b3fd46a4b27f6431792e2bb94b6` |
| Current entry | `current_pipeline.py`: `27a83b7e86c45d787822b5dd28670dd6f46fac2223d1f2ef79d9985169c56350` |
| Structured generator / planners | `refined_generator_r5_28.py`: `db190e824c33dc85d2a2f93c41181eb29842bae2f6a86511af39bbeacf0f7671`; shared/historical planner dependencies independently pinned in lock |
| Runtime | `refined_runtime_r5_28.py`: `897960b8cfe0e1c045edffda23c108a8c758c41ef74377d6a3e24ca80b816c47` |
| Semantic verifier / evidence | `refined_evidence_r5_28.py`: `d77e9231dfd9a25f861bce9ae1cf814660c9a20c19a2d1ce01ec4a12e4b224fd`; `current_pipeline.py` challenge also pinned |
| Scalar input binder | `input_binding_r5_32.py`: `5e2b978bddc536c8f0ed83e2a86aa20930e7fb8fe68596bb400b5e559ed70642` |
| Checked binding/output/persistence policy | `checked_transport_r5_35.py`: `a2d935be42229274b9be858ed8a4f189ad9b36df48d6eae67f0da8cba8389bcb` |
| Collection binder, transport and persistence runtime | `transport_runtime_r5_35.py`: `ae9e26e83156e3e4e8dd5489a7c895203d0cc4bc5f511db3275d3d812050fc94` |
| Checked public launcher / grounding | `checked_launch_r5_36.py`: `4662447497a6f235a477bf03347e995427515067c92f7999317b21bfecba85f3` |
| Standalone launch runtime | `launch_runtime_r5_36.py`: `bb0965ffa810ee94b15174733d5acae81d4e0150485b2bf37d7a4fe4d43bce7b` |
| Independent binding evidence | `public_binding_r5_32.py`: `71320a3fabbf37035debcfde718540d93e8f2e2afba4f7333e971ecdc842aae7` |
| Readiness identity | `R5_36-readiness-matrix.json`: `7dca4109a2667b430ba84de3de55097f7c87e5da3854bccf00ce3ec1a6363f0f` |

All remaining grounding helpers, relation definitions, adapter dependencies,
and frozen artifact hashes are recorded individually in the lock, rather than
represented by an unverified directory label. Post-lock additions are
evaluation/source/evidence files under `benchmark/results/phase5c/` and the
three requested living research documents. Historical evidence is unchanged.

## 2. Verification baseline

Before generation:

| Check | Actual outcome |
| --- | --- |
| `python -m unittest discover -s benchmark/harness -v` | 347 run / 347 pass / 0 skip / 0 failures, 131.701 s |
| `PYTHONPATH=src; python -m unittest discover -s tests -v` | 31 pass, 2.734 s |
| Model validation | `Lykoi validate: ok` |
| Safety | 0 capability violations; 0 invalid transitions; 6 invariants |
| R5.31, R5.32, R5.33, R5.35, R5.36 focused suites | 58 pass, 20.439 s; includes readiness matrix validation |
| Implementation lock immediately before generation | 224 hashes unchanged; HEAD unchanged |
| `git diff --check` | PASS |

First full harness attempt exceeded the tool's 120-second timeout; it was
rerun with a 600-second limit and completed successfully. This is a tool
timeout, not a failed test or B02 candidate failure. Unlike R5.36's special
verification wrapper, direct full discovery did not skip the nested historical
checkpoint revalidation. It replayed existing B01/B02/B03 history on a pinned
old candidate. **There was no R5.37 B03 candidate invocation or new exposure**;
it would be inaccurate to say no historical B03 process ran at all. The
mandatory baseline and that replay are recorded separately from evaluation.

Environment: Windows 11 `10.0.26300-SP0`, AMD64, Python **3.14.3**, executable
`C:\Users\lblan\AppData\Local\Python\pythoncore-3.14-64\python.exe`, PowerShell 7,
no third-party dependencies. `PYTHONPATH` unset for semantic/harness entry;
set to `src` for application/compiler CLI checks. `core.autocrlf=true`;
locked hashes are actual working-copy bytes, not LF-normalized Git blobs.
New evidence is emitted as UTF-8/LF. LF→CRLF checkout warnings are separate
from semantic failures; none caused the nullable analyzer rejection. Public
provider/path choices are checked metadata; no public runtime was reached.

## 3. Authoritative B02 reconstruction

The complete clause-by-clause record is
[R5_37-B02-CONTRACT-RECONSTRUCTION.md](R5_37-B02-CONTRACT-RECONSTRUCTION.md):
**24 obligation rows and four underspecified areas**, with public/raw/typed
input, pre/post shapes, relations, outcomes, persistence, encoding, failure,
evolution and selection/order behavior. The exact request, inherited B01 and
baseline, seven original regression methods, schema profile and capability
fragment were read directly.

Important distinctions preserved: schema 4; nullable persisted due dates;
exact HIGH filtering; completed tasks included in normal/HIGH lists; strictly
past pending dated tasks only; description verbatim; repeated trimmed
case-sensitive first-occurrence tags; all legacy records counted on migration;
missing-store read/migrate preserves physical absence; expected public errors
need not be typed semantic invocations.

## 4. R5.23 reconstruction comparison

**NONE** for mandatory tag/lifecycle/query/migration/public obligations.
**PREVIOUSLY_OVERINTERPRETED_REQUIREMENT** for treating malformed due-date
errors as necessarily operation-declared typed branches; the frozen contract
requires public `invalid_due_date` and no write, not a particular internal layer.
**BENCHMARK_AMBIGUITY** for unspecified invalid-input precedence and priority
rank observability. **OTHER** for R5.23's overbroad “complete semantic source”
label despite boundary/bare-list obligations being held separately.
No **PREVIOUSLY_MISSED_REQUIREMENT** was identified.

The decisive nullable blocker is **not a newly discovered requirement**.
R5.23 §6 explicitly records required-nullable `before` rejection. This
evaluation preserves R5.23 and R5.36 rather than rewriting their conclusions.

## 5. Semantic adequacy gate

All 24 obligations can be stated using the existing candidate vocabulary plus
type/binding/evolution architecture at the abstract contract level; four areas
are BENCHMARK_UNDERSPECIFIED. No genuinely new relation requiring #31 was
identified. This follows the established separation of semantic adequacy from
current-format/compiler coverage.

That abstract adequacy does **not** establish a coherent complete current
application: the existing analyzer cannot consume the nullable comparison
composition. The representation includes the null guard faithfully; the
analyzer rejects the operand rather than inferring a null elimination witness.
It is a type-integration coverage gap over existing semantics, not evidence
that strict time comparison lacks abstract meaning.

## 6. Complete semantic source

The authoritative complete behavioral **contract** is the reconstruction above.
[R5_37-b02-semantic-application.json](R5_37-b02-semantic-application.json) is
one prospective current-format **operation-family attempt**, authored by the
AST-only [r5_37_source.py](r5_37_source.py). It contains 15 operations: three
current reads; create; complete; delete; current migration; bare-list and
envelope migration; six legacy read failures. Types register bare legacy,
legacy envelope and current state. Migration uses side-qualified source/target
defaults and version equality; externals/fallback/normalization/frame/lifecycle
are semantic expressions, not manually authored target behavior.

**A complete checked B02 semantic application was not established.** Public
version-alternative dispatch and durable content validity remain obligations
in the complete contract, not covert Python helpers. This attempted operation
family must not be called a complete source-authoritative executable. No
semantic source or implementation was changed after observing generation.

## 7. Whole-program generation

One attempt only:

```text
python benchmark/results/phase5c/r5_37_source.py
python benchmark/results/phase5c/r5_37_evaluate.py verify
python benchmark/results/phase5c/r5_37_evaluate.py evaluate
```

The evaluator calls exactly `benchmark.semantic.current_pipeline.generate`.
The entry calls authoritative analysis/CheckedPlan before operation-unit
construction. `list` and `list-high` precede `list-overdue` in the source;
their checked-plan analysis returns, but the overdue plan fails. No sealed
whole-application plan set, structured-unit rendering, application assembly or
artifact output follows. No fallback compiler, text splicing or target code
was used. The empty generated-files list is preserved in evidence.

## 8. Generation classification

Exactly **`UNKNOWN_TYPE_COHERENCE_GAP`** from the permitted generation taxonomy.
Here “UNKNOWN” is the required classification label, not a claim the nullable
requirement was unknown historically.

```text
ValueError: before requires two typed instants; optional operand needs in-scope presence
```

Full diagnostic/traceback:
[R5_37-generation-evidence.json](R5_37-generation-evidence.json).
The call chain reaches `ordering_plan` → selection → conjunction → `before`
in `unified_types_r5_27.py:154`. The left operand is
`nullable<instant>`, the right is `instant`. `not(equals(due,null))` supplies
no accepted refinement. Presence witnesses recognize `optional`, not nullable.
The diagnostic's optional wording does not describe the actual left type.

The final gate is **integration gap**, because a known frozen-required domain
composition remains unresolved despite independently successful neighboring
capabilities. It is not an observed lowering defect, acceptance failure, new
semantic primitive, or evidence of wholesale architectural contradiction.

## 9. Source-authority audit

Executable candidate audit **BLOCKED**: no executable exists. Audit of the
attempt's authoring/evaluation files finds only AST construction, byte hashing,
JSON evidence, pipeline invocation and integrity checks; no target-language
task algorithm, benchmark adapter or manually assembled Python candidate.
No behavior was inserted into the frozen harness, launch, binder, bootstrap,
runtime or compiler. The final 224-file lock check substantiates that boundary.
This is not a source-authority PASS for a nonexistent candidate.

Static post-failure review identifies additional **unexecuted integration
concerns**, not additional measured failures:

1. `checked_transport_r5_35.validate` admits scalar element types, not
   `optional<nullable<instant>>` input. Current fallback typing requires its
   default to have the exact optional inner type. Omitted input→persisted null
   therefore also needs checked input/constructor-domain coherence.
2. A public transport route names one semantic operation and rejects duplicate
   public names. R5.33 demonstrates separate legacy/current operations, not one
   public `migrate` selecting bare/envelope/current alternatives or one `list`
   selecting legacy failure/current success by shape. Routing concern remains
   unexecuted; no task-specific dispatch was authored to hide it.
3. Runtime `valid()` checks structural fields/scalars, not population duplicate
   IDs, nonblank IDs/titles or status/priority domain invariants. The complete
   invalid-state contract cannot be certified by structural codecs alone.
   No candidate was run to demonstrate a particular bad-state acceptance.

These concerns are separately traced to code and C07/C18–C23; they are not
used to inflate the one observed generation failure into several executions.

## 10. Candidate identity

| Identity | Observation |
| --- | --- |
| Evaluation source file SHA-256 | `7686b801f560c04e1336f533241a3ea7e4863fc2bedd834a3547f2d8c8a875ee` |
| Source application ID | `r5.37.frozen-b02.attempt` |
| Complete CheckedPlan identity | NOT CREATED |
| Generated artifact identity | NOT CREATED |
| Checked transport/persistence/launch profile identities | NOT CREATED |
| Generated provenance identity | NOT CREATED |

The source/evidence is distinct from all historical candidates. No historical
candidate was modified or relabeled as R5.37.

## 11. Standalone launch

BLOCKED before launch-profile generation. Zero public candidate invocations.
Intended public boundary is the unchanged R5.36 copied entry plus checked
co-located profiles, public argv, actual cwd and controlled environment.
No hidden helper flag or older launcher substituted for a complete candidate.

## 12. Complete frozen acceptance matrix

Applicable original command, if generation had succeeded:
`python benchmark/harness/regression.py --app APP --achieved B01,B02`.
Artifacts are unmodified. No executable means no independently executable
acceptance case, rather than one failed case causing premature suite stopping.

| Original frozen method | Status | Reason |
| --- | --- | --- |
| test_baseline_lifecycle_filters_failures | BLOCKED | No complete candidate |
| test_baseline_migration_corruption | BLOCKED | No complete candidate |
| test_baseline_overdue_fixture | BLOCKED | No complete candidate |
| test_b01_priority_and_regression | BLOCKED | No complete candidate |
| test_b01_historical_priorities | BLOCKED | No complete candidate |
| test_b02_tags_and_failure | BLOCKED | No complete candidate |
| test_b02_explicit_migration | BLOCKED | No complete candidate |

Totals: **0 PASS, 0 FAIL, 0 SKIP, 7 BLOCKED**. No R5.37 oracle subprocess was
launched. Baseline historical acceptance is not counted as candidate acceptance.
Each method's original temporary-directory/subtest isolation and intentionally
shared lifecycle/migration sequence remain untouched (§3 reconstruction).

## 13. Failure classification

No acceptance behavior failure exists to assign GENERATED_BEHAVIOR_DEFECT,
SEMANTIC_SOURCE_MISMATCH, COMPILER_LOWERING_DEFECT, BINDING_DEFECT,
PERSISTENCE_DEFECT, TRANSPORT_DEFECT or LAUNCH_DEFECT. The **generation**
failure is a TYPE_COHERENCE_DEFECT/coverage gap: nullable guard + `before`
cannot form a CheckedPlan. Invalid-state/public-routing concerns are static
findings with no observed acceptance classification. No repair occurred.

## 14. Grounding matrix

| Major class | Public process/event/durable observations | Grounding |
| --- | --- | --- |
| create / fallback / external identity-clock | none | BLOCKED |
| normal / ordered / HIGH / overdue list | none | BLOCKED |
| repeated tags / normalization | none | BLOCKED |
| completion/update / remove | none | BLOCKED |
| failure/no-write / malformed binding | none | BLOCKED |
| migration / cross-shape transition | none | BLOCKED |

Zero execution events and zero grounded cases. This is **blocked grounding**,
not GROUNDING_FAILED: there was no observation to challenge. The compiler
traceback is generation evidence, not an internal application execution event.

## 15. Layered verdicts

All seven rows have LAUNCH_PROFILE, TRANSPORT, INPUT_BINDING, PERSISTENCE,
SEMANTIC_EXECUTION and OUTPUT **BLOCKED**. Analysis failure does not prove a
runtime layer failed. No false success verdict is inferred from independent
R5.32–R5.36 studies.

## 16. Semantic conformance matrix

For every blocked case: **NOT_SEMANTICALLY_INVOKED**. There are zero
GROUNDED + CONFORMANT, zero GROUNDED + NON_CONFORMANT, zero GROUNDING_FAILED.
No alternate semantic source or historical case checker was substituted.
The intended verifier would consume the same generated B02 contract/plan,
but the prerequisite complete candidate never existed.

## 17. Acceptance versus conformance

[R5_37-evaluation-matrix.json](R5_37-evaluation-matrix.json) preserves every
original case and each applicable dimension:

| Frozen acceptance | Launch | Transport | Binding | Persistence | Grounding | Semantic conformance | Output |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BLOCKED (each of 7 methods) | BLOCKED | BLOCKED | BLOCKED | BLOCKED | BLOCKED | NOT_SEMANTICALLY_INVOKED | BLOCKED |

No acceptance/conformance discrepancy is observable. Static source adequacy
versus type-checking rejection is a different discrepancy and is explained
in §§5–8. Passing pre-lock unit tests does not fill these empty cells.

## 18. Migration deep check

BLOCKED: no pre-version, durable pre-shape, transformed population, post-state,
post-version, actual count or public outcome observed. Source *declares*
priority/due/tags keyed defaults, preservation and cardinality over the entire
legacy population, bare-list→envelope and envelope→current transition. That
declaration is not an independent migration observation. Shared public
version-alternative routing remains a static concern (§9).

## 19. Create deep check

BLOCKED: no raw binding record, clock/ID value, constructed/returned task or
durable record observed. Source *declares* required title/description,
optional priority/due/tags fallback, repeated tag normalization, cached
externals and framed insertion. No result/persistence identity proof is made.
Nullable input-to-constructor typing is an unexecuted concern (§9).

## 20. Query/read deep check

The mandatory null-safe overdue composition is the actual generation blocker.
Exact pending selection and strict chronological comparison cannot be executed.
Normal/HIGH instant-key plans were reached in checking before that halt;
neither is rendered/executed/grounded in R5.37. Durable byte equality,
selection completeness, result projection and ordering are all unobserved.
Do not use strings, omitted due fields, a sentinel date or a fallback date
to force an accepted comparison with altered frozen semantics.

## 21. Failure deep check

No failed candidate invocation was observed, so transport/binding/typed
failure and durable preservation are untested for B02. The reconstructed
contract explicitly classifies malformed due dates and invalid storage as
pre-semantic boundary cases when applicable; blank typed tags/title and
lifecycle failures may be typed outcomes. Structural validity must not stand
in for the full invalid-state/no-write contract. No fake error event was emitted.

## 22. Direct R5.23 comparison

| R5.23 blocker/status | Independent resolution work | R5.37 actual transfer result |
| --- | --- | --- |
| instant creation versus orderable key collision | R5.24–R5.31 chronological instant/order integration | list and HIGH CheckedPlans reached; executable transfer NOT_REACHED |
| optional legacy priority/refinement | R5.25–R5.31 optional membership witness | separate state versions avoid optional current priority; optional refinement NOT_REQUIRED on current rows |
| nullable/optional overdue instant | optional witness work R5.25–R5.31, readiness marked resolved | **INTEGRATION_CONFLICT**: required nullable elimination still missing; definitive analyzer rejection |
| suppliedness/well-formedness | R5.32 scalar / R5.35 collection binding | NOT_REACHED; nullable input shape static concern |
| malformed-input boundary | R5.32–R5.36 public failure/noninvocation | NOT_REACHED; typed malformed branch not intrinsically required |
| one-shape migration / bare-list promotion | R5.33 cross-shape operations and codecs | NOT_REACHED; single public operation's multi-shape routing unestablished |
| public positional argv/error envelope/repeated tags/missing store | R5.34–R5.35 checked transport extensions | NOT_REACHED |
| standalone public launch/cwd-store/trace | R5.36 checked public launch | NOT_REACHED |

R5.23 executed 13 conformant diagnostic slices but produced no complete
candidate or frozen acceptance. R5.37 intentionally executes no slices after
the halt and likewise has no complete candidate. Progress in independent
architecture is real, but complete frozen composition remains unestablished.
The rejection moved past the prior first instant-order key failure and reaches
the already-known nullable subcase; it does not validate the rest of B02.

## 23. Independent capability transfer matrix

The machine-readable matrix enumerates 14 current readiness dimensions.
No dimension earns **TRANSFERRED** on complete frozen executable evidence.
Nullable `before` is **INTEGRATION_CONFLICT**. Single authority is
**REACHED_BUT_FAILED** to complete the application, while correctly rejecting
an unsupported domain; no duplicate-authority inconsistency was observed.
Current-row optional membership refinement is **NOT_REQUIRED**.
The remaining eleven dimensions are **NOT_REACHED** in execution.
Earlier checked ordering is explicitly acknowledged without counting it as
grounded runtime transfer. The 14-row denominator is readiness dimensions,
not semantic constructs or acceptance tests.

## 24. Overfitting reassessment

Evidence against a post-hoc fitted success: architecture locked before the
attempt; independent publication/archive/observatory/specimen/mineral/acoustic
domains in R5.24–R5.36; no B02-specific compiler edit or runtime branch added;
semantic-only operation source; honest unsuccessful integration preserved.

Remaining risk: B02 is **not fully held out**. Its frozen text and R5.23
blockers informed the capability backlog; prior B02-shaped fixtures and
retries exist; current state/CLI compositions were selected with benchmark
readiness in mind. Neighboring-domain success was overgeneralized to the
required nullable composition. A benchmark-derived readiness checklist is
not equivalent to systematic shared-domain coverage. This failed integration
is evidence against claiming broad generalization, not evidence of improved
performance over conventional development.

## 25. Compiler maturity assessment

| Layer | Established in this evaluation | Still unestablished |
| --- | --- | --- |
| Semantic model | full frozen obligation reconstruction, no new primitive identified | coherent complete supported-format source |
| Compiler coverage | actual current-entry invocation; fail-closed stop before emission | complete operation-unit lowering/assembly |
| Type coherence | instant-key checking reached; nullable rejection localized | non-null guard elimination and nullable input fallback coherence |
| State evolution | existing code intact; declarative side-qualified migration attempt | B02 migration/public version-alternative integration |
| Transport | implementation remains locked | B02 raw/public checked profile and full validity |
| Launch | implementation remains locked | B02 standalone launch |
| Grounding | implementation remains locked | any B02 candidate observation/event/durable linkage |
| Verification | 347+31 baseline, 58 focused; evaluation integrity checks | acceptance, grounded conformance, completeness proof |

No compiler internal inconsistency was observed: the analyzer's accepted
refinement domain does not include the nullable case. The readiness process
overstated integration coverage. This does not invalidate the bounded
independent observations or retroactively change historical gates.

## 26. Universal correctness

**`UNIVERSAL_IMPLEMENTATION_CORRECTNESS_ESTABLISHED = NO`**.
No acceptance success, grounded B02 success or universal proof exists.
Even complete acceptance plus finite grounded cases would not establish
universal implementation correctness.

## 27. Phase 5C implication

Phase 5C returns to paused status after this expressly authorized B02-only
evaluation. Do not execute B03 on a new candidate or begin a pressure sweep.
R5.2.2 retains historical authority, B17 stays unexposed/unclassified, semantic-
first format globally UNFROZEN. Historical B03 replay in the mandatory baseline
is disclosed in §2 and does not advance the prospective benchmark boundary.

Next-work categories: **focused general type-integration coverage** and
**methodology/readiness correction**, with independent semantic review of
the nullable domain and public multi-version/content-validity boundaries.
There is insufficient evidence to demand a wholesale architecture rethink
or new core semantic capability. No such work is implemented inside R5.37.

## 28. Research/publication notes

Positive observations: exact clean implementation checkpoint; complete
reconstruction against authoritative texts; functioning single-entry rejection;
instant-key checking passes the former first blocker; no repair or misleading
green artifact; immutable evidence and all blocked outcomes retained.

Negative finding: the final readiness review failed to distinguish optional
membership from nullable elimination despite the distinction appearing in
R5.23. Complete semantic generation, standalone launch, acceptance and all
major grounding classes remain blocked. Static public version dispatch,
nullable input binding and durable invariant concerns merit independent review.

Limitations: one rejected operation-family attempt; no executions; no
source-authority certification for a complete candidate; attempted AST not
a complete checked source; no systematic search over every equivalent encoding;
no runtime classification of the additional static concerns; no comparative
cost/time experiment. Token/cost/model-comparison telemetry is unavailable.
No claim that Lykoi outperforms conventional development follows.

## 29. Construct accounting and final verification

Candidate core **30**, historical categorized raw **46**, new core **0**,
implementation repairs **0**, new complete frozen-B02 grounded reuse/transfer
demonstrations **0**. Previous counts/evidence are preserved; no historical
ledger was edited to count declarations or failed checking as demonstrated reuse.

Six R5.37 integrity tests check lock bytes/seal, source identity, faithful null
typing, exact frozen method inventory and absence of invented execution/proof
claims. They consume collected evidence without regenerating/retrying B02.
Final lock verification is recorded in
[R5_37-final-lock-verification.json](R5_37-final-lock-verification.json):
224 protected hashes unchanged, HEAD unchanged. Final `git diff --check`
passes; LF→CRLF warnings remain environment-only. All generated/current
implementation files and frozen acceptance artifacts are unchanged.

## 30. Exact recommendation

**R5.38 = Independent Nullable-Domain and Whole-Contract Boundary Coherence
Review.** Start with the existing typed semantics for null elimination into
chronological predicates, not another frozen retry or #31. Review independently
on non-task domains: required-nullable versus optional fields; nullable
omission/default construction and checked scalar binding; one public operation
over multiple pre/post version shapes; and durable population/content validity
with public no-write failure mapping. Any approved implementation belongs in
a separately versioned development phase with positive/negative compositions,
source-only mutations and independent grounding. Replace readiness assertions
with evidence for exact shared-domain compositions and mandatory error paths.
Authorize another B02 evaluation only after that independent gate; do not
automatically resume B03–B16.

R5_37_B02_INTEGRATION_GAP
