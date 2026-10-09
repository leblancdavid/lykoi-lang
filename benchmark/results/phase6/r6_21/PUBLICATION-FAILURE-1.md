# Publication accounting setup failure

First `python benchmark/results/phase6/r6_21/publish.py collect` exited1 before
executing any code: `SyntaxError: unmatched ')'` at line94. The posthoc publisher
had one excess closing parenthesis in its static parity record. It was removed.
No inference, tokenization, validation replay or evidence write occurred in that
failed command. Frozen runner, prompts, contract, tasks and raw results unchanged.
