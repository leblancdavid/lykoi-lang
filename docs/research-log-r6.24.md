# R6.24 research log supplement

Observed: four scripted typed-tool calls construct a valid program; four functional
inputs and six rejection/rollback controls pass; valid-but-wrong control stays
separate. Existing Qwen/Ollama completes warmup and selects the correct inert tool
with its argument. Native API adds id/index metadata. The frozen harness rejects
that shape before task exposure, and the dispatcher would reject it too.

[Report/evidence](../benchmark/results/phase6/R6_24-REPORT.md) preserve the host
import preparation failure, task freeze, raw neutral responses, exact native
metadata and terminal halt. **R6_24_PROTOCOL_HALT**, not model failure. All model
functional cases and comparison stages NOT_REACHED.168 input/23 output tokens;
14.374713s bounded run; no repairs/runtime aborts; task timing unavailable.
No new semantic meanings or production changes;1,228 protected identities checked.
Stop pending separate authorization for a metadata-aware end-to-end qualification.
