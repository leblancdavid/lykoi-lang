# R6.44 — Practical stateful modification comparison

**Final classification: `R6_44_COMPARISON_INCONCLUSIVE`.**

Both conventional Python and production-backed Lykoi implement the frozen shared
policy change correctly: **188/188 observations**, **177 retained original
observations**, **zero observed modification regressions**, **zero candidate
repairs**, and identical deterministic results on AI-free replay. Lykoi did not
demonstrate a measurable practical advantage. Full starting-contract equivalence
is limited by a subsequently confirmed, inherited malformed-store error mismatch.
Reported effort is mixed and actual billing remains unavailable.

## 1. Authorization, preservation and baseline

One bounded exploratory comparison was authorized. [Baseline](r6_44/BASELINE.json)
verifies **5,059 protected SHA256 identities**, including R6.3–R6.43 evidence,
production implementation, R6.10 VM, R6.18 wrapper, R6.23 adapter, R6.25 contracts
and R6.32 registry semantics. R6.43's publication manifest and receipt bindings
were verified before authoring; its lossless archive is also checked at publication.
R6.43 was untracked at initial inspection and is preserved. The baseline records
the repository HEAD at preparation. No commit was requested or made by this agent.

Kernel remains **26**, verified by unchanged R5.114 accounting and protected
implementation identities, not a fresh independent construct recount. Production
kernel/compiler/lowerer/runtime remain unchanged. No execution semantics, training,
P6-A04 acceptance or P6-A05 content access were introduced.

[Starting application manifest](r6_44/STARTING-APPLICATION.json) identifies copies
of exposed R6.16 stage-2 kiln implementations: historical A for Python, historical
C for production-backed Lykoi (called **B in this round**). Historical results and
sources are untouched. Original Python passed174/175 initial observations; its
known blank-label error was invalid_input instead of invalid_label. Original Lykoi
passed175/175. The unscored Python baseline correction adds only a blank-string
label error branch; the failed observation and original source remain published.

Both accepted copies then passed175/175 initial checks and **182/182 final baseline
checks** each. [A](r6_44/BASELINE-ACCEPTED-v2-A.json) and
[B](r6_44/BASELINE-ACCEPTED-v2-B.json) use identical inputs, state fixtures and expected
outputs. Starting source, generated artifact and fixture identities are recorded.
The missing-store fixture is explicit absence; seeded JSON lists are recorded in
the frozen expectation files and raw execution records include exact store bytes.

### Capability inventory and selection bias

The existing R6.16 C path uses production scalar lowering, typed mutable-value
composition, predicate/guard validation, generated mutation execution and atomic
local storage. It supports this record-local application: create/list/ignite/
set_gate/cool/rescue, enum state, ordered prewrite guards, whole-store invariants,
durable writes and rejection preservation. It does not expose arbitrary callbacks,
distributed effects or arbitrary decoder-error overrides. See the
[semantic audit](r6_44/SEMANTIC-AUDIT.json) and preserved
[R6.43 inventory](r6_43/BENCHMARK-CAPABILITIES.md).

The kiln is a previously exposed synthetic fixture with interdependent operations,
conditional transitions and explicit invariants. Selection is nonrandom and
implementation-aware, favoring demonstrated Lykoi support; it is not an external
generalization sample. Both tracks must make the same existing-policy changes.
The known Python baseline correction is preparation cost, not a scored Lykoi win.

## 2. Frozen genuine modification and independent expectations

[Contract](../../../experiments/stateful_modification_r6_44/CONTRACT.md): extend the
existing emergency-load exception to **ignite and set_gate**. Cold/closed/emergency
ignition now succeeds; emergency firing loads can close or retain a closed vent.
Ordinary restrictions remain. The existing persisted invariant, rescue eligibility,
cool, create/list, field preservation and error precedence remain unchanged. No new
endpoint substitutes for changing existing logic.

The [protocol](../../../experiments/stateful_modification_r6_44/PROTOCOL.md),
[expected-impact map](../../../experiments/stateful_modification_r6_44/EXPECTED-IMPACT.json),
[original expectations](r6_44/ORIGINAL-EXPECTATIONS-v2.json),
[modified expectations](r6_44/MODIFIED-EXPECTATIONS-v2.json), prompts, inputs and
installation expectations are bound by [FREEZE](r6_44/FREEZE.json), before either
participant starts. Expectations derive from the requirements and exposed source
contracts, not submitted code or observed participant outcomes.

A separate AI review session first returned [BLOCK](r6_44/PREAUTHOR-REVIEW-1.md):
the modified emergency sequence omitted the retained two-record cold-state list.
The original draft remains preserved. Before authoring, v2 restores that observation
and adds invalid-unrelated-record and timestamp-tie controls. The second review
returned [PASS](r6_44/PREAUTHOR-REVIEW-2.md):165 cases,182 original/188 modified
steps;177 original observations retained and5 explicitly superseded. Error sites
were reviewed as store validation → lookup → ordered guard → input validation;
observable outputs carry codes, not internal source coordinates.

**Review independence limit:** separate-session, candidate-output-independent AI
review on the same platform/model; no independently sourced human reviewer or
attested hidden-context isolation. The reviewer's first overbroad utility read
exposed orchestration and the baseline-only label correction, disclosed in both
review records. It did not inspect participant application files or actual baseline
outputs. This is not a claim of independent human/cognitive review.

## 3. Model, authoring and preserved submissions

Both fresh sessions use the working OpenCode route **openai/gpt-6.1-sol**, requested
`--variant high`, `--pure`, ordinary Python/file tools, and separate temporary
directories. Exact effective provider reasoning settings and context capacity are
unavailable. Each receives only its own accepted application and the same contract.
B additionally receives the existing schema and read-only production generator.

Frozen budget per track:480-second process timeout,≤16 tool calls,≤2 self-test
batches of≤60 seconds, initial candidate plus≤1 self-directed repair. One trial,
fixed order A then B. No repeated-trial counterbalancing or acceptance-feedback
repair. Actual processes exit before AI-free scoring and are not resumed.

| Authoring result | A — Python | B — production-backed Lykoi |
|---|---:|---:|
| Fresh session | `ses_ed9a7f741ffeaYGoUK1lDHsiOQ` | `ses_ed9a50d72ffeRVCPkux425n4nB` |
| Participant wall |184.661s|295.384s|
| Tool calls |13|13|
| Visible model completions |14|10|
| Candidate repairs |0|0|
| Self-test batches |1|2|
| First/final candidate identity |Same|Same|

Preserved evidence: [A author ledger](r6_44/AUTHOR-A.json),
[B author ledger](r6_44/AUTHOR-B.json), [A first](r6_44/submissions/A/first.py),
[A final](r6_44/submissions/A/final.py), [B first](r6_44/submissions/B/first.json),
[B final](r6_44/submissions/B/final.json), both effort records, raw JSONL tool events,
sanitized session exports, generated artifacts and source diffs.

A reports942 self-test checks and12 restart operations; these are participant
claims/self-tests, not external acceptance denominators. B's first self-test fails
in its Unicode/cp1252 test transport. Its second enables UTF-8 and completes203
checks before encountering the inherited `{}` error discrepancy. This is one
self-test harness adjustment, **not** a candidate repair. Both failures and inline
test bodies are retained in raw events. No generated behavior is hand-edited.

[A audit](r6_44/AUDIT-A.json) and [B audit](r6_44/AUDIT-B.json) confirm baseline
identity, first/final identity and budget compliance; visible tool inputs contain
no opposite-implementation or external acceptance-read markers. The actual event
inputs are retained because sanitized exports redact them. Separation is
cooperative, not OS-enforced; provider/system hidden-context exclusion is unattested.

## 4. External functional, persistence and replay results

All applications execute without AI via the unchanged per-operation subprocess
transport. Expected results are identical across tracks; generated source similarity
is not scored. Every operation starts a fresh process and reloads the same local
store within its scenario. Raw records preserve stdout/stderr, return code, exact
before/after bytes, decoded state and timings.

| Check | A | B |
|---|---:|---:|
| Accepted starting original observations |182/182|182/182|
| Modified first submission |188/188|188/188|
| Modified final submission |188/188|188/188|
| Retained original observations in reviewed successor contexts |177/177|177/177|
| Authorized original supersessions |5|5|
| Observed modification regressions |0|0|
| Final AI-free replay |188/188|188/188|
| Replay observation/byte projection identity within track |Exact|Exact|
| Predecessor→successor installed path / existing store |5/5|5/5|

[Functional A](r6_44/FUNCTIONAL-A-final.json),
[functional B](r6_44/FUNCTIONAL-B-final.json), [replay A](r6_44/REPLAY-A.json),
[replay B](r6_44/REPLAY-B.json), [installation A](r6_44/INSTALL-A.json),
[installation B](r6_44/INSTALL-B.json). Cross-track observable result/state/error
projections match for188 observations. Serialized store bytes may differ across
implementations; rejection/read byte identity is required **within** each track.

The checks cover all eight phase/vent/load combinations; invalid ordinary firing/
closed states; missing/invalid gate values; phase/lookup/store error precedence;
blank labels and duplicate IDs; corrupt records; invalid unrelated records;
timestamp/ID sorting; unchanged fields/other records; ordinary and emergency
multi-operation cycles; list/reload; rejection exact bytes and store absence.
Installation changes the executable at one copied application path, preserves its
existing store bytes across replacement, and demonstrates changed behavior on that
same store. This is deterministic cooperating local persistence, not crash,
concurrent-writer or distributed-transaction qualification.

### Preserved scoring-summary correction

Initial [RESULT](r6_44/RESULT.json) and REGRESSION files falsely count one rescue
regression per track by replaying the old emergency sequence: its now-successful
superseded ignite leaves firing state, so the next old rescue invocation correctly
rejects. The pre-author reviewer had already mapped retained rescue/cool/list to
their appropriate successor sequence positions. The additive
[REGRESSION-v2-A](r6_44/REGRESSION-v2-A.json) and
[REGRESSION-v2-B](r6_44/REGRESSION-v2-B.json) use that exact frozen mapping and existing
raw results. [RESULT-v2](r6_44/RESULT-v2.json) is authoritative. No candidate,
expectation, execution or historical evidence was changed to obtain this correction.

### Inherited baseline limitation, independently confirmed

B disclosed a store containing raw `{}` returns `migration_required`, contrary
to the general invalid-store `invalid_state` requirement. Post-submission,
**unscored** AI-free diagnostics check list, set_gate and ignite for both predecessor
and successor. [A](r6_44/DIAGNOSTIC-A.json) returns invalid_state in6/6;
[B](r6_44/DIAGNOSTIC-B.json) returns migration_required in6/6. Both preserve `{}` bytes.
This exact discrepancy is inherited and not introduced by the policy modification.
The frozen182-observation baseline qualifies the tested domain, but does not
establish full starting-contract equivalence. The production intent interface has
no exposed decoder-error override; no production repair or host workaround is made.
The frozen oracle remains unchanged, and these are not retroactively scored tests.

## 5. Development effort and total measurement limits

Actual exported usage, separate from missing values:

| Participant telemetry | A | B |
|---|---:|---:|
| Input tokens excluding reported cache |52,824|71,622|
| Cached input tokens |595,072|471,296|
| Output tokens |5,164|10,493|
| Reasoning tokens reported separately |604|1,417|
| Cache write |0|0|
| Export-accounted tokens, all categories |653,664|554,828|
| Nested tool wall summed |3.842s|16.152s|
| External final syntax check / validation+lowering |0.00159s|0.00415s|
| External first syntax check / validation+lowering |0.00121s|0.04311s|
| External final test execution |9.674s|12.211s|
| OpenCode reported cost |0|0|
| Actual API billing |Unavailable|Unavailable|

B's two participant generation calls additionally record0.05934s and0.05742s
validation/lowering; these are **inside** its participant interval. External first
and final builds share a coordinator process, so final B timing is warm; the first
build and participant build times remain visible. Syntax checking is not semantic
validation. Lowering/integration/installation overhead is retained, not omitted.

[Measurements](r6_44/MEASUREMENTS.json) contain baseline-original, baseline-corrected,
baseline-v2, participant, export and external-scoring/replay intervals. The external
evaluation block is90.536s. Nested tool/test intervals are not added to enclosing
wall intervals. [Workflow wall receipt](r6_44/WORKFLOW-WALL-v3.json) gives the measurable
enclosing coordinator-session→publication interval, including setup, review and
publication elapsed time; it is not an active-time attribution or a complete bill.

Shared reviewer:9 visible completions,13 tools;121,307 input,748,800 cached input,
6,029 output and660 reasoning tokens. The coordinator snapshot captures43 completed
completions/74 tools through its checkpoint:144,182 input,4,108,672 cached input,
21,572 output and3,477 reasoning. These shared costs are not silently excluded or
allocated to one track. Later publication and the coordinator's incomplete current
turn/final response are excluded from that snapshot, so **complete total AI tokens
remain unavailable**. Reported zero cost is not evidence of free API billing.

Python uses less measured participant wall, fresh input and output; B uses fewer
visible completions and fewer total export-accounted tokens because its cache
usage differs. These mixed observations, shared preparation cost, missing billing,
unattested effective reasoning and one trial do not establish economic superiority.

## 6. Impact and architectural interpretation

The independently frozen impact map identifies ignite/set_gate guards, their
dependent load/phase/vent predicates and changed transitions, with unchanged
persisted invariant and unrelated operations. Production
[impact diagnostics](r6_44/IMPACT-DIAGNOSTIC.json) query field:phase, field:vent and
field:load on the legacy scalar base. That graph does not index typed extension
mutation users or their predicate invariant. It therefore omits the central
ignite/set_gate policy users and is incomplete for this modification. It is not
used as an oracle or claimed as a reliable practical impact advantage.

Production typed/binding/effect checks genuinely run. Both B candidates validate
without a rejection; **zero scored defects uniquely prevented by Lykoi** were
observed. No new defect-seeding campaign was run. Guards/invariants are meaningful
runtime semantics, but a well-typed policy still needs requirement-derived tests.
B changes exactly two declarative guards; restoring them reconstructs the accepted
baseline intent. The JSON transport performs no central application computation.

**Interpretation:** the bounded production profile can express and deploy this
genuine shared-policy modification while retaining tested persistence behavior.
Both tracks pass without candidate repairs, so reliability superiority remains
unestablished. Lykoi's additional machinery has demonstrated mechanics but no
measured advantage here, and its inherited decoder error seam prevents full
starting-contract equivalence. Consequently the practical comparison is
**inconclusive**, rather than an advantage verdict or unrestricted equivalence claim.
One synthetic application cannot support statistical significance or generality.

**Next recommendation:** retain the production-backed stateful path as the useful
bounded architecture; require external requirement/error contracts alongside typed
validation, and keep Python as a pragmatic comparator. A separately authorized
baseline-contract clarification/qualification should resolve malformed-store error
semantics before another comparison. Extension-aware impact indexing is another
prospective tooling question. Neither recommendation authorizes production changes,
another trial, expanded benchmarking or an adaptive stateful symbolic architecture.

## 7. Publication and stop

[Publication identities](r6_44/PUBLICATION-IDENTITIES.json) and
[verification receipt](r6_44/VERIFICATION.json) bind new evidence, verify the5,059
protected identities and frozen inputs, retained submissions/replays, R6.43 archive,
JSON/link/whitespace/credential checks and `git diff --check`. The first publication
check rejected unequal raw generated-file bytes; the participant writer used CRLF
and the external writer LF. The [failed check](r6_44/PUBLICATION-ATTEMPT-1.json) and
both identities remain preserved; the corrected check permits only exact CRLF→LF
normalization for regeneration provenance, without altering submitted artifacts.
A [second publication-only failure](r6_44/PUBLICATION-ATTEMPT-2.json) found that link
checking preceded creation of the manifest it linked. Creation now allows only
its two pending manifest/receipt links; final verification requires their existence.
The versioned
[boundary](../../../docs/project-overview-r6.44.md),
[research observations](../../../docs/research-log-r6.44.md) and
[decision](../../../docs/decisions-r6.44.md) preserve prior shared guidance.

**Stopped after this single bounded comparison and publication.** Await explicit
authorization before further review, repair, replay, trials or architectural work.
