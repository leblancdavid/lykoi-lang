# P6-A04 — Research Approval Review

**Original request:** The reporter says pip cannot install a package whose
`setup.py` lists a local wheel in `install_requires` when the wheel's path contains
a space. The preserved output rejects the requirement during setup metadata
generation. The reporter asks that pip parse the requirement and install that wheel.

**Proposed behavior:** Conditional exact-input interpretation: use the supplied
`my-local-package` 0.1.0 / `my_module` recipe, the accessible designated
`pipefunc-0.46.0-py3-none-any.whl` under `my folder`, and `pip install --verbose .`.
After the recipe's shell expansion of `$(pwd)`, preserve the literal space and the
wheel-filename token before `@`. With other installation prerequisites satisfied,
parse the requirement and install the containing package and that local dependency.
This interpretation is proposed for clarification, not decided or approved.

**Explicit obligations:**

- **A04-E1:** Parse the accepted local-wheel requirement despite a space in its path.
- **A04-E2:** Install that wheel as the containing package's dependency.

Both trace to: "`pip` should correctly parse the `install_requires` and install the
local wheel, even if its path contains spaces."

**Necessary implications:**

- **A04-I1:** No reported parsing/metadata rejection solely because of the path space
  for the clarified accepted input. Changing the error wording alone is not success.
- **A04-I2:** Install the specified local artifact, not an unrelated or remote substitute.
- **A04-I3:** The containing-package installation completes with otherwise satisfied
  prerequisites. Merely recognizing a string is insufficient.

**Preservation obligations:** Preserve the requested installation workflow, designated
local artifact and path containing a space; renaming the directory or substituting a
package is not a solution to the exact-input branch. The source does not authorize a
whole-pip compatibility guarantee, specify no-space control outputs, or promise
rollback, no network use, Windows support or invalid-input acceptance. Those are not
invented preservation tests. Name/URL correction needs explicit clarification.

**Material questions:**

1. **A04-Q1:** Require the source's raw-space URL unchanged, or a legitimately clarified
   encoded URL? These have different accepted-input and success/failure expectations.
2. **A04-Q2:** Require the original wheel-filename token before `@`, or a legitimately
   clarified project-name token? These change which requirement must install the wheel.

Prefer retaining the exact reproduction for source fidelity; do not claim that a
packaging/URL standard validates it. See [evidence, interpretations and consequences](MATERIAL-CLARIFICATION.md).
Which internal layer handles the change is delegated. Backend/wheel/dependency fixture
identities still need fixing before executable acceptance; no parser design decision
is requested from the human.

**Acceptance tests:** Four proposed external check groups, **all conditional, none run**:

- **A04-T1:** Source recipe parses/prepares metadata without a space-caused rejection.
- **A04-T2:** Successful end-to-end install and independent installed-state/artifact
  inspection establish both containing package and designated local dependency.
- **A04-T3:** Original versus encoded URL witness distinguishes Q1 interpretations;
  no selected oracle until clarification.
- **A04-T4:** Original wheel-filename versus clarified project-name witness distinguishes
  Q2 interpretations; no selected oracle until clarification.

Every obligation is bound to checks. Inputs, errors, effects and expected observations
are retained in [the candidate plan](ACCEPTANCE-PLAN-CANDIDATE.json). No source-derived
negative oracle exists for malformed wheels, missing files or unrelated pip behavior.
No exact output transcript, numeric exit status or rollback expectation is invented.

**Scope limitations:** Research-only preparation using preserved reporter title/body;
not upstream endorsement, production authority, causal diagnosis, general pip correctness,
successful generalization or a kernel capability result. Same-agent/same-model review
and candidate production; expectations are independent of generated software because
none was authored, not cognitively independent. This is one initial source-only review,
zero correction passes. The source was previously exposed during procedural curation;
not blinded/held-out. No source-linked fix, standard, external attachment or live probe
used. The reported pip 24.3.1 / Python 3.13.1 / macOS and Ubuntu environments are context,
not a universal platform/version contract. The candidate plan is not executable and
has no native payload. No controller approval, local receipt or seal was issued.

**Exact identities:** SHA-256; canonical JSON uses existing FRC CJ-1 tooling.

- Original source: `pypa/pip#13139`, author `basnijholt`, issue ID `2766862677`,
  node `I_kwDOABYSQ86k6vlV`, retrieved `2026-10-08T13:52:21.230149+00:00`.
  Source capture: `benchmark/results/phase6/r5_116a/captures/pypa__pip/candidate-01-source.json`.
  File hash: `811cd95034444011f50e13572ebd10c810692b9e26b6355863d1aae3aa1af747`.
  Title UTF-8: `a7dbf52fd52223da438a18d5f5a3ca0f25af86ed4478cf2d356d48dec91d8c03`.
  Body UTF-8: `f252041309b04c2c95b5cb3dbf3211d108b8793c92f560a43ee389b89f323a2b`.
  FRC source-record canonical: `89835744da01e163649a40de1d08d99c7a5b11766ad2d5f0fd7d68325ff04f19`.
  This is the R5.116A retrieved revision, not a recovered creation-time body.
- Candidate FRC: `FRC-CANDIDATE.json`, `R6.1/P6-A04/candidate`, revision 1.
  Canonical: `ec79136bf1c1bcee109e9d739299bd594587029c6b70203fcac1a768edc801a0`.
  File: `c6df6cde319ea3021443c71df865354ef8363bc4a20b5c000d9697fcd72d50a2`.
- Candidate acceptance plan: `ACCEPTANCE-PLAN-CANDIDATE.json`,
  `R6.1/P6-A04/acceptance-candidate/1`.
  Canonical: `97da6d516f08f45f77462cfd6d6f54f7a944dc2d86a0b92899c7fdc0ff438d59`.
  File: `14b6de7525b1d5907a037d1c2d714121ded05a9f2369cce05ce829fa1fe4cac2`.

Review and clarification file hashes are retained in `IDENTITIES.json`. Subsequent
research permission under R5.118A must bind exact source, clarified FRC, fixed plan,
review, assumptions, limits and designated evaluator. The project owner is the human
review/decision recipient named by this instruction; no human decision is manufactured.
Original pip maintainer approval is not required for research-only permission. Changes
to material interpretation or plan completion need newly identified linked artifacts;
this candidate cannot be approved for execution while its material questions remain.

**Recommendation:** **CLARIFY.** The candidate contract and conditional plan are ready
for human review. Resolve Q1/Q2 and fix source-faithful fixture identities before a
later exact-bound approval and separately authorized evaluation. Stop after preparation.
