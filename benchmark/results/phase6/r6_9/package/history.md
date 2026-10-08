## Historical authority

Select `historical_state_profile: historical-related-state-1` with the existing
typed mutable/reference profiles. The closed typed FRC facet
`historical_state_semantics` declares `steps`, `invalid: invalid_state`,
`rejection: unchanged`, `preservation: unrelated_fields`. Every step has integer
`from`, `to = from + 1`, and nonempty `entities`. Each entity declaration has
`entity`, nonempty `add_fields`, and `computations` (null or the existing bounded
typed graph). Each added field declares `field` and an exact typed `source`:

* `literal`: independently source-authorized historical value;
* `before`: named existing field in that entity's transition-before record;
* `computed`: named result of the existing checked graph.

Related identities are immutable. One field has one introduction boundary; fields
cannot be rewritten, removed, renamed or assigned from a creation default. Current
schema types determine exact nominal reference targets, ordered collection duplicate
policy, enum domains and nullable signed-64 domains. Nonnull computed values may
populate the identical nullable target domain under inherited directional widening.
Nullable literals preserve null; no historical zero, owner or role is invented.

Creation roles/defaults, current persisted roles, absent historical roles, explicit
migration roles and roles derived from historical fields are separate authority.
A declared old role observation can be copied; an explicit historical literal can
be introduced. Neither rule derives from a new-user default. Missing source
authority is a reconciliation clarification halt. Missing required historical data
in an authorized contract is a declared invalid-state rejection, not clarification
silently answered by software. Synthetic normative typed sources are development
authority only and cannot resolve disputed benchmark sources.

## Version transitions, snapshots and rejection

The existing one-store schema version covers primary and related collections.
Related-only transitions compose explicit empty-primary additive steps; existing
primary scalar/collection/integer introductions remain in their original migration
chain. Every transition up to the declared current version must exist. Related
introductions may share a boundary with primary introductions. At a given version,
the historical schema is the current schema minus fields explicitly introduced at
that boundary or later. Identity types and collection names do not change.

Every historical record must have exactly its version's declared fields, valid
typed values, unique nonblank identity and all existing required references. Unknown
fields, wrong types, missing old observations and duplicate identities reject
`invalid_state`; violated required references retain their declared existence error.
Graphs use only the coherent transition-before store and record, never a previously
partially migrated row, proposed new field, ambient actor, clock or creation default.
They retain the 16-node operator/dependency/type/error restrictions, including checked
overflow and explicit nullable refinement. Later transitions see the completed prior
transition. No unrestricted expressions or host-language migration callback.

The complete version chain is assembled privately. Every stage is typed and checks
existing references; current constants, primary invariants and reference integrity
are validated before one existing atomic store replacement. Failure at any stage,
including replacement failure, leaves original bytes intact. Existing field values,
record identities, sequence order and unrelated entities remain unchanged; JSON
serialization bytes may change on successful migration. Current-version migration
validates and returns zero without replacing bytes. Reload/restart checks the same
current schema. `migrated` counts records across the store on a version change;
zero means no replacement. Empty absent storage retains the existing no-op behavior.

This additive profile accepts explicitly stored related collections. It does not
infer absent old collection contents or convert legacy reference `missing_or_empty`
repair into additive authority. Selecting both refuses structurally; the preserved
legacy reference profile remains available separately. No backfill rewrites,
arbitrary schema conversion or enum-domain evolution is newly authorized here.


The existing prewrite authorization profile remains unchanged. A trusted actor is
asserted by an authorized controlled embedding, not authenticated by Lykoi. Ordinary
CLI actor flags are selectors and cannot establish this context. An authenticated
principal and a principal-to-actor mapping need separately supplied external
authority; no authentication system is introduced.


This is the existing trusted-local compiler/host boundary, not hostile-code OS
containment, cryptographic identity, general authentication or distributed state.
