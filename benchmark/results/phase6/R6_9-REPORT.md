# R6.9 — Provider-neutral reviewer isolation infrastructure

**Final classification: `R6_9_ISOLATION_CONTROL_GAP`.**

Bounded infrastructure was implemented and synthetically tested. The current host
cannot enforce the required reviewer filesystem/network boundary. The real runner
attempt refused dispatch and retained sealed failure evidence. **No substantive
review was conducted; independent-review readiness is not established.**

## Authorization, scope and chronology

The owner's R6.9 request explicitly authorizes infrastructure implementation,
synthetic qualification and publication. Initial Git status was clean at
`0c35cdf6ee141637dd45b1f8bb50573ce8d839b6`. The publisher inherited prior
finding-bearing guidance and remains ineligible to supply independent judgments.
No subagent was assigned. No provider credentials were sought or used.

1. Read applicable governance and R6.8 isolation/source records. Inspect only the
   authorized candidate and existing-kernel definitions needed for packaging.
2. Implement standalone Python infrastructure under `tools/reviewer_isolation/`:
   frozen export, exact package verification, data allowlist broker, provider-neutral
   request construction, offline sandbox runner, output capture and anchored seals.
3. Prepare the nondispatched candidate export and verify reproduction using two
   independent temporary output directories in tests.
4. Execute adversarial tests and unconfined negative controls. The initial evidence
   collection halted at Windows Winsock initialization with an empty environment;
   preserve its transcript and [halt record](r6_9/evidence/ATTEMPT-HALT.md).
   Correct only negative-control orchestration to explicitly permit `SystemRoot`,
   and execute again into a new evidence directory. Runner policy remains empty-env.
5. Publish final evidence and this report. Stop before substantive assignment.

## Deliverables

| Deliverable | Location |
| --- | --- |
| Infrastructure implementation report | This report |
| Reviewer package specification | [INPUT-PACKAGE-SPEC.md](r6_9/INPUT-PACKAGE-SPEC.md) |
| Isolation threat model and limitations | [THREAT-MODEL.md](r6_9/THREAT-MODEL.md) |
| Provider-neutral invocation contract | [INVOCATION-CONTRACT.md](r6_9/INVOCATION-CONTRACT.md) |
| Runner/package/seal utilities | `tools/reviewer_isolation/boundary.py`, `prepare.py` |
| Synthetic qualification/tests | `tools/reviewer_isolation/qualify.py`, `tests/test_boundary.py` |
| Executed evidence | [verification](r6_9/VERIFICATION.md), `r6_9/evidence-final/` |
| Candidate preparation export | `r6_9/package/`, with separate `publisher-provenance.json` |

## Package and evidence identities

Candidate package SHA-256:
`b2f178d0db9951e3f2ef781403e1d678921a1f7cd76b7328daf7553dec13e440`.

It contains **15 payload files** plus its manifest. Local names and per-file raw-byte
hashes are recorded in `package/manifest.json`. Publisher provenance pins every
source, slice and transformation. Frozen R6.6 definitions/witnesses and historical
sources were not edited. The package excludes R6.7/R6.8 findings and guidance.
Necessary proof questions are neutral; there is no expected substantive answer.
Dependency sufficiency and unbiased passage selection remain **UNREVIEWED**.
This package is prepared, not approved for dispatch.

Final actual host-attempt seal SHA-256:
`c77bd4567e059006da7e429e82bd6a7315553301f428d3bbeaf2e514527b6038`.

The sealed status is `ISOLATION_CONTROL_GAP`, not a reviewer result. An owner must
retain the anchor separately; SHA-256 sealing is not authentication or immutable
storage. A publication file-identity inventory is retained alongside the artifacts.

## Executed qualification

Environment: Windows (`win32`), Python **3.14.3**. Docker/bubblewrap executables
were unavailable. `wsl --list --quiet` listed no distribution. No installation or
provider execution was attempted.

- **28 tests run; 28 pass; 0 failures, 0 errors, 0 skips.**
- Executed package/broker tests reject forbidden files, unknown tools/retrieval,
  unexpected resources, symlinks, hardlinks, traversal and undeclared Markdown
  dependencies. Named guidance/prior-finding markers are rejected.
- Executed fresh subprocess test verifies explicit cwd, exact stdin, absence of a
  synthetic secret variable and absence of parent Python-global history. It does
  not verify model/provider memory or inherited provider instructions.
- Executed negative control reads synthetic forbidden and guidance files outside
  cwd and connects over loopback. All three accesses **succeed**, demonstrating
  that cwd/environment/startup isolation is insufficient. The Windows negative
  control permits `SystemRoot` only; values are not published.
- Configuration tests reject inherited message additions, reused sessions, expanded
  tools/environment, shared retrieval and uncontrolled network settings.
- Adapter-failure/timeout/success paths and Linux command construction are tested
  using **mocked subprocess transport**, explicitly not OS/provider qualification.
- Executed seal tests reject changed output, resealing against the retained old
  anchor and missing provenance.
- Actual host attempt constructs a synthetic request, refuses before adapter
  dispatch because sandbox controls are unavailable, and seals/verifies the refusal.
- Candidate package verification and `git diff --check` pass. Infrastructure
  publication records preserve the executed test transcript and failure chronology.

Linux bubblewrap access-denial qualification: **NOT_RUN**. Live provider adapter
failure tests: **NOT_RUN**. Provider/model calls: **0**. Independent cognition:
**not established**. Synthetic answers are not independence evidence.

## Implemented versus unavailable guarantees

Implemented/exercised: reproducible source-bound packaging, exact file identity,
data-API access denial, strict invocation configuration, new request construction,
explicit fresh-process cwd/environment for synthetic tests, fail-closed dispatch,
capture/failure handling and anchored output/provenance verification.

Unavailable/unqualified: actual hostile-reviewer filesystem/network containment,
Linux namespace usability and adversarial denial probes, a live provider adapter,
remote-provider destination restrictions, effective provider-side request/context
inspection, memory/retrieval disable attestation and complete input dependency audit.
Hidden provider prompts/training/cache/state cannot be independently excluded.
Exposed publisher bias and trusted-host/anchor tampering remain explicit limits.
No absolute isolation claim is made.

## Recommendation for the first controlled independent review

**A substantive review should not be dispatched on this host under this round's
evidence.** The owner may authorize a later, bounded qualification step on a host
with an enforceable boundary, followed by an explicitly approved review:

1. Independently inspect and approve exact candidate export, dependency closure,
   neutral questions, adapter/model choice and provider-side assumptions.
2. Exercise an actual sandbox against forbidden files/repository visibility,
   synthetic guidance injection, env leakage, retrieval, sessions, shared writable
   state and network/tool access. Bind that evidence to exact code/config/host.
3. For a remote provider, implement and qualify the explicit destination-restricted
   transport and credential separation; for a local provider, audit the standalone
   adapter and its model inputs. No provider-specific identity becomes normative.
4. Obtain owner approval of exact package and qualification evidence **before**
   enabling substantive dispatch in a separately versioned runner/protocol.
5. Form and externally anchor the reviewer result seal before exposing comparison
   material. Record unavoidable provider-side uncertainty without claiming absolute
   isolation or statistical independence.

The controls permit a path toward a future authorizable review, but **do not yet
support execution authorization for an independent semantic assessment**.

## Preservation and stop

Kernel remains **26**. Language, compiler, lowerer, runtime, canonical model and
historical artifacts unchanged. I-BOUND/C-ATOM not implemented. No benchmark
solutions authored or compiled. P6-A04 acceptance executions **0**; P6-A05 not
accessed. R6.6 substantive review **NOT_RUN**; no semantic verdict or repair priority
was formed. **Stopped after infrastructure, synthetic qualification and publication.
Await explicit owner approval before further qualification or review.**
