# R6.69 — Model identity and constrained-decoder qualification

One owner-authorized bounded nonproduction infrastructure repair/qualification.
Preserve R6.68 publication, halt, nine requirements and A/B/C conditions. No
diagnostic inference, historical rescoring, training, parameter updates, new
semantics, installations, P6-A04 acceptance or P6-A05 access.

## Identity repair

New experiment-local verifier strips only explicit `base_model.model.` from
PEFT-wrapped manifests and `base_layer` only on the frozen q_proj/v_proj module
families. Buffer/quantization-state markers are retained. Enforce bijective
coverage, reject normalized collisions and unsupported wrappers, compare complete
shape/dtype/raw-byte SHA256 records and nested quantization state. Historical raw
tensor arrays are not archived; cryptographic byte fingerprints are the existing
identity representation. No approximate equality or count-only acceptance.
Adapter names and fingerprints are compared separately without normalization.
Checkpoint/tokenizer/adapter file hashes are reverified through inherited audit.

CPU adversarial controls mutate detached manifest copies: missing tensor,
duplicate normalized/source names, unjustified wrapper, shape/dtype/content
differences, base mutation and wrong adapter identity must reject. Real base
loads are compared against the published training identity before generation;
actual adapter wrapping is compared both to its unwrapped snapshot and historical
identity. Post-probe snapshots must match, without modifying model tensors.

## Frozen decoder qualification

Import byte-identical R6.68 StructuralMask; no grammar change. Exhaust admitted
ASCII token-to-text correspondence at empty and in-string contexts. Test
multi-character tokens, all operation/result-label alternatives, structurally
valid but semantically wrong neutral actions, missing/wrong fields/types,
duplicate dependencies, overrange literals and malformed JSON. Synthetic CUDA
logits verify exact allowed set, forbidden -infinity, retained scores, EOS only
after completion and invalid-prefix rejection.

Neutral actual-model probes, four each for unwrapped base and trained adapter:
unseeded generation up to128 tokens, continuation from a neutral action missing
its last brace (max4), complete neutral action forcing EOS (max1), and one-token
budget exhaustion (max1). Seeded probes test integration/termination, not learned
generation. No diagnostic requirements, scope or solutions enter model prompts.
Use R6.68 decoding configuration, pinned model/tokenizer/adapter and precision.
An auditing subclass observes frozen mask behavior and asserts allowed scores
remain unchanged; it does not alter the grammar or insert output tokens.

At most8 neutral generate calls,120s per call,1800s per worker,8GiB reserved
maximum and1.5GiB free minimum; no training. Preserve failures; no runtime retry.
Expected one-token exhaustion is a passing budget control, not a valid action.
Unseeded exhaustion alone does not invalidate structural integration. Other
identity/runtime failures stop qualification; partial evidence determines verdict.

## Readiness and publication

Qualified requires real base/adapter identity correspondence and correct actual
generation-time masking/continuation/EOS/budget controls on both tracks.
Complete preflight verifies frozen input identities, scorer availability, paths,
resources and additive scope. Readiness is infrastructure qualification, not
semantic learning or guaranteed completion of every diagnostic under128 tokens.
The original R6.68 worker remains halted; a separately authorized successor
runner must use the new verifier and unchanged inputs, rather than restart or
edit historical R6.68. No A/B/C diagnostic dispatch is authorized here.

Publish report, mapping/control/probe evidence, inference-readiness receipt and
recommendation. Verify identities/preservation in a fresh process and git diff
--check. Stop and await explicit authorization.
