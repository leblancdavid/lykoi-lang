# R5.116A procedural selection policy — version 1

This policy must be committed before any candidate issue description is fetched or
inspected. It prospectively amends R5.116's independence prerequisite; the blocked
R5.116 record remains unchanged. Material is **externally authored, procedurally
selected evaluation material**, not independently blinded curation. The development
agent knows Lykoi's capabilities and will see source material during curation.

## Fixed repository frame and order

Use these established public open-source upstream projects, chosen by their ordinary
application function, without querying issues or predicting Lykoi suitability:

1. `jqlang/jq` — JSON data processing.
2. `curl/curl` — network data transfer.
3. `redis/redis` — database/server storage.
4. `pypa/pip` — software package installation.
5. `pytest-dev/pytest` — automated testing.

Exact repository identities are `https://github.com/<owner>/<name>` above. Preserve
GitHub numeric/node IDs, repository metadata, license metadata and default-branch
revision at retrieval as provenance. Domain diversity concerns these functions,
not artificially rewritten behaviors. No repository substitution is permitted.
The frame is a purposive five-domain sample, not random or population-representative.

## Sources, ordering and budget

Only original GitHub issue title/body from each named upstream repository is eligible.
Include open and closed issues. Fixed creation cutoff: `2025-01-01T00:00:00Z`.
Query GitHub REST issue search with `repo:<owner>/<name> is:issue
created:>=2025-01-01`, `sort=created`, `order=asc`. Retrieve one result per page and
inspect in that order. Preserve search response and issue API response for each
inspected candidate. Equal creation timestamps use the API's returned order; record
that tie-order limitation rather than claim an additional stable sort.

Select the first eligible issue per repository. Maximum **15 candidates per repository**,
75 total; stop scanning that repository immediately upon selection. Repository metadata
and license requests are not candidate inspection. Network failures permit at most
two retries per request, without changing queries, cutoff, ordering or candidate budget.
Do not bypass inaccessible candidates by alternate semantic searches. Exhausted budget,
unavailable source or unresolvable ordering produces an incomplete batch report.
Search indexing is mutable: retain retrieval times/responses; reproducibility is against
captured responses, not a promise future live search returns identical results.

## Eligibility and exclusions

Every inspected candidate must receive SELECTED or EXCLUDED with rule IDs and reasons.
An eligible issue is externally authored and supplies observable requested behavior
with a bounded, practical acceptance surface. Bug reports may qualify when the body
states an expected outcome, or a necessary correction is unambiguous from its stated
contract. Material ambiguities do not automatically exclude a bounded requirement:
preserve them and mark clarification-required obligations.

Exclude only on these fixed rules:

- E1: Not an actual upstream issue, outside cutoff, duplicate of an already selected
  source, or authored for this Lykoi experiment rather than an external project.
- E2: No requested observable software behavior (administration, question/support only,
  announcement, discussion without a behavior request).
- E3: Primarily visual design, styling, subjective presentation or documentation-only
  editing with no software behavior change.
- E4: Requires unavailable proprietary service/data, credentials, special physical
  hardware/environment or inaccessible essential attachments to establish acceptance.
  Ordinary open-source software dependencies/local networking are not grounds alone.
- E5: Unbounded redesign/umbrella roadmap, or original title/body lacks sufficient
  context to isolate any source-derived observable acceptance obligation.
- E6: Original source embeds a concrete fixing patch/solution/implementation narrative
  that cannot be separated from the requested behavior without using answer material.
  Record contamination on receipt; do not inspect linked solutions or use such content
  for criteria. Incidental issue links or implementation names are not automatically E6.
- E7: Exact original source cannot legally/practically be retained for research with
  provenance and attribution, or source authorship is not identifiable.

Never exclude for anticipated Lykoi difficulty, missing semantics, uncertain success,
project unfamiliarity, closure status or a requirement's material ambiguity alone.
After exclusion, advance to the next issue in the fixed order. Do not replace a selected
issue because it is difficult. If fewer than five qualify, report the incomplete batch.

## Preservation and acceptance

Retain UTF-8 original title and body without rewording, full API captures and SHA-256
identities, exact URL/number, author ID/login, creation/update/retrieval times, project
metadata and license/provenance limitations. Distinguish GitHub's current retrieved
body from an unrecoverable original creation revision; no claim of historical immutability.
Preserve search provenance and selection order. Do not open comments, timeline,
implementing pull requests, fixing commits or project implementation files. Context
is restricted to original title/body and non-solution repository metadata. Linked
context that is essential but unavailable under this rule is recorded, not invented.

For each selected issue create candidate acceptance obligations with four separate
sections: explicit requirements, necessary implications, unresolved ambiguities and
assumptions requiring clarification. Trace obligations to exact source quotations.
These are candidate source interpretations, not owner-approved FRCs, executable tests
or independently authored acceptance. No Lykoi capability information fills gaps.

Use five opaque IDs `P6-A01` through `P6-A05` in fixed repository order. Full manifest
binds source/API/repository/acceptance/policy hashes, policy commit, selection order,
timestamps and provenance. Development-visible summary contains only IDs/readiness.
It does not erase this curation session's exposure. Fix final files with hashes and
ordinary Git history; no isolation or controller framework. No evaluation or Lykoi
implementation modification is authorized. Stop after curation.
