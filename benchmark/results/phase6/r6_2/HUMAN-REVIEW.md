# P6-A04 — Revised Research Approval Review

**Recommendation: CLARIFY.**
**`R6_2_P6_A04_LITERAL_INPUT_CLARIFICATION_REQUIRED`**

## Original request

The preserved `pypa/pip#13139` asks that pip correctly parse `install_requires`
and install a local wheel whose filesystem path contains spaces, through the
containing-package installation. Its only recipe fails during metadata generation.
See [source-evidence analysis](SOURCE-EVIDENCE.md) for exact fragments and distinctions.

## Q1 finding

**Unresolved.** Deliberately creating `my folder` and using a raw-space URL strongly
supports considering literal-input behavior. But the expected-behavior sentence
does not distinguish a space-containing filesystem path from its URL spelling.
The literal URL is a failing reproduction, not an explicit unchanged-input rule.
Neither raw acceptance nor an encoded correction is sufficiently determined.

## Q2 finding

**Unresolved.** The wheel-filename token before `@` occurs in the reproduction and
its diagnostic. There is no explicit request to support that name form, nor an
instruction to correct it. It is incidental syntax relative to the stated path-space
problem. Do not silently substitute a project name or declare it invalid from memory.

## Proposed bounded interpretation

> Given the exact dependency declaration from the preserved issue, including its
> wheel-filename token and raw-space local file URL, installing the containing
> package resolves and installs the designated local wheel.

This remains **conditional research scope**, not source-established behavior or a
packaging-standard claim. No new candidate FRC is justified until Q1/Q2 are resolved.

## Exact input behavior

```text
pipefunc-0.46.0-py3-none-any.whl @ file://$(pwd)/my folder/pipefunc-0.46.0-py3-none-any.whl
```

The source shell expands `$(pwd)` before writing `setup.py`. The proposed literal
branch preserves the left token and raw space thereafter. A URL/name correction
changes the acceptance target and requires attributed clarification and new identities.
No branch is selected by this review. Internal parsing/build/install design remains free.

## Acceptance expectations

Parsing the intended requirement, resolving the designated local wheel, completing
`pip install --verbose .`, and independently observing installation of both
`my-local-package` 0.1.0 and that dependency are the source-grounded goals.
**Their exact-input expectations are not fixed.** R6.1 T1/T2 remain conditional;
T3/T4 have no selected oracle. Parsing alone, correcting the input, preinstalling
the dependency, or substituting another artifact cannot prove literal-branch success.
No tests have been executed; no revised acceptance plan is justified.

## Remaining material uncertainties

- Q1: literal raw-space URL versus an exactly specified clarified URL spelling.
- Q2: wheel-filename left token versus an exactly specified clarified name spelling.
- Execution-readiness details: source-faithful wheel content/digest, compatible
  environment/backend/transitive fixture pins and concrete observation procedure.
  These may be delegated as setup, but may not change disputed input behavior or
  source-designated artifact identity. No wheel has been downloaded.

Unrelated error wording, numerical exit status, rollback, no-network policy,
universal platform compatibility and internal fixing layer remain unspecified.
They are not extra questions that the owner must answer to design an algorithm.

## Source/FRC/acceptance identities

- Source: `pypa/pip#13139`, issue ID `2766862677`, node `I_kwDOABYSQ86k6vlV`,
  author `basnijholt` / `6897215`, retrieved `2026-10-08T13:52:21.230149+00:00`.
- Preserved source path:
  `benchmark/results/phase6/r5_116a/captures/pypa__pip/candidate-01-source.json`.
- Source file SHA-256:
  `811cd95034444011f50e13572ebd10c810692b9e26b6355863d1aae3aa1af747`.
- Title UTF-8 SHA-256:
  `a7dbf52fd52223da438a18d5f5a3ca0f25af86ed4478cf2d356d48dec91d8c03`.
- Body UTF-8 SHA-256:
  `f252041309b04c2c95b5cb3dbf3211d108b8793c92f560a43ee389b89f323a2b`.
- FRC source record canonical SHA-256:
  `89835744da01e163649a40de1d08d99c7a5b11766ad2d5f0fd7d68325ff04f19`.
- **Preserved, not revised** FRC revision 1:
  `benchmark/results/phase6/r6_1/FRC-CANDIDATE.json`, canonical SHA-256
  `ec79136bf1c1bcee109e9d739299bd594587029c6b70203fcac1a768edc801a0`.
- **Preserved, not revised** acceptance candidate:
  `benchmark/results/phase6/r6_1/ACCEPTANCE-PLAN-CANDIDATE.json`, canonical SHA-256
  `97da6d516f08f45f77462cfd6d6f54f7a944dc2d86a0b92899c7fdc0ff438d59`.
- This revised review and evidence analysis have byte identities in
  [IDENTITIES.json](IDENTITIES.json). They do not approve the original artifacts.

## Recommendation: clarify

No artifact set is ready for research approval now. The exact existing source,
FRC and conditional plan above require human **clarification review**, not approval
for execution. A later legitimate clarification must yield an exact linked FRC,
fixed acceptance/fixture plan and corresponding review, bound with source identity,
assumptions, limits and designated evaluator in the human research decision.
Research scope decisions must be attributed as such, not certified as reporter intent.
Material questions cannot be waived by an approval flag.

Same-agent/same-model source-only clarification pass after R6.1; no cognitively
independent review, upstream certification or held-out generalization claimed.
No approval, seal, receipt, evaluation, authoring, compilation or acceptance execution.
Lykoi and its 26-concept kernel are unchanged. **Stop after this review.**
