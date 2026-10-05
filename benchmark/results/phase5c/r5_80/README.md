# R5.80 public qualification evidence

Result: **R5_80_REQUIREMENT_FORMALIZATION_PARTIAL**. See the
[report](../R5_80-REQUIREMENT-FORMALIZATION-QUALIFICATION.md) for denominators,
disagreements, negative results, protection accounting and evidence limits.

All files here are newly public synthetic/public qualification records. They
are not protected benchmark packages, production approval authority or historical
benchmark amendments. There is no held-out resource discovery or source resolver.

## Inventory

* `corpus.json`: twelve AI-authored human-style public texts, concern rationale,
  and an exact-path reference to already-public B01.
* `fixtures.py`: manually authored FRC-0.1 clauses and three defective drafts;
  additional P01 explicitly selects existing public component context.
* `candidates.json`: fourteen source candidates plus three defective drafts.
* `independent-a.json`, `independent-b.json`: separate-context attempts on seven
  sources in independent notation, with admitted input inventories/limitations.
* `comparison.json`: reviewer obligation alignment and semantic judgments.
* `reviews.json`: separate eight-dimension source-fidelity review and receipts.
* `coverage.json`: exact code-point source fragment locators; overlap is not proof.
* `projection-review.json`: separate P01 complete-projection fidelity receipt.
* `qualification.json`: verified receipt bindings, all projection outcomes,
  P01 full V1 document/normalization/map, physical B01 provenance and scoped
  B03 zero-activity accounting.
* `qualify.py`: deterministic public evidence reproduction.
* `validation.json`: observed test results, initial development failures and
  disclosed input-scope deviations.

Schema/spec and executable infrastructure are outside this results directory:
[`docs/formal-requirement-contract-v0.1.md`](../../../../docs/formal-requirement-contract-v0.1.md),
[`schema/formal-requirement-contract-v0.1.schema.json`](../../../../schema/formal-requirement-contract-v0.1.schema.json),
[`benchmark/evaluation/formal_requirements_r5_80.py`](../../../evaluation/formal_requirements_r5_80.py).

## Reproduce mechanical evidence

From the repository root, Python 3.10+, no dependencies:

```powershell
Test-Path -LiteralPath "benchmark/results/phase5c/r5_80"
python -B -S -m benchmark.results.phase5c.r5_80.fixtures
python -B -S -m benchmark.results.phase5c.r5_80.qualify
python -B -S -m benchmark.evaluation.test_formal_requirements_r5_80
python -B -S -m benchmark.evaluation.test_benchmark_documents_v1
```

Materialization reconstructs the same manually authored records, not new AI
interpretations. Existing reviews must match exact reconstructed content or fail;
neither script creates review approval. FRC/schema tests exercise structural rules,
content binding, bounded clause comparison, stable revision edges, projection
failure and recognized-clause preservation. Semantic A/B comparison and review
remain recorded judgments, not automated prose reasoning.

Neither command authorizes or accesses a held-out request. Stop at R5.80.
