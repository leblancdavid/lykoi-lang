# R6.59 frozen single-attempt protocol

Owner authorizes one nonproduction attempt: exactly the complete R6.56
configuration, with R6.58 qualified controlled cache release after each completed
backward, scalar telemetry and graph/input cleanup. Accumulated gradients survive;
no microbatch zeroing. No optimizer/scheduler method instrumentation assignments.
Local counters increment only after native calls return; installed state is read-only.
CPU synthetic twin qualification compares exact parameters, moments and scheduler
state with/without read-only accounting across 20 updates before model dispatch.

Pinned Qwen/Qwen2.5-Coder-1.5B-Instruct revision
2e1fd397ee46e1388853d2af2c993145b0f1098a; NF4 double quantization/BF16;
rank8/alpha16/dropout0.05 q/v adapters, FP32; seed651; sequence cap2048,
microbatch1/accumulation4; E01–E06 cyclic80 presentations; per-record supervised
mean loss/4. Frozen AdamW including weight_decay0; frozen R6.54 linear schedule,
2 warmup steps,20 updates. Frozen clipping/checkpoint10/20 and all other settings.

Enforce reserved8GiB, device-free1.5GiB, actual worker RSS16GiB and1800s training
process timeout. Numerical/base-gradient/base-identity/serialization failures stop.
No retry or configuration change. Telemetry preserves values before threshold checks;
device-free minima are sampled, not guaranteed continuous minima. Each release
verifies exact accumulated gradient bytes. Watchdog interval remains100ms.

Reuse the identity-verified R6.56 six-item base diagnostics; no rerun. Conditional
on20 updates/save, fresh-process exact trained tensor/base/reference-logit reload;
then identical frozen six-item diagnostics on step20 only, no result-based selection,
repair, markdown extraction or seal assistance. These are exposed resubstitution
records; no broad generalization inference. No merge or comparison Python adapter.

Classification: supported requires20 updates, changed adapter and fresh reload.
If those hold classify R6_59_LORA_SMOKE_SUPPORTED regardless of improved scores.
Otherwise resource/stack halt -> R6_59_RESOURCE_OR_STACK_GAP; protocol/identity
halt -> R6_59_PROTOCOL_HALT; other partial update completion -> R6_59_TRAINING_PARTIAL.
R6_59_NO_OBSERVED_LEARNING is reserved for a completed interpretable measurement
without observed parameter or learning change (cannot satisfy supported criteria).

Preserve all historical publications and failed R6.58 scheduler assertion.
Production26/compiler/lowerer/runtime and experimental semantics unchanged.
No dataset expansion, P6-A04 acceptance or P6-A05 access. Publish exact artifact
identities, losses/memory/accounting, reload/comparison or explicit NOT_REACHED,
limitations and one recommended next experiment, then stop awaiting authorization.
