# Research observation supplement — R6.21

[R6.21](../benchmark/results/phase6/R6_21-REPORT.md) records three intact sentinel
requests at50/1651/2851 runtime-tokenized inputs. Evaluated symbolic prompts are
961/953 tokens; both strict JSON/schema valid. First self-references literals with
empty deps and rejects; second parameterized identity definition passes unchanged
wrapper/VM on0/17/65535, repeated exact envelopes. Third call returns HTTP500 with
token-repeat-limit body/log; final output/usage absent. Seven requests, six complete;
known input/output sums6500/250 exclude failed-call final usage.

All raw requests/body/log/counts and missing telemetry are retained. Three later
calibrations and both paired interfaces NOT_REACHED. No output repair or retry.
Classification `R6_21_PROTOCOL_HALT`; intact delivery and one executable definition
are narrower observations than runtime reliability or discovery readiness.
Coordinator knows prior outcomes; synthetic tailoring/single seed/shared host
prevent independence/generalization claims. Stop after publication.
