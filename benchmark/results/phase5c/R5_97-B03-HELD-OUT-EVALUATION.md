# R5.97 — B03 held-out evaluation

**`R5_97_B03_HELD_OUT_EVALUATION_COMPLETE`**

**`B03_FIRST_RESULT = DECISION_DISCOVERY_UNSUPPORTED`**

Native result: **`STRUCTURAL_COVERAGE_FAILURE`** at
**`STRUCTURAL_PROJECTION_COVERAGE`**, affecting **9/9** identified obligations.
The result was recorded at **2026-10-06T18:18:22.068907+00:00** before this report
or any post-result analysis. Round completion does not mean benchmark success.

## 1. Pre-B03 snapshot

[Fresh snapshot](R5_97-PRE-B03-SNAPSHOT.md):

- Git HEAD: `8c4240ae85336bc8700b788e44cc7f5b88f3c2d7` (`r5.96`).
- Started UTC: `2026-10-06T18:11:37.059564+00:00`.
- Finished UTC: `2026-10-06T18:14:30.285440+00:00`.
- Working tree: clean before and after checks, before snapshot publication.
- Core serialization/semantics: **0.3**; Python backend: **0.3.0**.
- Representation: **BenchmarkDocumentContractV1 / BehavioralContractV1**.
- Python: **CPython 3.14.3**, Windows; executable recorded in the snapshot.
- Active model/provider: **`openai/gpt-6.1-sol` / OpenAI**.
- Explicit attestation: B03 had not previously been inspected and remained unread.
  This is an operator attestation supported by inherited history, not proof of
  every possible prior exposure.
- Snapshot SHA-256:
  `63665039ad86c27f07c2ba56d9643987a4c7f8733e37720217579ef0c7ade45e`.

The existing `python -m lykoi_research.snapshot` command ran with
`--confirm-b03-unread --model openai/gpt-6.1-sol --provider OpenAI --output
benchmark/results/phase5c/R5_97-PRE-B03-SNAPSHOT.md`. All ten selected commands
exited **0**: model validation/safety and **190/190** tests:

| Suite | Passed |
| --- | ---: |
| Compiler | 22 |
| Application | 9 |
| Authority controller | 34 |
| Requirements workspace | 26 |
| Sealed pipeline | 30 |
| Public rehearsal | 33 |
| V1 document contract | 33 |
| External baseline | 3 |

These are pre-access baseline checks, not B03 verification. No infrastructure
qualification, protected activation, historical candidate eligibility, or model
switch was required or attempted.

## 2. Exact source and first access

[Access record](R5_97-B03-ACCESS.json) retains the exact UTF-8 source text and
physical-byte commitment, without newline normalization or source rewriting.

- Identity: **B03 — List by tag (local)**.
- Source: `benchmark/requirements/B03.md`, **385 bytes**.
- SHA-256: `56c6ac4c187962c71d5866b27f9568c8b6de055a0bab074896ef41b61a554630`.
- First read started UTC: **`2026-10-06T18:15:12.391794+00:00`**.
- Read completed UTC: `2026-10-06T18:15:12.412158+00:00`.
- Transition: **HELD_OUT_UNREAD → EXPOSED_TO_FORMALIZATION**.
- At access the only untracked files were the fresh snapshot and
  `R5_97-access.py`, the one-time evidence-capture script. Their exact paths
  are in the access record; no evaluated machinery had changed.

Exact behavioral body:

```text
Add `list-tag --tag VALUE`. Return tasks whose `tags` contains exactly VALUE
(case-sensitive; query input is not trimmed), including completed tasks, in
normal order. Reject blank or whitespace-only query input with `invalid_tag`.
A tag not present returns `[]`; the query never changes storage. For example,
`work` does not select a task tagged `Work`.
```

The original heading bytes/text are retained in the access record, including its
existing separator character. The benchmark source was not rewritten.

[Context evidence](R5_97-CONTEXT.json) commits to the frozen shared
`benchmark/baseline.md` and `benchmark/requirements/README.md`. They supply
the existing JSON subprocess success/error interface, cumulative compatibility,
and **`(created_at, id)` ascending** meaning of normal order. This authority is
benchmark documentation, not inferred conventional behavior or hidden answers.
No B04 requirement, hidden B03 acceptance case, or other-track B03 solution
was accessed. The snapshot's public baseline tests are separately disclosed.

## 3. Obligations and formalization

[FRC candidate](R5_97-FRC.json) uses the existing truthful protected-provenance
variant **FormalRequirementContract-protected-0.1** and
**PROTECTED_EVALUATION**, not a false PUBLIC/SYNTHETIC label. The existing
R5.94 compatibility module validates it without a protected controller invocation.
No new FRC vocabulary or compatibility patch was added.

| Stable ID | Required observable behavior |
| --- | --- |
| B03-REQ-001 | Expose `list-tag --tag VALUE` through the existing task CLI. |
| B03-REQ-002 | Return all and only tasks whose tags contain exactly VALUE. |
| B03-REQ-003 | Match case-sensitively; `work` does not match `Work`. |
| B03-REQ-004 | Use the query verbatim; do not trim it for matching. |
| B03-REQ-005 | Include qualifying completed tasks. |
| B03-REQ-006 | Return tasks in baseline `(created_at, id)` ascending order. |
| B03-REQ-007 | Reject blank/whitespace-only input with `invalid_tag` through the existing error interface. |
| B03-REQ-008 | Return `[]` when no tag matches. |
| B03-REQ-009 | Never mutate storage, on success or rejection. |

Exact source quotes, stable IDs, domains, frames and provenance remain in the
candidate. Shared compatibility is retained in its context rather than inventing
a new task schema or weakening earlier behavior. No new assumptions, clarification
answers, owner resolutions, or necessary-implication clauses were invented.

[Inventory](R5_97-SOI.json) and [formalization evidence](R5_97-FORMALIZATION.json)
retain exact character spans, complete line accounting, nine source items and
nine obligation mappings. The inventory was persisted before the FRC artifact.
The FRC passed the unchanged native structural validator with canonical commitment:

`ef80ce829df154d9405fa409d0ffffef67bf9325855af66d5446c4bab2b5a83c`.

**Formalization scope limitation:** this is current-model research drafting and
same-context source/FRC reconciliation. An independent/blind reviewer, independent
SOI commitment, content-bound approval receipt and owner-approved WHAT seal were
**not established**. No alternate identity was assigned to claim independence.
Thus candidate production/validation succeeded; fully independently approved
formalization did not occur. The source remains benchmark authority; this draft
is not a production implementation authorization. The simplified research run
called pure structural functions on the preserved candidate to obtain a negative
support result, rather than fabricating controller approvals.

No material ambiguity or conflict was detected by this agent. “Normal order” is
resolved by explicit benchmark authority. Blank/whitespace-only terminology is
retained rather than replaced with a newly selected whitespace algorithm. This
finding is a bounded interpretation, not independently established completeness.

## 4. First terminal analysis and stage accounting

The unchanged functions selected were:

1. `lykoi_protected.compatibility.frc.validate(contract)`;
2. `lykoi_protected.compatibility.contracts.structural(contract, commitment)`;
3. `lykoi_protected.compatibility.contracts.coverage(contract, projection)`.

The compatibility view uses the preserved `lykoi_pipeline/contracts.py` semantic
implementation. It changes historical provenance acceptance through its existing
recipe; R5.97 adds no recipe, semantic, structural or analysis rule.

[Structural evidence](R5_97-STRUCTURAL.json) contains all nine obligation rows,
each marked **UNSUPPORTED / No qualified structural mapping**, and no projected
operations. Current structural mappings support only specific bounded relation
shapes. In particular, `filter_order` only maps its explicit **unconstrained**
ordering shape; B03's fixed ordering must not be converted to that shape. The
existing task-create CRUD shape cannot stand in for a tag-query CLI, and no
generic transition adapter handles the rejection/read-only clauses.

The coverage function raised:

```json
{
  "code": "STRUCTURAL_COVERAGE_FAILURE",
  "details": {
    "unsupported": [
      "B03-REQ-001", "B03-REQ-002", "B03-REQ-003",
      "B03-REQ-004", "B03-REQ-005", "B03-REQ-006",
      "B03-REQ-007", "B03-REQ-008", "B03-REQ-009"
    ]
  }
}
```

This was the first native terminal failure. The reporting class
**DECISION_DISCOVERY_UNSUPPORTED** uses the existing R5.83 taxonomy's unsupported
structural annotation/discovery-scope category; it does not claim the BDI engine
returned `OUTSIDE_ANALYSIS_SCOPE`, because the BDI engine was never called.

| Stage/question | Actual outcome |
| --- | --- |
| FRC drafting/native validation | Candidate produced and structurally valid; independent approval not established. |
| Structural projection | Ran; 0/9 supported, 9/9 explicitly unsupported. |
| Structural coverage | Ran; `STRUCTURAL_COVERAGE_FAILURE`; terminal. |
| Behavioral Decision Discovery | NOT_RUN after structural halt. |
| Implementation adequacy | NOT_RUN; adequacy and underspecification both undetermined. |
| Faithful complete V1 representation | NOT_RUN; full representability undetermined by this evaluation. |
| Lykoi authoring | NOT_RUN. |
| B03 compilation | NOT_RUN; no authored B03 model or generated implementation. |
| Runtime/behavioral verification | NOT_RUN; no software produced to verify. |

[Stage evidence](R5_97-STAGES.json) explicitly records representation and all
unreached stages. No missing-mapping or language-capability classification was
substituted for the earlier structural halt. No downstream mapping, BDI or
adequacy probe was run to search for a preferred result.

## 5. Preservation and integrity

[Immutable first-result record](R5_97-B03_FIRST_RESULT.json) binds snapshot,
source/access, formalization, inventory, structural/stage evidence and both
one-time research scripts by SHA-256. Its separate
[commitment](R5_97-B03_FIRST_RESULT.sha256) binds the exact result bytes.
Evidence writers use exclusive creation and refuse an existing first result;
neither script is permission to rerun B03. Immutability here is a retained,
hash-bound research record and no-overwrite discipline, not a hardware/WORM claim.

At result recording, `git diff HEAD` over source, schema, canonical model,
generated output, rehearsal configuration, evaluation machinery, requirements,
harness and conventional track was empty. **No Lykoi machinery was changed after
B03 access and before the result**, and none was repaired afterward. Added scripts
capture source/evaluation evidence; they are not installed shared formalizers,
BDI families, mappings, author prompts or verifier capabilities.

The result precedes status/report edits. A final evidence-only audit verifies
its commitments and unchanged machinery without replaying the evaluation or
reading the benchmark source again. Reports and documentation are the only
subsequent work. Historical frozen records and achieved comparative histories
remain their original evidence.

## 6. Required final analysis

1. **Snapshot?** Fresh clean-tree snapshot at the recorded HEAD, with all selected
   checks passing, current versions/model/provider, UTC times and unread attestation
   (section 1).
2. **Exact requirement?** Original 385-byte B03 source and hash, preserved verbatim
   in the access record, with frozen shared contract context (section 2).
3. **Obligations?** The nine stable source-anchored clauses above (section 3).
4. **Ambiguities/conflicts?** None detected in same-context interpretation; normal
   order has explicit authority. No independent completeness claim.
5. **Formalization succeeded?** Candidate drafting and native validation succeeded;
   independent review/approval and an owner-sealed WHAT were not established.
6. **Structural/decision analysis succeeded?** Structural processing ran and
   explicitly failed coverage. BDI did not run.
7. **Implementation-adequate?** Not established; adequacy did not run.
8. **Faithfully representable through current V1?** Undetermined; representation
   was not reached. There is no complete B03 V1 package.
9. **Authoring?** No.
10. **Compilation and success?** No B03 compilation; baseline compiler tests are
    separate pre-access evidence.
11. **Behavioral verification?** No B03 behavioral verification.
12. **Exact first result?** `DECISION_DISCOVERY_UNSUPPORTED`, native
    `STRUCTURAL_COVERAGE_FAILURE`, with all nine unsupported IDs retained.
13. **Termination layer?** FRC-to-structural-interface coverage, before BDI.
14. **Machinery changed in the protected interval?** No; Git drift evidence is
    empty and evidence scripts are separately identified.
15. **What does this tell us?** The current automatic structural bridge cannot
    carry this preserved tag-query candidate into the decision-analysis pipeline.
    Removal of infrastructure gates exposes a concrete bounded product-analysis
    limitation, without dropping any obligation to progress.
16. **What does it not tell us?** It does not prove that V1 or Lykoi's core language
    fundamentally cannot express tag querying, that the compiler is wrong, or that
    generated software would fail behavior. No software was authored. It also
    does not establish reliable independent formalization, universal analysis,
    model/provider independence, comparative superiority, or complete B03 behavior.
17. **Next investigation, deferred?** In a separately instructed round, first
    independently review this exact source/candidate and its cumulative context;
    then investigate the general structural-annotation boundary for read-only
    collection queries, exact predicates, fixed ordering and validation/state
    frames using public/synthetic examples. Separate limitations of the automatic
    adapter from fundamental representation and language limitations. Do not add
    B03-specific shortcuts. Any later B03 work is post-exposure evidence; use a
    new unseen requirement for subsequent pristine held-out evaluation.

## 7. Honest benchmark status and stop

B03 is permanently **exposed to formalization and structural analysis**. It is
**not exposed to Lykoi authoring**, and **not evaluated behaviorally** in R5.97.
No post-exposure Lykoi development has been performed in this round. Current
overview, decisions, research log and entry-point status now reflect this outcome;
historical R5.96/earlier unread declarations retain their original round scope.

The first result, evidence and report complete R5.97. **No repair, improved
second attempt, B03 rerun, or B04 access follows.**
