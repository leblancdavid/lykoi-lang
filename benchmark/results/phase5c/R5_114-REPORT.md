# R5.114 — Historical-state evolution and trusted-host verification closure

**Final classification: `R5_114_HISTORICAL_STATE_TRUSTED_VERIFICATION_CLOSED`.**

Both targeted bounded interfaces now traverse typed requirements → source inventory/
reconciliation → structural coverage → BDI → adequacy → faithful V1 → deterministic
compiler/backend → independent external observations. Related-state migration has
explicit historical authority; controlled-host execution is part of the normal sealed
verification artifact rather than a separate success probe. The proposed kernel
remains **26**, with no new core candidate.

This closure is scoped to the versioned supported profile and trusted-local embedding.
It does not establish authentication, hostile-code isolation, unrestricted evolution,
held-out generalization or actual clarified B18/B19 behavior. Source authority is still
mandatory. Fresh exposed transfer retains **16/20 successes B01–B16**, **447 external
invocations**. B17–B20 remain formalization disputes; B18/B19 downstream execution
remains **`NOT_REACHED`**. No role or error authority is invented.

## Deliverables

| Deliverable | Implementation / specification / evidence |
| --- | --- |
| Historical-state and trusted verification specification | `docs/historical-state-trusted-verification-v1.md` |
| Related fields and version-chain integration | `src/air_compiler/historical_state.py`, `historical_runtime.py`, `mutable_values.py`, `references.py`, `reference_runtime.py`, `profiles.py` |
| Closed FRC, reconciliation, structure, BDI, adequacy, V1 | `src/lykoi_workspace/historical_schema.py`, `mutable_schema.py`; `src/lykoi_pipeline/mutable_profile.py` and existing normal services |
| Sealed controlled-host external execution | `src/lykoi_pipeline/host_verifier.py`, `plans.py`, `pipeline.py`, `controller.py` |
| Synthetic multi-domain evidence | `src/lykoi_workspace/historical_corpus.py`, `tests/test_historical_state.py`, `R5_114-SYNTHETIC-EVIDENCE.json` |
| Kernel accounting | `R5_114-KERNEL-ACCOUNTING.json`, exact R5.113 accounting hash retained |
| Fresh twenty-case typed transfer | `R5_114-Bxx-CANDIDATE.json`, `R5_114-Bxx-RESULT.json`, `R5_114-TRANSFER-EVIDENCE.json` |
| Matrix and before/after blockers | [Capability matrix](R5_114-CAPABILITY-MATRIX.md), `R5_114-COMPARISON.json` |
| Source-bound checks and pre-transfer locks | `R5_114-CHECK-*.json`, `R5_114-GENERIC-VERIFICATION.json`, `R5_114-GENERIC-LOCK.json`, `R5_114-CORPUS-LOCK.json` |
| Final preservation/scope audit | `R5_114-FINAL-AUDIT.json` |

## Historical-state evolution

The new selected interface adds an explicit historical facet, not a migration command
for a particular benchmark. Source-authorized additive steps introduce related enum/
role, nominal reference, reference collection and nullable signed-64 fields. Sources
are separately declared literals, exact existing historical fields or existing checked
computations. New-entity defaults are never consulted. Related-only transitions join
the existing complete primary/related one-store version chain.

Historical schemas are inferred only from explicit introduction boundaries. Before
values come from the coherent whole transition-before snapshot. Existing records,
identities, occurrence order, unrelated fields and unrelated collections are preserved.
Current persisted roles are not rederived on restart or repeated migration. Nominal
targets and reference existence/deletion policies remain exact; no string-based cast
or role from owner identity is allowed.

All version steps are private candidates. Invalid field sets, absent old observations,
invalid enum/numeric values, duplicate identity, dangling required reference, computation
failure and persistence replacement failure reject without committing a prefix. The
final candidate uses ordinary current-state/invariant/reference validation and the
existing atomic replacement. Current-version migration validates, returns zero and
leaves bytes unchanged. Fresh application processes prove reload/restart persistence.

The bounded profile requires explicitly stored related collections and additive fields.
It does not guess contents for absent historical entity collections, mix legacy
`missing_or_empty` repair with additive introduction, rewrite existing fields or perform
arbitrary rename/removal/type conversion. Legacy reference behavior is preserved outside
the new selected profile. These are explicit supported-interface limits, not implicit
defaults or newly justified core concepts.

## Trusted execution and independent classification

R5.113 actor semantics are reused: trusted host-supplied actor, CLI selector,
authenticated principal and role/owner permission are distinct. The controlled fixture
asserts an actor through the exact declared source. Lykoi neither authenticates that
actor nor derives a principal mapping. The CLI cannot establish trust with `--actor`.

Host test requests are part of the source-bound plan sealed before authoring. A
verifier-owned, component-pinned adapter loads the exact deterministically compiled
target in a fresh isolated subprocess and supplies separate context to the existing
entrypoint. It reserves the inherited cooperating one-store operation lock. Context
does not come from ordinary flags, environment or generated success assertions.

The external parent observes return code, stdout/stderr, exact durable JSON and
byte-preserving rejection. Host observations retain exact inputs/context and durable
before/after hashes. Verification artifacts bind the WHAT seal, exact target/hash,
plan seal, adapter hash and ordered requests including the trusted actor source.
The controller recomputes expected binding and classification; changed context/input,
forged pass bits and a target printing `BEHAVIORALLY_VERIFIED` cannot certify success.
Generated authors cannot review/seal plans or register the verifier's authority.

This is finite verification inside the existing trusted compiler/embedding/controller
boundary, not an OS sandbox against arbitrary malicious host code. The parent owns
classification, but a controlled host assertion is not a cryptographic credential or
an authenticated principal. No new authentication or benchmark firewall system is built.

## Generic verification and synthetic evidence

**397 passing tests across 30 commands**, including canonical validation/safety. The
complete inherited R5.113 command set passes on the final implementation. Four new
tests cover normal multi-domain migration/host chains, clarification refusal, exact
source reconciliation and structural/BDI/V1 authority, overflow/replacement rollback,
and forged observations/target self-certification rejection. Existing compiler,
application, migration/persistence/reference/atomic/computation/authorization,
workspace/controller/FRC/coverage/BDI/adequacy/V1 and external-baseline tests pass.

| Domain | Distinct historical demand | Published external invocations |
| --- | --- | ---: |
| Inventory / Stock | Explicit nullable reservation introduction, derived quantity | 26 |
| Document / DocumentRevision | Owner reference copied from authorized prior-owner state | 27 |
| Account / Employee | Historical role literal explicitly editor, separate from viewer creation | 27 |
| Renewal / Subscription | Nullable numeric introduction and actor-authorized change | 27 |
| Project / Membership | Explicit ordered unique nominal member references | 26 |
| **Total** | | **133** |

Each successful domain also exercises historical operator-role derivation from a
persisted authorized observation, checked computed nullable introduction, four starting
versions (1/2/3/4), repeated migration, restart, missing old authority/data, invalid role/
numeric field, unknown field and dangling reference rejection. Permissions exercise
authorized role, insufficient role, authorized owner, unauthorized owner, forged
ordinary actor, wrong context source and CLI trusted-context refusal. All rejected
operations preserve store bytes, including history and successors. Successful trusted
operations create exactly the declared primary successor and two ordinary histories.

One additional ambiguous Account capture halts **FORMALIZATION / DISPUTED**, zero
external invocations, all downstream stages `NOT_REACHED`. No hypothetical clarified
success is counted. Native generated-backend tests separately exercise signed-64
overflow, a second invalid historical record and injected replacement failure with
no durable prefix or temporary-file leak; these are not additional published pipeline
invocations. The artifact transport retains its inherited safe-integer restrictions.

Captures, source inventories, literal oracles and approvals are same-agent synthetic
development evidence. Related schemas vary, but primary permission/history scaffolding
is shared. This is not independent cognition, broad formalization accuracy, held-out
generalization or proof of kernel minimality.

## Chronology and preservation

The initial worktree was clean. Focused verification passed before final regression
receipts. The first broad regression driver exceeded its terminal timeout after 18
completed passing commands; no Python process remained, and the driver resumed exact
source-bound receipts, counting each once. A generic-driver invocation initially lacked
the repository root on `PYTHONPATH`; it failed before evidence publication and was
rerun with `PYTHONPATH=src;.`. These are execution interruptions, not semantic results.

Final source-bound verification preceded published synthetic evidence and unchanged
kernel accounting. The generic content lock then fixed implementation, specification,
tests and evidence. All twenty fresh captures/plans were fixed before first transfer
outcome. The producers reread frozen sources using existing typed capture logic rather
than replaying saved FRCs. Product/specification/tests/candidate bytes remained fixed
through transfer. Only prospective report/status documentation and final audit were
added afterwards. All R5.113 and earlier evidence, content-lock records, frozen
requirements, canonical model, generated artifacts and external harness are preserved.

## Before/after blocker analysis

| Cases | R5.113 blocker | R5.114 blocker | Actual external result / stage change |
| --- | --- | --- | --- |
| B01–B16 | Success | Success | 16 fresh successes, 447 invocations; no new stage |
| B17 | Formalization dispute | Formalization dispute | Non-system historical role authority absent |
| B18 | Formalization dispute | Formalization dispute | Same inherited role authority; downstream `NOT_REACHED` |
| B19 | Formalization dispute | Formalization dispute | Same inherited role authority; downstream `NOT_REACHED` |
| B20 | Formalization dispute | Formalization dispute | Nonexistent-member error authority unanswered |

B17 specifies `system=ADMIN` and new-user `USER`, but not the role for pre-existing
non-system users. B18's empty-history migration and B19's null recurrence migration
do not answer that role question. B20 does not specify the missing-member error.
Synthetic authority and conventional oracle outputs supply no answer. B18/B19 diagnostic
typed candidates remain unsealed and have no actual authoring, compilation or external
behavior after clarification. No further downstream gap is ruled out by generic success.

## Kernel accounting

Preserve the exact R5.113 accounting and all 26 proposed concepts, including K24 checked
addition, K25 fixed-second UTC displacement and K26 elapsed-day conversion. No additions.

* **Existing-core composition:** historical literals/copies, enum/nullable/reference
  typing, pure checked graph values, explicit errors and atomic durable-state evolution.
* **Profile/interface integration:** related-only version steps, typed historical FRC/
  BDI/V1 facts and independently sealed controlled-host execution requests/bindings.
* **Backend implementation:** historical-schema projection, private candidate assembly,
  one replacement, verifier-owned target loading and external parent observations.
* **Justified new core candidate:** none.

No HistoricalRole, OwnershipMigration, TrustedUser, AuthenticatedActor or benchmark
operation becomes a core primitive. Architectural count **26 → 26**, not a minimum proof.

## Completion answers

1. **Yes:** supported related fields migrate only from explicit historical sources.
2. **Yes:** creation defaults and migration authority are separate; no inference.
3. **Yes within the bounded profile:** role/enum, nominal reference/collection and nullable
   numeric fields pass version, integrity, idempotence, atomic rejection and reload checks.
4. **Yes:** the normal sealed external verifier now supports controlled-host actor contexts.
5. **Yes:** wrong owner/role, forged input and wrong/missing context are externally observed;
   rejected operations preserve all durable state, history and successors.
6. **Yes within the existing authority boundary:** software outputs are observations,
   not verifier grants; exact sealed inputs/bindings and classification are checked externally.
7. **Yes, 26:** no new core candidate.
8. **No:** B18/B19 remain blocked at formalization; downstream `NOT_REACHED`.
9. **16/20, B01–B16:** 447 fresh exposed external invocations.
10. **Yes:** B17/B20 remain disputed, as do inherited B18/B19 role authorities.
11. **Still outside supported semantics/interfaces:** arbitrary existing-field/type/collection
    evolution, missing-collection initialization without authority, general conditional
    implication, arbitrary lifecycle/deletion branching and computed legacy creation.
    External authenticated principal mapping needs actual source and an existing trusted
    provider; it is not invented here. Distributed/hostile-code guarantees remain excluded.
    Actual clarified B18/B19 paths are unverified. Authority ambiguity is not a core gap.
12. **Its marginal semantic yield is now limited:** B01–B20 remains useful regression and
    provenance/clarification evidence; this round discovers no new core concept or success.
    Earlier genuine pressures remain valid. It cannot establish broader generality.
13. **Follow with separately supplied development-unexposed requirements** across employee
    access changes, document revisions/ownership, inventory reservations and project/asset
    membership, with complete historical authority and trusted-context contracts. Include
    adversarial invalid histories, cross-version evolution, authority disputes and coupled
    effects. Record fresh first results before informed changes, then evaluate observable
    behavior. Broader domains should vary workflow/schema shape, not merely rename this one.
    This is a recommendation only; no new evaluation or round is begun.
14. **Yes:** benchmark-specific primitives, authentication infrastructure, distributed
    transactions, unrestricted arithmetic, UI, qualification and firewall machinery avoided.

**Stop after R5.114.** The central question has a bounded positive answer: explicit
historical related-state evolution and independently classified controlled-host behavior
compose the existing 26-concept kernel, while absent authority remains a visible halt.
