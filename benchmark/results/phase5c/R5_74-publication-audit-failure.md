# R5.74 frozen controller publication-audit failure — preserved

The qualified candidate passed eight fresh health stages and completed exactly
one fake actual-mode opening and static observation, followed by post-check,
replay/second-authorization rejection and intentional synthetic repair invalidation.

The subsequent `r5_74_qualification.py audit` command failed:
`Rejected: unsafe publication value`. Its source-text scanner rejected the
controller's own public detection-marker concatenation expression. The expression
contains regex metacharacters and no concrete private-key header or payload.
The same problem was historically encountered in R5.72's source-as-value audit.

Preserve this frozen controller failure. Do not modify its source, replay the
lifecycle, or replace its failed audit with a retrospectively successful command.
The separate `r5_74_readonly_audit.py` independently verifies canonical evidence,
health/freeze linkage, event sequence, history preservation, accounting and source
publication. Its narrowly AST-bound detection-placeholder handling rejects
concrete credential headers and marked-secret values. This audit does not issue
grants, open a benchmark, dispatch an observation or mutate experiment state.

B02 authorization, access and observation remain zero. R5.73 stays halted.
