# Preserved pre-freeze preparation failure

The first `run.py prepare` invocation failed before qualification/freeze/inference:
`AttributeError: module 'controls' has no attribute 'run'`, run.py line106.
R6.23 adapter import prepends the R6.18 directory to sys.path, so a subsequent
short-name controls import selected the historical R6.18 module. Task/schema/prompt
preparation files existed, but no model exposure, qualification or freeze occurred.
The R6.24 runner now loads its controls by exact file path. Historical files are
untouched. This is a host import failure, not a model or tool programming failure.
