# Contract-to-runtime mapping

| Authoritative obligation | Successor mechanism | Verification |
|---|---|---|
| JSON list, version1, no migrations | Explicit closed declaration in `profile.json`; installer checks selected existing state's actual integer version and absence of model migrations | Six adapter methods; K01/K08/K09/K10/K12 |
| Invalid persisted state → invalid_state | Catch only Failure from original decode_state; translate only its migration_required; independently reject original non-list payload even when decoder accepts it | K01/K08/K09/K10/K12 |
| Required fields/types/domains/uniqueness/invariant | Valid lists return through original decoder and unchanged read_state/valid_state; no record interpretation in adapter | K02/K03/K07/K11;188 retained observations |
| Existing error precedence | Same JSON parse/read and decode boundary before existing whole-store validation, lookup, guards and input checks | K14–K18;188 retained observations |
| Rejection and list preserve exact bytes/absence | Adapter has no IO or mutation; raises before existing write path; unchanged read_state/write_state | Every matrix error/read; K13 absence; all188 regressions |
| Valid old same-schema data | No new schema/default/migration; same unchanged validation and transition | K06 list then cool; K07 rejects invalid invariant |
| Preserve transition/operation semantics | Intent and lowered IR exact; original generated application prefix exact; append integration installer | IMPLEMENTATION.json;188 original accepted projections exact |
| Other persistence profiles and migration semantics | No declaration is exact no-op; installation refuses migrated/version-conflicting models; actual selected state object identity scopes decoding | 36 other-state decoder differential comparisons; existing explicit migration tests; protected production hashes |
| Runtime effect authorization | Adapter never intercepts operation exceptions or host context/effect execution | Decoder-origin-only negative control; six direct authorization/atomic failure controls; compiler authority tests |

The integration targets the exposed `handle(op,args,providers)` interface defined
by COMMON:23–30. The existing per-operation JSON transport imports the application,
then calls that interface after profile installation. Its provider bindings,
command dispatch and mutation engine are unchanged. Generated behavior is built
by the successor generator, never hand-edited. This is an explicitly attached
application integration profile, not automatic adoption by production applications.

Profile selection is not inferred from application/field/operation names, input
values or the mere presence of version1. The state ID is supplied explicitly as a
normal reference, checked against the lowered model; no kiln identifier is embedded
in adapter logic. A matching version1 envelope is rejected regardless of record
validity. A stale/future object can trigger the inherited decoder's version error,
which is mapped only inside this application declaration. `migration_required`
outside decoder execution retains its original meaning and code.

Same-read property: original read_state performs one json.load, calls its global
decode_state binding (now the scoped closure), then unchanged valid_state. The
adapter calls the original decoder once and checks that same parsed payload; it
does not reopen storage, normalize data, supply defaults or choose a migration.
