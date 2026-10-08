# R6.2 — P6-A04 clarification and research contract revision review

**`R6_2_P6_A04_LITERAL_INPUT_CLARIFICATION_REQUIRED`**

The exact preserved source is verified. It establishes a local-wheel installation
goal despite filesystem path spaces, but does not sufficiently determine raw-space
URL acceptance or wheel-filename-token acceptance. **Q1/Q2 remain unresolved;
recommend CLARIFY.** No revised FRC or acceptance plan is justified. R6.1 artifacts
and identities are preserved. This is preparation, not a P6-A04 evaluation result.

## Deliverables

- [Q1/Q2 source-evidence analysis and fixture authority](r6_2/SOURCE-EVIDENCE.md)
- [P6-A04 — Revised Research Approval Review](r6_2/HUMAN-REVIEW.md)
- [Exact identities and focused verification](r6_2/IDENTITIES.json)
- [Finite identity/scope verifier](r6_2/verify.py)
- Revised FRC: **NOT_PRODUCED**, unresolved material input authority.
- Revised acceptance plan: **NOT_PRODUCED**, exact eligible-input expectations unfixed.

## Exact source and history

The R5.116A source capture is
`r5_116a/captures/pypa__pip/candidate-01-source.json`, `pypa/pip#13139`, issue
`2766862677`, node `I_kwDOABYSQ86k6vlV`, author `basnijholt` / `6897215`.
Captured `2026-10-08T13:52:21.230149+00:00`; this is the preserved retrieved
revision, not reconstructed creation-time text.

| Identity | SHA-256 |
| --- | --- |
| Source capture bytes | `811cd95034444011f50e13572ebd10c810692b9e26b6355863d1aae3aa1af747` |
| Title UTF-8 | `a7dbf52fd52223da438a18d5f5a3ca0f25af86ed4478cf2d356d48dec91d8c03` |
| Body UTF-8 | `f252041309b04c2c95b5cb3dbf3211d108b8793c92f560a43ee389b89f323a2b` |
| Preserved FRC revision 1 canonical | `ec79136bf1c1bcee109e9d739299bd594587029c6b70203fcac1a768edc801a0` |
| Preserved acceptance candidate canonical | `97da6d516f08f45f77462cfd6d6f54f7a944dc2d86a0b92899c7fdc0ff438d59` |

Original source/raw API/title/body/author/repository/search/ref/receipt hashes and
identities checked with R6.1's offline verifier. Repository ref metadata is only
identity evidence: no implementation at that revision was inspected. Full saved
body reviewed; embedded caller shim used only as failure context. No network,
newer issue, fixing PR, implementation commit, linked solution or P6-A05 access.

Initial `git status --short` was clean. Starting HEAD
`91e1d772b0afa3be4729d347391e8acbebdc2e96`; tree recorded in `IDENTITIES.json`.
Implementation manifest equals R6.1's retained manifest, canonical identity
`96bc0a1c781409752fd88416fe58e76311744d5a7c77d75d3247f7eb4caa0edb`.
Kernel **26**, model **0.3**, compiler/backend **0.3.0**, FRC semantics, mappings,
profiles, tests and historical benchmark results unchanged. Historical exposed
16/20 success count retained, not rerun. All prior R5/R6.1 evidence remains untouched.

## Interpretation finding

Q1 has substantial literal-branch evidence: deliberate `my folder`, raw URL and
requested parsing/installation. However, the desired path-space behavior does not
explicitly require that URL spelling unchanged. Q2 has weaker evidence: the left
token is present, but not the subject of any explicit support request. Neither a
failing example nor a diagnostic settles the intended accepted-input contract.
No standard is needed merely to request unusual syntax; no standard was imported.
The insufficiency is desired input authority, not lack of a standards citation.

The exact-input interpretation requested in this round is retained verbatim as a
conditional proposal in the review. No source-established literal-input claim is
made, no token corrected, and no scope decision manufactured. A future human
clarification must be explicitly attributed and cannot masquerade as source intent.

Fixture directory, controlled environment and observation mechanism may be
delegated within source-fidelity constraints. A valid arbitrary wheel is not a
substitute for the designated source artifact. Exact wheel/backend/transitive pins
and observation details remain setup work; they cannot decide Q1/Q2. No fixtures
were fetched, built or tested. End-to-end installation remains necessary; parsing
alone cannot satisfy the source objective. All original check groups are conditional.

## Focused verification

Repository root, PowerShell (`PYTHONPATH=src`, UTF-8 stdout):

```powershell
python -m benchmark.results.phase6.r6_2.verify --publish
python -m benchmark.results.phase6.r6_2.verify
git diff --check
```

Checks pass for exact source identity/provenance; preserved FRC envelope validation;
conditional acceptance source/FRC/obligation bindings and nonapproval; R6.1 byte and
canonical identities; unchanged implementation manifest; all changes restricted to
additive R6.2 evidence/minimal status prose; tracked and new-file whitespace.
Revised-candidate validity is **not applicable** because no new candidate is justified.
Mechanical validity does not prove source entailment; the substantive review is above.
The verifier publishes only a new identity record exclusively, then verifies read-only.

Zero tests executed. No structural coverage, BDI, adequacy, V1 projection, Lykoi
authoring, compilation, acceptance execution, approval, seal or research receipt.
All evaluation stages **NOT_RUN**. No first-result record or capability verdict.

## Completion answers

1. **Raw-space URL authorized?** Not sufficiently determined. Explicit path-space
   installation objective; raw URL is the demonstrated failure, not a settled rule.
2. **Wheel-filename token authorized?** Not sufficiently determined. Example-only
   left token; no explicit support request or authorized correction.
3. **Established versus assumed?** Parsing and installing the designated local wheel
   through the containing package despite path spaces is established. Requiring the
   entire reproduction unchanged remains a conditional research interpretation.
4. **Delegable fixtures?** Temporary absolute directory, source-faithful artifact
   staging/pinning, compatible controlled environment and reliable installed-state
   observation. No input normalization, artifact substitution or preinstallation mask.
5. **Acceptance fixed?** No exact-input oracle; R6.1 conditional plan preserved.
6. **Ambiguities?** Q1/Q2; execution fixture identities/procedure still unfixed.
7. **Artifacts requiring approval?** None ready now. Human clarification reviews the
   exact preserved source/FRC/plan and new review. Later approval must bind newly
   clarified FRC, fixed plan/fixtures and corresponding review with source/evaluator.
8. **Lykoi unchanged?** Yes, implementation manifest and Git scope checks pass.
9. **Ready for research approval?** No; ready for clarification review only.

**Stopped after preparing the review. R6.2 only.**
