# Pre-author infrastructure correction

The first infrastructure test could not import the syntax checker: original
intent.schema.json omitted one closing brace in the AND/OR expression branch.
Original bytes and TASK-FREEZE remain immutable. intent-2.schema.json is the
prospective corrected schema, with identical intended syntax and one title note.
The checker uses that version. Both B and C authors receive the same correction;
COMMON.md's schema reference is resolved to intent-2.schema.json by their prompt.
No application authoring or acceptance had begun. No scored failure was repaired.
The infrastructure freeze will bind this amendment and the tested generators
before author dispatch. Setup failure is reported, not counted as an AI task repair.
