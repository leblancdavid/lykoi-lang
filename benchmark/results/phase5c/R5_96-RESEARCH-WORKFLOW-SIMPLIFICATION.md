# R5.96 — Research workflow simplification and benchmark reset

**Classification: `R5_96_RESEARCH_WORKFLOW_SIMPLIFIED`**

Date: 2026-10-06. Scope: prospective research policy, default guidance, lightweight
snapshot tooling and current-environment baseline. Stop after simplification.
**B03 remains unread/unexposed; no B03 benchmark was attempted.**

## Decision and deliverables

The priority is again evaluating and improving Lykoi with the current compatible
environment and available model. The [versioned decision/protocol](../../../docs/research-workflow-r5.96.md)
retires exact runtime/OpenCode identity, runtime/adapter/transport/machine/model
qualification, cross-machine freeze eligibility, execution-infrastructure hash gates,
protected activation and controller authorization merely for benchmark access.
Historical candidates remain in their recorded states; no activation is necessary
for the new ordinary research path.

Delivered:

1. Research-workflow decision and product-useful/research-useful/experimental-deferred
   classification: `docs/research-workflow-r5.96.md`.
2. Updated current boundary: `docs/project-overview.md`, with previous summaries
   explicitly retained as historical boundaries.
3. Prospective entries in `docs/decisions.md` and `docs/research-log.md`.
4. Simplified held-out protocol in the decision document, linked by benchmark README.
5. Current default guidance in `AGENTS.md`, `docs/agent-workflow.md`, root README and
   benchmark README; explicit core/public test selections replace broad default discovery.
6. Lightweight command: `src/lykoi_research/snapshot.py`, invoked as
   `python -m lykoi_research.snapshot` with `PYTHONPATH=src`.
7. [Human-readable current-environment baseline with full output](R5_96-CURRENT-ENVIRONMENT-BASELINE.md).
8. This report.

No historical R5.x report/evidence, compiler, runtime template, mapping, schema,
semantic model, generated artifact or prototype was deleted or rewritten. The
new command is research provenance tooling, not a new authority system.

## Current-environment baseline

Initial Git state was clean. HEAD:
`5543a3a1bb7a43fb0adb21c0c461b6141ef9fb22`. The baseline records the documentation
and new snapshot-tool working-tree changes before/after checks. No commit was made.
Report publication follows that baseline; it is not represented as part of its
earlier working-tree listing. Refresh the snapshot immediately before later access.

- Python: CPython **3.14.3**, AMD64, current available `python` command.
- Platform: Windows 11 (`Windows-11-10.0.26300-SP0`).
- Model/provider: **OpenAI `openai/gpt-6.1-sol`**, declared by the active environment.
  No model qualification or live adapter/transport qualification was performed.
- Core serialization/semantics: **0.3**, `docs/axiom-v0.3.md`; backend **0.3.0**.
- Generic semantic prototype: unchanged current sources at recorded commit/tree,
  including `benchmark/semantic/current_pipeline.py` (R5.27 analysis and R5.28
  checked emitter/verifier). No new generic semantic version is invented by R5.96.
- Representation: **BenchmarkDocumentContractV1 / BehavioralContractV1**.
- Baseline interval: **18:00:59–18:03:51 UTC**, 2026-10-06.

The command actually executed was:

```powershell
$env:PYTHONPATH='src'
python -m lykoi_research.snapshot --confirm-b03-unread --model openai/gpt-6.1-sol --provider OpenAI --output benchmark/results/phase5c/R5_96-CURRENT-ENVIRONMENT-BASELINE.md
```

| Check | Current result |
| --- | --- |
| Canonical model validation | PASS |
| Semantic safety report | PASS; zero capability violations / invalid transitions |
| Compiler | 22/22 PASS |
| Application | 9/9 PASS |
| Authority/artifact controller | 34/34 PASS |
| Requirements workspace | 26/26 PASS |
| Sealed authoring/verification pipeline | 30/30 PASS |
| Public rehearsal mappings/adapters/verification (public/synthetic fixtures) | 33/33 PASS |
| V1 document representation (public/synthetic) | 33/33 PASS |
| Independent external subprocess baseline | 3/3 PASS |
| **Total selected tests** | **190/190 PASS** |

All ten selected commands returned zero. This demonstrates the relevant current
baseline, not universal capability, production AI quality or a held-out result.
Tests of experimental wrapper contracts are regression evidence, not prerequisites
for benchmark access. Passing negative-control tests does not mean those product
limitations disappeared.

Additional command checks: help output works; three argument controls reject absent
declaration, existing output and missing output parent before running checks. Two
mocked controls verify failed checks retain evidence/nonzero status and unknown
model/provider defaults with stdout publication. The first ad-hoc argument-control
invocation had a PowerShell/Python quoting `SyntaxError`; the corrected invocation
passed. No baseline failure was hidden or repaired. `git diff --check` passed.

### Known historical failures and limitations

R5.86–R5.94 history records **two physical-byte CRLF pin failures** in guarded
historical suites; R5.94C's initial 242-test execution records **one historical
exact R5.91 installation snapshot failure**. Those results are retained, not
reclassified as current passes. The relevant history also records failed live
OpenCode/transport attempts and unavailable designated runtime. R5.96 does not
rerun live qualification or historical exact-installation suites; these are
optional experiments rather than current benchmark gates.

Bounded formalization, correlated agreement, incomplete discovery/adequacy and
missing faithful mappings remain substantive limitations. The original public
wizard still has its documented V1 mapping halt, exercised by passing regression
tests. A future requirement can legitimately terminate at any of these boundaries.

## Integrity and B03 status

The single central rule is: **do not modify Lykoi using held-out information before
the first terminal benchmark result is recorded**. Normal requirement formalization
and application authoring with existing capabilities are permitted. Do not repair
semantics/mappings/compiler in response to B03 to obtain that first result.

Immediately before B03 access, record Git commit/tree, relevant tests, core and V1
versions, current model/provider when known, UTC date/time and confirmation of no
previous inspection. On access mark B03 exposed; on informed development mark later
attempts post-exposure. Keep ambiguity, formalization, representation, BDI/adequacy,
capability, compilation and behavioral verification failures distinct from success.

R5.96 made no B03 requirement/source/metadata inspection, protected-source opening,
formalization, implementation or behavioral evaluation. Held-out status is carried
from historical declarations plus this session's no-access discipline; the snapshot
does not claim a machine-enforced proof of nonexposure. No B03-driven retention choice
was made. The next step is the **B03 benchmark in a subsequent instructed round**,
starting with a fresh snapshot, with no further infrastructure qualification round.

## Completion answers

1. **Retained useful architecture:** FRC/formalization/clarification, wizard/policies,
   SOI/reconciliation, BDI/adequacy, faithful representation, authority/artifact
   controller, requirements workspace, independent behavioral verification and
   deterministic compilation/lowering.
2. **Optional/deferred:** exact runtime/OpenCode bytes/versions, all machine/model/
   runtime/adapter/transport qualifications and registry eligibility, cross-machine
   freeze eligibility, exact infrastructure hashes, protected activation/access
   authority and elaborate exposure machinery. Provenance/audit tools remain useful.
3. **Particular Python installation required?** No; compatible Python 3.10+ is needed.
4. **OpenCode required?** No; it is an optional development tool.
5. **Model qualification required?** No; use the current available model and record it.
6. **Held-out protection?** No held-out-informed Lykoi change before the first recorded
   terminal result; exposure and later development are labeled honestly.
7. **Immediately before access?** Fresh commit/tree/tests/core/V1/model/time snapshot
   and confirmation that B03 has never been inspected.
8. **B03 still unread?** Yes; no access during R5.96.
9. **Next step finally B03?** Yes, in the next instructed benchmark round after its
   fresh snapshot. R5.96 stops here.
