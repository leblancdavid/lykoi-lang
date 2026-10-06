# R5.84 public experiment evidence

Final classification: **R5_84_INDEPENDENT_COVERAGE_AUTHORITY_PARTIAL**.
See [report](../R5_84-INDEPENDENT-COVERAGE-AUTHORITY.md),
[SCCA-0.1](../../../../docs/source-contract-interface-coverage-v0.1.md) and
[SOI-0.1](../../../../docs/source-obligation-inventory-v0.1.md).

## Reproduction (repo root, PowerShell)

```powershell
python -m unittest benchmark.evaluation.test_source_coverage_r5_84 -v
python -m unittest benchmark.evaluation.test_behavioral_discovery_r5_82 benchmark.evaluation.test_implementation_adequacy_r5_81 benchmark.evaluation.test_formal_requirements_r5_80 -v
python -m benchmark.results.phase5c.r5_84.qualify
python -m benchmark.results.phase5c.r5_84.qualify --corpus
```

The final driver prints inspectable per-class outcomes, isolated inventory
comparison/navigation maps and the full public B01 source ledger/mapping. `--corpus`
prints all 23 deterministic source/SOI/FRC/interface triples. `fixtures.py` defines
the corruptions reproducibly; tests cover six inventions and six plausible-but-not-
necessary additions, exclusions, implications, mutations and the residual counterexample.
No command writes evidence, invokes static consumers, authoring or protected IO.
The corpus is executable public evidence, not a universal NLP benchmark. Its review
receipts are explicitly synthetic bookkeeping, not independent semantic approvals.

## Artifacts and publication order

1. `sources.json`: 23 coordinating-AI-authored synthetic sources, published first.
2. `independent-soi.json`: Process B source-only extraction in a fresh same-model
   context; published **before** candidate fixture/module creation. The coordinating
   process computed physical SHA-256
   `ff124b66301901a9e945338ccad1a354f8e393d8fe9175f06d1fbf3068d29d44`
   before opening it and before creating candidate machinery. This is the immutable
   inventory commitment, not a Git commit or independent timestamp service.
3. `fixtures.py`: Process A known-answer primary and two-clause candidate construction;
   separate same-context source inventory function runs before formalization.
4. `qualify.py`: Process C comparison and public B01 calibration; checks the original
   inventory pin rather than editing the publication to match candidates.
5. `results.json`: authored frozen summary of actual driver/test observations,
   denominators, limitations and zero protected activity; not a raw captured transcript.
   Exact physical-byte hashes of the six public experiment source/component artifacts
   record the tested snapshot, not a production freeze or newline-normalized identity.

Process B received only the source corpus as task data, saw no candidate before
publication, and used an explicit source-only access instruction. All 23 texts were
visible in that file, but only six were inventoried. It disclosed a narrowly scoped
pre-edit Git status command; Git's internal metadata accesses were not traced.
Repository guidance was supplied by the harness. Shared files remained accessible
in principle: this is cooperative context isolation, not strict sandboxing. Process A
could see Process B's publication before candidate creation; independence is one-way
source-extraction isolation, not a blinded randomized candidate-generation study.
Process C runs in the coordinating context. No model/provider isolation occurred.

## Verification and evidence interpretation

Final new tests **21/21**, unchanged R5.80/R5.81/R5.82 **52/52**, driver assertions
PASS. The initial development suite passed 14 tests; additional source-accounting,
independence, implication/exclusion, source-mutation and historical reproduction
challenges brought it to 21. No failing run is hidden or repaired in historical
evidence. Component changes and tests are prospective R5.84 only.

The one truthful positive mechanism control is a narrowly scoped durability
bookkeeping example, not real software or independent source fidelity approval.
The residual negative control intentionally rebuilds a vague incomplete inventory,
covering the whole source with an umbrella span, and supplies a fresh dishonest
review/admission. Its experimental authorization is **true**, while production
authorization is **false**. This prevents promoting synthetic graph checks to
qualified semantic review authority. Full-source disputed cases are not counted
as approved merely because their primary accounting fixtures can pass.

Reads are exact public files: this directory's sources/inventory, public B01.md,
public R5.80 candidates, and imported public helpers/tests with their public fixture
allowlists. No broad harness discovery or protected resource/ledger/metadata query
is performed. B03 pristine status is inherited with zero session activity counters,
not freshly established by opening or inspecting protected evidence. Core **30**
is inherited. Phase 5C remains paused; R5.83-CANDIDATE-1 is not activated.
