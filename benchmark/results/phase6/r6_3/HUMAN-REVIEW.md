# P6-A04 — Final Research Approval Review

**Recommendation: Ready for explicit research approval of the contract and fixed
expectations.** `R6_3_P6_A04_CLARIFIED_RESEARCH_CONTRACT_READY`.
No approval or execution permission is inferred from this recommendation.

## Original issue

The preserved `pypa/pip#13139` asks pip to correctly parse `install_requires` and
install the designated local wheel despite spaces in its path, through installation
of its containing package. The reproduced metadata-generation failure is evidence
of the problem, not a fixing-layer prescription or universal compatibility contract.

## Human clarification

> For P6-A04 (pypa/pip#13139), I authorize the following bounded research clarification, without claiming pip maintainer intent. Q1: Require the exact raw-space file:// URL from the preserved issue. Q2: Require the exact wheel-filename token before @ from the preserved issue.

Q1 requires the original raw-space URL; Q2 requires the original wheel-filename
token. This is project-owner research clarification, not pip maintainer intent,
cryptographic authentication, product approval or approval of these new artifacts.
Conversation attribution and observed recording timestamp are retained separately.

## Proposed experimental behavior

Given the exact reported declaration after its documented shell expansion, parse
it, resolve the designated local wheel, successfully install the containing package,
and actually install that dependency in the controlled environment:

```text
pipefunc-0.46.0-py3-none-any.whl @ file://$(pwd)/my folder/pipefunc-0.46.0-py3-none-any.whl
```

The pinned working directory yields this exact concrete input:

```text
pipefunc-0.46.0-py3-none-any.whl @ file:///tmp/lykoi-r6-3-p6-a04/my folder/pipefunc-0.46.0-py3-none-any.whl
```

Shell interpolation is source-prescribed. No percent-encoding, left-token
substitution, renamed space-containing directory, replacement wheel, dependency
preinstallation or conventional-input rewrite is eligible. Internal representation
and output URL canonicalization are delegated; caller input correction is not.

## Explicit source obligations

All five stable source obligations are retained, with domain refinements declared
in revision lineage:

- **A04-E1:** Parse the local-wheel requirement despite its path space.
- **A04-E2:** Install the designated wheel as the containing package's dependency.
- **A04-I1:** Avoid the substantive space-caused parsing/metadata rejection.
- **A04-I2:** Resolve and install the designated local artifact, not a substitute.
- **A04-I3:** Complete containing-package installation with other prerequisites met.

E1/E2 are stated; I1/I2/I3 are necessary implications of the issue's installation
objective. Changing diagnostics or parsing alone is insufficient.

## Human-authorized additions

- **A04-H1:** Accept the exact raw-space `file://` URL.
- **A04-H2:** Accept the exact wheel-filename dependency token preceding `@`.

These quote the human statement in a new composite source record. The original
body is retained verbatim as its prefix and remains independently hash-bound.
Q1/Q2 are resolved in new clarification provenance; historical unresolved issue
records remain unchanged. No unsupported `resolved: true` flag is inserted into
the old FRC envelope. The logical contract ID stays stable for existing revision
checks; revision 2 has a fresh R6.3 artifact label and canonical identity.

## Fixture choices

- Source containing package: **my-local-package 0.1.0**, empty **my_module.py**;
  exact concrete setup.py content and both digests retained in the fixture manifest.
- Source wheel: **pipefunc-0.46.0-py3-none-any.whl**, exact source URL, SHA-256
  `bd1bc99a9788f01d218d83a0389ebb17e740b0cab60e7ac57d8d3c0d51f28181`.
- Research setup: Ubuntu 24.04 Linux x86_64, ordinary CPython 3.13.1, fresh isolated
  venv; pip 24.3.1 baseline, setuptools 75.6.0, wheel 0.45.1.
- Research prerequisites: cloudpickle 3.1.0, networkx 3.4.2, numpy 2.2.1;
  each wheel URL, filename, digest, metadata and payload hashes fixed. No extras.
- Only tools and those unrelated prerequisites may be preloaded. Both target
  distributions must initially be absent. Offline separate wheelhouse excludes
  pipefunc. Working directory **/tmp/lykoi-r6-3-p6-a04**, local subdirectory **my folder**.
- Observation: fixed install-report path/provenance/digest checks plus independent
  target-venv distribution and payload inspection, input hashes before/after.

These versions/platform/isolation/observation choices are fixture engineering,
not added product behavior. Compatibility is supported by wheel tags and declared
Python requirements; unusual-input or installation success is not empirically
established. The evaluated subject must handle the declared setup, rather than
silently switching input or tools after an observed failure.

## Acceptance expectations

[Fixed procedure](ACCEPTANCE-PROCEDURE.md), [observer](observe.py), and
[bound plan](ACCEPTANCE-PLAN.json) define four separately identified predicates:

1. **Parsing:** unchanged exact declaration accepted, containing dependency metadata
   generated without syntax rejection.
2. **Resolution:** designated pipefunc wheel selected from exact local path/digest.
3. **Containing-package installation:** command succeeds; my-local-package 0.1.0 and
   its module independently observable in target environment.
4. **Dependency installation:** previously absent pipefunc becomes installed at
   0.46.0, local provenance/digest matches and wheel payload hashes match.

The initial absent-state control prevents installed-state success before the
command. No unrelated malformed-input or alternative-spelling oracle is invented.
All four checks must pass in the same exact-input run. **All are NOT_RUN.**

## Remaining uncertainties

**No unresolved material behavioral-authority question.** Q1/Q2 are legitimately
resolved by the human for this bounded experiment. Fixture identities are fixed;
implementation algorithms and layer responsibility remain delegated.

**Execution integration limitation:** the fixed shell/observer procedure is not an
existing native package-install payload. `native_plan` remains null; the unchanged
local evaluator cannot be claimed execution-ready for this procedure. Any later
integration preparation requires separate authorization and exact approval of its
representation before authoring. This is a concrete integration limitation, not
another request to clarify pip behavior, and does not justify an adapter here.
No candidate subject, backend success or installation has been tested.

## Scope limitations

Research-only, same-agent/same-model preparation and review; expectations independent
of generated software, not independent cognition. Procedurally selected, previously
exposed source; not blinded generalization. No upstream intent certification,
packaging-standard validity ruling, causal diagnosis, production authority, whole-pip
compatibility guarantee or Lykoi capability/kernel verdict. Original source and all
R6.1/R6.2 evidence preserved. Kernel 26 and implementation remain unchanged.

## Exact identities

SHA-256 of existing CJ-1 canonical JSON, except original capture bytes:

| Artifact | Exact identity |
| --- | --- |
| Original source capture | `811cd95034444011f50e13572ebd10c810692b9e26b6355863d1aae3aa1af747` |
| Original FRC source record | `89835744da01e163649a40de1d08d99c7a5b11766ad2d5f0fd7d68325ff04f19` |
| Human clarification | `232fef22356ed5b743c0e3e572c69c76ed6669ff7dcceab7989c5e7fbc9d48d8` |
| Revised FRC, revision 2 | `aa2af92cf77073f1f42a70065d64135d211bf7bc6889aeeb4a033ce3aa449aba` |
| Fixed acceptance plan | `2ec947565b95dbed28bf5096aa945dbf528c1bdaf2763a99cc95f7da587f0dc4` |
| Fixture manifest | `d3f38f5cdcf4aac2602e83ce66de6b227200f7e12185a42f2d3ece83efb4c6e1` |

Original source is `pypa/pip#13139`, issue ID `2766862677`, node
`I_kwDOABYSQ86k6vlV`, author `basnijholt` / `6897215`, retrieved
`2026-10-08T13:52:21.230149+00:00`. Original title/body/provenance identities and
all new byte identities, including this review, are in [IDENTITIES.json](IDENTITIES.json)
and [source verification](SOURCE-VERIFICATION.json).

## Recommendation

**Ready for explicit research approval of the exact revised FRC, fixed acceptance
expectations, clarification and fixture identities above, with this review and its
execution-integration limitation.** No material clarification round is needed.
Artifact approval must come from a subsequent human interaction; execution additionally
needs separate authorization, a designated evaluator and a properly bound compatible
execution representation under the existing local path. Approval is not a stage pass.

No approval, research execution receipt, grant, seal, semantic evaluation, authoring,
compilation or behavioral verification has occurred. **Stop after publication.**
