# R6.32 decisions and tradeoffs

- Reuse R6.18 identity/schema/type/expansion/VM checks; never invent a registry opcode.
  Preserve definition revision1 and put versions/supersession in immutable metadata.
- Prefer complete immutable generation snapshots to a mutable head/index plus object
  database. This small bounded implementation trades disk/replay cost for atomic
  no-clobber publication and transparent interruption reconstruction.
- Exact SHA pins are authoritative; deterministic name/signature search is discovery
  only. Multiple matches cannot choose a latest version silently.
- Require explicit selected/retained decisions for every immediate caller. Retain
  transitive pins until a separate immediate-layer update; incomplete migrations reject.
- Generate copied exposed stateful fixtures using unchanged production semantics.
  Edit two existing consumers plus their invariant; installation archives original
  code and preserves the store. Host plumbing does not decide application behavior.
- Measure legacy production impact unchanged, exposing its extension gap. Publish a
  partial lifecycle verdict instead of claiming automatic dependency-complete H2.
- Use fsynced immutable events and retained pending bytes. Recovery branches explicitly;
  missing timings remain unavailable. Process-exit safety is not power-loss/authentication.
- Publish additive current-round guidance to preserve pinned root historical prose.
  Stop after qualification; an exploratory AI workflow pilot needs separate authorization.
