# R5.85 — Production Formalization & Evaluation Architecture

## Result

**R5_85_PRODUCTION_ARCHITECTURE_DEFINED**.

The [core architecture reference](../../../docs/production-formalization-evaluation-architecture-r5.85.md)
consolidates R5.79–R5.84 into a concrete requirements-to-software service. It defines
components, scoped authority, artifact handoffs, deterministic enforcement, fallible
AI judgment, human decisions, isolation, failure behavior and a minimal engineering
path. This is an architecture consolidation, not another qualification experiment.
No production authority is exercised or empirical reliability upgrade claimed.

## Deliverables and design choices

All requested architecture deliverables are integrated in the reference rather
than split into disconnected gate documents:

| Deliverable | Architecture sections |
| --- | --- |
| Evidence consolidation and component design | 1–3 |
| Authority model and explicit authority graph | 2 |
| AI wizard and material question selection | 4 |
| Clarification/versioning/invalidation protocol | 5 |
| Project-policy eligibility, authority and precedence | 6 |
| Independent SOI/reconciliation and finite reviewer trust model | 7 |
| FRC lifecycle and WHAT versus implementation seals | 8 |
| Content-bound artifacts and downstream identity | 9 |
| BDI, adequacy, full faithful unchanged-V1 projection | 10 |
| Least-authority Lykoi author boundary | 11 |
| Independent prefrozen verification planning and external execution | 12 |
| Protected admission, permitted readers, containment and contamination | 13 |
| Machine-verifiable executable freeze design | 14 |
| End-to-end graph with every handoff contract | 15 |
| Core trust-boundary table | 16 |
| Threat/failure controls and residual risks | 17 |
| Normal-user workflow | 18 |
| Product/research/held-out separation | 19 |
| Minimal implementation stages and completion evidence | 20 |
| Remaining-unknowns classification | 21 |
| Protection, stop and final three answers | 22–23 |

The central choice is **explicit human source/product authority with fallible AI
evidence**, mediated by one deterministic controller. Independent review commits
source-only inventory before candidate access; agreement is evidence, not a grant.
Finite review terminates in owner approval or a visible unresolved issue. Sealed
WHAT is separate from the implementation grant: supported structural coverage,
BDI/adequacy, complete faithful V1 and an independently sealed verification plan
must precede author dispatch. Verification criteria are fixed before implementation.

The architecture is general product infrastructure. Protected-source custody,
one-time exposure/first-result accounting and a locked benchmark deployment are
additional held-out containment requirements. No universal natural-language proof,
autonomous approval reliability or semantic completeness is asserted.

## Evidence reviewed and limits

Read exact public reports R5.79–R5.84, the R5.83 nonactivated precommitment, current
FRC/SCCA/BDI/adequacy specifications, repository guidance, project overview and
benchmark README. Existing reported observations supply the design basis; they
were not rerun or relabeled. R5.84's dishonest umbrella-inventory counterexample
is preserved as the reviewer truth boundary, not addressed by another review chain.

No small prototype was necessary: the new claims concern responsibility, authority,
artifact/state contracts and engineering sequence. Their operational completion
evidence is specified in roadmap §20. Implementing that roadmap is future work,
not an R5.85 activity. Documentation verification is recorded below; compiler and
benchmark suites are not evidence for architecture correctness.

## Protected accounting and historical preservation

| B03 activity in R5.85 | Count/status |
| --- | --- |
| Source access attempts / reads | **0 / 0** |
| Content-revealing metadata access / inference | **0 / 0** |
| Formalization / review / discovery / adequacy | **0 / 0 / 0 / 0** |
| Authorizations / reservations / packaging / openings | **0 / 0 / 0 / 0** |
| Consumer observations / generation / execution / acceptance / repair | **0 / 0 / 0 / 0 / 0** |
| FRC / V1 package / protected commitment / runner eligibility | **Not created / not claimed** |

**B03_PRISTINE / B03_NOT_EVALUATED /
B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT** remain true. This is scoped session activity
and inherited status, not an inspection of protected content, metadata or ledger.
No other protected requirement is read. **R5.83-CANDIDATE-1 remains unactivated**.
R5.80–R5.84 classifications, frozen requirements/oracles, historic evidence,
language/compiler/runtime/schema, generated artifacts and V1 retain their content.
Core **30** inherited; B02 exposed/indeterminate history preserved; Phase 5C paused.

## Verification

Documentation-only checks completed:

* **PASS:** all **14** declared ordinary relative links in the new architecture/report
  resolve; all **23** numbered architecture sections occur in order; result and
  protection markers are present; both new documents have no trailing whitespace.
* **PASS:** scoped `git diff --check` for the five intended documentation paths.
  Git reports checkout LF/CRLF conversion notices, not whitespace errors.
* **PASS:** tracked diffs and final change inventory contain only the architecture,
  round report, project overview, decisions and research-log updates.

The initial Python link-check invocation could not start because `python` was
unavailable in this environment. Equivalent scoped PowerShell/.NET checks passed.
They read only the two new documents and check existence of their explicitly declared
ordinary link targets; no protected resource enumeration/content inspection occurs.
No broad harness discovery, production prototype or qualification test runs.

## Stop and final answers

**R5_85_PRODUCTION_ARCHITECTURE_DEFINED. Stop after R5.85.** The roadmap is not
implemented, no next round starts and no held-out exposure is authorized.

1. **What exact system are we now proposing to build?** A requirements wizard with
   versioned owner source/policies and clarification, blind independent SOI review,
   an immutable authority/artifact controller, sealed FRC, bounded discovery/adequacy,
   faithful V1, restricted Lykoi author, pinned compilation and independent external
   verification planned before implementation.
2. **Which parts are trusted, untrusted, human-authorized, AI-judged and mechanically
   enforced?** Humans authorize meaning/choices and declared delegates approve scoped
   evidence. AI interpretations/review remain fallible. The controller, store,
   isolation platform and deterministic tools enforce bindings, roles, bounded
   checks and halts. Author code and executable behavior are candidates for validation
   and independent verification, not their own behavioral authority.
3. **What is the shortest credible engineering path to an end-to-end public rehearsal?**
   Build the authority/artifact controller; integrate wizard/clarification/policies
   and blind reconciliation with existing bounded analysis; close isolated authorship
   and independent prefrozen verification; rehearse a frozen public end-to-end
   deployment with successes, intentional faults and visible unsupported refusals.
