# R5.110 — frozen exposed transfer

R5.109 is preserved. Exposed requirement-local regression, not held-out/cumulative evidence.

| Case | R5.109 blocker | R5.110 blocker | Newly reached stages | Behavioral success |
| --- | --- | --- | --- | --- |
| B01 | SUCCESS | SUCCESS | None | Yes |
| B02 | SUCCESS | SUCCESS | None | Yes |
| B03 | SUCCESS | SUCCESS | None | Yes |
| B04 | SUCCESS | SUCCESS | None | Yes |
| B05 | SUCCESS | SUCCESS | None | Yes |
| B06 | SUCCESS | SUCCESS | None | Yes |
| B07 | SUCCESS | SUCCESS | None | Yes |
| B08 | SUCCESS | SUCCESS | None | Yes |
| B09 | SUCCESS | SUCCESS | None | Yes |
| B10 | SUCCESS | SUCCESS | None | Yes |
| B11 | SUCCESS | SUCCESS | None | Yes |
| B12 | SUCCESS | SUCCESS | None | Yes |
| B13 | SUCCESS | SUCCESS | None | Yes |
| B14 | SUCCESS | SUCCESS | None | Yes |
| B15 | SUCCESS | SUCCESS | None | Yes |
| B16 | SUCCESS | SUCCESS | None | Yes |
| B17 | FORMALIZATION | FORMALIZATION | None | No |
| B18 | BDI | STRUCTURAL | None | No |
| B19 | STRUCTURAL | STRUCTURAL | None | No |
| B20 | FORMALIZATION | FORMALIZATION | None | No |

B18 now has ordinary typed durable-state demands rather than an external-effect label. Its required numeric sequence and inherited primary actor bindings remain unsupported; partial coverage rejects before BDI. Generic ordered history succeeds in five domains, but does not establish B18 success.

Exact native/stage receipts: `R5_110-COMPARISON.json`, `R5_110-TRANSFER-EVIDENCE.json`.
