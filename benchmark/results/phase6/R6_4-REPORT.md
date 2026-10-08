# R6.4 — P6-A04 research approval and native execution readiness

**Final classification: `R6_4_LYKOI_SEMANTIC_GAP`.**

Exact conditional research approval is recorded and all four canonical artifact identities
and preserved source provenance verify. The current **implemented native semantics and
lowering** cannot express and execute the required package workflow. The missing verifier
payload is real, but supplying it alone would not produce a faithfully authored executable.
This is a static readiness assessment, **not a benchmark evaluation or proof that the
abstract 26-construct kernel can never express packaging behavior**.

## Published evidence

1. [Exact user authorization](r6_4/AUTHORIZATION.md) and
   [research approval receipt](r6_4/RESEARCH-APPROVAL-RECEIPT.json).
2. [Verified identity/provenance and implementation manifest](r6_4/IDENTITY-PROVENANCE.json).
3. [Native capability inventory, classified gaps and observation analysis](r6_4/CAPABILITY-INVENTORY.md).
4. [Hash-bound static code excerpts](r6_4/STATIC-EVIDENCE.json),
   [offline publication verifier](r6_4/record.py) and
   [publication identities](r6_4/PUBLICATION-IDENTITIES.json).

## Approval, identity and preservation

| R6.3 artifact | Verified CJ-1 canonical JSON SHA-256 |
| --- | --- |
| Human clarification | `232fef22356ed5b743c0e3e572c69c76ed6669ff7dcceab7989c5e7fbc9d48d8` |
| Revised FRC revision 2 | `aa2af92cf77073f1f42a70065d64135d211bf7bc6889aeeb4a033ce3aa449aba` |
| Fixed acceptance plan | `2ec947565b95dbed28bf5096aa945dbf528c1bdaf2763a99cc95f7da587f0dc4` |
| Fixture manifest | `d3f38f5cdcf4aac2602e83ce66de6b227200f7e12185a42f2d3ece83efb4c6e1` |

The P6-A04-only retained source verifier checked original capture/API, title/body,
author/repository/ref/search and retrieval receipt bindings against R5.116A. Original
capture SHA-256 remains `811cd95034444011f50e13572ebd10c810692b9e26b6355863d1aae3aa1af747`.
The revised composite source retains the original body and separately attributed human
clarification. FRC, plan, fixture, procedure and observer bindings are checked offline.
No upstream live issue, fixing PR, linked solution or P6-A05 was accessed.

The user approves the four exact artifacts for bounded readiness research, conditional
on identity/provenance verification; those conditions passed before investigation.
The receipt retains the full user statement, conversation attribution and agent-recorded
UTC time. No human signature/time/session ID, upstream endorsement or execution evaluator
is invented. This is **not** a `local-research-receipt-1` permitting `execute`.
R6.3's historical `approved: false` and preparation statuses remain unchanged; new approval
is recorded prospectively, without changing approved bytes or expectations.

Exact input remains:

```text
pipefunc-0.46.0-py3-none-any.whl @ file:///tmp/lykoi-r6-3-p6-a04/my folder/pipefunc-0.46.0-py3-none-any.whl
```

The raw space, wheel-filename token, designated wheel and containing-package workflow
are preserved. All four fixed checks and initial absence control remain intact.

## Readiness findings

- **Demonstrated repository facts:** identities/provenance verify; implementation manifest
  matches R6.1; kernel accounting is 26. Native storage is JSON-record state, resources
  are JSON read/write, UUID and UTC clock; normal transformations/profiles are closed.
  Existing receipt/pipeline and independent subprocess interfaces are provider-independent.
- **Missing semantic capabilities:** accepted native operations do not implement requirement
  grammar interpretation, wheel/archive/metadata processing, containing build workflow or
  file/distribution installation effects. Storing an exact declaration and declaring an
  `effects` channel are insufficient. No package-specific profile/V1/lowering path exists.
- **Missing execution infrastructure:** `native_plan: null`; the approved high-level plan
  lacks the `external-cli-plan-1` payload shape. Verifier currently runs a generated target
  with host Python `-I -S`, empty environment, case-local JSON files and a ten-second timeout.
  It has no bound pinned-venv/wheel-staging/install/report/observer workflow or enforced
  install-time network containment.
- **Fixture/environment gaps:** approved Linux/CPython environment and staged wheels are
  not provisioned or exercised. R6.3 hashes and declared compatibility are useful inputs,
  not demonstrated bootstrap/install feasibility. Recording host is Windows.
- **Unresolved evidence:** kernel-level composition sufficiency, layer responsibility,
  actual observation availability/independence and repeatable safe outcomes remain untested.
  No readiness claim follows from pinning versions or specifying a design.

The inventory assigns S1-S3 semantic, I1-I3 infrastructure, F1-F2 fixture/environment and
E1-E3 evidence gaps with concrete code/procedure references. Semantic gaps describe the
current executable language boundary, not a minimality theorem or authorization to add
constructs. Generic relation mapping gaps are distinguished from unsupported operations.
No native structural-coverage result or first-blocker code was generated in this round.
An infrastructure-only classification would conceal these additional semantic limitations.

## Minimal proposed execution approach

**Proposal only; no currently complete existing-semantics-only route is demonstrated.**

1. Retain the exact approved contract/fixture/oracle as immutable inputs. Reuse existing
   records, explicit identities, predicates and finite reference/selection operations for
   decoded metadata/manifests where their semantics apply.
2. First investigate whether general parsing and typed artifact/resource effects can be
   composed from the current vocabulary. Explicitly identify any missing meaning and its
   non-package uses; separate core semantics from binary-resource and environment adapters.
   Do not hide a conventional parser/installer behind a generated command or arbitrary
   callback. No specialized benchmark construct is proposed or admitted here.
3. Only after a separately authorized, justified native semantic/lowering path exists,
   propose a content-bound verifier representation that stages hash-checked wheels in a
   disposable approved Linux environment, uses the exact working directory/venv/tools,
   captures the identified subject's unchanged `pip install --verbose .`, and binds before
   absence, command outcome/report and after payload observations to one run. Bootstrap
   may install the six permitted tools/prerequisites, never either target distribution.
4. Keep observer/report classification verifier-owned, retain all four expectations and
   disclosed limits, and obtain exact approval of any new execution representation plus
   separate execution authorization/evaluator designation. No fallback oracle, input
   repair or direct dependency-install shortcut is eligible.

A conventional fixture/observer is permissible as external setup/measurement, but conventional
code deciding the missing parse/resolve/install behavior would bypass native semantics.
Calling pip externally would measure pip, not establish Lykoi capability. Provider credentials
are unnecessary for identity checks, deterministic validation/lowering or verification; none
are introduced as requirements.

## Recommended next bounded research step

Request separate authorization for a **documentation-only general capability decomposition**
of parsing and typed binary/artifact effects across non-package examples (for example,
structured text import and archive-backed asset materialization). Produce an explicit
existing-construct composition argument or precise reusable missing-meaning inventory,
including authority/failure contracts and backend obligations. Kernel remains 26 during
that investigation; no repair, P6-A04 authoring or acceptance execution is implied.
An install harness alone is not the next sufficient step. Any later semantic extension
must have general-purpose justification and separately authorized implementation/verification.

## Verification and stop boundary

Initial `git status --short` was clean. Before analysis, a read-only Python command verified
all four identities, P6-A04 provenance, unchanged original body prefix, procedure/observer
hashes and implementation-manifest equality. Publication checks:

```powershell
$env:PYTHONPATH='src'
python -m benchmark.results.phase6.r6_4.record publish
python -m benchmark.results.phase6.r6_4.record verify
git diff --check
```

Checks cover identity/provenance, cross-bindings, static excerpt/file hashes, publication
identities, implementation equality, kernel accounting and constrained Git change scope.
The initial publication command stopped on a recorder-local undefined provenance variable
after writing the approval receipt. The return binding was corrected; the existing receipt
and its recording time were retained and publication rerun. No experiment stage was invoked.
These are evidence/publication checks, not semantic or behavioral acceptance tests.
No package retrieval/staging/bootstrap, tests, subject invocation, observer, native pipeline,
authoring, compilation, benchmark scoring, repair or P6-A05 access occurred.
All semantic/evaluation stages **NOT_RUN**; behavioral acceptance executions **0**.
Implementation/kernel **26**, model **0.3**, compiler/backend **0.3.0** and historical
artifacts/outcomes unchanged. No production certificate or benchmark success.

**Stopped after R6.4 publication. Await the user's next authorization.**
