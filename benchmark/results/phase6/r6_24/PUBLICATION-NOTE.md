# Preserved first publication verification failure

The first `publish.py` invocation stopped at line28, scripted requalification
comparison, before producing measurements or a publication manifest/receipt.
Live Python VM envelopes contain bytes; the frozen JSON evidence serializes these
as `{bytes_hex:...}`. The initial comparison removed timings but omitted this
deterministic serialization normalization, causing an AssertionError.

The posthoc publisher now normalizes bytes to the existing saved hex representation.
No frozen tool/runner/task/prompt, raw inference or historical artifact changed.
This comparison repair issues no model/tokenizer requests and does not repair the
native tool-envelope defect. The halted model run remains terminal.

The second invocation passed requalification and produced posthoc measurements,
but stopped at the relative-link check because report links named the not-yet-written
publication manifest and verification receipt. Those two expected outputs are now
checked after they are written; all other links remain checked before publication.
Again, no inference or frozen experimental change occurred.
