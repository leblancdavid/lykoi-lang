# P6-A04 — material clarification record

Status: **UNRESOLVED; research review only**. Source: preserved `pypa/pip#13139`,
`basnijholt`, captured 2026-10-08T13:52:21.230149+00:00. No linked context,
packaging standard, fixing PR, implementation commit or solution discussion used.

## A04-Q1 — raw-space URL acceptance

**Question:** Does the research contract require the original `file://` URL with
its literal space to be accepted, or is an authoritatively clarified encoded URL
the intended accepted input?

**Evidence:** Expected behavior says: "`pip` should correctly parse the
`install_requires` and install the local wheel, even if its path contains spaces."
The exact reproduction requirement before shell interpolation is:

```text
pipefunc-0.46.0-py3-none-any.whl @ file://$(pwd)/my folder/pipefunc-0.46.0-py3-none-any.whl
```

**Competing interpretations / consequences:**

- Exact-input change: the raw-space URL must parse and identify/install that
  local wheel. Requiring the reporter to encode the URL would not satisfy this branch.
- Corrected-input contract: a clarified space-encoded URL is eligible. The original
  input's rejection would not by itself violate that revised bounded contract.
  This branch is not currently authorized by the preserved issue.

**Recommendation:** Prefer the exact-input interpretation for fidelity to the supplied
reproduction and expected behavior. Ask the project owner to explicitly settle the
accepted spelling for the research experiment. The source does not incorporate a
URL standard that establishes whether this spelling is already valid; no standard
or conventional pip policy is imported to answer that question. This recommendation
is not approval or a claim of upstream format validity.

## A04-Q2 — requirement-name spelling and artifact identity

**Question:** Must the exact wheel-filename token before `@` be accepted and lead to
installation of the designated wheel, or is the intended input an authoritatively
clarified project-name token?

**Evidence:** The reproduction uses
`pipefunc-0.46.0-py3-none-any.whl @ file://...`, not a separately specified project
name. Its failure says `'install_requires' must be a string or iterable of strings
containing valid project/version requirement specifiers`. The source gives no
standards-based name-validity ruling or alternate accepted token.

**Competing interpretations / consequences:**

- Exact-input change: accept that original left-hand spelling while still installing
  the source-designated local artifact. A remote/name-derived substitute is not success.
- Corrected-input contract: replace the left-hand spelling using legitimate
  clarification. The original input need not be accepted under that revised scope.
  No correction is silently made in this candidate.

**Recommendation:** Preserve the literal source input in the proposed exact-input
branch, but obtain an explicit decision. Do not assert the token is invalid from
memory, or infer that fixing only the URL necessarily makes the requirement valid.
If the owner chooses a corrected input, retain the original source and publish a
linked clarification/new candidate and acceptance identity before approval.

## Related evidence that does not require an internal-design question

The traceback reports `python setup.py egg_info`, `metadata-generation-failed`,
"This error originates from a subprocess, and is likely not a problem with pip."
and "This is an issue with the package mentioned above, not pip."
These qualify the reporter's attribution, not the end-to-end requested result.
The experiment can specify parsing and installation without choosing which internal
layer changes. No demand for a pip-only parser patch or bypass of backend validation
is derived. Do not ask the owner to choose a parser algorithm, language or code layout.

Exact backend versions, wheel bytes/digest and transitive dependency fixtures are
absent. They must be fixed as compatible, source-faithful execution prerequisites
before an executable acceptance plan can be approved. They are fixture-readiness
limitations, not additional invented behavioral choices. The wheel URL was not fetched.

Exact verbose output, numeric exit codes, rollback, network restrictions, unrelated
invalid-input behavior and universal no-space/platform compatibility are outside the
source-defined delta. No human question is needed to fill those unrelated policies.

## Decision handling

Recommendation: **CLARIFY A04-Q1 and A04-Q2**. All acceptance groups remain
conditional. The current candidate is ready to inspect, not to consume as an approved
executable experiment. Project-owner research clarification is attributed as a research
scope decision, not as original-maintainer intent. No source question is waived by
setting an approval flag. This round records no clarification answer or approval.
