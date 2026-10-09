# Pre-exposure preparation observations

The first `runner.py qualify` command halted at Python import before creating a
qualification freeze or dispatching inference. Importing the new preflight by its
generic module name caused a circular import of its historical helper. The runner
now loads it under a unique module name. The already frozen preflight bytes remain
unchanged. No model response or semantic decision was repaired.

The first `prepare.py` invocation halted at parse time on an unmatched closing
parenthesis. No controls, task freeze or inference ran. That syntax was corrected
before preparation execution and participant exposure.

The next preparation command halted at import: historical helper loading put
R6.36 ahead of R6.37 in Python's module path. The live MCP child had correctly
executed the explicit R6.37 `tools.py` path, as its exchange log demonstrates,
but the coordinator's `QUALIFICATION-FREEZE.json.tools` accidentally recorded
R6.36 schemas. That original freeze and runner are preserved. A uniquely named
`transport.py` loads the correct local tools for all subsequent preparation,
oracle and task freeze records. `QUALIFICATION-CONTROLS.json` verifies the actual
live schema names and backend effects, separately from that metadata defect.
No additional qualification model request or task exposure occurred.
