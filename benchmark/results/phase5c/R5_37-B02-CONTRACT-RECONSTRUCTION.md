# R5.37 authoritative frozen B02 reconstruction

Reconstructed from the actual `benchmark/requirements/B02.md`, `B01.md`,
`benchmark/baseline.md`, `harness/regression.py`, `profiles/B02.json` and
`capabilities/B02.json`, after the implementation lock and before generation.
R5.23 is comparison evidence, not the source of this reconstruction.

## Types and boundary conventions

**Task T4** has exactly eight public fields: `id:string`, `title:string`,
`description:string`, `status:{pending,completed}`,
`priority:{LOW,NORMAL,HIGH,CRITICAL}`, `created_at:UTC instant`,
`due_date:nullable<UTC instant>`, `tags:sequence<string>`.
Strings in storage are not automatically nonblank: `id` and `title` have
additional validity obligations. IDs are unique across the population.
Timestamp public representations end in `Z`. Description is verbatim.

**S4** is `{schema_version:4, records:sequence<T4>}`. **S1** is a bare legacy
sequence with optional priority/due/tags; **S2/S3** are versioned legacy
envelopes. Present older fields are preserved; missing fields receive the
profile defaults. The legacy-permissive row type is not a substitute for
current-state validity. **M** is physical missing storage, with effective
empty S4 and lazy materialization only on generated writes.

All invocations use public argv only, actual cwd, and `tasks.json` in that cwd.
Public success is one bare JSON value on stdout, empty stderr, exit 0.
Public expected failure is empty stdout, stderr `{"error":"CODE"}`, exit 1.
Boundary validation precedes typed semantic invocation for malformed public
inputs or unreadable state. It must preserve durable bytes/absence.

## Clause-by-clause obligations

In the following table, `preserve` means physical bytes unchanged, including
absence; `write S4` means durable post-state equals the semantic post-state.
Each row supplies raw input, typed input, pre/post, relation, outcome,
persistence, public encoding, failure, evolution and ordering obligations.
`REPRESENTED` concerns existing abstract constructs and established boundary
concepts; it does **not** certify current compiler coverage of the composition.

| ID / origin | Public operation; raw → typed input | Pre → post; semantic relations and outcome | Persistence / public encoding / failure / evolution / ordering | Adequacy |
| --- | --- | --- | --- | --- |
| C01 baseline 3–7 | all; argv/cwd/env → checked route/input | source-authoritative operation; state from cwd | cross-process `tasks.json`; checked launch, no research argv; boundary failures no write; version binding explicit | REPRESENTED |
| C02 baseline 7 | list; no flags → empty input | M effective empty S4 → same; selection/order returns [] | preserve absence; stdout [] / exit 0; no migration or initialization write | REPRESENTED |
| C03 baseline 9–11 + B02 6 | all task-valued results; typed T4 | result/persisted records carry exactly eight fields | bare record/array; tags always array; UTC Z encoding; state validity rejects wrong shapes; evolution supplies missing fields | REPRESENTED |
| C04 baseline 13–17 | create `--title T --description D` → required strings | S4/M → S4; trim/nonblank title guard; description copied verbatim | blank title `invalid_title`, preserve; success does not trim description; no silent migration | REPRESENTED |
| C05 baseline 14 | create → external fresh identity and UTC clock | constructed record with pending status and cached externals; exact framed insertion | write S4; same ID/time in returned and durable record; unique nonblank ID; clock is actual checked provider | REPRESENTED |
| C06 baseline 13,16 + B01 | create optional `--priority` → optional string/domain | fallback NORMAL; LOW/NORMAL/HIGH/CRITICAL accepted | write accepted priority; invalid priority has established public rejection but exact code not stated by frozen prose; existing values preserved | REPRESENTED |
| C07 baseline 15–17 | create optional `--due-date` → optional UTC instant; absence ≠ malformed | omission → null; supplied valid UTC instant retained | malformed/non-UTC `invalid_due_date` pre-semantic binding failure, preserve; null remains a persisted/public value | REPRESENTED |
| C08 B02 3–4 | create zero/many `--tag VALUE` → optional sequence<string>, encounter order | for_each(nonblank(trim)); map(trim) | blank/empty VALUE `invalid_tag`, no new task, preserve; omission → [] | REPRESENTED |
| C09 B02 5 | create tags sequence | stable_unique after map(trim), case-sensitive, first occurrence | returned and stored arrays identical; no sorting/case folding; arbitrary finite population | REPRESENTED |
| C10 B02 6 | create omitted tags → absent input key | fallback []; exact constructed-record insertion | write tags:[]; no extra public field; no omitted-vs-empty confusion | REPRESENTED |
| C11 baseline 18 | list; empty input | S4 → S4; all records including completed | preserve; bare array; order(created_at,id) ascending; legacy path C19 | REPRESENTED |
| C12 baseline 19 + B01 4–5 | list-high; empty input | S4 → S4; exact priority=HIGH selection | preserve; bare ordered array; completed HIGH included, CRITICAL excluded; legacy path C19 | REPRESENTED |
| C13 baseline 20–21 | list-overdue; empty input + external UTC now | S4 → S4; pending AND due≠null AND before(due,now), then order | preserve; exact ordered array; null/completed/equal-time excluded; nullable refinement is required, not optional membership | REPRESENTED |
| C14 baseline 22–24 | complete `--id ID` → required string | S4 → S4; selected pending row status replacement; post sole projection | write only matched status; return full updated T4 including tags; remaining records framed/preserved | REPRESENTED |
| C15 baseline 23–24 | complete missing/already completed ID | S4 → S4; cardinality/selection tagged failure | task_not_found / invalid_transition; preserve exact bytes; stderr error / exit 1 | REPRESENTED |
| C16 baseline 25–26 | delete `--id ID` → required string | S4 → S4; keyed removal, pre sole projection | return full removed T4 (either status); write only removal; other rows unchanged; missing ID C17 | REPRESENTED |
| C17 baseline 26 | delete absent ID | S4 → S4; zero selected cardinality failure | task_not_found; preserve; error stderr / exit 1 | REPRESENTED |
| C18 baseline 27–32 + B01 + B02/profile | migrate; empty typed input | S1/S2/S3 → S4; overlapping keyed default_missing(priority=NORMAL,due=null,tags=[]); version=4; migrated=cardinality(all legacy rows) | write explicit cross-shape/post codec; preserve present fields; do not count changed fields; bare {migrated:N}; ordering unchanged in persistence, ordered later reads | REPRESENTED |
| C19 baseline 30–32 | list/list-high/list-overdue on S1/S2/S3 | legacy state → same; migration_required failure | preserve exact bytes; no implicit defaults/write on read; checked dispatch must reach legacy alternative | REPRESENTED |
| C20 baseline 29–30 | migrate on S4/M | current/effective empty S4 → same; literal migrated 0 | preserve including absence; stdout {migrated:0}; migration repeat idempotent | REPRESENTED |
| C21 B01 5–6 | migrate preexisting LOW/NORMAL/HIGH/CRITICAL | legacy → S4; keyed default only when absent | priorities preserved; due/tag defaults independent; count entire converted population | REPRESENTED |
| C22 B02 6 | migrate missing tags | legacy → S4; keyed default tags=[] | every later task result carries tags; no deletion of existing fields | REPRESENTED |
| C23 baseline 34–36 | reads of malformed JSON / invalid state; no typed invocation for failed codec | physical invalid state → identical physical state | invalid_state; malformed shape, duplicate IDs, blank IDs/titles, invalid status/priority/timestamps; structural type checking alone insufficient | REPRESENTED (abstract validity + boundary), current coverage unestablished |
| C24 baseline 35–36 | every failed operation | physical pre → same bytes/absence | no durable mutation, separately check transport/binding/typed failure; do not invent a semantic outcome for a binding rejection | REPRESENTED |
| U01 request silence | multiply invalid create args | no precedence specified | authoring may choose an ordering; it is not a frozen requirement | BENCHMARK_UNDERSPECIFIED |
| U02 request silence | whitespace taxonomy / malformed persisted tags | trim is specified, further taxonomy is not | do not infer additional codes, normalize old present tags, or claim oracle proves unspecified cases | BENCHMARK_UNDERSPECIFIED |
| U03 B01 “above HIGH” | priority rank | accepted CRITICAL plus exact HIGH filter; no public rank comparator | do not invent a priority-sort requirement | BENCHMARK_UNDERSPECIFIED |
| U04 baseline/profile | unsupported envelope versions, migration errors, writes against legacy | not fully specified by applicable artifacts | preserve known explicit migration/read requirements; do not invent arbitrary-version successful migration | BENCHMARK_UNDERSPECIFIED |

## Frozen profile and isolation

The applicable complete original profile is `regression.py --app APP
--achieved B01,B02`: seven methods, no B03 module. `profiles/B02.json` sets
schema version 4, exact eight fields and migration defaults. Each independent
method creates disposable working directories; `upgraded` intentionally shares
a read → migrate → list → migrate sequence. Multi-input lifecycle sequences
also intentionally share one store. Subtests retain their original isolation.
If candidate generation fails, all seven methods are BLOCKED, not SKIP/PASS.

## Comparison with R5.23 reconstruction

The frozen requirements have not changed. Comparison classifications:

| Item | Classification | Explanation |
| --- | --- | --- |
| tag normalization, omission, case sensitivity, exact HIGH, ordered reads, lifecycle, migration defaults/count, public envelope | NONE | Same authoritative obligations. |
| nullable due-date guard | NONE | R5.23 §6 explicitly identified required-nullable `before` rejection, separately from optional presence. |
| R5.23 “complete source” label | OTHER | Its concrete command tree omitted malformed-input/invalid-state obligations, used one legacy envelope, and had no bare-list public dispatch; adequacy table acknowledged these separately. R5.37 does not promote a typed operation-family attempt to a complete executable source. |
| invalid_due_date as typed semantic branch | PREVIOUSLY_OVERINTERPRETED_REQUIREMENT | Public error/no-write is required; frozen prose does not require malformed data to enter a typed semantic operation. R5.32's boundary distinction is legitimate. |
| priority “above HIGH”; invalid input precedence; unspecified state/version edges | BENCHMARK_AMBIGUITY | No extra comparator, precedence or arbitrary-version policy can be inferred. |
| new mandatory frozen requirement missed in R5.23 | NONE | No new requirement found; the decisive nullable composition was already described. |

## Adequacy gate before execution

Existing 30 abstract candidates plus type/binding/evolution metadata suffice
to state this contract; no genuine new semantic primitive is identified.
This is a representation claim, not a claim all nodes are admitted by the
locked current grammar. Nullable elimination, public version-alternative
dispatch and durable content validity must not be supplied by hand-authored
task Python. If whole-program checking rejects the faithful nullable source,
collect the diagnostic and stop. Do not substitute an absent field/sentinel
for frozen `due_date:null`, modify the analyzer, or generate reduced slices.
