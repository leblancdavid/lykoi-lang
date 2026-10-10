# Requirement-authority inventory

Line references address preserved files, not newly invented requirements. The
[baseline](BASELINE.json) binds R6.44 publication and R6.16 task freeze identities.

## Authority order

1. Original synthetic application authority:
   [R6.16 COMMON](../r6_16/tasks/COMMON.md) and
   [kiln base](../r6_16/tasks/kiln.md), amended by
   [stage 1](../r6_16/sealed/kiln-s1.md) and
   [stage 2](../r6_16/sealed/kiln-s2.md).
2. Frozen [R6.44 contract](../../../../experiments/stateful_modification_r6_44/CONTRACT.md),
   bound by [FREEZE](../r6_44/FREEZE.json), preserves those persistence/error rules
   while changing two operating policies.
3. Frozen acceptance files and diagnostics are executable expectations and historical
   observations. They do not override application requirements or authorize migrations.
4. Versioned language semantics explain available mechanisms. A generic backend's
   observed permissiveness/error branch is not application intent.

## Exact clauses and their consequences

| Subject | Authoritative clause | Explicit rule / derived consequence |
|---|---|---|
| Persisted representation | COMMON:3–5: “Local records.json persistent JSON list, missing file is empty.” Every operation reloads/validates the whole store. | Explicit list format and absence policy. `{}` is an existing object, neither a list nor file absence; its invalidity is a direct consequence, not a literal `{}` example in the source. |
| Required record fields | COMMON:5–11: fields exactly id, created_at, label, phase and two domain fields; valid field types/domains, nonblank label, unique IDs and invariant. Kiln:3–5 names vent/load domains. | Missing or extra fields in a record, including `[{}]`, are invalid. No inferred defaults. |
| Malformed-state error | COMMON:12: “Invalid persisted state fails invalid_state, even for list; no repair is authorized.” | Explicit public error for malformed persisted state, including wrong top-level shape. |
| Migration scope | COMMON:13: “No migrations, concurrency or distributed IO.” COMMON:21 forbids implicit defaults/override/history repair. | No legacy schema, migration eligibility or migrate command is authorized for kiln. Lack of a version tag cannot create migration eligibility. |
| R6.44 retention | CONTRACT:6–14: records, absence, replacement/rejection and invariant; “No normalization, schema migration, concurrency or external effects are required.” :23: invalid whole-store state is invalid_state before lookup/guards/input validation; :40: no other error/order/invariant changes. | The weaker “not required” wording in isolation does not cancel COMMON's no-migration rule or the repeated explicit error requirement. |
| Error precedence | CONTRACT:44–49: validate entire persisted store first; invalid unrelated record wins over missing ID, invalid mutation value or phase error; missing ID before guards; ordered phase/gate and lock/input rules. | Store rejection wins for valid operation requests with simultaneous store and lookup/input/guard defects. No general precedence over malformed transport/unknown commands is asserted. |
| Previously stored valid kiln state | Stage 2:6–10 broadens invariant; CONTRACT:51–58 preserves valid cold/closed and firing/closed/emergency records; invalid firing/closed/ordinary never repaired. | Old valid same-schema lists remain current-valid. “Old store” is not a different legacy schema. |
| Rejection preservation | COMMON:4; CONTRACT:11–12 and :53–55 | Exact preexisting bytes or absence preserved on rejection; reads do not rewrite. |

## Historical language authority, separately scoped

* [AIR v0.1](../../../../docs/air-v0.1.md):12–20 specifies typed lists, direct
  record-list storage, absence-as-empty, invalid JSON/records/invariants → invalid_state.
* [v0.2](../../../../docs/axiom-v0.2.md):79–85: schema version 1 uses a historical
  list; version 2 uses `{schema_version:2, records:[...]}`. Normal commands on a legacy
  list require explicit migration; model-declared additive defaults and validation
  precede atomic replacement. This establishes a real migration case, not permission
  to interpret every malformed object as legacy.
* [v0.3](../../../../docs/axiom-v0.3.md):3–7 retains v0.2 and normative validator
  checks; :47–54 distinguishes runtime invariants from proof.
* [Historical state profile](../../../../docs/historical-state-trusted-verification-v1.md):
  24–31 separates historical source authority from creation defaults; :35–46 requires
  version chains and exact old fields/types; :53–67 preserves failure bytes and forbids
  inferred old collections. This profile is **not selected by kiln**.

The kiln IR has version 1, no migrations, no historical-state facet and no migrate
command. Language migration authority is not inherited merely because its loader is
shared. Generic normal-read precedence between an older version tag and malformed old
records is not fully specified by the cited language clauses: explicit migration-time
invalidity does not settle which normal-read error wins.

## Frozen expectations and coverage

[R6.44 original-v2](../r6_44/ORIGINAL-EXPECTATIONS-v2.json) and
[modified-v2](../r6_44/MODIFIED-EXPECTATIONS-v2.json) are unchanged. Their successful
denominators do not establish coverage of every JSON shape. R6.44's `{}` diagnostics
are explicitly unscored, post-author evidence; their expected `invalid_state` is
supported by COMMON:3–13 and CONTRACT:23/44, not by treating Python as an oracle.

No clarification is required to classify `{}` in kiln. Clarification is required
before defining **new** kiln legacy schemas or revising generic versioned-loader
precedence: specify recognized envelopes/versions, structural recognition before
version selection, unsupported-version errors and normal-read versus explicit-migrate
precedence. Do not freeze those new meanings from current backend behavior.
