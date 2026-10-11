# R6.70 — Final constrained-decoder integration qualification

**Final classification: `R6_70_INFERENCE_COMPARISON_READY`.** Neutral serialization
is corrected locally; live base and R6.67 adapter verification and actual
generation-time constrained decoding pass. The frozen R6.68 comparison has
qualified inference prerequisites. Its execution still requires separate owner
authorization and a fresh successor runner/output path. No scored comparison ran.

## Preservation and scope

Initial git status contained the existing untracked R6.69 publication and source.
These files were treated as protected baseline, not overwritten. The
[preflight](r6_70/PREFLIGHT.json) verifies R6.68/R6.69 publication manifests,
R6.69 frozen source and original halt, R6.67 adapter publication/files, R6.52
checkpoint/tokenizer and inherited executable identities, R6.65 scorer, all nine
R6.68 diagnostic identities and all frozen A/B/C prompt/configuration identities.
Checks ran before dispatch and again for publication; no historical responses
were rescored and no scored diagnostic solutions entered a model prompt.

- Base: Qwen2.5-Coder-1.5B-Instruct, revision
  `2e1fd397ee46e1388853d2af2c993145b0f1098a`.
- Adapter file content identity:
  `7fa3e7bfd5f99dd54caf700d53537c165a1193752d9820b3283423dfc9aef921`.
- Loaded adapter tensor-manifest identity:
  `57c1281624acd0fe6249e78fdbea8755c3d81f24c35d203df0be5779b1f6db03`.
- Frozen decoder source SHA256:
  `f93b261933487a9a95f8fc07339cfb9e902374a5421e4037f009ccf06cc9a01f`.

The byte-identical R6.69 namespace-aware verifier remains in use. It rejects
unexpected names, ambiguous mappings and normalized collisions and compares
exact shape/dtype/raw-byte fingerprints plus complete quantization state.
Historical arrays are not available for an independent elementwise comparison;
the established identity mechanism is exact cryptographic byte fingerprints.
Production kernel26 accounting, compiler/lowerer/runtime and experimental
semantics are unchanged. R6.68/R6.69 failures and R6.67 historical0/13 acceptance
remain intact.

## Exact correction and CPU qualification

The R6.69 configuration writer sorted dictionaries. Its neutral-action round
trip yielded outer `deps,id,node,type` and nested `expr,op`; the fixed grammar
requires outer `id,type,deps,node` and nested `op,expr`. The
[local correction](../../../experiments/inference_qualification_r6_70/qualify.py)
reconstructs only those two envelopes after reading the configuration. It asserts
identical dictionary content and preserves the expression, operation, operands,
dependencies and result label exactly. Compact ASCII JSON is then serialized in
insertion order. No grammar, scored input or semantic-selection rule changed.

[CPU controls](r6_70/CPU-SERIALIZATION-CONTROLS.json), completed before loading:

- Correct order accepted; original sorted order rejected.
- Both wrong outer and wrong nested order rejected.
- Missing field, extra outer/nested field, invalid result/dependency/operand
  types and invalid expression/node operation alternatives rejected:10 controls.
- All six add/le/eq × Int64/Bool alternatives and every character prefix pass.
- 100 sorted-configuration round trips produce identical serialization bytes;
  parsed content remains identical to the original neutral action.

The neutral Bool-addition probe is deliberately semantically inconsistent and
references an arbitrary name. Acceptance establishes structural permissiveness,
not valid Lykoi construction. R6.69's original failure was not repaired in place.

## Frozen worker and actual live verification

[Protocol](R6_70-PROTOCOL.md), [configuration](r6_70/QUALIFICATION-CONFIGURATION.json),
[effective worker](r6_70/EFFECTIVE-WORKER.py.txt) and
[source freeze](r6_70/SOURCE-FREEZE.json) precede dispatch. The derived worker
retains the R6.69 loading/verification path with only the envelope reconstruction,
a repeated neutral suffix probe and evidence instrumentation. Parameters are
frozen, model eval mode and `torch.inference_mode()` are used; no parameter merge,
optimizer, scheduler or training step occurs.

| Live verification | Result |
| --- | --- |
| Base worker unwrapped base mapping |535/535 exact entries PASS |
| Adapter worker unwrapped base mapping |535/535 exact entries PASS |
| Adapter-wrapped historical base mapping |535/535 exact entries PASS |
| Wrapped versus same-process unwrapped base contents |PASS |
| Adapter file hashes and sizes |PASS |
| Loaded adapter tensors |112/112 exact shapes/dtypes/fingerprints PASS |
| Inference initialization/all parameters frozen |PASS both workers |
| Post-generation base fingerprints |Unchanged both workers |
| Post-generation adapter fingerprints |Unchanged |

Evidence: [base mapping](r6_70/BASE-UNWRAPPED-MAPPING.json),
[adapter unwrapped](r6_70/ADAPTER-UNWRAPPED-MAPPING.json),
[adapter wrapped](r6_70/ADAPTER-WRAPPED-MAPPING.json),
[adapter tensors](r6_70/ADAPTER-TENSORS.json),
[base initialization](r6_70/BASE-INITIALIZATION.json),
[adapter initialization](r6_70/ADAPTER-INITIALIZATION.json),
[base result](r6_70/BASE-RESULT.json) and [adapter result](r6_70/ADAPTER-RESULT.json).
The112 live adapter tensors are float32, with the original rank8 q/v shapes.

## Generation-time token masks and termination

[Base controls](r6_70/BASE-DECODER-CONTROLS.json) and
[adapter controls](r6_70/ADAPTER-DECODER-CONTROLS.json) exhaust94,366 admitted
ASCII tokens at two contexts:188,732 token-text checks per worker, zero mismatches.
94,238 tokens have multiple characters. Four CUDA synthetic-logit prefix controls
per worker verify exact allowed sets, unchanged allowed logits, forbidden
negative infinity and EOS only after completion. Invalid-prefix masking rejects
with `GRAMMAR_PREFIX_REJECTED`. Eleven malformed structural controls per worker
also reject.

Ten actual model generations use neutral prompts only:

| Probe | Base | Adapter |
| --- | --- | --- |
| Unseeded,128-token maximum |49 tokens, complete JSON + EOS |49 tokens, complete JSON + EOS |
| Last-brace suffix continuation |`}` then EOS,2 tokens |`}` then EOS,2 tokens |
| Identical suffix repeat |Identical2 token IDs |Identical2 token IDs |
| Complete neutral action |EOS only,1 token |EOS only,1 token |
| One-token budget |1 token, viable incomplete prefix, no EOS |Same budget behavior |

[Raw base probes](r6_70/BASE-PROBES.json) and
[raw adapter probes](r6_70/ADAPTER-PROBES.json) retain outputs, token IDs,
per-step prefixes, allowed counts/set fingerprints, selected text and masking
assertions. The actual returned token sequence equals the mask's greedy
selections in all55 steps per worker. A separate post-dispatch
[CPU token-mask audit](r6_70/TOKEN-MASK-AUDIT.json) reconstructs all110 actual
prefixes, recomputes every exact allowed-set fingerprint, checks token membership
and token-to-text correspondence and verifies termination/repeatability. This
read-only audit source is publication-bound; it did not change the frozen worker
or perform additional inference.

Both unseeded outputs happen to be identical:

```json
{"id":"selected","type":"Int64","deps":["dep1","dep2"],"node":{"op":"value","expr":{"add":[{"ref":"const1"},{"ref":"const2"}]}}}
```

These are unscored structural outputs. No application scope or solution was
provided. The mask admits all operation/result alternatives, arbitrary reference
names, literals and dependencies; it never selects the correct operation,
operand order or dependencies. It constrains only the frozen structural subset
(including declared Int64 bounds and dependency uniqueness). Complete output is
JSON-validated by the unchanged structural checker. The neutral semantic
inconsistency also passes, demonstrating that task semantics are not enforced.
This remains a compact ASCII fixed-key-order subset, not arbitrary JSON Schema;
other prefixes can dead-end or exhaust budget. Seeded repeatability qualifies
this continuation, not reproducibility of every possible model output.

## Resources and failed attempts

[Measurements](r6_70/RESOURCE-MEASUREMENTS.json) record all generation timings,
mask timings, allocated/reserved peaks and device free memory; process logs
retain stdout/stderr. Limits remain120s per generation,1800s per worker,
8GiB reserved maximum and1.5GiB free minimum, checked during generation.

| Measurement | Base | Adapter |
| --- | --- | --- |
| Worker wall time |52.457233s |48.562555s |
| Unseeded inference wall time |16.109428s |17.449543s |
| Unseeded mask enforcement time |11.168400s |11.999223s |
| Largest observed generation allocated peak |1,672,568,320 bytes |1,676,926,464 bytes |
| Largest observed generation reserved peak |2,529,165,312 bytes |2,533,359,616 bytes |
| Lowest recorded generation-end free memory |9,074,376,704 bytes |9,070,182,400 bytes |
| Generated tokens / calls |55 /5 |55 /5 |
| Live runtime failures |0 |0 |

Mask times include CUDA synchronization; worker times include load/verification
and controls. Allocated/reserved statistics reset per probe. The final worker
resource snapshots therefore describe the last probe, not an uninterrupted
whole-worker peak; the table uses maxima across the recorded generation peaks.
Free memory was checked at each stopping-criteria step; archived numeric free
values are generation-end measurements, not sampled whole-run minima.

One initial read-only preflight exceeded the shell tool's120s allowance before
the output directory existed. It involved zero model loads/generation calls.
[Preflight attempts](r6_70/PREFLIGHT-ATTEMPTS.json) preserve the tool failure and
successful subsequent audit with a600s shell allowance. Model/worker limits
were unchanged. Each live worker dispatched once; no model retry occurred.

## Final readiness receipt and next step

[Final receipt](r6_70/INFERENCE-READINESS.json): **ready=true**, no remaining
mandatory qualification blocker. [Model-time summary](r6_70/MODEL-TIME-TOKEN-MASK.json)
binds both tracks and their evidence. Qualified components are checkpoint/base
loading, live adapter loading, actual constrained decoding, nine frozen
diagnostics, frozen A/B/C generation settings, unchanged qualified R6.65 scorer,
resource/timeout configuration and observed enforcement, and fresh publication
paths. Generation is greedy, one beam,128-token paired maximum, repetition
penalty1.1, cache off and seed651, with the inherited precision configuration.

**The frozen comparison is inference-executable through a separately authorized
fresh successor runner** using these qualified components. The historical
R6.68 runner still contains its preserved verifier defect and remains halted;
its original output directory must not be reused. The receipt is qualification,
not a claim that all scored diagnostics finish successfully or that the adapter
improves Lykoi construction. No A/B/C comparative result or semantic advantage
is established here.

Recommended next step: separately authorize that bounded successor A/B/C
comparison with unchanged nine-case inputs/settings, R6.69 verifier, frozen
R6.68 decoder and new output paths. No further training is justified by this
qualification alone.

## Publication integrity and stop

[Publication identities](r6_70/PUBLICATION-IDENTITIES.json) and
[verification](r6_70/VERIFICATION.json) bind source, frozen worker, raw evidence,
receipts, report and supplement. Fresh-process verification checks publication
and inherited identities, JSON/Python syntax, links, whitespace, credential
patterns, additive scope and `git diff --check`. No tracked file was modified;
existing R6.69 untracked publication files match their original manifest.

Training0, model/optimizer/scheduler updates0, dataset expansion0, installations0,
Python comparison adapter0, historical rescoring0, P6-A04 acceptance0 and P6-A05
access false. Production kernel26 and AI-independent deterministic execution
remain preserved. **Stopped after bounded qualification and publication;
await explicit authorization before further work.**
