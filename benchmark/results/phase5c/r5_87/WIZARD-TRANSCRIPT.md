# Public synthetic requirements wizard

This is the normal-user rendering of the executable deterministic example in
`src/lykoi_workspace/example.py`. Synthetic authenticated human actions occur through
the controller. The separate audit view exposes exact bindings when requested.

**Wizard:** Describe what you want.

**Human:** Create tasks with titles. Allow optional priority. List important tasks.

**Wizard:** What should happen when priority is omitted?

**Human:** Use NORMAL.

**Wizard:** Which priority makes a task important?

**Human:** HIGH.

**Wizard:** A separate source review agrees with this interpretation. Review what
the application will do:

- Create tasks with the supplied title.
- Omitted priority uses NORMAL.
- List all tasks whose priority is HIGH.
- Collection ordering is explicitly unconstrained.

**Wizard:** Your adopted project policy leaves list ordering unconstrained. Approve
these behaviors?

**Human:** Approve.

**Wizard:** This exact requirements version is approved and sealed. Requirements
preparation is complete.

The ordering policy was explicitly adopted for this synthetic project before this
session. It is not a Lykoi-wide default. “Separate source review” here describes the
fresh subprocess fixture; it does not claim independently qualified AI understanding.
The demonstration stops at requirements sealing.
