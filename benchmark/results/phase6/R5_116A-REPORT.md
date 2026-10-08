# R5.116A — Procedural open-source requirement curation

**`R5_116A_PROCEDURAL_OPEN_SOURCE_BATCH_CURATED`.**

The batch contains five real public issue sources from five projects/functions.
It is **Externally authored, procedurally selected evaluation material.** It is not
independently blinded curation, upstream-approved requirements or held-out generalization
evidence. The development curation session has seen all selected source bodies.

## Prospective amendment and chronology

R5.116's `R5_116_BLOCKED_CURATOR_SEPARATION_UNAVAILABLE` report is preserved unchanged.
The user authorized a prospective procedural alternative, not a retrospective correction.
Starting commit: `185073db0667ab10cdf033c03846548f21b48fac` (R5.115).
Initial worktree already contained the preceding R5.116 reporting/status edits.

Before any candidate description request, the fixed
[selection policy](r5_116a/SELECTION-POLICY.md) was committed alone:
`c840083469efc9f94920ebce41103a51092ac915` (`r5.116a selection policy`).

- Policy commit: **2026-10-08T13:50:52Z** (Git records `06:50:52-07:00`).
- First candidate description request: **2026-10-08T13:52:20.312335+00:00**.
- Batch/hash fixation: **2026-10-08T14:00:12.628086+00:00**.
- Policy was neither amended nor replaced after issue inspection.

The fixed purposive frame names jq, curl, Redis, pip and pytest in that order, chosen
for ordinary application function before querying issues. Creation cutoff is 2025-01-01;
GitHub issue search is oldest-created-first, all states, one result per page, at most
15 candidates per repository. No repository replacements. Fixing PRs, commits, comments,
timelines, linked context and implementation files are outside the permitted context.
This is a reproducible captured procedure, not random sampling or unbiased cognition.
Eligibility judgments still involve interpretation and are openly recorded.

## Selected batch

| ID / order | Exact public issue | Project function | Candidate page |
| --- | --- | --- | --- |
| P6-A01 / 1 | [jqlang/jq#3228](https://github.com/jqlang/jq/issues/3228) | JSON data processing | 2 |
| P6-A02 / 2 | [curl/curl#15914](https://github.com/curl/curl/issues/15914) | Network data transfer | 1 |
| P6-A03 / 3 | [redis/redis#13736](https://github.com/redis/redis/issues/13736) | Database/server storage | 6 |
| P6-A04 / 4 | [pypa/pip#13139](https://github.com/pypa/pip/issues/13139) | Software package installation | 1 |
| P6-A05 / 5 | [pytest-dev/pytest#13101](https://github.com/pytest-dev/pytest/issues/13101) | Automated testing | 2 |

Five distinct project functions are represented, though all belong to the broad
software-tooling/systems ecosystem. No broader business-domain diversity claim.
No requirement was rewritten, dropped for difficulty or fitted to the 26 concepts.
Externally authored issue requests are not necessarily accepted upstream contracts.
In particular, the jq reporter's requested format, pip input validity and pytest's
support-question/change-request authority remain unresolved. Those uncertainties were
retained, not settled from post-resolution labels or fixes.

## Candidate/exclusion record

**12 inspected; 5 selected; 7 excluded**, all within the 75-candidate overall budget.
Every inspected body and its search provenance are retained in
[captures](r5_116a/captures/); decisions are in
[selection-log.json](r5_116a/selection-log.json) and the hashed
[candidate audit](r5_116a/candidate-audit.json). Actual retrieval order/times are in receipts;
requests across repositories ran in parallel, while selection order follows the fixed
repository frame and each repository's ascending candidate pages.

| Excluded candidate | Precommitted rule | Reason |
| --- | --- | --- |
| jq#3227 | E6 | Body embeds a concrete fixing narrative/instruction sequence |
| redis#13718 | E4 | Hosted website geographic-access policy requires unavailable operator/environment context |
| redis#13720 | E3 | Documentation cheat-sheet correction only |
| redis#13730 | E5 | Unable-to-reproduce crash; missing/redacted essential scenario context |
| redis#13733 | E5 | Required script absent from permitted body; attachments not opened |
| redis#13734 | E2 | Release publication administration, not specified software behavior change |
| pytest#13099 | E3 | Broken documentation/blog link only |

jq#3227's solution-containing body was received and displayed before exclusion could
be determined. This is disclosed exposure to an excluded source's embedded answer
material; no linked PR or commit was opened and no acceptance was derived from it.
Redis's `+select` workaround is source user configuration, not a server-fixing patch.
pip's existing failure traceback contains shim code; it is retained as failure context,
not used as a proposed fix. API metadata includes current labels/state, potentially
post-resolution; it was not used as acceptance authority. These observations prevent
a claim that this session has seen no implementation-related material at all.

## Source and acceptance preservation

Each selected source has:

- Exact retrieved original title/body in `captures/<owner>__<repo>/candidate-NN-source.json`;
  raw search/issue API response bytes and retrieval receipts, with SHA-256 identities.
- Issue URL/number/numeric/node IDs, author login/numeric ID/association, creation/update/
  retrieval times and exact title/body UTF-8 hashes in `P6-ANN-provenance.json`.
- Repository numeric/node IDs, metadata, default-branch revision and license metadata.
- A [candidate acceptance record](r5_116a/acceptance/) tracing explicit requirements,
  necessary implications, ambiguities and clarification-dependent assumptions to quotations.

Identity is the **retrieved current issue body**, not a reconstructed creation-time
revision. All selected sources are attributable public contributor-authored issues;
none were authored for this research. The GitHub license metadata reports MIT for pip
and pytest and `NOASSERTION`/Other for jq, curl and Redis. This does not classify those
projects as proprietary or establish a blanket license for every issue contribution.
Public attributed research captures and these license limitations are recorded; no
implementation files or external attachments were copied. No license text audit or
creation-date licensing claim is made.

All five candidate records are **CURATED_CLARIFICATION_REQUIRED**. They are source-derived
interpretations by this capability-aware curation agent, not independently authored
acceptance, owner-approved FRCs or complete behavioral oracles. Source silence stays
unresolved, including format scope, TLS matching/trust, ACL ordering, package requirement
validity and skipped-fixture lifecycle. No Lykoi inventory supplies missing behavior.

## Manifest and visibility

[manifest.json](r5_116a/manifest.json) binds five opaque IDs, exact source identities,
selection order, acceptance identities, policy version/commit, provenance, curation time,
exposure declaration and artifact hashes. SHA-256:

`441cbf46ae23275cff01c4096fba81edb8d0438cc955841240bc9b6aa89cfa72`

[manifest.sha256](r5_116a/manifest.sha256) pins its physical bytes. Corrections require
new linked records rather than overwriting the fixed batch. The policy is committed;
the resulting batch/status records remain uncommitted working-tree files at completion.
Hashes bind content; no write protection, authentication or fully Git-versioned batch
immutability is claimed.

[opaque-summary.json](r5_116a/opaque-summary.json) contains **only IDs and readiness**.
It is suitable for a separate development-visible summary, but cannot undo this
session's actual exposure. Filenames of requirements/acceptance records use opaque IDs;
the full curation evidence intentionally includes source identities and semantics.

## Verification and implementation preservation

`python benchmark/results/phase6/r5_116a/seal.py build` checked policy chronology,
ascending pages/creation dates, complete search responses, actual non-PR issue identities,
exact title/body equality, every candidate disposition, five selected IDs and acceptance
section presence before creating hashes. `seal.py verify` passed manifest/artifact hash
checks, opaque-summary shape, unchanged policy and implementation scope.
Acceptance quotations and inferences were manually compared to the retrieved bodies;
the hash/shape checks alone do not prove semantic interpretation accuracy.

Git comparison with starting R5.115 commit shows no changes or new untracked files in
`src`, `schema`, `air`, `generated`, `tests`, `benchmark/harness`, `benchmark/evaluation`
or `benchmark/conventional`. The **26-concept** kernel, existing compiler/profiles and
**16/20 exposed-development-corpus successes** are preserved historical evidence, not
new test results. No Lykoi validation, formalization, structural projection, BDI, adequacy,
V1, authoring, compilation or behavioral verification occurred. No dependencies added,
qualification, activation, isolation service or benchmark controller introduced.

Two finite one-round helpers capture public API bytes and compute/audit hashes; they
do not invoke the semantic pipeline. One pip capture completed successfully but console
rendering then failed on a Unicode character under cp1252. UTF-8 display was enabled and
the same saved source displayed with `--show`, without refetch, overwrite or selection
change. No HTTP retry was needed. No unrelated semantic-development tests were run.

## Completion answers and stop

1. Five real open-source requirements selected? **Yes: five externally authored public
   behavior requests; acceptance authority remains candidate-level.**
2. Repositories/domains? **jq/data processing, curl/network transfer, Redis/database,
   pip/package installation and pytest/testing**, as identified above.
3. Policy fixed before inspection? **Yes**, committed 88 seconds before the first request.
4. Exclusions objective and recorded? **Yes**, seven exclusions tied to fixed rules,
   with their context-sufficiency judgments and every inspected candidate preserved.
5. Exact sources preserved? **Yes**, retrieved title/body and raw API bytes with hashes;
   no claim to recover issue creation revisions.
6. Acceptance source-derived? **Yes**, candidate obligations with quotations;
   neither independent acceptance authorship nor upstream approval is claimed.
7. Material ambiguities retained? **Yes**, all five retain clarification-required items.
8. Lykoi unchanged? **Yes**, implementation, profiles and proposed kernel unchanged.
9. Any requirement evaluated? **No.**
10. First requirement ready for R5.117? **The source and candidate obligations are ready
    for a separately authorized clarification-first attempt**, with an accurate snapshot
    and exposure declaration. It is **not ready for a complete behavioral oracle or a
    pristine held-out claim**, and no R5.117 action is authorized here.

The central question has a bounded positive answer: this transparent precommitted
procedure produced a diverse-by-project-function, externally authored batch without
changing Lykoi or constructing isolation infrastructure. It does not establish unbiased
cognition, independent acceptance, project endorsement or semantic generalization.
**Stop after R5.116A curation.**
