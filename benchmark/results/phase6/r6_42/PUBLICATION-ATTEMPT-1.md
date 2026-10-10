# Preserved publication-check attempt 1

Command: `python experiments/provenance_r6_42/publication.py` (after the parent
directory existence check). Exit1, before publishing an implementation index,
publication manifest or receipt.

The checker asserted that each protected-implementation group was nonempty, but
incorrectly searched `experiments/` for the R6.23 adapter and R6.25 contracts.
Those preserved implementation files live under `benchmark/results/phase6/r6_23/`
and `r6_25/`. This is an index-selection error, not a protected-hash mismatch.

Preserved diagnostic:

```text
publication.py line47: index = implementation_index(protected)
publication.py line23: assert all(groups.values())
AssertionError: {'production': 129, 'R6_10_VM': 21, 'R6_18_wrapper': 27,
 'R6_23_adapter': 0, 'R6_25_contracts': 0, 'R6_32_registry': 11,
 'historical_R6_40_acceptance': 49}
```

Only the unfrozen publication checker's path selection was corrected to inventory
the existing protected locations. No candidate, frozen expectation, first result
or semantic implementation changed. Publication verification reruns only hash,
structure and integrity checks; it does not execute plans or rescore acceptance.
