# R5.86 — Authority and Artifact Controller Implementation

## Result

**R5_86_AUTHORITY_CONTROLLER_IMPLEMENTED** in authority/artifact-integrity scope.
R5.85's architecture was implemented without redesign or a discovered contradiction.
This is executable engineering evidence, not production-architecture qualification,
AI semantic reliability qualification or a complete deployed requirements service.

Implementation: [`src/lykoi_controller/`](../../../src/lykoi_controller/).
[Versioned interface/boundary](../../../docs/authority-artifact-controller-r5.86.md)
extracts requirements and records decisions. [34 controller tests](../../../tests/test_authority_controller.py)
and the [public synthetic driver](r5_86/demonstrate.py) exercise the mechanics.
The [prospective evidence summary](r5_86/evidence.json) records final counts and
the driver's exact synthetic grant/target bindings.

## Delivered mechanics

* Typed canonical SHA-256 immutable identities, exact bytes and schema/project/
  dependency binding; safe-integer CJ-1 conformance and strict JSON decoding.
* Typed DAG covering source through external verification, with coherent target
  roots and exact upstream versions; source recovery provenance extension point.
* Separate candidate/review/human/mechanical/seal/implementation claims and exact
  R5.85 FRC lifecycle, including visible clarification/revision/rejection halts.
* Append-only digest-linked authority journal with actor, role, exact subject,
  prerequisites, resulting state, reasons and evidence identities. Approval/seal/
  grant artifacts bind supporting event identities.
* Provisioned synthetic credential/role/project authority; immutable registry on
  restart; reviewer/formalizer escalation and author self-verification denial.
* WHAT and independent verifier-plan seals, implementation grants, exact freeze/
  action/bundle checks, conservative supersession/revocation, retained history.
* Explicit policy adoption/application/feature exceptions and new-root human
  clarification authority without silently transferring old approvals.
* Atomic SQLite persistence and expected-revision checks; durable single-use
  reservations, incomplete crash inspection, stale completion denial and replay
  rejection; service-side programmatic audit and applicability interfaces.

## Executable evidence

| Check | Actual outcome |
| --- | --- |
| New controller suite | **34/34 PASS**, final run 39.255 s. |
| False AI approval/coverage/adequacy/verification/human-confirmation | No self-created human/sealed/implementation authority; invalid downstream use denied. |
| Wrong human version, identical locator/different content, clarification mismatch, reviewer escalation, author self-verification | Denied with structured failures. |
| Source, policy, FRC, structure, adequacy, V1 and plan supersession | Seven stage-replacement subcases invalidate old descendant grants; history retained. |
| Clarification-answer withdrawal and multi-answer transcript retention | Prior answers stay normative in later roots; withdrawal blocks descendant use. |
| Supported synthetic chain | Grant issued only after all bound prerequisites, including plan seal; source replacement makes it inapplicable. |
| Determinism | Two databases with identical artifacts/event sequence produce identical identities, semantic journals and grant decisions. |
| Persistence/restart | Separate Python child process reproduces the audit; live grant applicability unchanged; incomplete reservation/replay rejection survives restart. |
| Concurrency/corruption | Stale expected revision denies with no partial registration; update/delete triggers reject; corrupted database copies refuse startup. |
| Compiler/application | **22/22 + 9/9 PASS**. |
| Selected historical R5.80/R5.81/R5.82/R5.84/V1 suites | **104 PASS / 2 FAIL**, 106 selected tests; details below. |
| Model validation/safety | PASS; safety reports zero capability violations and zero invalid transitions. |
| Whitespace/change scope | Scoped Git and new-file checks PASS; only prospective R5.86 implementation/tests/evidence/documentation and three current-status documents changed. |

Selected historical test counts are R5.80 **17 pass / 1 fail**, R5.81 **18/18**,
R5.82 **16/16**, R5.84 **20 pass / 1 fail**, V1 **33/33**. The two failures are
physical-byte checkout reproduction checks, not changed semantic outcomes:

1. `test_reproducible_results_and_exact_coverage_locators`: public B01 checkout
   bytes hash `431c0c024d371284e9546171b06db1c2d11e4a1c6cbddb9babaf5fb3c8689e54`
   rather than historical `b7b2d714db5cee566e9e55982dd4c4d95d3d57f0c341e04ba1e15c24e9a8e94d`.
   Its six CRLF sequences normalized to LF reproduce the historical pin.
2. `test_independent_disagreement_and_public_b01_calibration`: public R5.84
   independent-SOI checkout bytes hash
   `74d9ab9ea3dc6d266c881a6d5f2156e94243589a68155c5db3a7a7de846b9273`, rather than
   historical `ff124b66301901a9e945338ccad1a354f8e393d8fe9175f06d1fbf3068d29d44`.
   Its 120 CRLF sequences normalized to LF reproduce the historical pin.

The synthetic driver performs those **two explicitly named public-file** diagnostics.
They explain this Windows checkout limitation; the failed tests remain failed, and
their pins/tests/history are preserved. No normalization or bypass was installed.
No broad benchmark/harness discovery occurred.

`python` was absent on PATH; `py` offers only 3.9, below the repository minimum.
Verification used official CPython **3.12.10 embeddable amd64** under the approved
temporary directory, with explicit `sys.path` bootstrapping for `src`/repository
imports (embedded Python ignores `PYTHONPATH`). No dependencies or repository runtime
configuration were changed. Tests requiring subprocesses use that same interpreter.

## Engineering limits and next integration work

The trusted authority service provisions credentials; workers cannot select roles.
Synthetic credentials demonstrate attribution/restrictions, not final human login,
delegation expiry or OS process containment. SQLite/controller administration is
trusted. Read/access receipts, analysis results, V1 mappings and verification cases
in the new positive case are **synthetic**, explicitly labeled placeholders.
The controller enforces occurrence/binding of approvals and admitted evidence; it
cannot establish that an AI's natural-language judgment is true.

Before an AI requirements wizard can safely use the service: provide real scoped
human authentication/approval UX and conflict-resolution flows; integrate existing
bounded producers and their exact schemas/checkers; establish actual blind reviewer
input/access isolation; mediate worker capabilities and audit disclosure; connect
restricted author/build and independently sealed verifier execution to the reservation
API; enforce real executable manifest pins and rehearse public faults/end-to-end
outcomes. Dynamic delegation/rotation, deployment backup/rollback protection and
fine-grained dependency reuse remain additional service work. Nothing here activates
those later rounds.

## Protection, preservation and stop

All B03 source attempts/reads, content-revealing metadata access/inference,
formalization/review/discovery/adequacy, authorization/reservation/packaging/opening,
consumer observation/generation/execution/acceptance/repair counters are **zero**.
**B03_PRISTINE / B03_NOT_EVALUATED /
B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT** remain true by inherited status and scoped
session activity, without inspecting any protected content, metadata, digest or
ledger. No B03 FRC/package/commitment/eligibility exists from this round.
**R5.83-CANDIDATE-1 remains unactivated**. Historical R5.79–R5.85 results, compiler,
runtime/schema, generated files, semantics, V1 and BDI families retain their content.
Core **30** inherited; Phase 5C paused. **Stop after R5.86.**

## Final answers

1. **Can arbitrary AI assertions create authority?** No. They remain content until
   authenticated permitted events and required bound evidence exist.
2. **Can authority be traced to exact artifacts and authorized actors?** Yes.
   Typed identities, event/evidence digests, immutable graph and role-scoped journal
   link approvals, seals and grants to exact content and principals.
3. **Does dependency change prevent stale grants authorizing the new graph?** Yes.
   Exact graph substitution denies; explicit authoritative supersession/revocation
   also blocks new use of the retained old graph's grant.
4. **Does restart preserve authority?** Yes, including cross-process audit equality,
   live applicability, reservations and monotone historical invalidation.
5. **What remains before wizard use?** Real human/session integration, bounded
   semantic adapters, genuine blind worker isolation, mediated dispatch/build/verifier
   closure, executable freeze enforcement and public end-to-end rehearsal.
