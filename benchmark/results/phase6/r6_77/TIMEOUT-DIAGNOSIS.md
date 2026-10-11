# R6.77 timeout diagnosis

## Responsible layer and supported setting

R6.76's [preserved interruption](../r6_76/HARNESS-INTERRUPTION.json) records
`shell tool terminated command after exceeding timeout 600000 ms`. Its dispatch
source launches four sequential phases and independently tests elapsed time against
1800 seconds **inside each phase's worker-monitoring loop**. The 600-second limit
therefore belongs to the outer shell-tool command runner, not the experiment's
1800-second watchdog. The enforcing executable/PID and runner implementation were
not preserved; attribution to a particular OpenCode internal process is unavailable.
The local CLI currently reports OpenCode **1.18.32**. This does not prove the old
enforcing process identity. An attempted version-specific upstream source lookup
returned HTTP 404, providing no implementation evidence.

The available command tool documents its `timeout` argument in milliseconds.
R6.77's synthetic qualification command was accepted with **1800000 ms** and
completed in approximately three seconds. This establishes a supported configurable
request, not a measured 30-minute survival test or proof that no other host limit
exists. No OpenCode configuration, daemon, detached process or resource bypass was
used. The identity/reuse audit used a 600000-ms foreground command and completed.
An initial PowerShell parser error occurred before the audit launched; it made no
model calls and was corrected by separating the parent-path check from environment
assignments.

## Why increasing the outer timeout alone is insufficient

The original launcher has one base worker, one training worker and one adapter
worker, each limited to 1800 seconds; it does not grant the whole experiment only
1800 seconds. The participant configuration additionally limits each generation to
120 seconds, CUDA reserved memory to 8 GiB, free device memory to at least 1.5 GiB,
and resident memory to 16 GiB. All these limits remain unchanged.

The four completed base cases took 352.462 seconds combined: an 88.1155-second
mean. Extrapolation gives approximately 2643 seconds for 30 cases, or 2291 seconds
for the remaining 26, **excluding model initialization**. These are planning
estimates, not measurements of remaining cases. The original 30-case-per-worker
execution plan is consequently not demonstrated to fit its 1800-second watchdog.
Thirty generations can consume up to 3600 seconds under the individual ceilings.
An increased outer budget does not remove this mismatch.

Experiment-local bounded foreground batches with immutable per-case commitments
would be a possible orchestration design, retaining worker and generation ceilings.
No model batches were dispatched or newly participant-qualified in R6.77: recovery
fails first because the historical next case has an ambiguous generation state.
The frozen training worker would still have to complete in one 1800-second worker;
training splitting, resumption and retries are not authorized corrections.

## Durable correction qualified here

[durable77.py](../../../../experiments/contrastive_learning_r6_77/durable77.py)
implements exclusive ordered starts, immutable raw/commit pairs, digest-verified
recovery, fail-closed interruption/corruption detection, synchronous tracked children,
nonce/interpreter/parent-bound actual-worker PID records, flushed external RSS
samples and durable exit status. It retains resource enforcement and cleanup.
[Qualification](LAUNCHER-QUALIFICATION.json) exercises real pinned Python processes
but no participant/model execution. A complete synthetic worker exits zero; a
separate interrupted worker reaches the actual-PID handshake, is terminated by the
two-second control ceiling, and has exit status and resource samples preserved.
Both control ceilings are smaller than the frozen maximum.

Four historical commitments are qualified for linked reuse. The next generation's
state cannot be recovered. The correction is **synthetically qualified only**;
complete live orchestration remains unqualified. No claim that merely changing a
timeout makes the frozen experiment executable is made.
