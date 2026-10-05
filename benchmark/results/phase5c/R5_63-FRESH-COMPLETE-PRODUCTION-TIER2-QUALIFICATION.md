# R5.63 — Fresh complete production Tier-2 qualification

## Outcome

**`R5_63_PROTOCOL_HALT`**.

The first and only freeze invocation fails while sealing the fresh qualification
identity. The existing publication guard rejects its `authorization` field as a
credential-reserved field. That field contains a public authority-policy digest,
but the qualified guard's structural rule still applies. The stage plan and
worker registry were already persisted; the qualification identity was not.

The candidate stops before starting-state verification, authority qualification,
capsule capture, workspace materialization or the first production batch. No field
is renamed, no guard is weakened, and no freeze, stage or observation is retried.
The candidate is durably quarantined. Its plan and orchestration bytes are preserved.

**Answer to the research question:** this R5.63 candidate does not qualify the
Phase 5 production gate for a separately authorized locked B02 static observation.
It provides no new finding about Lykoi's B02 behavioral support.

| Final accounting | Count |
| --- | ---: |
| B02 exposure / reservation / dispatch / completion | **0 / 0 / 0 / 0** |
| Production batches / receipts | **0 / 0** |
| Synthetic reservation / dispatch / completion | **0 / 0 / 0** |
| Fresh qualification identities / capsules / certificates issued | **0 / 0 / 0** |
| Core semantics | **30** |

Phase 5C remains **paused**. R5.63 is stopped permanently.

## Inherited R5.62 state

[R5.62](R5_62-MEDIATED-CHILD-EXECUTION-AND-SAFE-WORKER-QUALIFICATION.md)
remains **`R5_62_MEDIATED_CHILD_EXECUTION_QUALIFIED`** with 232/232 focused
tests, including 47 mediated-child adversarial witnesses. It qualified content-pinned
worker selection, same-or-narrower child/descendant capabilities, binding integrity,
pre-import safe exclusion, child resource enforcement, durable quarantine, minimal
secret-safe environment, explicit mediation budgeting and enclosing deadlines.
Its synthetic CertificateV2 compatibility evidence is preserved.

Its 36 prohibited skips, validation/safety/schema, 99-leaf traceability, continuity,
contamination, AI independence, publication checks and 2,026 unsealed historical
byte-digest checks remain inherited evidence. They are not fresh R5.63 production
receipts. Its production accounting was zero and no production certificate existed.

R5.60 remains **`R5_60_PROTOCOL_HALT`**. R5.61 remains
**`R5_61_PROTECTED_RESOURCE_GAP`**. No previous stopped or quarantined receipt is
reused or reinterpreted. Initial Git status was clean before R5.63 files were added.

## Frozen stage plan and attempted qualification identity

The persisted [stage plan](R5_63-evidence/stage-plan.json) has canonical identity:

```text
b3f180677350a6975d6e20062bb0e26ca93345ddab622999468aa6690fa892f3
```

It declares **173 required regression stages**, **six starting-state prerequisites**
and **11 production integration checkpoints**. Membership comes from the earlier
plan's metadata, supplemented with exact-method AST metadata for the current
QualifiedAuthority/certificate, capability/resource and mediated-child suites.
Historical PASS receipts supply no qualification result. Sealed test modules are
not opened or imported to enumerate membership.

The fixed regression coverage includes restricted harness, compiler/application,
R5.41 focused support, recorder/canonical evidence, QualifiedAuthority,
ProductionCertificateV2, security, methodology, Tier-2, bounded driver, continuity,
publication, capability/resource guard, mediated child/SUT, AI independence,
matrix/coherence, schema, traceability, contamination, validation, safety,
authority, publication/integrity and `git diff --check`.

Stages retain the earlier bounded method sizes: at most eight methods, at most
four for CertificateV2; new suites use at most four. Declared invocation budget is
110 seconds with a five-second boundary reserve. Costs use the existing
`production_cost(35)` helper, including mediation, child validation and exclusion.
No budget admission or fresh calibration result is claimed: starting-state
verification was never reached. No stage is renamed or subdivided after results.

Child/test stages declare `qualified_child` with `safe_workers_r5_62.harness`,
content-bound worker identity/closure, explicit generic capabilities, R5.62
mediation version and the R5.61 exclusion pin. Control-plane entries declare
existing APIs without raw child execution. The
[worker registry](R5_63-evidence/worker-registry.json) binds ordinary source files;
protected modules are excluded. Construction/pinning of this registry is preparation,
not a claim that every selected worker tree has freshly qualified.

Attempted experiment name:

```text
R5.63-fresh-complete-production-tier2-qualification-v1
```

The attempted identity would bind the plan, R5.53 successor, authority-policy
digest, bounded-driver version, worker registry, mediated policy, exclusion,
resource policy and orchestration identity. **No canonical qualification identity
was issued.** There is no `qualification-identity.json` or completed `freeze.json`.
The failed identity is not reconstructed after the failure.

## Concrete first failure and stop

Only qualification command attempted:

```text
python -B -S benchmark/results/phase5c/r5_63_qualification.py freeze
```

Exit status: **1**. Exception: **`SecretRejected`**.

```text
SECRET_VALUE_REJECTED: credential field field authorization
```

Current call chain:

```text
freeze -> tier.seal(qualification identity) -> security.safe_bytes -> inspect
```

This is an experiment-orchestration/publication failure, not a language capability
gap, protected-content exposure or production regression result. The secret-safe
guard correctly applies its existing credential-field rejection rule. The public
digest's intended meaning does not authorize a scanner exemption.

[Terminal failure](R5_63-evidence/terminal-failure.json) records the command,
exception, failed field, one attempt, retained plan identity and physical source/plan
digests. [Quarantine](R5_63-evidence/quarantine.json) makes the entire candidate
terminal. [Summary](R5_63-evidence/summary.json) records every required downstream
stage as **NOT_RUN**, not PASS, FAIL or a clean-budget-boundary continuation.

## Required production work: actual disposition

| Requirement | R5.63 disposition |
| --- | --- |
| Complete stage-plan declaration | Persisted; candidate subsequently quarantined |
| Fresh qualification identity | **FAIL — publication rejected; not issued** |
| Starting-state verification | NOT_RUN |
| Fresh QualifiedAuthority; 1,083-member/frozen/provenance/ancestry/checkout checks | NOT_RUN |
| Deterministic Tier-2 capsule and canonical reload | NOT_RUN |
| Bounded batches, fresh receipts and cross-batch linkage | NOT_RUN; zero batches/receipts |
| Mediated worker/SUT execution | NOT_RUN; no child/SUT launched |
| Safe exclusion | Pin and 36 metadata IDs retained; fresh child skip execution NOT_RUN |
| All required production regressions | NOT_RUN |
| ProductionCertificateV2 assembly/linkage/freshness | NOT_RUN; no certificate issued |
| Dedicated cooperative production workspace | NOT_RUN; not materialized |
| Exact production pre-observation gate | NOT_RUN |
| Exactly one synthetic production observation | NOT_RUN; zero accounting |
| Immediate post-observation verification | NOT_RUN |
| Second-observation rejection | NOT_RUN |
| Post-observation mutation/no-repair witness | NOT_RUN |
| Fresh production security/publication and AI-independence subsets | NOT_RUN |
| Production final independent audit | NOT_RUN |
| Independent stopped-candidate integrity audit | **PASS**, bounded scope below |

No production repair occurred. The absence of repair is not promoted into a PASS
for the unrun post-observation mutation test. Synthetic accounting is not reset.

## Sealed-resource compatibility concern from code inspection

Before the freeze attempt, ordinary implementation inspection identified a possible
downstream conflict with the absolute sealed-resource restriction:

- `qualified_authority_r5_55.qualify` bulk-loads all successor member blobs through
  `checkout.blobs`, then `authority_r5_53.verify` reads physical members.
- `tier2_r5_51.Workspace.materialize` hashes all tracked files before copying.
- The authorization metadata includes protected B02 frozen pins.

These APIs were **not called**. Their compatibility prerequisite was never executed,
and no fresh authority gap classification is issued. Protected Git blobs are not
extracted to diagnose this concern. It remains an unexecuted code-inspection concern,
separate from the actual first failure. No replacement authority or materialization
mechanism is introduced in this round.

## Historical preservation and independent stopped audit

[The independent stopped audit](R5_63-evidence/independent-stopped-audit.json)
recomputes plan/registry identities and retained source/plan digests without invoking
the failed runner or reconstructing the missing qualification identity. It verifies:

- unchanged persisted plan and failed orchestration source;
- durable quarantine and absence of qualification/capsule/certificate/receipt artifacts;
- zero production and synthetic accounting;
- 36 unique prohibited IDs in the restricted plan, using only the pinned exclusion index;
- unchanged historical R5.60/R5.61/R5.62 classifications;
- fresh core count **30** and clean established contamination scan;
- canonical publication-safe persisted stopped evidence.

The [preservation baseline](R5_63-evidence/preservation-baseline.json) covers
**2,058 inherited benchmark-result files**. **2,054 unsealed files** are verified by
physical-byte digest. Four protected historical fixtures remain unopened: size/mtime
metadata matches and Git reports no tracked benchmark-result changes. This is
metadata/Git continuity, not a fresh content-hash attestation of sealed files.
New prospective orchestration/audit sources were explicitly excluded before baseline
capture; no post-failure preservation exception is added.

The audit's PASS establishes stopped-candidate integrity only. It does not qualify
authority, receipts, worker execution, workspace or the production observation gate.

## Security, publication and AI independence

The initial publication rejection is retained as FAIL. The guard is unchanged.
Stopped evidence uses public digests and fixed diagnostics; no raw secret or child
output is published. Final
[publication/integrity verification](R5_63-evidence/publication-integrity.json)
checks canonical evidence, new/modified source publication safety, tracked diff
whitespace and new-file whitespace. It does not replace the failed identity stage.

No child environment was propagated because no worker started. Minimal environment,
synthetic fixture rules, raw-secret rejection and redacted diagnostics remain
R5.62-qualified mechanisms; their fresh production regressions were not reached.

**Lykoi is a language, not an AI runtime.** Core source, runtime, compiler, schema
and observation controls are unchanged. Development AI state is excluded from the
declared fixed-source identity. No AI provider/model/OpenCode/network-inference
dependency was added. Fresh production AI-independence tests are **NOT_RUN**.

## Evidence commands and recommendation

After the failed freeze, only terminal recording and read-only stopped auditing are
performed:

```text
python -B -S benchmark/results/phase5c/r5_63_terminal_audit.py record
python -B -S benchmark/results/phase5c/r5_63_terminal_audit.py audit
python -B -S benchmark/results/phase5c/r5_63_terminal_audit.py publication
```

`r5_63_independent_audit.py` is a prospective, unexecuted audit source written before
the freeze. Its anticipated authority-gap path and the runner's `start` path are
never invoked. The separate terminal audit records the actual earlier failure.

**Recommendation:** owner adjudication of the concrete qualification-identity
publication rejection before any separately authorized successor candidate.
This round makes no repair or infrastructure change and starts no further
qualification. Do not authorize the B02 observation from this stopped candidate.
The locked static-only **observe → record → classify → stop** objective remains
unchanged, but its prerequisite production gate is not qualified by R5.63.
