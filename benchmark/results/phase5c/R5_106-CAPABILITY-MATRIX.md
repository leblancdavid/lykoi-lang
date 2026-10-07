# R5.106 — fixed exposed current typed transfer

R5.105 is the preserved baseline. Exposed local regression only; no held-out/cumulative claim.

| Case | R5.105 first blocker | R5.106 first blocker | Newly reached stages | Behavioral success |
| --- | --- | --- | --- | --- |
| B01 | SUCCESS | SUCCESS | None | Yes |
| B02 | SUCCESS | SUCCESS | None | Yes |
| B03 | SUCCESS | SUCCESS | None | Yes |
| B04 | SUCCESS | SUCCESS | None | Yes |
| B05 | SUCCESS | SUCCESS | None | Yes |
| B06 | SUCCESS | SUCCESS | None | Yes |
| B07 | SUCCESS | SUCCESS | None | Yes |
| B08 | STRUCTURAL | STRUCTURAL | None | No |
| B09 | STRUCTURAL | STRUCTURAL | None | No |
| B10 | SUCCESS | SUCCESS | None | Yes |
| B11 | STRUCTURAL | STRUCTURAL | None | No |
| B12 | STRUCTURAL | FORMALIZATION | None | No |
| B13 | STRUCTURAL | STRUCTURAL | None | No |
| B14 | STRUCTURAL | STRUCTURAL | None | No |
| B15 | STRUCTURAL | STRUCTURAL | None | No |
| B16 | STRUCTURAL | STRUCTURAL | None | No |
| B17 | FORMALIZATION | FORMALIZATION | None | No |
| B18 | BDI | BDI | None | No |
| B19 | STRUCTURAL | STRUCTURAL | None | No |
| B20 | FORMALIZATION | FORMALIZATION | None | No |

All stages/native blockers: `R5_106-COMPARISON.json`. Full source, reconciliation, normal pipeline and external evidence: `R5_106-TRANSFER-EVIDENCE.json`.

B08/B09/B11/B12/B13 now retain typed predicate/boolean/guard components; whole coverage still refuses unclosed interface/precursor demands. Partial component representation is not counted as behavioral success.

The initial in-memory producer canonicalization interruption is preserved in `R5_106-TRANSFER-INTERRUPTION.json`; this completed evaluation reads the original locked candidate bytes.
