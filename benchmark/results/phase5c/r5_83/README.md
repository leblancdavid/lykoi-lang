# R5.83 audit evidence

Read [the report](../R5_83-HELD-OUT-EXPOSURE-READINESS.md) and frozen
[candidate precommitment](PRECOMMITMENT.md). `audit.json` freezes stdout from the
read-only public `audit.py` diagnostic and exact physical-byte ordinary-component
hashes. It is not a B03 package, content commitment, grant or executable-run closure.

From repository root:

```powershell
python -B -S -m benchmark.results.phase5c.r5_83.audit
python -B -S -m benchmark.results.phase5c.r5_83.verify
python -B -S -m unittest benchmark.evaluation.test_behavioral_discovery_r5_82 benchmark.evaluation.test_implementation_adequacy_r5_81 benchmark.evaluation.test_formal_requirements_r5_80 -v
git diff --check
```

The audit performs assertions for declared unsupported scope, unreviewed coverage,
intentionally false coverage/exclusion attestations and already-public B01 refusal.
Its false-positive authorization-helper outputs are negative controls, **not real
review approvals or authoring grants**. No static consumers, runner, implementation,
oracle or broad test discovery is invoked. All runtime reads are an explicit
ordinary-file allowlist. No protected resource metadata or ledger is inspected.

Qualification is coordinating/source-local; no isolated independent review or
full end-to-end behavioral evaluation is claimed. The candidate's incomplete
operational closure is part of the NOT READY result, not silently completed here.
Stop at R5.83; all B03 counters remain zero.

Initial audit construction failures are preserved as observations: the first run
asserted an empty UNKNOWN list but omitted the supported failure-atomicity rule's
prerequisite; the second reached B01 and failed on the review file's nested
`receipts` container. The prospective audit was corrected to declare its
successful-call-only diagnostic scope and select `receipts.B01`. Neither changed
an upstream mechanism, requirement or historical result. Final outputs are from
the corrected audit, not a repaired held-out evaluation.

Final corrected audit assertions PASS. The unchanged focused suites above pass
**52/52** (16 discovery, 18 adequacy, 18 formalization), zero failures/errors.
These tests corroborate existing bounded behavior, not exposure readiness.
`verify.py` compares the full reproduced output against the frozen public
`audit.json`, including all 29 ordinary-file commitments and scoped accounting;
it never inspects protected ledgers or resources.
Final evidence reproduction **PASS (29/29 pins)**. `git diff --check` **PASS**
for tracked changes (Git emitted only LF/CRLF checkout warnings). No broad
benchmark/harness discovery or protected verification was run.
