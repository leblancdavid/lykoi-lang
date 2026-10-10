# R6.43 decision — keep observations separate from execution

Adopt a versioned experiment-only [observation contract](../experiments/provenance_r6_43/OBSERVATION-1.md)
and pure labels over raw records. Empty numeric origins are labeled available-empty;
missing dynamic ancestry is unavailable. Do not reconstruct lineage from spans,
normalize flat offsets or replace a check consumer's path with its producer path.

Keep historical R6.42 expectation failures intact. New expectations use unchanged
semantic authority and a pre-execution static review with explicit independence
limits. Reject unsupported coordinate claims locally without adding VM semantics.

Assess realistic stateful comparisons through production's existing bounded profile.
Do not execute stateful host callbacks as if they were R6.18 symbolic semantics.
Recommend a small existing production-backed modification study only after independent
requirements/baseline review and separately authorized authoring. Full measurement
gaps are disclosed rather than filled by a new telemetry platform. Stop at publication.
