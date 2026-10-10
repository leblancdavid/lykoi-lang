# R6.44 architectural decision record

**Observed decision:** no production architecture change. Classification is
R6_44_COMPARISON_INCONCLUSIVE; [report](../benchmark/results/phase6/R6_44-REPORT.md).

The existing production stateful path expresses and deploys the shared-policy
modification with correct finite persistence/error/regression observations. Python
achieves the same behavior. Both first candidates pass without candidate repairs;
this establishes no reliability superiority. Python has lower measured participant
wall/fresh-input/output effort; Lykoi has fewer visible completions/export-accounted
tokens. Missing actual billing and shared preparation effort prevent a total-cost win.

An inherited decoder-error mismatch limits the baseline contract, and production
impact omits typed extension users. Typed validation is useful mechanics but did
not uniquely prevent a scored defect. External requirements checks remain necessary.

**Proposal only:** separately authorize malformed-store baseline-contract review
before another comparison; separately consider extension-aware impact diagnostics.
Retain the bounded production-backed stateful route and Python comparator. No kernel
extension, broader campaign, rerun or adaptive stateful wrapper adoption follows.
Stop after publication and wait for explicit owner authorization.
