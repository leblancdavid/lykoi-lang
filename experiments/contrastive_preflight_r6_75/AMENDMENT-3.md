# R6.75 actual-worker attribution amendment

Version2 passes CPU numerical, dataset, evaluation and resource self-measurement
checks. Its three dry phases complete, but final audit rejects attribution: the pinned
Windows venv executable is a redirector. `Popen.pid` is not the Python worker PID.
Original measurements are genuine launcher RSS, not fabricated worker RSS; the
version2 result and HALT-finish.json stay intact and are not readiness evidence.

Version3 preserves semantic/training choices and corrected v2 fixtures. An exclusive
per-phase nonce-bound handshake reports current worker PID, parent PID, mode and
pinned interpreter before the worker reaches model boundaries. The launcher validates
nonce/mode/interpreter and immediate parent identity (or same PID on a nonredirecting
platform), monitors that worker's RSS, and separately labels startup-launcher samples.
The worker's self-measurement and launcher samples must agree on process attribution.
No process IDs are hard-coded. Failed worker limits terminate worker and redirector.
This is experiment-local instrumentation, not a new training or execution meaning.

Version3 has separate qualification_3 paths and a pre-execution source/configuration
freeze. Handshake rejection controls and final audit must pass before readiness.
