# R6.1 — P6-A04 external requirement preparation

**`R6_1_P6_A04_RESEARCH_REVIEW_PREPARED`**

The exact R5.116A-preserved `pypa/pip#13139` is verified. An unapproved,
envelope-valid candidate FRC and source-derived conditional acceptance plan are
ready for project-owner review. **Recommendation: CLARIFY**, not approval for
execution. No requirement evaluation or semantic development occurred.

R5 numbering ends historically at
`R5_121_P6_A03_POST_FIRST_EVALUATION_COMPLETE`. New work uses R6.x. No historical
identifier, artifact, commitment or result was renamed, rewritten or renumbered.

## Deliverables

| Deliverable | Evidence |
| --- | --- |
| Fresh Git/tree/implementation snapshot | [SNAPSHOT.json](r6_1/SNAPSHOT.json) |
| Verified original source and provenance | [SOURCE-VERIFICATION.json](r6_1/SOURCE-VERIFICATION.json) |
| Source-traceable FRC candidate | [FRC-CANDIDATE.json](r6_1/FRC-CANDIDATE.json) |
| Pre-author conditional acceptance plan | [ACCEPTANCE-PLAN-CANDIDATE.json](r6_1/ACCEPTANCE-PLAN-CANDIDATE.json) |
| Material source questions | [MATERIAL-CLARIFICATION.md](r6_1/MATERIAL-CLARIFICATION.md) |
| Concise owner approval review | [HUMAN-REVIEW.md](r6_1/HUMAN-REVIEW.md) |
| Exact candidate/approval-preparation identities and check outcomes | [IDENTITIES.json](r6_1/IDENTITIES.json) |
| Finite artifact recorder/read-only verifier | [prepare.py](r6_1/prepare.py) |

## Snapshot and unchanged baseline

- Initial Git status was clean, recorded before source reading.
- Git commit: `de9f1b67cc614e76e090766434096696e78089d2`.
- Git tree: `fc965b73f96aa569faa5ce566ad395d75e6cf8f8`.
- Full implementation manifest recorded at `2026-10-08T17:43:58.971183+00:00`,
  after source reading but before candidate construction. This timing is disclosed;
  it is not claimed as a separately timed pre-access implementation manifest.
  Initial clean HEAD and final Git/manifest equality establish the unchanged baseline.
- Implementation canonical identity:
  `96bc0a1c781409752fd88416fe58e76311744d5a7c77d75d3247f7eb4caa0edb`.
- Proposed kernel **26**, canonical model **0.3**, compiler/Python backend **0.3.0**,
  historical exposed B01–B20 successes **16/20**. These are retained baseline facts,
  not new behavioral measurements. Existing R5.120A local path retained, unused.
- Model/provider: OpenCode / `openai/gpt-6.1-sol`, session-reported.

## Source identity and permitted context

Original source: `pypa/pip#13139`, issue numeric ID `2766862677`,
node `I_kwDOABYSQ86k6vlV`, author `basnijholt` / numeric ID `6897215`.
Title: **`pip` fails to parse `install_requires` containing local wheel with spaces in path**.
Created `2025-01-03T01:43:34Z`, preserved updated timestamp `2025-02-02T07:05:11Z`,
retrieved `2026-10-08T13:52:21.230149+00:00`.

| Identity | SHA-256 |
| --- | --- |
| Original source capture bytes | `811cd95034444011f50e13572ebd10c810692b9e26b6355863d1aae3aa1af747` |
| Title UTF-8 | `a7dbf52fd52223da438a18d5f5a3ca0f25af86ed4478cf2d356d48dec91d8c03` |
| Body UTF-8 | `f252041309b04c2c95b5cb3dbf3211d108b8793c92f560a43ee389b89f323a2b` |
| Candidate FRC canonical | `ec79136bf1c1bcee109e9d739299bd594587029c6b70203fcac1a768edc801a0` |
| Candidate acceptance canonical | `97da6d516f08f45f77462cfd6d6f54f7a944dc2d86a0b92899c7fdc0ff438d59` |

Verification checks saved raw issue, source, search, repository and default-ref
captures against provenance hashes, exact title/body equality, issue/author/repository
identities, selected issue presence in search, and original API receipt/time/policy
commit. Repository revision-at-retrieval metadata is
`a7002c9771a6c3f0317a4e6b9fbdcd22e643f7b6`; no implementation at that revision was read.
This is the preserved retrieved body, not reconstructed creation-time text. API
labels/state and later resolution metadata do not supply behavioral authority.

No network access, newer issue substitution, linked context, fixing PR, implementation
commit, solution discussion, wheel download or P6-A05 content access occurred. The
existing failure traceback contains a caller shim, retained only as failure context;
it is not a fixing patch or algorithm recommendation. The dedicated reader truncated
the long JSON body, so the saved body was rendered once via Python after enabling
UTF-8 stdout; an initial cp1252 rendering error caused no refetch or source modification.

## Requested behavior, freedoms and missing decisions

The reporter's install fails while preparing metadata for a package whose
`install_requires` references a local wheel under `my folder`. They ask for correct
parsing and installation of that wheel despite the space. The proposed source-faithful
branch preserves the literal reproduction after shell working-directory interpolation,
then requires successful containing-package and local-dependency installation with
otherwise satisfied prerequisites.

Five stable obligations retain exact source quotes and existing typed relation kinds:
E1 parsing (`invariant`), E2 installation (`effects`), I1 no space-caused rejection
(`invariant`), I2 designated local artifact (`effects`), I3 successful containing-package
installation (`transition`). This is declarative FRC bookkeeping, not a structural
mapping, capability claim or authored package manager.

Internal algorithms, language, data structures, code organization and responsibility
among parsing/build/installation layers are delegated, subject to the approved observable
contract. Absolute fixture directory and observation method may vary faithfully.
Accepted URL/name spellings are material behavior, not implementation freedom.

**Two material questions:** raw-space versus clarified encoded URL (**Q1**), and
original wheel-filename token before `@` versus clarified project-name token (**Q2**).
The source supplies the literal example and desired result but does not settle input
validity under an incorporated packaging/URL authority. Prefer exact input fidelity;
retain both questions rather than silently repair or claim validity from conventional
pip knowledge. The traceback's subprocess/package attribution does not require a
third question about internal implementation ownership.

Exact wheel bytes/digest, setuptools/build-backend versions and transitive dependency
fixtures are absent. They are execution-readiness prerequisites to fix before an
executable plan, not demands for human algorithm design. Error text, numeric exit codes,
rollback, network prohibition, Windows support and unrelated pip behavior remain
unspecified. Preservation is limited to the intended local artifact, path containing
a space and containing-package workflow; no whole-application preservation invented.

## Acceptance and approval preparation

Four check groups bind every obligation, without generated-software access:
T1 parsing/metadata, T2 installed state/artifact correspondence, T3 URL-spelling
witness, T4 name-spelling witness. All are **CONDITIONAL_NOT_RUN**. T3/T4 have no
selected expected result. T1/T2 positive expectations apply only after material input
clarification and source-faithful fixture prerequisites. No invented malformed-input
or unrelated-regression oracle, byte-exact diagnostic or rollback expectation.

R5.118A distinguishes reporter behavioral evidence, exact project-owner research
permission and product authority. The current instruction names the project owner
as review/decision recipient; it does not approve any artifact. `IDENTITIES.json`
prepares exact source/FRC/plan/review bindings, records approval **NOT_GIVEN**, and
leaves evaluator designation to a subsequent exact decision. No upstream pip maintainer
approval is required for research-only permission; none is asserted.

No material question may be waived by approval. Clarification and executable acceptance
completion require newly identified linked artifacts/review before later approval and
separate attempt permission. Candidate metadata remains `approved: false`,
`sealed: false`, `review: null`, `native_plan: null`. No controller, authenticated role,
approval event, local execution receipt, grant, seal, new service or harness created.

Review is one initial source-only pass, zero correction passes; same-agent/same-model
production and review disclosed. Acceptance is independent of generated software, not
independent cognition. This is externally authored, procedurally selected, previously
exposed material, not blinded/held-out or upstream-certified intent.

## Focused verification

Commands (repository root; `PYTHONPATH=src`):

```powershell
python -m benchmark.results.phase6.r6_1.prepare snapshot
python -m benchmark.results.phase6.r6_1.prepare build
python -m benchmark.results.phase6.r6_1.prepare verify --publish
python -m benchmark.results.phase6.r6_1.prepare verify
git diff --check
```

Snapshot/build exclusively create retained evidence. Verify is read-only except
the one `--publish` identity record. Checks pass for exact source/provenance,
existing FRC `validate` envelope/provenance/derivation rules, plan bindings/check
coverage/conditional expectations, implementation manifest equality, Git preservation
of all prior tracked results and implementation, documentation whitespace including
new files, and additive R6.1/minimal-status scope. Mechanical validity is not proof
of source entailment or human approval; the substantive source-only review is retained.

No tests executed. No broad qualification, model validation/safety rerun, structural
coverage, BDI, adequacy, V1 projection, authoring, compilation or behavioral verification.
**Zero P6-A04 acceptance executions.** All evaluation stages are **NOT_RUN**, not
an evaluation first result. No first-result record or representability verdict created.
P6-A01/P6-A02/P6-A03 first/post-first results, R5.116A selection and B01–B20 history
remain unchanged. No other-source investigation or semantic work begun.

## Completion answers and stop

1. **Exact source verified?** Yes, preserved identity/raw bytes/title/body/provenance.
2. **Requested behavior?** Parse the space-containing local-wheel requirement and
   install that wheel through the containing-package install.
3. **Preserve?** Intended local artifact, space-containing path and installation
   workflow; no unauthorized whole-pip compatibility promise.
4. **Delegated?** Internal design and processing layer, faithful fixture directory
   and observation method; not material accepted input spellings.
5. **Material ambiguities?** Q1 raw-space URL acceptance; Q2 wheel-filename name token.
   Fixture versions/artifact identities also remain unfixed before execution.
6. **FRC valid?** Yes, existing FRC envelope validation; unapproved and unsealed.
7. **Acceptance source-derived?** Yes, four conditional groups, no invented outcomes.
8. **Exact artifacts requiring human decision?** Source-bound FRC revision 1, candidate
   plan, human review and Q1/Q2 record identified above. Any clarified replacements
   need fresh exact identities plus evaluator/assumption/limit binding before approval.
9. **Lykoi unchanged?** Yes, 26 concepts/model 0.3/compiler 0.3.0/profiles/backend/history.
10. **Ready for research approval?** Ready for human review with recommendation
    **CLARIFY**; not ready for executable approval or evaluation.

**Stopped after preparation.** This round authorizes no approval, evaluation,
semantic development, infrastructure work or P6-A05 access.
