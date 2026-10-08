# Local research execution 1 — R5.120A

Implemented in `src/lykoi_research/local.py`. This is an experimental execution
interface, with **no production authority**. [Protocol 3](phase6-generalization-protocol-r5.120a.md)
governs prospective use; prior protocols and first results retain historical force.

## Two workflows

| Workflow | Approval and execution | Authority boundary |
| --- | --- | --- |
| Production / authenticated controller | Existing authenticated principals, exact controller artifacts, approvals, seals, grants and journals | Existing production checks unchanged; production adoption/release needs its applicable authority |
| Local research | Exact retained human research decision, content-bound receipt, native semantic functions, restricted author worker, external subprocess verification | Plain research data only; no controller connection, credentials, seals, grants or deployment approval |

Local receipts are not `authority-1` envelopes. The runner does not instantiate a
controller or invoke its dispatch. Existing authenticated research workflow 1
remains available; it is not required for this explicitly local workflow.

## Human decision and trust input

An actual human supplies permission to experiment against exact source/FRC/acceptance
identities and a named evaluator. Preserve their **exact statement** and attributable
provenance. The caller retains this as `approved`, independently of the receipt and
author. AI recommendations and a generated `approved: true` are insufficient.

Conversation attribution is decision evidence, **not cryptographic authentication**.
The evaluator name is a declaration, not an authenticated principal. This lightweight
API cannot prove the human's identity, natural-language completeness, past exposure,
or pre-author chronology from a hash. Those are inspectable research provenance and
review obligations, not fabricated security guarantees. Synthetic approval statements
in the tests are explicitly role simulation under the user's synthetic-round permission.

## Minimal receipt

Closed record with exactly:

- `version: local-research-receipt-1`;
- `approval`: closed string-valued record with `requirement_id`, `source_identity`,
  `frc_identity`, `acceptance_identity`, `human_statement`, `provenance`, `evaluator`,
  `purpose: local-research-only`;
- `implementation_snapshot`: SHA-256 of the canonical path-to-file-hash manifest;
- `recorded_at_utc`: observed timezone-aware UTC timestamp, not a human signing time.

`digest` uses the existing CJ-1 canonical JSON/SHA-256 utility. Source identity hashes
the entire exact FRC source record (ID, classification, text and text hash). Preserve
external locator/revision/original-capture provenance with the retained approval/source
records; the source ID must identify that exact capture. FRC identity hashes the complete
contract; plan identity hashes the complete approved **existing native execution plan**,
including case identities, checks, expectations, coverage and limitations. JSON formatting
is not behavioral content; original files remain untouched.

`implementation_snapshot()` returns the reproducible manifest: all current `src/**/*.py`,
the existing FRC/BDI/adequacy/V1 engines, canonical application model, R5.114 26-concept
accounting, and the three public qualification/fixture test modules. This is content
provenance and an equality check, not machine/model qualification or a runtime freeze.

`receipt(approved)` records supplied permission, snapshot and UTC time. It does not
approve anything. `verify_receipt(record, approved, source, contract, plan, evaluator)`
requires literal equality with the separately retained human decision, correct scope
and evaluator, all three artifact digests, exact FRC-source equality, current snapshot
identity and UTC timestamp shape. Any mismatch halts before semantics. The runner
copies these inputs and rechecks them before authorship and external verification.

For an approved plan lacking an executable native payload, do not invent one or replace
expectations. The local adapter halts `RESEARCH_ACCEPTANCE_BINDING_REQUIRED` when reached.
An approved high-level plan is not by itself an executable backend/verifier interface.

## Narrow execution entry point

```python
from lykoi_research.local import receipt, execute

# These are retained human-approved artifacts, loaded without regeneration.
record = receipt(approved)
result = execute(record, approved, source, frc, acceptance_plan,
                 evaluator=approved["evaluator"], run="separately-authorized-attempt-id")
```

`execute` accepts no controller, controller path, credential, role registry, arbitrary
author callback or verifier success callback. An optional `author_fixture` is only the
existing explicit public fixture interface, principally for negative calibration.
Normal supported profiles use the existing fixed author worker automatically. Author
input is V1/toolchain/run/fixture; no approved expectations are delivered to it.

The runner calls the unchanged pipeline functions in order:

1. FRC validation and existing relation validation; unresolved issues halt clarification.
2. Structural projection and coverage; unsupported/omitted obligations halt.
3. BDI; any non-supported result halts `UNSUPPORTED_BDI_SCOPE`.
4. Adequacy; a non-adequate result retains its native status, including
   `IMPLEMENTATION_UNDERSPECIFIED`.
5. Faithful V1; unrepresentable source halts without authorship.
6. Existing acceptance coverage/source-binding checks against the exact supplied plan.
7. Existing restricted author subprocess; supported profiles must equal the existing
   faithful `author(normalized)` mapping.
8. Existing compiler dispatcher/validator/lowering via `profiles.generate`; errors
   retain `COMPILATION_FAILURE`.
9. Existing `external_execute` and its `classify_observations`; finite external behavior
   determines `BEHAVIORALLY_VERIFIED`, behavioral failure or runtime failure.

Research approval supplies permission to call these functions, **not stage success**.
No production review/seal/grant receipt is synthesized. Structural coverage and native
checks are computed, not supplied by the author; source-only substantive review and
exact human approval are prerequisites retained outside the author. This is a local
semantic execution workflow, not a claim to have traversed controller authority stages.

The returned `local-research-result-1` records purpose, receipt identity, run, stage ledger,
native evidence, first blocker and UTC completion time; `production_authorized` is always
false. A blocker makes that stage `HALTED` and every later stage `NOT_REACHED`. The caller
publishes the result and actual provenance. There is no retry service or approval database.
Each external attempt needs separate permission/linkage; function availability is not
permission to rerun or a cryptographic single-use token.

## Acceptance and isolation

Expectations must be source-derived and fixed before authorship. The runner never
produces/falls back to a generated plan and never repairs expectations after failure.
The existing external verifier owns observations/classification in fresh case-local
processes. Producer output cannot certify success. Finite same-agent synthetic coverage
is methodology evidence, not independent cognition or held-out generalization.

Tests demonstrate that production refuses receipt strings as credentials, unknown
receipt identities as approval/grant subjects, receipt/reserved-artifact registration,
and even a normally registered context containing a receipt as a grant subject. They
also compare the test production database bytes/revision/events before and after a
local run. Intentionally attempted production refusals are audited by production;
those audit events are measured separately from the local execution's zero changes.

This is isolation of the **research authority interface**, not hostile Python/OS
containment. The existing worker's audit hooks and verifier processes are bounded
cooperative fixtures. Ordinary generated code or a copied target file is not a
deployable approval artifact and receives no release permission from this runner.

## R5.120A boundary

Synthetic/public contracts only; [qualification](../benchmark/results/phase6/R5_120A-REPORT.md).
Kernel 26, FRC/BDI/adequacy/V1/compiler/backend/acceptance semantics and production
security unchanged. No P6-A03 software or Redis probes, no P6-A04/P6-A05 inspection.
The P6-A03 first result remains immutable. Later use must be separately authorized
and labeled **linked post-first-result research attempt**. Source-specific executable
acceptance and Redis backend readiness have not been established in this round.
