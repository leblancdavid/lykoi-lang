# Preserved unsuccessful initial probe execution

Command: `python -B benchmark/results/phase6/r6_13/probes.py`.
Tool timeout: 120000 ms; tool reported termination after exceeding 120000 ms,
no captured stdout. A subsequent Get-Process check found no Python process.
PROBE-INPUTS.json and PROBE-FREEZE.json were written before execution. There is
no PROBE-RESULTS.json from that invocation; completed in-memory observations
were not published and are not credited. Exact interruption site was not traced.
Source order and later individually bounded runs can support a likely site, not
an attested initial stack trace. Original probes.py and its frozen inputs remain
unchanged. Terminal tool timeout is actual enforcement; original coordinator
probe function had no per-probe deadline. UTC completion was not captured in the
original attempted result, and no timestamp is reconstructed as measured.

The successor probe_process.py isolates each already frozen construction in a
10-second direct subprocess, cooperatively within a 900-second probe session.
This is a new execution-method version, not a repaired candidate or a first-attempt
success. Validator work is outside VM runtime work limits; even invalid large
plans can be expensive to validate. No VM change is authorized or performed.
