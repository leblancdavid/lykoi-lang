# Common formal contract and author interface

Standard-library Python 3.10+. Local records.json persistent JSON list, missing file
is empty. Atomic replacement; rejection preserves exact existing bytes or absence.
Every operation reloads/validates the whole store. Record fields exactly id,
created_at, label, phase and the two domain fields below. id is immutable UUID-v4
provider output; created_at immutable UTC provider output; label nonblank but retain
all characters. Creation supplies label and both enum domain fields, phase is the
declared idle literal. Test inputs conform to these creation types except blank label.
Creation duplicate provider identity fails id_collision. Persisted records must have
valid field types/domains, nonblank label, unique IDs and the behavioral invariant.
Invalid persisted state fails invalid_state, even for list; no repair is authorized.
List whole records by created_at then id. No migrations, concurrency or distributed IO.

Each lookup operation takes id. Missing identity fails not_found before guards.
All guards evaluate original state; ordered error precedence as specified.
set_gate takes value, writes the domain gate verbatim; absent/out-of-domain value
fails invalid_input after its guard. Reject gate_locked if active AND supplied
value equals blocked, even if already blocked. Other changes preserve all fields.
Do not change category or label after creation. All other writes preserve identity,
timestamp, label and category. No implicit default, override or history repair.

A: write application.py exposing handle(op, args, providers) -> {"ok": record/list}
or {"error": code}. providers maps uuid_v4 and utc_clock to callables; no external
dependencies. B/C: write intent.json conforming to intent.schema.json; both use the
same fields/create/operations/invariants grammar. create/list implicit commands,
lookup id implicit, ordered guards, simultaneous exact writes. Nonblank creation
fields are also persisted invariants. All supplied mutation inputs required.
Use typed operands with exact declared domains. No arbitrary Python expressions.
Generators are shared infrastructure; authors cannot edit them. Errors as above.
Return authored path and effort: tool/model availability, repairs, timestamps,
self-tests and unsupported behavior. Do not read acceptance, sealed changes, other
track sources or old scored application implementations. Shared access is cooperative.
300 seconds, <=12 tool calls, <=2 self-test batches <=30s, first candidate plus
one repair. Save first candidate before self-testing; final candidate separate.
