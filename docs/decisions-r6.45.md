# Decision — R6.45

Classify the inherited kiln `{}` error as `R6_45_INTEGRATION_DEFECT`, retain original
requirements and R6.44 classification, and prefer an application-scoped correction
over changing production semantics or weakening the oracle. Error remapping is the
smallest observed-code repair; same-read list-shape enforcement is the more complete
storage-contract closure. Neither is implemented or verified.

Do not infer migration eligibility from absent version tags or creation defaults.
Do not confuse typed validity with raw persistence/error-contract fidelity. Generic
versioned-loader recognition/precedence needs explicit clarification before broader
changes. [Report](../benchmark/results/phase6/R6_45-REPORT.md) and its supported matrix
are documentation only; wait for owner authorization before successor work.
