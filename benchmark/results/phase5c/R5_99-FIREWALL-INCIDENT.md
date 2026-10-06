# R5.99 — unintended historical-log disclosure

After the first full regression run (before a passing generic freeze), the agent
requested `functions.grep` with `path` equal to the exact new file
`D:\Dev\axiom\benchmark\results\phase5c\R5_99-VERIFICATION.json` and pattern
`FAIL|ERROR|Traceback|AssertionError|error:|Ran [0-9]+|tests":`.

The tool returned matches from the **parent directory**, including B03, B04 and
later historical implementation/prediction/regression logs, rather than only
the requested verification file. Those logs included behavioral descriptions.
No B04/later requirement file was directly opened, but **indirect semantic
disclosure occurred**. The round cannot claim B04/later remained unexposed or
that its no-access instruction was satisfied. This is an agent/tool boundary
failure, not an authorized benchmark evaluation and not evidence of capability.

The agent disclosed the incident immediately, stopped content searches in this
area and used exact-file reads. No further B03/later input was deliberately
selected. The optional `B03_POST_EXPOSURE_TRANSFER_2` is **NOT_RUN**. Neither
the immutable B03 first result nor R5.98's transfer result is changed.

Remaining engineering work addresses only the **pre-existing regression failure**:
the R5.98 test expects the historical normal mapper to refuse its unselected
query contract. Explicit, reconciled normal capability-profile selection preserves
that historical route while enabling the additive normal V1 extension. This
correction is motivated by the failed public test already recorded before the
incident, not by any disclosed benchmark wording. No feature family or benchmark
special case is added in response to the logs.

Generic verification/evidence can establish bounded integration behavior, but
the overall R5.99 research round must carry a **benchmark firewall violation**
classification. Future work must treat the accidentally disclosed scope as
potentially contaminated; an unread requirement file alone is not pristine
held-out status. Historical logs/results/files remain unchanged.
