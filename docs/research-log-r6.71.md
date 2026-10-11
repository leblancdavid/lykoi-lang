# R6.71 research-log supplement

[Comparison report](../benchmark/results/phase6/R6_71-REPORT.md):
`R6_71_STRUCTURED_GENERATION_ONLY`. The explicitly authorized fresh successor
executes54/54 frozen R6.68 generations through R6.70-qualified infrastructure.
All baseline identities pass. Production kernel26, semantics and historical
evidence remain preserved; no training, repairs, retries or historical rescoring.

A/B strict/schema validity0/9 for both models; all36 outputs have Markdown fences.
C validity6/9 base and9/9 adapter, but semantic acceptance1/9 base and0/9 adapter.
Matched schema-valid cases show no operation gain and lower operand/dependency
correctness for adapter. Decoder structural enforcement/completion improvement
does not demonstrate learned semantic construction. One base prior-result chain
action is usable; no adapter action is accepted.

Observed mask enforcement343.665s plus setup26.169s. The inherited outer PEFT
forward hook records zero, so adapter forward-only timing is unavailable; preserve
the instrumentation limitation without an inference retry. No broad generalization
or language superiority claim. Recommend a separately authorized independently
curated, operation-balanced binding diagnostic with a corrected pre-frozen timer.
Stopped after publication; subsequent work requires explicit owner authorization.
