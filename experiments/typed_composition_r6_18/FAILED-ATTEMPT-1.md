# Preserved first test attempt

Command: `python -m unittest discover -s experiments/typed_composition_r6_18 -p test_composition.py -v`

Eight test methods ran in0.038 seconds; four assertions failed in the mutation
sweep. All named adversarial controls, nested reuse/twin identity, scalar failure,
serialization, Boolean/Unit and mutation isolation tests passed.

Original sweep asserted `self.assertEqual(diagnose(p)['status'], 'reject')` for
every replacement, including exact no-op replacements. Three inputs were correctly
valid: `program.params=[]`, `definitions[0].dependencies={}` and
`program.steps[0].deps=[]`. Each replacement was identical to its original field.
The three assertion errors were `'valid' != 'reject'`. Final sweep assertion was
`self.assertEqual(count, 174)` but actual count was156 (26 fields x6 candidates).

Correction: test expectation recognizes exact same-type no-op replacement;
denominator corrected to156. The validator/expander was unchanged. No failed
behavioral execution was hidden or reclassified. This is a test-construction
failure, not evidence that the wrapper admitted an invalid symbolic payload.
