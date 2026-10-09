# Attempt 2 — fixture storage-envelope failure

Registry qualification completed. The first original stateful case returned
`migration_required`, preserving rejected bytes. The runner seeded
`{version:1,records:[...]}` but the unchanged production schema-version-1 storage
accepts a bare record list (or an exact schema_version envelope).
The request, wrong seed, generated original program, expectation and diagnostic
are preserved under `attempt-2/`; remaining functional cases/recovery were not reached.

Attempt 3 corrects only the test seed to the supported bare list. Original and
modified symbolic predicates, expected observable behaviors and production code
remain unchanged. No behavioral candidate was repaired from scored output.
