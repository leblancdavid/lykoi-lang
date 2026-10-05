# CertificateV3 mode and authorization contract — R5.68 v1

This prospective research-infrastructure contract succeeds CertificateV2 without
changing its historical interpretation. Implementation:
`benchmark/evaluation/certificate_r5_68.py`. No language construct is added.

## Version and modes

Canonical evidence uses `protocol = lykoi-production-certificate-v3`, `version = 3`,
an explicit `mode`, `authorization_binding`, and `authorization_schema`. No consumer
may reinterpret V2's absent mode as production-sealed. The unchanged R5.66 V2
adapter retains its historical synthetic prefix predicate and `SYNTHETIC_ONLY` scope.

| Mode | Scope | Allowed certificate operation |
| --- | --- | --- |
| `SYNTHETIC_QUALIFICATION` | `SYNTHETIC_ONLY` | `SYNTHETIC_GATE_QUALIFIED` |
| `PRODUCTION_SEALED` | `PRODUCTION_SEALED_ONLY` | `PRODUCTION_GATE_QUALIFIED` |

Synthetic qualification can bind synthetic protected resources. Synthetic opening
still requires R5.66's separate externally pinned opening grant and durable ledger.
Neither V3 mode itself grants even synthetic opening. Historical opening behavior,
including reserve-before-read and one-time/alternate-ledger rejection, is retained.

Production-sealed certification expresses readiness relative to the explicitly
declared qualification and its required receipts while benchmark seals remain closed.
It can bind a real qualification identity, QualifiedAuthority, immutable sealed
commitments, Tier-2 capsule, production receipts and cooperative workspace. An
R5.68 bounded mechanism candidate with non-B02 receipts does not establish the full
production environment's readiness. A complete future qualification must declare
and freshly satisfy its complete required stage set.

## Public, externally pinned declaration

Declaration protocol: `lykoi-certificate-mode-declaration-r5.68-v1`.

The producer-owned immutable schema's SHA-256 is
`f3648f3ce5bb2e8ff4f105dd0af82db096b77de33ad2e78d5586ff02fd10ea17`.
All fields are mandatory, types are exact, extra fields reject. The schema classifies
the declaration as public protocol authorization, with protocol/content identities
and an exact Boolean opening prohibition. R5.64 typed publication, R5.47 value
inspection and R5.59 synthetic-security-fixture nonpublication stay active.

Required bindings:

- protocol and immutable schema identity;
- experiment and qualification identity;
- explicit mode and corresponding authorization scope;
- authority identity, freshly verified QualifiedAuthority identity and resource-policy pin;
- Tier-2 capsule identity and canonical complete certificate-policy digest;
- allowed gate operation;
- `sealed_policy = CLOSED_NO_OPEN_NO_OBSERVATION`;
- `observation_state = ZERO_UNOBSERVED`;
- `seal_open_authorized = false`.

The caller's reviewed control plane supplies a separate trusted declaration digest.
The payload cannot register itself or choose its trusted pin. Issuance checks the
canonical declaration against that digest and the exact expected cross-bindings.
Qualification identity is also linked through the identity receipt; all required
receipts must be sealed, successful and match capsule, experiment, stage and mechanism.
Authority linkage is freshly verified through R5.66. Current capsule must equal the
bound capsule. Validation reproduces the whole sealed certificate deterministically.

Mutation of any declaration field, mode, policy, receipt, capsule, authority or sealed
commitment invalidates its existing binding. Rehashing a mutated certificate does
not bypass deterministic reproduction. Even a newly pinned declaration cannot relax
the fixed no-open policy. Missing declarations and misleading names confer no eligibility.

Experiment prefixes and descriptive strings are identifiers only. Explicit production
declarations may bind identities containing `synthetic`; explicit synthetic declarations
may bind identities lacking `synthetic:`. Cross-mode declaration use rejects.

## Actual sealed authority and cooperative boundary

Use only R5.66's already-qualified commitment/provenance inventory and Git metadata
observer. `ls-tree` and `cat-file --batch-check` establish immutable object mappings;
no blob extraction or protected file reads occur. Evidence retains
`SEALED_COMMITMENT_VERIFIED`, `seal = CLOSED`, `current_content_read = false` and
`checkout = DEFERRED_UNTIL_OPEN`. The two frozen commitments remain independently
pinned. This attests historically qualified immutable resources, not present protected
worktree bytes. No fallback read is permitted.

The R5.68 candidate uses the 11-member sealed subset, a narrow actual Tier-2 capture,
four fresh non-B02 receipts and an 11-reference deferred cooperative workspace. It
does not verify all 1,083 authority members or execute the full production regression
plan. The trust boundary remains reviewed local cooperative control-plane adapters,
external owner pins and ordinary OS/Python services, as in R5.50/R5.66.

## Future observation authorization boundary — definition only

```text
fresh validated ProductionCertificateV3(PRODUCTION_SEALED)
  + separate externally authorized one-time B02 observation declaration
  -> eligible for a future B02 seal-open reservation gate
```

Neither object alone suffices. The future separately qualified consumer must bind
the observation declaration to the exact certificate/qualification, QualifiedAuthority,
resource commitment, permitted observation operation and one durable ledger; enforce
fresh state and reserve-before-read; and consume opening authority exactly once.
This is a proposed future chain, not an implemented actual B02 opener. R5.68 does
not create an observation declaration or invoke a reservation gate.

`require_operation` validates all current certificate evidence and admits only the
mode's gate-qualification operation. `SEALED_RESOURCE_OPEN`,
`B02_SEAL_OPEN_AUTHORIZED`, B02 observation and cross-mode operations reject. Every
certificate explicitly records `seal_open_authorized = false` and
`b02_observation_authorized = false`. Issuance has no ledger or observation API.

AI/provider/model identity is absent. Core semantic count remains 30. R5.67 remains
permanently `R5_67_PRODUCTION_CERTIFICATE_GAP`; no retrospective certificate issues.
