# Research log supplement — R6.22

Owner-authorized local streaming diagnosis [published](../benchmark/results/phase6/R6_22-REPORT.md)
as **`R6_22_PROTOCOL_HALT`**. Seven synthetic request types and seven configuration
variants were frozen before inference; coordinator knew prior outcomes. No scored
symbolic construction or independent-replication claim.

Excess repetition is visible: requested128 zeros produce1,023 zero lexemes and
budget exhaustion; requested64 identifiers produce201 decoded entries with one
corrupted string. Repeat penalty1.1 instead produces63 correct identifiers but
still fails the exact-length schema. Temperature0.6/top_p0.8 show no output change.
No generation repeat-guard abort or HTTP500 occurred; original R6.21 cause unresolved.

One requested context reduction completes, then obsolete tokenizer-port preflight
halts the runner. This is an established harness defect, not evidence of resource
exhaustion. All evidence/frozen code is preserved without rerun.34 challenges:
28 complete,15 schema-valid/exact, six budget exhaustions; warmup separate.
New log's unrelated PATH fields filtered with provenance; generation bytes untouched.
1,014 protected identities preserved. Further neutral qualification requires
explicit authorization; authoring/discovery readiness is not established.
