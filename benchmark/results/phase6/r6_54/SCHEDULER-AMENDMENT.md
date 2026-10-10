# R6.54 — Prospective scheduler amendment

This amendment closes the scheduler gap prospectively. R6.53's original
`R6_53_PROTOCOL_HALT` and all historical bytes remain unchanged. It does not
adopt unspecified optimizer hyperparameters or qualify a model training run.

## Qualified framework semantics

Use Transformers4.55.4 `get_linear_schedule_with_warmup`, backed by
PyTorch2.7.1+cu128 `LambdaLR`, peak LR1e-4, warmup2, total20. The installed
function docstring and implementation are retained with their module hash in
[the exact schedule](LEARNING-RATE-SCHEDULE.json). The documented interface is
also described at https://huggingface.co/docs/transformers/v4.55.4/en/main_classes/optimizer_schedules#transformers.get_linear_schedule_with_warmup .
No remote code or new framework is used.

Let k be the number of completed successful optimizer updates:

```text
f(k) = k/2                         for 0 <= k < 2
f(k) = max(0, (20-k)/(20-2))        for k >= 2
LR(k) = 1e-4 * f(k)
```

Scheduler construction evaluates index0 and installs LR0. For optimizer update
s=1..20, use LR(s-1). After that successful update, call `scheduler.step()` exactly
once, installing LR(s). Thus the first update uses zero LR; this is the selected
framework's warmup semantics, not an altered schedule. Peak LR is installed after
step2 and used by update3. LR after step20 is zero; update20 uses LR19.

| Completed optimizer step | LR used by that update | LR after scheduler tick |
| ---: | ---: | ---: |
| 1 | 0 | 5e-5 |
| 2 | 5e-5 | 1e-4 |
| 3 | 1e-4 | 9.444444444444444e-5 |
| 4 | 9.444444444444444e-5 | 8.888888888888889e-5 |
| 5 | 8.888888888888889e-5 | 8.333333333333334e-5 |
| 6 | 8.333333333333334e-5 | 7.777777777777778e-5 |
| 7 | 7.777777777777778e-5 | 7.222222222222222e-5 |
| 8 | 7.222222222222222e-5 | 6.666666666666667e-5 |
| 9 | 6.666666666666667e-5 | 6.111111111111112e-5 |
| 10 | 6.111111111111112e-5 | 5.555555555555556e-5 |
| 11 | 5.555555555555556e-5 | 5e-5 |
| 12 | 5e-5 | 4.4444444444444447e-5 |
| 13 | 4.4444444444444447e-5 | 3.888888888888889e-5 |
| 14 | 3.888888888888889e-5 | 3.3333333333333335e-5 |
| 15 | 3.3333333333333335e-5 | 2.777777777777778e-5 |
| 16 | 2.777777777777778e-5 | 2.2222222222222223e-5 |
| 17 | 2.2222222222222223e-5 | 1.6666666666666667e-5 |
| 18 | 1.6666666666666667e-5 | 1.1111111111111112e-5 |
| 19 | 1.1111111111111112e-5 | 5.555555555555556e-6 |
| 20 | 5.555555555555556e-6 | 0 |

The JSON preserves actual Python float values and exact rational peak multipliers;
the formula and JSON are authoritative over rounded prose decimals.

## Accumulation and failed-update contract

Four microsteps produce one planned optimizer-update boundary. No scheduler call
occurs inside a microstep. Call the scheduler only after a completed, unskipped
optimizer update; a failed/skipped update gets no tick. Twenty completed updates
would require80 example presentations at microbatch1. No extra attempts or automatic
retry on a failed update are authorized.

Qualification uses an inert CPU scalar with SGD purely as a LambdaLR control. It
has no gradients, no parameter change, no model or examples, and is not the selected
training optimizer. Twenty no-gradient optimizer method calls plus20 scheduler
ticks match the exact formula. Eighty microstep controls and20 deliberate no-call
skipped-update controls preserve scheduler state. These checks establish scheduler
semantics/intended accounting; they do not test a real training loop or failure
detection. Model optimizer steps remain0.

## Remaining gate

AdamW `betas` and `eps` were not fixed in the prior proposal, nor adopted as defaults
in R6.53. R6.54 authorizes the scheduler amendment only and prohibits inventing other
values. The complete training configuration remains unqualified; stop before training.
