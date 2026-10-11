# Curriculum specification v1

Stage progression requires source-bound deterministic validation and frozen
functional acceptance, not a loss threshold alone. Stages are proposal scopes;
no new examples or training are generated in R6.62. See
[record quality contract](RECORD-CONTRACT.md) for rejection rules.

| Stage | Learnable construction and check | Capability/evidence boundary | Suitable supervision |
| --- | --- | --- | --- |
| 1 Valid package structure | Closed envelope, version/profile/foundation, result, identity; reject missing/extra fields and duplicate keys | Eight experimental wrapper packages; production uses its own IR/profile; no shared universal package | A for endpoint formatting; B declaration/finalization; C only where dispatcher supports it |
| 2 Typed literals and operations | Choose ref/const/add/le/eq with Int64/Bool/Unit; overflow/type control, result typing | Experimental wrapper and narrow R6.25 tools; production checked addition/predicates have different representation | B single-step first skill; equivalent A/C views if qualified |
| 3 Dependency references | Prior binding scope, exact deps, no forward/cyclic/unbound ref, typed result | Eight wrapper endpoints; frozen signatures/aliases in narrow dispatcher | B/C scoped updates, A full DAG; independent invalid-ref controls |
| 4 Ordered checks/error precedence | Check/read order, site/provenance and simultaneous failures, EOF/end/trailing data | E03/E04/E05/E06 experimental byte-read/check traces; production S01/S02 ordered lookup/guard/input/invariant differs | Profile-specific A/B; C cannot be assumed to expose every byte-read/check operation |
| 5 Reusable compositions | Definition identity, typed arguments, hygienic nesting, deps, definition order and equivalence to explicit twin | E07/E08 experimental pinned composition; production not this wrapper; R6.18 bounded mechanics only | A libraries; B/C definition+compose units for supported subset |
| 6 Stateful transitions/invariants | Enum domains, legal guard/transition, staged invariant and rejected-state preservation | Production S01/S02 actual AI intent edits, shared correction; experimental VM not stateful store | A production IR/intent distinguished; B stateful updates need surface qualification; no current stateful C |
| 7 Persistence/effects | Atomic one-store writes, fresh-process restart, effect/authority declarations | Production local persistence S01/S02 finite evidence; no concurrency/power-loss proof, relation/authority coverage gaps | Production-specific A/B; C requires qualified state/effect interface first |
| 8 Successor modifications | Exact base identity, explicit changed obligation, retained invariant/history, reject undeclared migration sources | Production existing successor/migration meanings; no Tier T predecessor→successor edit cohort here; S02 sibling is not a captured S01 modification | B modification plan or A successor; C not universally supported |
| 9 Requirement→program | Select operations/guards/order from source, assemble complete target without solved semantic scaffold | Narrow synthetic endpoints are available; teacher-forced fitting is not this skill; real tools R6.25 failed completion | Compare A/B/C on identical supported requirements; score endpoint |
| 10 Cross-feature generalization | Combine independently specified typed/dependency/check/state/effect features in unseen structural families | Tier E0, two broad scaffold components, no independent withheld families; relations/time/authority/migrations absent | Future held-out study; never relabel reproduced or renamed training rows |

Production-backed means unchanged kernel26/compiler/backend capabilities with the
corresponding profile's limits. Experimental-only means fixed R6.10/R6.18/R6.23
foundations and R6.25 contracts, not newly adopted production meanings. Do not
union vocabularies, compile experimental packages with the production compiler,
or infer a full26-construct curriculum from this ten-endpoint corpus.

Each future stage should include ordinary/boundary/type-invalid and semantically
wrong-but-well-typed contrasts. Wrong targets are negative controls, not positive
supervision. Qualify deterministic correction pairs only from real feedback or
explicit expert demonstrations, keeping pre-failure and corrected states. Advancement
uses a development family partition; final evaluation families remain custodian-only.
Avoid ordering stages based on access to withheld acceptance results.
