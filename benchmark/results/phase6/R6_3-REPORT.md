# R6.3 — P6-A04 human-clarified FRC and acceptance plan

**`R6_3_P6_A04_CLARIFIED_RESEARCH_CONTRACT_READY`**

The exact preserved external source plus the project owner's explicit Q1/Q2 research
clarification yields a complete, testable bounded contract without correcting the
reported declaration or modifying Lykoi. Contract and fixed expectations are ready
for subsequent exact human approval. **No approval or evaluation occurred.**

## Published deliverables

1. [Exact human clarification/provenance](r6_3/HUMAN-CLARIFICATION.json)
2. [Revised FRC, revision 2](r6_3/FRC-CANDIDATE.json)
3. [Fixed acceptance plan](r6_3/ACCEPTANCE-PLAN.json)
4. [Pinned fixture manifest](r6_3/FIXTURE-MANIFEST.json)
5. [Final Research Approval Review](r6_3/HUMAN-REVIEW.md)
6. [Executable acceptance procedure](r6_3/ACCEPTANCE-PROCEDURE.md) and
   [fixed observer](r6_3/observe.py), prepared but not executed
7. [Source verification](r6_3/SOURCE-VERIFICATION.json),
   [finite preparation/verifier](r6_3/prepare.py), [identities/checks](r6_3/IDENTITIES.json)

## Evidence, authority and fidelity

Offline original-source checks reuse R6.1's exact P6-A04-only verifier. Raw API/source,
title/body, author/repository/search/ref and receipt hashes/provenance match R5.116A.
No live issue, fixing PR, implementation commit, post-resolution solution, external
linked discussion or P6-A05 was accessed. The original full body was reviewed; the
embedded caller shim remains failure context only.

The exact human statement is retained verbatim with original source and prior candidate
identities, Q1/Q2 decisions, observed UTC recording time, bounded research purpose and
current conversation attribution. No supplied human signing timestamp/session ID is
invented. Conversation provenance is not cryptographic authentication or upstream approval.

The original body is unchanged in the new composite source record; the separately
attributed human statement supplies raw URL/token authority. All five source obligations
are retained and their domain refinements declared in revision lineage. H1/H2 are new
human-authorized syntax obligations. Existing envelope and revision checks are used;
no schema or meaning-engine change. Logical contract ID remains stable for revision
validation; new revision/artifact and canonical identities distinguish R6.3 from R6.1.

The reported declaration stays exact, including `my folder` and the wheel-filename token.
Only source-prescribed `$(pwd)` interpolation uses a pinned research working directory.
No percent-encoding/name repair, directory rename, wheel replacement or dependency
preinstallation is permitted. Parsing alone is insufficient.

## Fixture completeness and acceptance

The exact source wheel was fetched in memory from its preserved URL, SHA-256 verified,
and ZIP metadata/payload hashes recorded without importing/executing it. Six pinned
tool/prerequisite wheels were likewise retrieved from package release metadata and
hash-verified. This bounded fixture sourcing did not inspect any pip solution. URLs,
filenames, versions, byte digests, Python compatibility declarations, containing-package
content hashes, concrete space-containing path and installed observation predicates are
fixed. Ubuntu 24.04 x86_64 / CPython 3.13.1, setuptools 75.6.0 / wheel 0.45.1,
pip 24.3.1 baseline and unrelated prerequisites are explicitly research fixture choices.
No dependency extras, target preinstallation or index substitution masks the experiment.

Four fixed checks distinguish parsing, designated-artifact resolution, containing
installation and actual dependency installation. Independent installed-state/payload
inspection supplements report provenance; the initially absent-state control guards
against false success. Missing evidence is a limitation, not a pass. No unsupported
malformed-input or alternate-syntax compatibility tests are invented.

No material behavioral ambiguity remains. Ordinary setup choices are fixed; algorithms
and internal handling layers remain delegated. Declared tool/Python compatibility is
not empirical success evidence for this unusual input.

**Concrete execution integration limitation:** the fixed shell/observer acceptance
procedure has no bound package-install payload in the existing native local verifier.
`native_plan: null` is disclosed. This classification means clarified contract/expectation
readiness for exact review, **not native evaluator execution readiness**. A later attempt
cannot silently substitute this plan into that runner; any authorized integration must
retain these expectations and receive exact approval before authoring. No adapter or
infrastructure was added. This does not reopen Q1/Q2 or authorize input repair.

## Exact new identities

CJ-1 canonical JSON SHA-256:

| Artifact | Identity |
| --- | --- |
| Human clarification | `232fef22356ed5b743c0e3e572c69c76ed6669ff7dcceab7989c5e7fbc9d48d8` |
| Revised FRC | `aa2af92cf77073f1f42a70065d64135d211bf7bc6889aeeb4a033ce3aa449aba` |
| Fixed acceptance plan | `2ec947565b95dbed28bf5096aa945dbf528c1bdaf2763a99cc95f7da587f0dc4` |
| Fixture manifest | `d3f38f5cdcf4aac2602e83ce66de6b227200f7e12185a42f2d3ece83efb4c6e1` |

Original capture bytes: `811cd95034444011f50e13572ebd10c810692b9e26b6355863d1aae3aa1af747`.
Original source record: `89835744da01e163649a40de1d08d99c7a5b11766ad2d5f0fd7d68325ff04f19`.
Source wheel: `bd1bc99a9788f01d218d83a0389ebb17e740b0cab60e7ac57d8d3c0d51f28181`.
All byte/review/report identities are in the publication record.

## Focused verification

Initial `git status --short` was clean. The retained verifier records starting HEAD/tree,
checks the R6.1 implementation manifest exactly and constrains changes to additive R6.3
artifacts and minimal status prose. Historical R5.116A/R6.1/R6.2 records and all other
tracked implementation/history files remain untouched. Existing FRC `validate` and
`check_revision` pass; source quotes/derivation graph/revision lineage and new bindings
are checked. Envelope validity is not source entailment or artifact approval.

Successful preparation and verification commands from repository root:

```powershell
$env:PYTHONPATH='src'
$env:PYTHONIOENCODING='utf-8'
python -m benchmark.results.phase6.r6_3.prepare build
python -m benchmark.results.phase6.r6_3.prepare verify --publish
python -m benchmark.results.phase6.r6_3.prepare verify
git diff --check
```

Preparation encountered two tooling errors before completion: a PowerShell assignment
after `&&` parse error, and multiple vendored METADATA entries in the pip wheel.
Neither ran an experiment. The recorder was corrected to select only the wheel's
top-level distribution metadata and refuse evidence overwrites. Already recorded exact
clarification and timestamp were preserved; the successful retry completed preparation.

Focused checks cover source identity/provenance, literal clarification, revised envelope
and revision consistency, acceptance/fixture identity bindings/completeness, original
input, historical preservation, implementation equality and whitespace/change scope.
No test suite, stock pip probe, subject command or observer was executed. No structural
coverage, BDI, adequacy, V1 projection, authoring, compilation or external behavioral
verification. All evaluation stages **NOT_RUN**, acceptance executions **0**.
Kernel **26**, model **0.3**, compiler/backend **0.3.0** and historical outcomes retained.

## Completion answers

1. **Original source verified?** Yes, exact preserved capture/provenance and text hashes.
2. **Human clarification exact?** Yes, literal statement and honest conversation provenance.
3. **Q1/Q2 faithful?** Yes; require raw-space URL and exact wheel-filename token.
4. **Original declaration preserved?** Yes; only its prescribed shell interpolation applied.
5. **Fixture identities complete?** Yes for the declared bounded fixture: designated wheel,
   all tool/prerequisite wheels, package content, path, environment constraints and observer.
6. **Parsing/resolution/installation separately verified?** Separately specified, **not
   behaviorally executed or verified**. All four checks fixed; no parsing-only success.
7. **Expectations fixed?** Yes, source/human/FRC/fixture/procedure/observer-bound before authoring.
8. **Material ambiguities?** None in behavioral authority. Native acceptance integration
   remains a disclosed execution limitation; no implementation/backend success claimed.
9. **Exact new identities?** Listed above and in IDENTITIES.json.
10. **Ready for explicit approval?** Yes, contract and fixed expectations ready for subsequent
    exact research approval, with the integration limitation; no approval has been issued.
11. **Lykoi unchanged?** Yes, implementation manifest and Git history/scope checks pass.

**Stopped after preparation/publication. R6.3 only. No approval, execution receipt,
grant, seal, evaluation, implementation work or P6-A05 access.**
