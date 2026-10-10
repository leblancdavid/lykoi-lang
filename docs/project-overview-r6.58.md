# Lykoi boundary after R6.58

[R6.58 report](../benchmark/results/phase6/R6_58-REPORT.md):
`R6_58_CACHE_RELEASE_SUPPORTED`. Unchanged baseline stops during E04 forward;
microbatch cache release completes four backward calls under8GiB reserved limit,
peak4.297GiB reserved/3.614GiB allocated. Finite112 LoRA gradients, exact shared
prefix losses/gradient identities and actual parameter-equality assertion pass.
Subsequent diagnostic scheduler-state assertion fails due to the installed forbidden
step guard being included in state_dict; raw exit1 is preserved and CPU explanation
published. Final equality manifests were not separately persisted.

Exactly one recommendation: A, prospectively adopt controlled cache release.
No training change is made. Full20-step fit is unqualified; later bounded training
requires authorization. Device-wide attribution remains partial under WDDM.
Production/kernel26, all historical semantics/evidence and frozen workers preserved.
No optimizer/scheduler updates, trained adapter, P6-A04 execution or P6-A05 access.
Stopped after publication.
