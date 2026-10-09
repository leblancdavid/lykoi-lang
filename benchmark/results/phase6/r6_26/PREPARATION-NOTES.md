# R6.26 preparation and neutral compatibility notes

- Initial Git status clean;1,318 inherited protected identities and R6.25
  publication hashes verified before participant exposure.
- Model choice, four synthetic requirements/25 observations, calibration source,
  prompt and exact semantic schemas frozen in PREPARATION-FREEZE.json before the
  one neutral model session. No scored task exposed.
- Neutral MCP initialize and tools/list answered normally at the server boundary.
  OpenCode exposed none of these tools. One model completion explicitly reports
  the requested tools unavailable. No tools/call request exists.
- A model-free resolved-config and MCP status probe reports `lykoi failed` /
  `Failed to get tools`. It shows intended tools and permission rules present.
  Global MCP servers were still connected despite model permissions denying them.
  Their existing names were recorded without credentials. No calls to those
  servers were model-selected; no PixelLab generation occurred.
- The first diagnostic command then raised UnicodeEncodeError while printing its
  already-saved status text to the cp1252 console. Its output files and status are
  retained. This was not participant inference or semantic construction failure.
- A second model-free probe disabled those inherited MCP connections. It again
  exchanged only initialize/tools/list. Requested MCP-specific debug lines were
  not returned; the filtered log list is empty. No precise SDK exception is
  available. Do not invent one or claim a definitive root-cause repair.
- `apply_operation.inputSchema` has root oneOf and no root type; this is a
  candidate SDK shape mismatch. Exact schema identity was preserved. Adding a
  root type/flattening schemas would change the published tool argument schema,
  beyond a tool-call-envelope normalization. No such change attempted.
- Calibration/scored invocation paths were not entered or implemented after the
  prerequisite failed. Their budgets describe the prospective protocol, not an
  actually qualified scored runner. In particular, live correction-turn and
  cumulative-token enforcement remain unqualified.
- No new dependency or service installed. The temporary per-process config uses
  existing OpenCode authentication, and never writes persistent user configuration.
  Current OpenCode sessions need no restart.

Protocol documentation reference, consulted after the failed neutral probe:
[MCP tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools).
The live negotiated protocol was2025-11-25. Documentation alone does not prove
the exact client's failure cause.
