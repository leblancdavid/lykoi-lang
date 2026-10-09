# R6.27 preparation observations

The first synthetic session (`SYNTHETIC-LIVE`) completed with no calls and asked
for the tool list. Session export established that the delivered user message
contained only the first line of the requested multiline prompt, surrounded by
quotes. Python's `shutil.which('opencode')` resolves the Windows command shim;
multiline argument delivery through that route was not intact. This is a separate
CLI prompt-delivery defect, not evidence of model/schema rejection. The requested
prompt, MCP list, events and original pre-inference freeze are retained.

Prospective correction: invoke the installed `opencode-ai/bin/opencode.exe`
directly and verify exported user text matches the request. Save only user text,
session identity and binary identity from export; do not publish opaque encrypted
reasoning data. A second pre-inference freeze records the corrected harness.
No scored prompt or construction state was involved.

The corrected synthetic session completes ten positive calls and one intentionally
malformed call, with intact prompt delivery. The first exact-Lykoi session
(`EXACT-LIVE`) refuses invocation because original tool descriptions describe
semantic effects whereas the neutral instructions prohibit program construction.
No calls occur; this is a prompt/description conflict, not discovery failure.
Preserve that refusal. A separately frozen neutral clarification explains that
the sandbox retains those descriptions as fixtures but never dispatches semantics.
The bridge and published schemas remain unchanged for `EXACT-LIVE-2`.

The direct-executable exported prompt still has Windows argv quoting/backslash
artifacts, despite retaining every line and producing all requested synthetic
calls. Its exact `matches_requested` flag is false. The gate before the second
exact session detects this and halts locally (no inference for that invocation).
The claim of intact *byte-exact* prompt delivery above is superseded by this
check. Correct prospectively by supplying UTF-8 prompt on standard input with no
positional message. Preserve all previous delivery records and freezes; freeze4
records stdin routing. Repeat synthetic qualification with byte-exact delivery
before the second exact session. This is neutral infrastructure repair only.

`EXACT-LIVE-2` has byte-exact stdin delivery but repeats the effect-description
refusal. Preserve both exact-description attempts. The final prospective neutral
mode prepends an honest inert-endpoint qualification to each published description,
retaining the full original description after that prefix. Names, order, schemas,
normalization and original validation are identical. This is exposure metadata,
not semantic arguments or a change to the frozen definitions. Freeze5 records it;
no further prompt attempts after this final qualification session.
