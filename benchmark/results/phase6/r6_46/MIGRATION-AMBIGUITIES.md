# Remaining migration boundaries

The kiln contract is determined: list-only storage, no migration, all invalid
persisted state fails invalid_state. No unresolved versioned-app expectation
limits the supported K01–K18 interpretation.

The R6.45 V rows remain outside scored acceptance:

* V01: no distinct authorized legacy kiln schema; old same-schema valid lists are
  current-valid data, not a migration example.
* V02: an actual version2 application's valid version1 store and explicit migration
  require its separately pinned schema/default/version-chain contract. Existing
  production regression tests are preservation controls, not new V02 acceptance.
* V03: malformed recognized old-schema records plus stale version under normal read
  still have unresolved invalid_state versus migration_required precedence.
* V04: unsupported/future envelope plus invalid types still has unresolved envelope
  recognition and public shape/version/type precedence.

Other-state decoder comparisons assert predecessor/successor equality only,
including unresolved-looking inputs; they do not select a new public error
requirement. No general migration_required meaning, migration defaults, historical
role authority or migration-enabled application behavior was changed.

Recommended next architectural step (proposal only): make persistence shape,
recognized version policy, migration permission and decode-error precedence
explicit application integration facts validated against lowered storage, then
carry them through deterministic lowering. Resolve V03/V04 with source authority
before extending that representation to migration-enabled applications. Retain
the existing26 meanings; a new primitive is not justified by this defect.

Further implementation, migration clarification work or experiments require owner
authorization. Stop after this bounded publication.
