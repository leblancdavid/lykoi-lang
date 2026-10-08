# R5.121 — P6-A03 linked post-first-result semantic evaluation

**`R5_121_P6_A03_POST_FIRST_EVALUATION_COMPLETE`**

**`P6_A03_POST_FIRST_RESULT = STRUCTURAL_COVERAGE_FAILURE`**

The unchanged 26-concept implementation passes exact approval/receipt verification
and FRC validation, then stops at structural coverage. Six obligations have **no
qualified structural mapping**. No BDI, adequacy, faithful V1, authoring, compilation
or Redis acceptance execution follows. This is the separately authorized **linked
post-first-result** attempt, not a pristine first attempt or a replacement result.

The original R5.120 result remains **NEEDS_CLARIFICATION /
RESEARCH_APPROVER_UNAVAILABLE**, byte-for-byte preserved.

## Evidence and bindings

| Deliverable | Retained evidence |
| --- | --- |
| Exact approval/artifact verification and prior-result linkage | [APPROVAL-VERIFICATION.json](r5_121/APPROVAL-VERIFICATION.json) |
| Fresh implementation, Git/tree/kernel/model/provider/time snapshot | [SNAPSHOT.json](r5_121/SNAPSHOT.json) |
| Fresh baseline, artifact-integrity, model-validation and safety output | [BASELINE-CHECKS.json](r5_121/BASELINE-CHECKS.json) |
| Minimal native local receipt | [LOCAL-EXECUTION-RECEIPT.json](r5_121/LOCAL-EXECUTION-RECEIPT.json) |
| Unmodified native result, structural rows and exact failure details | [SEMANTIC-STAGE-EVIDENCE.json](r5_121/SEMANTIC-STAGE-EVIDENCE.json) |
| Immutable terminal post-first-result record | [P6_A03_POST_FIRST_RESULT.json](r5_121/P6_A03_POST_FIRST_RESULT.json) |
| Publication content identities | [PUBLICATION-IDENTITIES.json](r5_121/PUBLICATION-IDENTITIES.json) |
| Read-only integrity/scope verifier | [verify_publication.py](r5_121/verify_publication.py) |

The evidence recorder uses exclusive file creation and refuses a second attempt once
the receipt exists. Content pinning and repository preservation are research audit
measures, not tamper-proof OS storage or production single-use grants.

| Exact approved artifact | Verified SHA-256 |
| --- | --- |
| FRC revision 2, canonical contract | `69d32178bb065e1fa80ac6bb319a1147e3ac7c699a99bb0f56a6db52129ce0f8` |
| Acceptance plan revision 2, canonical plan | `6d0551086fffacc52ce9c35f1d87b127ec181c06120f67b177eefe5f6a1406b3` |
| Original source capture, file bytes | `90132320ad5aa7e7c3996ed97096a798a9ecceea76927a9f9c1948bda58d9970` |
| Composite source, UTF-8 text | `61f939652d67777081306ee0c9d3caeca47872f49af155bab9f2723838f3819a` |

`r5_119a.verify_revision` also verifies physical artifact/publication hashes, original
P6-A03 provenance, literal composite reconstruction, inherited documentary evidence,
revision edge and unchanged fixed expectations. No approved artifact is regenerated.
Its retained `approved: false` preparation metadata is not rewritten: the later exact
human decision is separately retained, as required by the local interface.

### Legitimate local permission

The exact project-owner approval statement is copied literally from the preserved
R5.120 approval receipt. That receipt scoped its attempt to R5.120; it alone is not
reusable attempt permission. The current user instruction separately authorizes
R5.121 against those same identities and specifically selects the local runner.
`APPROVAL-VERIFICATION.json` records both provenance layers and literal current-message
excerpts. The evaluator is the current OpenCode coding-agent session, explicitly
declared rather than fabricated as an authenticated controller principal.

`local.verify_receipt` succeeds before the one `local.execute` call, which independently
verifies it again. Source identity in the receipt hashes the **entire FRC source record**;
it is intentionally distinct from the composite **text** identity. Scope, evaluator,
exact retained decision and current implementation identity all match. This is plain
research permission with conversation attribution, not cryptographic authentication,
Redis-maintainer endorsement, product WHAT approval or deployment permission. No
controller is instantiated and no production approval, seal or grant is issued.

## Fresh snapshot and verification

- Git commit: `4c5b5a2143a5e28204d893a34cb2718fee71ab1f`.
- Initial working tree clean. At snapshot only the new evidence recorder and completed
  baseline output are untracked; the full status is retained in `SNAPSHOT.json`.
- Snapshot UTC: `2026-10-08T17:33:04.147917+00:00`, after baseline checks and before
  receipt issuance/execution. Terminal UTC: `2026-10-08T17:33:14.905513+00:00`.
- Implementation manifest identity:
  `96bc0a1c781409752fd88416fe58e76311744d5a7c77d75d3247f7eb4caa0edb`.
- Kernel: **26**, unchanged R5.114 accounting SHA-256
  `e054c69612a8d3ce2054d0bbfbb6df28acb2bdc522c4d1e0c6feb955b66ae0a3`.
- Compiler/Python backend `0.3.0`; canonical model `0.3`; normal dispatcher
  `LykoiProgram-1`; pipeline `sealed-pipeline-1`; local receipt
  `local-research-receipt-1`. Individual semantic-engine versions and file hashes
  are retained in the snapshot.
- Actual model/provider: **OpenAI `openai/gpt-6.1-sol` via OpenCode**, session-reported.
- **146 distinct baseline tests pass**: local research 13, research authority 22,
  sealed pipeline 30, authority controller 34, compiler 22, application 9,
  scalar normal path 13, external baseline harness 3.
- Canonical model validation passes. Safety passes with **0 capability violations /
  0 invalid transitions**. Artifact-integrity verification passes.
- The first baseline command exceeded the 120-second shell timeout. No receipt or
  external semantic attempt had begun; the baseline alone was rerun with a 600-second
  budget and completed. Duplicate/interrupted tests are not added to the 146 count.
- Publication checks verify snapshot equality, retained historical file hashes,
  model/backend/schema/test/evaluation preservation, approved identities, prior-result
  linkage, native stage ledger, whitespace and the exact additive change scope.

No implementation changes occur after the snapshot. Synthetic regression tests are
baseline evidence, not P6-A03 acceptance observations. No unrelated infrastructure
qualification or other-source evaluation is performed.

## Actual semantic stages and first blocker

| Stage | Actual status |
| --- | --- |
| Exact local approval/receipt integrity | PASS |
| FRC validation and existing relation validation | PASS |
| Structural projection / coverage | HALTED — `STRUCTURAL_COVERAGE_FAILURE` |
| BDI | NOT_REACHED |
| Adequacy | NOT_REACHED |
| Faithful V1 | NOT_REACHED |
| Acceptance coverage / executable binding | NOT_REACHED |
| Lykoi authoring | NOT_REACHED |
| Compilation | NOT_REACHED |
| External behavioral verification | NOT_REACHED |

The unchanged dispatcher in `src/lykoi_pipeline/contracts.py` finds no selected typed
profile for these exact general `invariant` / `transition` / `effects` relations. Its
fallback projection marks **A03-E1, A03-E2, A03-I1, A03-I2, A03-H1 and A03-I3**
`UNSUPPORTED`, each justified by `No qualified structural mapping`. Coverage rejects
that list without omitting obligations or substituting a smaller contract.

**A03-H2 alone is marked REPRESENTED** because the fallback retains `effects` relations
and exposes an `external_effect: MEANINGFUL` channel. Its operation has empty facts
and authority. This is retention of an effect obligation, **not** a demonstrated
ordered ACL evaluator, adequacy result or executable grant/revoke implementation.
BDI is not called, including for this row. There is no downstream BDI verdict.

The measured blocker is **structural semantic integration / representation**, not
authority, a compile error, a backend runtime defect or evaluation infrastructure
failure. It shows the exact approved contract cannot enter the current qualified
semantic composition path. It does not prove a minimal-kernel impossibility.

## Precise capability diagnosis — observations versus hypotheses

This is a source/evidence-based diagnosis after the terminal halt, not another stage
execution, alternative contract, attempted authoring or implementation repair.

| Behavior family | Observed boundary and composability assessment |
| --- | --- |
| Ordered permission-set transformations (H1/H2) | H1 is unmapped; H2 is retained only as a generic effect. Finite sequences, selection, membership, transitions and atomic commit provide ingredients. Existing pointwise map and fixed ordered input pipelines do not by themselves establish an accumulator-dependent fold over arbitrary ACL rule lists, category expansion, or set subtraction. Investigate general ordered transformation/composition expressiveness; no new primitive is proven necessary here. |
| Command/category membership (E1/E2/I3) | Exact invariant relations are unmapped. Typed identities, reference collections, equality and membership already have meaning; ordinary finite category/member data and guards are plausibly composable. The missing qualified source-to-typed mapping is real, but a category-specific kernel primitive is not justified. Narrow preservation of other memberships remains an obligation, not a guessed baseline inventory. |
| Grant/revoke precedence (I1/H1/H2/I3) | Last applicable add/remove behavior is source-fixed, not underspecification or author freedom. It may be derivable from an ordered rule transformation or suitable order-sensitive selection of applicable rules. No current complete mapping was demonstrated. Neither permanent explicit-denial priority nor explicit-grant immunity may be invented. Precedence is not automatically a separate primitive from ordered processing. |
| Connection-local selected database (I2) | The authenticated-connection transition is unmapped. A selected-database field and guarded transition are abstract state ingredients, but current durable one-store records do not establish per-connection lifetime, isolation, authentication binding or routing subsequent operations. Those may need a general execution-context/state-scope interface or new lifetime meaning; this round cannot decide that by renaming durable state. |
| Inherited ACL behavior (H1/H2/I3) | Approved pinned documentation settles the ordinary rule-order authority in this bounded scope. The blocker is not the old unanswered ordering question. Retaining the processor, unrelated commands and narrow membership frame needs faithful general composition; there is no requirement for a new primitive named inherited ACL. Modules/selectors/cluster/version-wide behavior remain outside scope. |
| Backend/protocol and acceptance | No generated target exists and no interface trial is reached. Existing Python CLI/controlled-host execution does not establish Redis-compatible persistent connections, command dispatch, ACL setup/category queries or database routing. These are backend/adapter concerns unless a general state-scope meaning is independently found missing. They were not tested or repaired. |

Existing composition evidence comes from the versioned typed mutable-value,
persistent-reference and prewrite authorization interfaces, not from executing this
Redis requirement. Generic set policies can use existing typed predicates; permission
testing alone is not ordered permission construction. A claim of genuinely new meaning
requires an independent expressiveness argument beyond this structural refusal.

## Acceptance evidence and limits

**NOT_REACHED; zero P6-A03 acceptance executions; no executable identity.** The unchanged
approved plan fixes seven check groups, twelve mixed-rule rows, four direct-command
controls and category-membership checks. Its retained `native_plan` is **null** and it
is not an `external-cli-plan-1` payload. That known artifact fact is not a newly observed
integration-stage failure: the structural blocker comes first and the runner never
checks acceptance coverage. If that stage were reached under another authorization,
the existing runner's missing-payload guard would apply; it is not executed here.

No Redis-compatible acceptance executability has been established. No Redis probe,
simplified simulation, adapter, protocol handler or generated-Python patch is produced.
Do not replace the actual terminal result with `EVALUATION_INFRASTRUCTURE_FAILURE` for
an unexecuted downstream stage.

## Generalization and stop

The existing system carries this real external requirement through legitimate local
permission and FRC validation, **but not through structural coverage into BDI or HOW**.
This is diagnostic evidence of a qualified representation/composition boundary outside
the exposed task-manager corpus. It is not successful Redis generalization, an
upstream-compatible implementation, a behavioral failure of generated software, a
proof that the 26 concepts cannot express the behavior, or evidence that each missing
surface needs its own primitive. Source selection was procedural; prior preparation
exposed it, and source interpretation uses the same model/agent context. No blinded,
held-out or independent-cognition claim is made.

A separately authorized **general** investigation would be justified into source-to-
typed relation mapping, order-sensitive finite set/rule transformations, and scoped
session-state composition, using non-Redis examples and explicit expressiveness bounds.
Only demonstrated new meaning should motivate kernel growth. Backend/interface and
fixed-plan execution preparation would be a separate integration investigation, with
fresh exact approval before any later authoring. These are recommendations only.

Historical first result, approved artifacts, curation and reports are preserved;
kernel/model/compiler/backend/production authority remain unchanged. No P6-A01/P6-A02
revisit or P6-A04/P6-A05 access. **Stopped after this one terminal post-first-result
publication; no repair, retry, adapter work or next round.**
