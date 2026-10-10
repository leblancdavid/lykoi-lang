# Lykoi boundary supplement — R6.41

Parent: [R6.40 boundary](project-overview-r6.40.md).

**R6.41: `R6_41_REQUIREMENT_CLARIFICATION_NEEDED`.** The
[documentation-only investigation](../benchmark/results/phase6/R6_41-REPORT.md)
establishes why both combination tasks disagree with the frozen oracle: composed
arithmetic returns region-start spans2, while later checks' oracle sites expect
input-origin1/0. R6.18 explicitly makes seq-return spans normative; R6.40 task prose
does not explicitly settle derived provenance across boundaries. Historical failures
and scores remain preserved. Recorded work also differs between compact and flat
plans; the template control is not full-envelope equivalent.

Existing node maps, immutable pins and generated occurrence paths support separate
bounded operation/symbolic provenance. Full expression/text coordinates and runtime
integer input ancestry are not provided. Recommend retaining raw VM semantics plus
separate node-level symbolic origins; adopt no new contract until human clarification.

Kernel26, production/VM/wrapper/adapter/contracts/registry and R6.3–R6.40 identities
remain unchanged. No new execution, AI authoring/training, historical rescoring,
P6-A04 acceptance or P6-A05 access. Smallest next proposal: independently frozen,
model-free compact/exact-expanded/flat provenance micro-qualification after explicit
clarification and authorization. Stopped after publication.
