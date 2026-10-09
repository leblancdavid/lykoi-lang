# Pre-freeze qualification correction

First `run.py prepare` invocation wrote schemas and task manifest, then retained
`PREPARATION-FAILURE.json`: importing the short module name `controls` selected
R6.18's controls because the wrapper import prepended its directory to sys.path.
The new runner now loads the R6.23 control module by its exact path and distinct
module name. Neither the wrapper nor its import behavior was modified.

No freeze or model inference had occurred. The schema/task definitions were
unchanged when preparation resumed. Original failure evidence remains preserved.
