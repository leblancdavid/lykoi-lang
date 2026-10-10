# R6.43 measurement readiness assessment

Read-only assessment of existing mechanisms. No model preflight, telemetry service,
export of this coordinator session or new authoring comparison was performed.
Evidence: [R6.16 telemetry source](../../../../experiments/value_added_r6_16/telemetry.py),
[R6.32 journal specification](../../../../experiments/lifecycle_r6_32/SPEC-1.md),
[R6.39 report](../R6_39-REPORT.md) and [R6.40 measurement discussion](../R6_40-REPORT.md).
Past functioning routes are evidence of capability, not a guarantee of future
provider fields, availability or effective reasoning settings.

| Requested measurement | Readiness | Rule / missing information |
| --- | --- | --- |
| Functional correctness | Supported within frozen finite acceptance scope | External exact typed envelopes, bytes, state and errors; validate-only acceptance is insufficient. Acceptance authority must be independent of candidates. |
| Modification regressions | Supported | Retain base cases and test modified artifact; separately report superseded cases, old/new counts, passing-to-failing transitions and store continuity. |
| AI model calls | Partial but demonstrated | Visible completion events, session/message IDs and terminal statuses can count calls. Preserve failures/timeouts/incomplete sessions. Upstream hidden retries are unavailable. |
| Input/output/cached tokens | Partial but demonstrated | Per-call exported usage contains input, output, reasoning and cache read/write; preserve original fields and missingness. Report processed input only using documented provider conventions. No characters-to-tokens estimate. |
| Development wall time | Partial but demonstrated | Monotonic enclosing participant intervals and session timestamps include startup/tools. They omit unmetered coordination unless separately bounded; not pure inference time. |
| Tool/validation overhead | Partial but demonstrated | R6.32 journal and R6.40 dispatch records measure retrieval/admission/validation/expansion/execution. Some metadata stages lack inner intervals. VM logical work excludes these costs. |
| Complete workflow effort | Not reliably complete today | Prior coordinator planning, baseline preparation, freezes, oracle design, export, publication and manual review are not completely metered. New experiment must include these stages or mark total effort unavailable. |
| Provider billing | Unavailable here | SDK reported cost0 is not a billing receipt. Use actual provider receipt with declared accounting period and currency when supplied; otherwise null, not zero or an inferred price. |

## Future minimum ledger, using existing records

Before authoring, specify stages: baseline construction/qualification; requirement
and acceptance preparation/review; setup/preflight; author inspection/modification;
selftests/repairs; validation/generation/retrieval/install; external scoring; export;
analysis/publication. Record start/end, actor, session, submitted artifact hashes,
terminal status, available call IDs/usage and tool intervals for every stage.
Allocate common setup consistently; show unamortized totals. Count failed attempts,
rejected proposals and retained predecessors. Discovery costs, if later authorized,
must include retrieval/admission/documentation and be fully charged to each relevant
contrast, not silently shared away.

Enclosing wall time and nested tool intervals overlap. Show inclusive intervals and
exclusive breakdowns only when established; do not sum nested intervals as total.
Token totals need an explicit per-provider convention, especially cache and reasoning
fields. Exact retrieval-token attribution is unavailable; serialized retrieval bytes
can be reported separately. Missing token fields are null rather than default-zero.
The old R6.16 collector's default-zero subfield behavior is historical; a later study
must disclose incomplete fields rather than inherit a completeness claim.

Separate authoring efficiency among fully accepted matched tasks from all-attempt
effort and failures. A faster structural halt is not faster successful development.
Report changed/unchanged functionality, static rejection and external rejection
separately. One exposed example cannot establish superiority or a stable cost rate.

No attestation of hidden provider context, effective reasoning, pure inference time,
upstream retries or cognitive independence is available. A new independent curator
or reviewer must actually be identified and their permitted input recorded.

**Conclusion:** correctness/regression observations are feasible. Visible model and
tool usage is partially measurable. Complete economic or complete-workflow advantage
is not ready for a strong claim; use a small existing ledger and explicit nulls rather
than build a telemetry platform. A separately authorized study may report bounded
participant effort, but must not label it complete workflow effort while stages lack data.
