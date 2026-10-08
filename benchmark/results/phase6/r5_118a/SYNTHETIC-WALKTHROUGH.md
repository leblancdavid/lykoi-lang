# R5.118A synthetic research evaluation walkthrough

Public known-answer **methodology development evidence**, not external generalization
or independent cognition. Implemented by `NativeResearchTests.research_seal` and
`test_native_research_evaluation_without_product_approval` in
`tests/test_research_authority.py`. The smaller `ping → pong` fixture additionally
tests Workspace identity/start compatibility and a literal external observation.

## Inputs and actors

Reuse public synthetic calibration P01 from preserved R5.80 `candidates.json` and
the separately source-side-authored `verification_fixture` in
`tests/test_sealed_pipeline.py`. Its declared store check runs
`store --code public --value 17`, expects exit 0/output containing `17` and
`measurements.json = {revision: 1, samples: [{code: public, value: 17}]}`.
Coverage is one positive sample, not exhaustive equivalence.

The test administrator explicitly provisions distinct synthetic credentials/roles:
candidate formalizer, reviewer, verifier, `research_approver`, designated
`research_evaluator`, controller, author and verification authority. They simulate
legitimate role boundaries in a test-owned database; no real human approver,
independent cognition, upstream approval or batch delegation is fabricated.
The current coding agent is **not appointed as an external research approver**.

## Inspectable execution

1. Register exact public source text/origin and candidate FRC, without product adoption
   or owner WHAT approval. Commit its identity through the existing mechanical check.
2. Register the source-side research plan, all obligation/check bindings and the exact
   native acceptance payload before an authored model or generated target exists.
3. Register quote traceability and disclosed `SAME_AGENT` review; list assumptions,
   material questions, contradictions and nonblocking uncertainties explicitly.
4. Synthetic appointed approver issues exact approval; only designated evaluator can
   consume it. Controller emits a purpose-labeled research seal, not product approval.
5. Existing native structural/BDI/adequacy/V1/plan checks run. Source-side `native_plan`
   must equal approved payload. The later plan seal precedes author dispatch.
6. Existing restricted author fixture deliberately produces the unrelated canonical
   task CLI. It compiles, but the external verifier executes the fixed store check:
   exit **2**, stdout empty, command `store` rejected, measurement file unobservable.
7. Native result is **`BEHAVIORAL_VERIFICATION_FAILURE`**. This is the correct negative
   control, not software success. Research approval permits an experiment whose
   result can be failure. Author self-verification is refused; deploy use is refused.

The captured [receipt](WALKTHROUGH-RECEIPT.json) records exact content identities,
authority revisions and observations. Temporary controller storage is not retained;
this receipt is a bounded extracted observation, not a complete replay database or
independent reviewer signature. Reproduction creates fresh component/grant identities
when interface files or environment provenance differ; unchanged source/FRC/plan
bindings remain content-addressed.

## Other controls

- Source B, altered FRC, altered expected plan, wrong actor/project, replay and stale
  source/plan/review authority cannot consume source A's approval.
- Candidate approval strings and producer/owner credentials cannot issue research
  authority. A dual-role candidate producer cannot approve itself.
- Blocking clarification, source contradiction and a newly discovered material question
  retain `NEEDS_CLARIFICATION`; newer review invalidates old-review approval.
- Fourth review refused after the initial pass and two corrections.
- Native fault injections retain `STRUCTURAL_COVERAGE_FAILURE`,
  `UNSUPPORTED_BDI_SCOPE`, `IMPLEMENTATION_UNDERSPECIFIED` and
  `UNREPRESENTABLE_SOURCE` with no grant/authoring after the halt.
- Existing product owner/seal path remains compatible and separate; research-only
  issuance/start/native execution creates no `APPROVAL_GRANTED` product event.

Run focused controls from the repository root:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p test_research_authority.py -v
```

No P6-A01/P6-A02 rerun, P6-A03–P6-A05 exposure, new semantic primitive or backend
behavior is involved. The fixture target uses the existing compiler/backend.
