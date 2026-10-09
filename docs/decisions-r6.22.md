# Decision supplement — R6.22

## Preserve the stopped diagnostic rather than repairing its outcome

[R6.22](../benchmark/results/phase6/R6_22-REPORT.md) uses experiment-local raw
streaming and single-variable variations to expose repetition while keeping runtime
safeguards and original historical failure intact. Generic JSON success is separated
from exact-count schema validity and terminal completion. Cap exhaustion is not a
runtime crash; excess repeated content does not by itself isolate a decoder/model cause.

The tokenizer port was discovered once; a context reload invalidated that address.
Frozen stop rules terminate on the resulting transport failure. Preserve faulty
harness, traceback, partial sensitivity and unexecuted schema/free comparisons.
Choose **`R6_22_PROTOCOL_HALT`**, rather than claiming local stability or a
causally established model/decoder gap. Do not resume the frozen attempt.

Only a separately authorized successor should qualify backend endpoint lifecycle
and complete a minimal matched-format repetition test. Neutral successes provide
bounded operational evidence, not symbolic authoring/discovery readiness. Production
kernel26/VM/wrapper and all historical publications remain byte-identical; shared
pinned guidance is updated through additive supplements.
