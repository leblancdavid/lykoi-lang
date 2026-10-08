# R5.119 fresh pre-access snapshot — P6-A03 preparation only

Recorded UTC **2026-10-08T15:43:05.489869+00:00**, before opening P6-A03
provenance, source or acceptance content. User authorization: R5.119 preparation
only for preserved `redis/redis#13736`; project owner appointed research approver
by this request, with no candidate approval yet. Research-only, not Redis maintainer
or product/deployment authority. No evaluator designated or authority credentials
provisioned in this preparation.

## Git identity

HEAD `aaa1121915b7b3786d430460043556e87a7fae8e`; root tree
`ccd04387d0557f83d08551224c0aae68befbceb0`. Initial and pre-access
`git status --porcelain=v1 --untracked-files=all` and `git diff --stat` empty.
No pre-existing user edits. Snapshot itself is the first R5.119 addition.

| Scope | Git object identity |
| --- | --- |
| src | ef0c20d576a9b52816c025e7a2c8292dda8eb236 |
| src/air_compiler | 87f3c8c1c8b1af394235aa835d39342b770b6c49 |
| schema | 8c04839087c76ab111e1eabb05b3e14e6b36ca1c |
| air | c7abd1483a14cf0c1ca21dd8d2edd3ee3db7ca39 |
| generated | d666daef4f362b2d4423e0be1942954ad4846bed |
| tests | 32d128f556561391919ae7c49a10ebae6c265eda |
| benchmark/evaluation | 68c94828b6b16ad5000d80cb999ff4ecc4233df1 |
| R5_114-KERNEL-ACCOUNTING.json (blob) | cb0f5c566149fae770e270bdbe71d456a03fe8b9 |

## Versions and baseline evidence

Implementation semantics R5.114, kernel **26**; no additions/removals/reclassification.
FRC `FormalRequirementContract-0.1`; compiler/backend `0.3.0`; canonical model
`0.3`; dispatcher `LykoiProgram-1`; representation `LykoiContractV1`; pipeline
`sealed-pipeline-1`; external plan `external-cli-plan-1`; authority `authority-1`;
research approval policy 1 / Phase 6 protocol 2 (R5.118A).

Profiles: collection-query-1, existing-scalar-1, existing-model-1,
existing-composed-1, typed-mutable-values-1, typed-input-values-1,
typed-predicates-1, persistent-references-1, atomic-durable-state-1,
primary-value-interfaces-1, prewrite-authorization-1, typed-computation-1,
elapsed-day-conversion-1, conditional-created-effects-1, historical-related-state-1.
Exact bounds: `docs/phase5-baseline-r5.115.md` and committed specifications.

Relevant recorded tests: R5.118A report records 146 passing tests: research
authority 22, authority controller 34, requirements workspace 26, sealed pipeline
30, compiler 22, application 9, baseline harness 3, plus validation/safety.
R5.114 records 397 tests, 133 synthetic external invocations, and exposed transfer
16/20 successes / 447 invocations. These are **historical results**, not fresh
R5.119 runs. This round runs no baseline tests that could compile, author, project,
or behaviorally verify anything. Fresh checks are limited to source hashes,
candidate FRC envelope/JSON consistency, identities and publication scope.

CPython 3.14.3 / Windows / PowerShell / `D:\Dev\axiom`.
Current model/provider: OpenAI `openai/gpt-6.1-sol` via OpenCode, as reported by
the session. OpenCode build/settings unavailable; no live provider call.

## Exposure, review and stop

Externally authored, procedurally selected R5.116A material; curation previously
saw the sources. Not blinded or pristine held-out. This session will access only
P6-A03 selected capture/provenance/acceptance; no online lookup, fixing PR/commit,
implementation, comments, P6-A04 or P6-A05 content. One same-agent source-only
review, disclosed as SAME_AGENT/SAME_MODEL; expectations independent of generated
implementation, not independent cognition. Stop after review publication. No
approval, grant, seal, structural coverage, BDI, adequacy, V1 projection,
authoring, compilation or external behavioral checks authorized or run.
