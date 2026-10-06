# R5.90 — Live AI Worker Qualification

## Classification and operational stop

**`R5_90_LIVE_AI_WORKERS_BLOCKED_CREDENTIAL_UNAVAILABLE`**.

The required live credential cannot be obtained through the available configured
environment mechanism. R5.90 stops at operational preflight under the explicit
credential-unavailability stop rule. **Provider requests: 0; live runs: 0; qualified
roles: 0/4.** This is neither a partial live qualification nor a model failure.

[Machine-readable preflight](r5_90/operational-preflight.json) records only
credential presence, public configuration information and execution status.

## Observations

- The working tree was clean before edits.
- The existing `public-ai-adapter-1` HTTPS adapter accepts the designated
  `LYKOI_REHEARSAL_API_KEY` environment variable in its trusted service process.
- A presence-only PowerShell probe of `LYKOI_REHEARSAL_API_KEY` and the conventional
  `OPENAI_API_KEY` found neither nonempty in Process, User or Machine scopes.
  The latter is not an adapter input; it was checked only as a potential externally
  provisioned credential source. No credential values were printed or persisted.
- `rehearsal/model-configurations-1.json` retains `model: null` for formalizer,
  reviewer, author and verifier (candidate verification-plan producer). Model
  selection is an additional configuration prerequisite.
- No external secret mechanism was supplied. The coding harness's own model identity
  is not a configured R5.89 HTTPS worker or a provisioned service credential.
- No provider request, scored run, mock replacement, retries, synthetic approval,
  registry eligibility or public activation was performed.

## Deliverable accounting

The operational preflight, this report and current-boundary documentation updates
are complete. The requested worker-configuration specification, new frozen corpus,
predeclared criteria, four live role evidence sets, end-to-end calibration,
correlated-error analysis, qualification records, registry, replacement test,
exact-worker freeze integration and provider cost/performance evidence are
**NOT_RUN / NOT_IMPLEMENTED due to the operational stop**. Existing R5.89 fixtures
and mock results are not promoted to R5.90 live evidence. No qualified worker
identity is invented to fill the missing deliverables.

## Completion answers

1. **Exact configurations exercised live:** none.
2. **Roles qualified:** none; all four remain operationally untested.
3. **Observed semantic failure modes:** none observed live. Missing credentials
   and null model selections are operational blockers, not semantic failures.
4. **Formalizer/reviewer correlated errors:** not measured; no inference occurred.
5. **Replacement without changing artifact meaning:** still the architectural rule:
   models are replaceable untrusted workers, while exact artifacts, explicit authority,
   seals, grants and deterministic validation determine meaning. No live replacement
   demonstration was obtained in R5.90.
6. **New configurations require independent qualification:** yes, as the required
   policy; no inheritance or new registry enforcement is implemented in this stopped
   round. Changed models, versions, prompts or inference parameters must receive new
   content-bound identities and new evidence before eligibility.
7. **Public freeze binds exact qualified worker configurations:** no. The existing
   inactive R5.89 candidate binds its unqualified configuration; R5.90 freeze integration
   was not implemented.
8. **Infrastructure eligible to freeze before selecting a requirement:** no. The
   live-qualification blocker remains, with no approved role qualifications. No future
   public rehearsal requirement has been selected.

## Verification and next operational prerequisite

Verification consisted of reading the public adapter/configuration and executing
the presence-only environment probe. No application/compiler or benchmark suite
was run: this round changes only documentation and the preflight evidence record.
No qualification success or independently authenticated approval is claimed.

A separately authorized continuation needs a service credential provisioned through
`LYKOI_REHEARSAL_API_KEY` and explicit provider/model settings. The calibration corpus,
role criteria and candidate prompts must then be frozen before inspecting scored live
results; qualification decisions must bind exact evidence and explicit declared-authority
review. Provisioning alone does not remove the qualification blocker.

## Protection and stop

**B03_PRISTINE / B03_NOT_EVALUATED / B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT** remain
true by inherited boundary and public-only operations. All inherited B03 counters
remain zero; R5.90 B03 access/activity counters are zero. No protected resource was
read, opened, packaged, inferred, authorized or sent to a worker. This is not a new
protected-content audit or a B03-readiness classification.

**`R5.83-CANDIDATE-1` remains unactivated.** The capability profile, mapping registry,
Lykoi semantics, V1 and existing freeze machinery retain their prior boundary.
Phase 5C remains paused. **Stop after R5.90 operational preflight.**
