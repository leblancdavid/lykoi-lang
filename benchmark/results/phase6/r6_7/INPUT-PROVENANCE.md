# R6.7 frozen inputs and provenance

Owner authority is the conversation request “R6.7 — Independent Specification
Reduction Audit”: specification-only review, publication and integrity checks.
It grants no execution, implementation, approval or external-source authority.
Initial tracked/untracked Git status was clean; HEAD was
`c1c31072cf38907e81f55a4d9463e03012b872c3`. Freeze uses raw working-tree bytes,
checked against R6.6's published SHA-256 manifest before reviewer invocation.

| Frozen R6.6 file, relative to benchmark/results/phase6/ | Raw-byte SHA-256 |
| --- | --- |
| R6_6-REPORT.md | a525ca71e780bc5c6ecdd650b5c2500a924d76d8e06c54f81944fca4a2d40e22 |
| r6_6/CANDIDATE-SEMANTICS.md | 65befaec8dcf45257c22e7dac38f59c93489330081f3c1818164ae6eeb5392de |
| r6_6/COMPOSITION-WITNESSES.md | f272705d93c4c23f77d64517f765b180a400cb67c80523d6f784f00c25ab434d |
| r6_6/ADVERSARIAL-MATRIX.md | c6f865c56c880d66a421ff3333d66d84b4e193ad528907e1fcf7f4dcc8470ff9 |
| r6_6/ARCHITECTURAL-ALTERNATIVES.md | bfd970cba357e9ab0818fec89668e55dd6f04a3b31190d882105d29275118288 |
| r6_6/OPEN-OBLIGATIONS.md | 38b39d89c1c2c47f4ea87d0ececc6c505d639367f029783fb6f142f15b764f8f |

The R6.6 manifest is evidence of historical publication, not a signature or
proof of meaning. No copied/repaired R6.6 specification supersedes these bytes.
R6.3–R6.6 reports/directories and other historical tracked artifacts remain exact
baseline objects; preservation is checked by Git differences without reopening
curated sources. P6-A05 was not accessed.

## Review chronology

1. Read repository governance and R6.6 report to scope the publisher's task.
2. Verify six hashes; publish REVIEW-PROTOCOL.md before independent judgments.
3. Appoint a separate general reviewer with no supplied substantive conclusion;
   withhold R6.6 report/alternatives/open obligations until its judgments return.
4. Reviewer returns its analysis; resume the same reviewer solely to preserve its
   full response verbatim as REVIEWER-JUDGMENTS.md. No second substantive pass.
5. Record its SHA-256 before comparison, then publisher reads definitions,
   witnesses, adversarial cells, kernel accounting and relevant value/computation
   docs, followed by R6.6 alternatives/open obligations for explicit comparison.

Protocol SHA-256: `a7b4a363f4a8117d083a583c6323e878f460a35a239d58b7a8df44d6e104c479`.
Precomparison reviewer SHA-256:
`0884c1c934ff78e166512cca4a1c53f70dbcd2c13701747df08d39b6fba0b8e2`.
Reviewer task/session: `ses_ee2ff199dffejoPHysXibH6Jck`. Tool transcript supplies
ordering evidence; local hashes identify retained text, not authenticated authorship.

The initial disclosure understated inherited exposure: a later narrow clarification
confirmed harness guidance had also supplied an R6.7 verdict and substantive findings
before judgment formation. See EXPOSURE-CLARIFICATION.md for the verbatim correction.
Distinct reasoning context and withheld on-disk conclusions do not establish the
protocol's required independent precomparison judgment. Final classification is
R6_7_INDEPENDENCE_NOT_ESTABLISHED. Original protocol/judgment hashes are preserved,
including their unsupported separation assumptions. No clean-room or independent
behavioral claim; read-only review and subsequent exact transcription remain disclosed.

## Existing-kernel authority

`benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json` pins the 26 meanings;
`docs/typed-computation-v1.md` fixes signed-64 addition and the 16-node graph;
`docs/typed-mutable-values-v1.md` fixes ordered map/validation/value behavior.
Additional versioned interfaces read by the reviewer are listed verbatim at the
end of its retained response. No unspecified map body, host codec, contract,
reachability operation or authority gate supplies raw interpretation. Current
profile limitations remain separate from mathematical composition arguments.
