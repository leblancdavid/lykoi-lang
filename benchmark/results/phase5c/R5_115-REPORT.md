# R5.115 — Phase 6 generalization research transition

**Final classification: `R5_115_PHASE6_RESEARCH_READY`.**

Planning and baseline preservation are complete. The next research priority is whether
the compact representation generalizes beyond the exposed task-management corpus.
No new source was selected, generated, inspected or evaluated, and no Lykoi capability,
compiler/backend, schema, model, generated artifact, test or oracle was changed.

## Deliverables

| Deliverable | Record |
| --- | --- |
| Phase 5 exact baseline, versions, capabilities, limitations and tests | [Baseline](../../../docs/phase5-baseline-r5.115.md) |
| Phase 6 questions, diversity and entry criteria | [Research plan](../../../docs/phase6-research-plan-r5.115.md) |
| External-source independence policy | Research plan, external-source policy section |
| Lightweight first-result protocol and result taxonomy | [Protocol](../../../docs/phase6-generalization-protocol-r5.115.md) |
| Kernel-growth accounting and gap distinctions | Protocol, accounting section |
| Future AI-efficiency comparison outline and deferred backlog | Research plan, deferred sections |
| Direction, tradeoffs and observations | `docs/project-overview.md`, `docs/decisions.md`, `docs/research-log.md` |
| Current entry-point/workflow discovery | `AGENTS.md`, `docs/agent-workflow.md`, `README.md`, `benchmark/README.md` |

## Evidence and preservation

Start commit `694c4e02f13111e65781e48e69da97c1ea6f4502`, root tree
`82152054ba76f049dd85f3e7d389f2bd64aedee6`, clean tree before documentation edits.
Preserve R5.114's **26 concepts**, **397 passing tests / 30 commands**, **133 synthetic
invocations**, and **16/20 B01–B16 / 447 exposed transfer invocations**. Native B17–B20
formalization disputes and B18/B19 downstream `NOT_REACHED` remain intact. All original
benchmark evidence and immutable first results remain historical evidence, not new runs.

Fresh default checks passed: validation, safety (0 violations/invalid transitions),
**22 compiler + 9 application + 3 external baseline = 34 tests**. No broader rerun is
claimed. Baseline receipt and actual fresh checks are distinguished in the baseline
record; current shared implementation/tests remain unchanged. A shell quoting error
on root-tree provenance was corrected with no file mutation.

Scope audit passed: `git diff --check`, individual new-file `git diff --no-index --check`,
and changed-path/diff review. `git diff --exit-code HEAD` reports no changes for `src`,
`schema`, `air`, `generated`, `tests`, `benchmark/requirements`, `benchmark/harness`,
`benchmark/evaluation`, `benchmark/conventional`, `experiments` or tracked
`benchmark/results/phase5c` evidence. HEAD/root-tree identities remain unchanged.
Final worktree: seven modified guidance/status Markdown files and four new deliverable
Markdown files, uncommitted. Documentation-only differences are prospective; no historical report,
lock, requirement, oracle or result is rewritten. No executable protocol/telemetry,
qualification, activation or new infrastructure is added. No new held-out semantics
are present in these deliverables. Existing regression sources remain exposed.

## Completion answers

1. **Exact baseline:** the commit/root tree above, canonical model 0.3, compiler 0.3.0,
   LykoiProgram-1 and pinned supported profiles/V1, 26-concept ledger, R5.114 evidence
   and today's 34-test recheck; clean initial tree and environment/model provenance.
2. **Questions:** Q1 unfamiliar-software representation; Q2 stability versus irreducible
   kernel growth; Q3 independently accepted behavior; Q4 later AI-development efficiency.
3. **Independent sourcing:** external curator, real-world specifications/public issues,
   independent humans or isolated inventory-blind AI, exact source/version/provenance
   retained, no development semantic access before evaluation. No capability-based selection.
4. **First result:** snapshot → source identity/exposure → legitimate formalization/
   clarification → unchanged pipeline → independent acceptance when reached → immutable
   terminal record → stop. Preserve native codes/stages and `NOT_REACHED` downstream.
5. **Correctness:** source-only independent expectations fixed before authoring; external
   observations of exact builds, criterion-to-source coverage, bounded tests and unverified
   behavior reported separately. Generated software cannot define its own correctness.
6. **Growth:** per-source concept/composition ledger, separate later candidate investigation,
   admitted growth and reclassification history; new functionality is not automatically core.
7. **Gap distinction:** an absent connection between existing meanings is integration debt;
   target lowering/storage is backend debt; only evidenced absent observable meaning is a
   semantic candidate. Authority/authoring/evaluation failures do not imply new semantics.
8. **Deferred efficiency:** input/context and output tokens, calls, repairs, elapsed time,
   changed semantic nodes/conventional files and lines, correctness/regressions; optional
   receipts/diffs later, `N/A` allowed, no framework or prerequisite now.
9. **Entry criteria:** recorded baseline, passing/documented regressions, protocol,
   independence policy, immutable first-record procedure and taxonomy. All complete;
   no universal correctness, exact-machine qualification or security certification gate.
10. **Next concrete action:** a separately instructed independent curator sources/fixes
    the small multi-domain batch outside development context; refresh the snapshot before
    first delivery and attempt the unchanged pipeline. R5.115 does not begin that action.

**Stop after R5.115 documentation.** Methodology readiness is not held-out success,
production readiness, kernel minimality or an AI-efficiency claim.
