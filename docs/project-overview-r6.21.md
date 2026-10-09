# Lykoi boundary supplement — R6.21

Latest bounded round: **`R6_21_PROTOCOL_HALT`**.
See the [report](../benchmark/results/phase6/R6_21-REPORT.md).

Compact raw serialized prompts and local tokenizer/count/log delivery checks
support intact delivery for two evaluated authoring calls. One model-authored
typed identity definition validates and executes on three cases, twice each.
Third calibration request HTTP500 explicitly reports token-repeat-limit abort.
Inference stops; ordered/nested calibrations and paired A/B comparison NOT_REACHED.
No discovery readiness or efficiency advantage. Existing local Qwen3 8B/Ollama
unchanged; kernel26/production/R6.10/R6.18 and972 protected identities preserved.

Next recommended separately authorized work: bounded neutral repeat-abort diagnosis
with streaming output capture, then a new interface comparison if reliability is
supported. No experiment, downloads, training, MCP, production change, P6-A04
acceptance or P6-A05 access authorized by this recommendation. Stopped after
publication; await owner authorization. Pinned shared guidance stays unchanged.
