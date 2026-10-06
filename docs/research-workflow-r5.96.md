# R5.96 — Research workflow simplification decision

Effective 2026-10-06, the priority is **evaluate and improve Lykoi using the
current development environment and current AI model**. This prospective decision
supersedes infrastructure prerequisites for ordinary research and future held-out
evaluation. It does not amend any historical R5.x experiment, freeze, evidence,
readiness decision or result. R5.96 is cleanup only; B03 remains unread.

## Decision and tradeoff

Exact Python executable/DLL/ZIP identity, exact OpenCode version, OpenCode adapter
qualification, provider-neutral AI transport qualification, machine eligibility,
model qualification, cross-machine freeze qualification, exact execution-infrastructure
hashes, protected activation and controller authorization merely to permit benchmark
access are **no longer prerequisites**. Their code and historical records remain
available. A historical candidate can remain inactive/ineligible without blocking
the new research path. Do not activate or rewrite it to simulate readiness.

OpenCode is a development tool, not Lykoi semantics. Python is an implementation
dependency, not a semantic definition or an exact installation requirement. Use
compatible Python 3.10+ and available development tools; record useful environment
facts as provenance. Reproducing another machine's bytes is optional research.

Use the AI model available in the active development environment. Record model and
provider when known (otherwise `unknown`). No model qualification, invariance,
provider independence, cross-model reproduction or model-registry eligibility is
required. Future model changes are allowed; note material changes. For a benchmark's
first attempt, do not intentionally switch models after reading it to improve the
result. Provider/model metadata does not establish independent cognition.

This exchanges elaborate eligibility enforcement for an inspectable research
snapshot and a first-result discipline. It does not establish production readiness,
universal formalization, faithful mapping coverage or behavioral correctness.
Existing bounded semantic/representation failures must remain visible.

## Infrastructure classification

These classifications describe prospective use, not revised historical outcomes.
A module may contain useful product logic and deferred experimental wrappers.

| Classification | Mechanisms retained | Current role |
| --- | --- | --- |
| **Product-useful** | Formal Requirement Contracts, formalization, clarification, AI requirements wizard, project policies, Source Obligation Inventory, reconciliation, Behavioral Decision Discovery, implementation adequacy, faithful representation, authority/artifact controller, requirements workspace, independent behavioral verification, deterministic validation/compilation/lowering | Continue developing and using their bounded behavior. Artifact/owner authority protects product handoffs; it is not permission to open a benchmark. |
| **Research-useful** | Git/version snapshots, environment/model provenance, test logs, independent public/synthetic checks, external subprocess oracle, contamination and first-result records, optional content-integrity/portability diagnostics, role separation and audit journals | Helpful evidence and tools; infrastructure qualification is not mandatory. |
| **Experimental/deferred** | Exact runtime binary/DLL/ZIP pins, exact OpenCode installations, adapter/runtime/transport qualification gates, machine/model registries and eligibility, fixed-model transport freezes, cross-machine freeze eligibility, exact execution-infrastructure hashes, protected-source activation/access authorization/reservations and elaborate exposure receipts | Preserve functioning prototypes (`lykoi_runtime`, `lykoi_freeze`, `lykoi_transport`, `lykoi_protected`, rehearsal freeze/qualification commands and earlier evaluation runners). Optional diagnostics/experiments only. |

`lykoi_controller`, `lykoi_workspace`, `lykoi_pipeline`, formalization/BDI/adequacy
and V1 adapters retain useful architecture. Their experimental end-to-end wrappers
can still enforce their own contracts when explicitly invoked. Ordinary research
uses model/compiler commands and the protocol below; no frozen-wrapper invocation
or weakened historical contract is necessary. Missing complete mappings and bounded
discovery/adequacy remain real limitations, not retired infrastructure requirements.

## Default commands

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH='src'
python -m air_compiler.cli validate air/task_manager.json
python -m air_compiler.cli safety air/task_manager.json
python -m unittest discover -s tests -p test_compiler.py -v
python -m unittest discover -s tests -p test_application.py -v
python -m unittest discover -s benchmark/harness -p test_baseline.py -v
```

For the broader public/synthetic product and V1 baseline plus these checks:

```powershell
python -m lykoi_research.snapshot --confirm-b03-unread --model openai/gpt-6.1-sol --provider OpenAI --output benchmark/results/phase5c/pre-b03-snapshot.md
```

Supply the **then-current** model/provider, not this example's identity by habit.
Omit either option if unknown. The command records HEAD, working-tree status before
and after checks, UTC time, Python/platform provenance, actual core/backend/V1
versions, command exit codes and complete test output. It uses the current Python;
no credentials, AI calls, protected sources or freeze eligibility APIs. It never
reads B03. The held-out declaration is a human/agent attestation, not a technical
proof. It refuses an existing output file; stdout is available without `--output`.
Nonzero check exits produce a nonzero command exit while retaining the evidence;
investigate and report failures honestly rather than recasting them as machine
ineligibility. A dirty tree is recorded, not rejected; retain its diff/untracked
work with the snapshot when it changes the evaluated baseline.

Broad discovery across all historical harness/evaluation suites is optional and
must respect held-out boundaries. Historical exact-installation and CRLF-pin
assertions are not current core gates; do not rewrite their failures as passes.

## Simplified held-out benchmark protocol

1. **Immediately before B03 access**, record current Git commit and working-tree
   state (preserve relevant local changes), relevant current test status, core
   semantics/backend version, representation/V1 version, current model/provider
   when known, UTC time, and confirmation that B03 has not previously been inspected.
   The snapshot command above is the lightweight process. The R5.96 baseline is
   not a substitute for refreshing the snapshot immediately before a later access.
2. Until first access, B03 is held out. On first access, mark **B03 exposed** and
   record the exposure time. No protected activation, machine eligibility or
   controller access grant is required under this research protocol.
3. Read the requirement and process it through the current Lykoi workflow. Normal
   formalization, clarification, FRC/SOI/reconciliation, BDI/adequacy analysis and
   faithful representation are permitted where helpful. Derive independent
   behavioral verification from the requirement; keep acceptance separate from
   authoring and do not tailor implementation to hidden oracle answers.
4. **Do not modify Lykoi using held-out information before the first terminal result
   is recorded.** In particular, do not change semantics, mappings, representation
   rules, compiler/lowering or shared capability code in response to B03. Author
   the application/model using existing capabilities if representable, compile
   deterministically and run independent behavioral verification. If a stage
   cannot proceed, record that terminal failure with evidence and downstream
   checks as not run; do not extend Lykoi to obtain the first result.
5. Record the first terminal result, attempted artifacts, stage reached, verification
   evidence and provenance. That result is the held-out benchmark result. Distinguish
   requirement ambiguity, formalization failure, representation gap, BDI/adequacy
   gap, Lykoi capability gap, compilation failure, behavioral verification failure
   and success. Describe execution/tool failures separately when they prevent a
   behavioral conclusion; never infer a semantic gap from infrastructure alone.
6. Only after that record exists may B03-informed development begin. Mark that
   transition and label subsequent attempts **post-exposure development/diagnostic
   evaluations**, never pristine held-out results. Preserve the first result.

No infrastructure qualification round is required before the next B03 benchmark.
R5.96 ends before access; a subsequent instructed benchmark round must take its
fresh snapshot and then evaluate. Historical Phase 5C achieved histories, the
R5.2.2 post-B16 boundary and B17 nonexposure remain their separate experiment.
