# R6.69 — Model identity and constrained-decoder qualification

**Final classification: `R6_69_PROTOCOL_HALT`.** The namespace-aware verifier
repairs the original base-manifest comparison: a real pinned base load matches
all535 historical base/buffer/quantization-state entries by exact shape, dtype
and byte-content fingerprint. All nine invalid verifier controls reject.
Qualification subsequently halts at a neutral structural-control serialization
defect, before model generation. **The frozen A/B/C comparison is not ready.**

## Scope and preserved identities

Initial git status was clean. [Preflight](r6_69/PREFLIGHT.json) verifies the
R6.68 publication and original protocol halt, R6.67 publication and trained
adapter files, R6.66 training/diagnostic identities, R6.65 scorer publication,
and inherited R6.52 checkpoint/tokenizer/executable checks. The exact nine
R6.68 diagnostic records and A/B/C condition files are hash-bound and unchanged.
Every diagnostic record and prompt canonical identity is rechecked without
calling the scorer on historical responses or exposing diagnostic answers to a
model. R6.68's halt and R6.67's0/13 acceptance remain historical evidence.

Base: Qwen2.5-Coder-1.5B-Instruct, pinned revision
`2e1fd397ee46e1388853d2af2c993145b0f1098a`. Adapter content identity:
`7fa3e7bfd5f99dd54caf700d53537c165a1193752d9820b3283423dfc9aef921`.
All external adapter file sizes/hashes match. The base checkpoint, tokenizer,
adapter, model parameters, grammar, semantic scorer and assembly are unchanged.
No installations or model/optimizer/scheduler updates occur. Production kernel26
is preserved accounting and implementation, not a new construct recount.

## Namespace-aware tensor verifier

The new experiment-local [verifier](../../../experiments/inference_qualification_r6_69/verifier.py)
normalizes only two documented PEFT naming transformations:

1. Remove an explicit leading `base_model.model.` for a manifest declared
   PEFT-wrapped; retain `buffer:` and `quant_state:` entry markers.
2. Remove `base_layer` only within `model.layers.N.self_attn.q_proj` or
   `v_proj`, the two frozen LoRA target families.

Unsupported wrappers and residual wrapper/LoRA names reject. Missing/unexpected
entries and duplicate normalized/source names reject. Correspondence must be
bijective against the pinned reference manifest. Each mapped record must match
completely: exact tensor shape, dtype and SHA256 of contiguous raw tensor bytes,
plus all nested quantization-state tensors/scalars. Count equality alone is
never sufficient. No approximate numerical comparisons or arbitrary prefix
stripping are used.

Historical raw arrays are not archived; their frozen raw-byte fingerprints are
the project's available tensor-content identity representation. This is exact
cryptographic byte-identity checking, not an elementwise recomparison against
unavailable historical arrays. It does not weaken checkpoint file verification.
Adapter tensors are checked separately with exact, unnormalized LoRA names and
shape/dtype/byte fingerprints; adapter files are separately hash-bound.

[Real mapping evidence](r6_69/BASE-UNWRAPPED-MAPPING.json) records the actual
unwrapped model manifest, canonical identity and every source/normalized name.
The [summary](r6_69/TENSOR-MAPPING-SUMMARY.json) reports535 matching entries.
This demonstrates the R6.68 base-name incompatibility can be resolved without
bypassing content verification. Live adapter wrapping and its tensor comparison
are **NOT_REACHED**; only adapter file identity and synthetic adapter-verifier
controls are established here.

## Adversarial verifier qualification

[Controls](r6_69/ADVERSARIAL-VERIFIER.json) run before the frozen dispatch.
The legitimate wrapper-name positive control passes. All invalid controls reject:

| Invalid control | Result |
| --- | --- |
| Missing base tensor | REJECT |
| Incorrect tensor shape | REJECT |
| Incorrect tensor dtype | REJECT |
| Changed byte-content fingerprint | REJECT |
| Unexpected base mutation fingerprint | REJECT |
| Duplicate normalized tensor name | REJECT |
| Duplicate original tensor name | REJECT |
| Unjustified wrapper namespace | REJECT |
| Incorrect adapter tensor identity | REJECT |

These are detached manifest mutations, not deliberate mutations of a model or
checkpoint. They qualify verifier rejection behavior; they do not demonstrate
that a live model mutation occurred. The actual base load passes the same
verifier against historical fingerprints. No training or tensor modification
was performed.

## Frozen qualification and first failure

[Protocol](R6_69-PROTOCOL.md), [configuration](r6_69/QUALIFICATION-CONFIGURATION.json)
and [source/input freeze](r6_69/SOURCE-FREEZE.json) predate dispatch. The planned
neutral probes are unseeded128-token generation, a suffix-continuation control,
complete-action EOS control and one-token budget exhaustion, on base and adapter:
at most eight generation calls. These probes contain no application requirement,
typed diagnostic scope or any of the nine diagnostic solutions. The neutral
action deliberately permits semantically inconsistent Bool addition and an
arbitrary reference: it is a structural test, not a correct construction example.

The [first base process](r6_69/BASE-PROCESS.json) exits1 after **16.353549s**.
Base identity checking passes and its mapping is persisted. The worker next
constructs a neutral action from a JSON configuration written with sorted keys.
Serializing that loaded dictionary preserves `deps,id,node,type` and nested
`expr,op` order. The frozen grammar requires `id,type,deps,node` and `op,expr`.
The neutral structural assertion therefore fails at `qualify.py:164` before the
CUDA mask controls and all `model.generate` probes.

[Halt](r6_69/HALT.json) and [failure analysis](r6_69/FAILURE-ANALYSIS.json)
preserve the exact first error. This is an **experiment-local qualification
harness defect**, not evidence that the grammar fails its advertised structural
subset or that the model cannot generate valid JSON. The frozen no-runtime-retry
rule is honored: no source/configuration repair, second model dispatch or
adapter dispatch follows. One base load, zero neutral generation calls.

## Decoder structural and tokenizer evidence

Post-halt [CPU diagnosis](r6_69/DECODER-CPU-DIAGNOSIS.json) uses the unchanged
R6.68 decoder and pinned tokenizer. It does not rerun or repair the worker.
It confirms the original loaded neutral object rejects in its sorted key order,
while the same action content in the grammar's required order is accepted.
That reordered text is diagnosis evidence only; it is not a repaired model
response, scored action or replacement frozen input.

- All **six** add/le/eq × Int64/Bool structural alternatives pass, including
  semantically inconsistent operands and arbitrary out-of-scope references.
- Every character prefix of those neutral actions is viable.
- **Eleven** invalid controls reject: missing fields, wrong result/dependency/
  operand types, missing nested field, unsupported operation, duplicate
  dependencies, Int64 overflow, empty envelope, Markdown and trailing content.
- Every one of **94,366 admitted ASCII tokens** has correct decoded
  token-to-text correspondence at both an empty and an in-string prefix:
  **188,732 correspondence checks, zero mismatches**. Of the admitted tokens,
  **94,238** have multi-character decoded text.

These checks establish bounded CPU predicate/tokenizer behavior only. The
decoder still admits a restricted compact ASCII fixed-key-order serialization
subset, with escaped Unicode strings. It is not a general JSON Schema decoder
and may encounter dead ends or budget exhaustion. Nothing selects the task's
operation, operands, literal, dependencies or result type.

## Model-time qualification and resource measurements

[Model-time receipt](r6_69/MODEL-TIME-TOKEN-MASK.json) explicitly marks all
remaining planned controls NOT_REACHED:

| Control | Base | Adapter |
| --- | --- | --- |
| Actual generation-time allowed-token masking | NOT_REACHED | NOT_REACHED |
| Neutral unseeded generation | NOT_REACHED | NOT_REACHED |
| Seeded suffix continuation | NOT_REACHED | NOT_REACHED |
| EOS after complete action | NOT_REACHED | NOT_REACHED |
| One-token budget exhaustion | NOT_REACHED | NOT_REACHED |
| Before/after probe tensor preservation | NOT_REACHED | NOT_REACHED |

The worker's token-correspondence loop precedes its failure, but its full decoder
receipt was not yet persisted; the reported tokenizer results above come from
the separately recorded post-halt CPU analysis. There are no actual model
outputs, generated token counts or measured inference/mask-enforcement times.
The16.353549s dispatch time includes model loading, identity checks and neutral
control work; it is not generation latency. Peak generation VRAM is unavailable.

Configured limits remain120s per generation,1800s per worker,8GiB reserved VRAM
maximum and1.5GiB device-free minimum. Generation-time enforcement is unreached;
configuration alone is not a resource qualification result. No CUDA numerical
failure was reported; the preserved error is the structural-control assertion.

## Complete preflight verdict

[Inference readiness](r6_69/INFERENCE-READINESS.json): **ready=false**.

| Component | Status |
| --- | --- |
| Checkpoint/tokenizer/adapter file identities | PASS |
| Nine diagnostic and A/B/C condition identities | PASS |
| R6.65 scorer availability/publication | PASS |
| Real unwrapped base tensor mapping | PASS |
| Adversarial namespace/tensor rejection controls | PASS |
| Frozen grammar CPU diagnosis | PASS, post-halt evidence |
| Live adapter base/adapter tensor comparison | NOT_REACHED |
| Actual model-time mask/continuation/EOS/budget controls | NOT_REACHED |
| Resource-limit configuration | PASS |
| Generation-time resource enforcement | NOT_REACHED |
| Qualification output paths | PASS, new R6.69 directory |
| Publication scope | Additive R6.69 only |

No inference-ready claim or improved generation/semantic-learning claim is made.
The original halted R6.68 runner is never reactivated or overwritten.

## Recommendation, integrity and stop

Retain the namespace-aware verifier and both first failures. Recommend a
**separately authorized corrected neutral-probe serialization and remaining
model-time qualification**, using the unchanged grammar/model/adapter and
diagnostics. Pre-qualify the exact configuration round trip before loading a
model. Require the actual adapter and masked-generation controls to pass before
authorizing a successor A/B/C comparison with fresh output paths. No new
training is justified by these infrastructure observations.

[Publication manifest](r6_69/PUBLICATION-IDENTITIES.json) and
[verification](r6_69/VERIFICATION.json) bind source, report, frozen inputs,
mapping evidence, controls and terminal receipts. Fresh-process integrity and
preservation checks, JSON/Python/links/whitespace/credential checks, additive
scope and git diff --check pass. The additive
[research/decision supplement](../../../docs/research-log-r6.69.md) records the
boundary without changing pinned historical guidance.

Production kernel26/compiler/lowerer/runtime and experimental semantics remain
unchanged; R6.3–R6.68 tracked evidence unchanged; training0, optimizer/scheduler
updates0, dataset expansion0, Python comparison adapter0, installations0,
historical rescoring0, P6-A04 acceptance0, P6-A05 access false. Execution remains
deterministic and AI-independent. **Stopped after partial qualification and
publication. Await explicit authorization for further work.**
