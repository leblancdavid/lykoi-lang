# R5.44 — Newly Authorized Locked Whole-Contract Static Support-Transfer

Primary classification: **`R5_44_PROTOCOL_HALT`**.

**Halted before B02 exposure. Zero dispatches, zero completed observations.**
The required pre-exposure verification command was terminated by the shell tool
after 120,000 ms. It produced no persisted prepass, experimental baseline,
authorization receipt or dispatch reservation. The qualified starting state was
therefore not established. No verification retry or B02 evaluation followed.

## Inherited state and new experiment

R5.43 remains **`R5_43_EVALUATION_INFRASTRUCTURE_QUALIFIED`**. Its historical
evidence records 29/29 independent qualification tests, repeated; 393 restricted
harness passes / 36 prohibited-B02 skips; 31 application/compiler passes; 14
R5.41 focused passes; and a coherent 16-profile / 84-row independent matrix.
Those are inherited results, not newly completed R5.44 verification results.

This was a newly authorized experiment using the unchanged R5.43 production
recorder and generic R5.41 support system. It did not invoke or continue the
R5.42 evaluation. R5.42 remains permanently **`R5_42_PROTOCOL_HALT`**.
The intended question was whole-contract static behavioral support, without
comparison to conventional source structure. That question was not reached.

## Pre-exposure verification and exact interruption

Initial `git status --short` was empty. The observation-only orchestration was
written in `r5_44_review.py`; no semantic, profile, compiler, application,
readiness, audit, admission, recorder or canonicalization implementation changed.
Its prepass uses the inherited restriction-aware suite runner, canonical matrix
comparison and independent structural/source/contamination checks. The B02
application loader is confined to the callback of `Recorder.observe`.

Executed once, with tool timeout **120000 ms**:

```powershell
Test-Path -LiteralPath 'D:\Dev\axiom\benchmark\results\phase5c' && python benchmark/results/phase5c/r5_44_review.py prepass
```

Captured output:

```text
True
Axiom validate: ok
```

The tool then reported:

```text
shell tool terminated command after exceeding timeout 120000 ms
```

The output does not establish completed suite results, the outer validation gate
or where within the regression suite execution stopped. Suite output is buffered
by the inherited runner and no R5.44 prepass artifact was persisted. Consequently,
no fresh harness, application/compiler, qualification, focused-test, matrix,
structural-schema, traceability or safety pass is claimed. The interruption is
an execution-envelope failure at the verification gate, not evidence of a
semantic capability gap or a defect in canonical equivalence.

After interruption, a filesystem glob found no `R5_44*` evidence artifacts and
`Get-Process python -ErrorAction SilentlyContinue` found no running Python process.
The stopped-run recorder additionally checked that neither `R5_44-prepass.json`
nor `R5_44-recorder/` existed before recording the halt. The code sequence creates
the recorder directory only after successful prepass; dispatch is a separate
command that was never issued.

## Authority and unchanged-system integrity

After the interruption, only stopped-run accounting and byte-integrity checks
were performed. These did not load B02 into readiness, audit, admission or the
compatible-path evaluator.

| Check | Observed result |
| --- | --- |
| Historical lock | **678/678**, identity/ancestry valid, zero mismatches |
| Prospective lock | **695/695**, identity/ancestry valid, zero mismatches |
| R5.43 infrastructure lock | **731/731**, identity valid, zero mismatches |
| Frozen B01/B02 requirements and B02 profile | Pinned authority hashes unchanged |
| Frozen oracle authority | Saved bytes and original `5064950` member hash agree; not executed |
| Generic implementation contamination | Clean, no findings |
| Core semantics | **30 → 30** |

Lock identities:

- Historical: `e58888b096d317cb6a3f5d2673a901df2c3ed6d25d0b503c323b4b1c1fe4486e`.
- Prospective: `ac53da927f116639c52d7c2df5d6e9574e7cf0b516fa8ac5037a3f6538dca2aa`.
- Infrastructure: `5ded5ebc2a9412883a9796026fec8cd7d9477fa163e05012ac6a3a10a2254242`.

Qualified protocol: **`lykoi-canonical-evidence-r5.43`**.
Qualified production recorder: **`benchmark/evaluation/recorder_r5_43.py`**.
Exact protocol/recorder SHA-256 values and frozen-authority member hashes are
recorded in `R5_44-halt-verification.json`. Their qualified bytes remain covered
by the valid infrastructure lock. Operational observation accounting and
second-dispatch prevention retain their R5.43 qualification; fresh full
qualification reproduction was not established by the interrupted gate.

## Seal, authorization and accounting

The user authorized exactly one static dispatch **after successful verification
and sealing**. Those prerequisites were not completed. No experimental starting
baseline or dispatch authorization receipt was sealed; the authorized dispatch
was not consumed.

After the interruption, `r5_44_halt.py` used the unchanged qualified production
recorder to preserve a canonical **halt-accounting baseline**, explicitly marked
as post-interruption evidence. It is not the missing experimental starting seal.
Halt-accounting baseline identity:

`2c3261016f30759d55ba247660d8b70c848919cb24d3e2bb38bb413782c7df17`.

The halt baseline protects its evidence, both new orchestration files, the
qualified protocol and the production recorder. The recorder writes its halt and
final stop receipts without any `observe` call. Its stopped lifecycle blocks
subsequent dispatch or prepass replacement.

| Accounting event | Evidence |
| --- | --- |
| Before halted-run finalization | 0 reservations / 0 completed observations / `zero` |
| B02 dispatch-start event | **Absent; dispatch never began** |
| B02 dispatch-completion event | **Absent** |
| After halted-run finalization | 0 reservations / 0 completed observations / `zero` |
| Recorder final status | **HALT**, `observation_occurred=false`, `repair_permitted=false` |

This is a zero-dispatch pre-exposure protocol halt, not an incomplete authorized
dispatch or an indeterminate B02 observation. No B02 result is inferred manually.

## Whole-contract results

All B02 support fields are **NOT EVALUATED**:

- Frozen contract count: historical R5.40 registration records 15 operation
  contracts; no fresh contract enumeration or plan formation occurred in R5.44.
- CheckedPlans formed, rejected plans and rejection reasons: not evaluated.
- Readiness and supplemental/static audit: not evaluated.
- Aggregate admission, compatibility relationships and supported application
  paths: not evaluated.
- Whole-contract aggregation and complete behavioral support: not evaluated.
- Unsupported requirements, support-coherence disagreements, configuration gaps
  and potential new-semantic candidates: no finding established.

No smaller contract slice, exploratory exposure, generation or conventional
implementation comparison was substituted for the unmet gate.

## Final integrity and evidence

Evidence beside this report:

- `R5_44-halt-verification.json`: interruption, inherited versions, hashes, locks,
  authority, contamination, scope and unevaluated fields.
- `R5_44-classification.json`: sole primary classification and recorder final state.
- `R5_44-recorder/`: canonical halt baseline, lock, before/after counts, halt and
  final receipts; no reservation or observation receipt.
- `R5_44-final-integrity.json`: final historical/prospective/infrastructure and
  halt-baseline verification, observation accounting, artifact hashes and diff check.

No post-exposure regression suite was run because no exposure occurred. The
interrupted pre-exposure regressions remain incomplete. Final byte locks and
`git diff --check` are checked independently; any LF→CRLF advisory stderr is
recorded separately from the exit status and is not a regression failure.

## End state and next gate

- Exactly **zero** B02 static dispatches and completed observations.
- Zero semantic/profile/compiler/evaluation repairs; zero post-exposure repair.
- Zero B02 generation, execution and frozen acceptance.
- Core semantics **30**, no semantic #31.
- B03 prospectively untouched; B17 unexposed/unclassified; Phase 5C paused.
- R5.43 qualification and R5.42 historical halt preserved.

The sole primary classification is **`R5_44_PROTOCOL_HALT`**.
Recommend a separately authorized investigation of the pre-exposure verification
interruption and its execution budget. Preserve this stopped experiment; any
future transfer evaluation needs a new authorization and its own successful
pre-exposure gate and seal. Generation/execution is not the next gate because
R5.44 established no whole-contract static-transfer result.
