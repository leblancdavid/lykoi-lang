# Lykoi current-boundary supplement — R6.20

**R6.20: `R6_20_PROTOCOL_HALT`.**
[Diagnostic report](../benchmark/results/phase6/R6_20-REPORT.md) supersedes R6.19 as
the latest bounded observation. Existing local Ollama0.35.0/Qwen3 8B Q4_K_M completed
49 neutral requests with HTTP200; the historical500 was not reproduced or explained.
Fifteen schema-constrained neutral requests and two inert tool selections passed.
Three deliberately insufficient generation caps produced incomplete JSON.

The new shared symbolic prompt was oversized: all28 feature/comparison calls were
input-truncated to4098 tokens. Every symbolic output failed JSON/schema checks;
no accepted model composition and no incremental-validity benefit. Feature-specific
semantic failure attribution is NOT_REACHED. This is an R6.20 harness/delivery
defect, not evidence of semantic incapacity.

Production kernel26, production, R6.10, R6.18 and all R6.19 publication identities
remain exact (883 protected files). Shared historical guidance is itself pinned,
so this status is an additive supplement. No discovery, training, downloads, MCP
infrastructure, P6-A04 acceptance or P6-A05 access occurred.

Recommend a separately authorized compact-prompt/delivery integrity qualification,
then bounded runtime investigation and a fresh neutral interface comparison before
discovery. Stopped after publication; await explicit authorization.
