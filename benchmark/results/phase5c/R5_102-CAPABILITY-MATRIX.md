# R5.102 — frozen exposed B01–B20 transfer

Requirement-local development/regression evidence; **not held-out generalization or cumulative achievement**.

| Case | R5.101 first blocker | R5.102 first blocker | Native result | Newly reached stages |
| --- | --- | --- | --- | --- |
| B01 | STRUCTURAL | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | None |
| B02 | STRUCTURAL | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | None |
| B03 | STRUCTURAL | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | None |
| B04 | STRUCTURAL | SUCCESS | `BEHAVIORALLY_VERIFIED` | BDI, ADEQUACY, REPRESENTATION, AUTHORING, COMPILATION, RUNTIME, BEHAVIORAL_VERIFICATION |
| B05 | SUCCESS | SUCCESS | `BEHAVIORALLY_VERIFIED` | None |
| B06 | STRUCTURAL | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | None |
| B07 | STRUCTURAL | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | None |
| B08 | STRUCTURAL | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | None |
| B09 | STRUCTURAL | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | None |
| B10 | STRUCTURAL | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | None |
| B11 | STRUCTURAL | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | None |
| B12 | STRUCTURAL | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | None |
| B13 | STRUCTURAL | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | None |
| B14 | STRUCTURAL | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | None |
| B15 | STRUCTURAL | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | None |
| B16 | STRUCTURAL | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | None |
| B17 | FORMALIZATION | FORMALIZATION | `NEEDS_CLARIFICATION` | None |
| B18 | BDI | BDI | `UNSUPPORTED_BDI_SCOPE` | None |
| B19 | STRUCTURAL | STRUCTURAL | `STRUCTURAL_COVERAGE_FAILURE` | None |
| B20 | FORMALIZATION | FORMALIZATION | `NEEDS_CLARIFICATION` | None |

First-blocker distribution: `{"BDI": 1, "FORMALIZATION": 2, "STRUCTURAL": 15, "SUCCESS": 2}`.

B04 uses new typed formalizer output; nineteen rows retain R5.101 captures. Prose-shaped legacy facts are not reparsed downstream. This comparison consequently measures both legacy-capture compatibility and one fresh typed transfer; unchanged halts are not exhaustive current typed-formalization results.

Implementation pins matched before each case and after the whole transfer. B17/B20 questions remain unanswered. R5.101 files match the pre-transfer baseline.
