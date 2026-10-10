# Exact R6.40 combination-failure inventory

Machine-readable authority for this extraction: [FAILURE-INVENTORY.json](FAILURE-INVENTORY.json).
Original records remain in [R6.40](../r6_40/EVALUATION-TASKS.json).

## Coverage and identity

All ACCEPTANCE files for E3-B/C and E4-B/C are inspected, not merely the first
failure sample. All8 final E3/E4 A/B/C/X artifacts are compared by matching ordered
recorded cases/controls. No scorer function or executor is called. Original
`passed` flags are copied, never recalculated. The JSON has original file hashes,
root/plan identities, exact failing rows, 1-based row indices, node operations,
definition/local mapping, caller chains, primitive expression sites and recorded
A/X counterparts. Every preserved submission/package is anchored by the R6.40
publication manifest. E3-C SUBMISSION-001 and002 have the same root; their46
failed observations are repeated occurrences, not92 distinct task failures.

| Recorded submission | Root | Failures |
| --- | --- | ---: |
| E3-B/001 |`80bacae6cbd7285f4698712b4123136df290c33f6c00970776d7ed80bd29f367` |46 |
| E3-C/001 and002 |`1d588d78c8d0e82baa5ebcd1c2e47b7928d7657a2a41974f315fed822ee15863` |46 each |
| E4-B/001 |`18a5eae4668cb12cd6a5368464d9cbff0f5129ec692bcae86855c165ed2d6bce` |88 |
| E4-C/001 |`69f88486aa126f6181d517436f2a492602ee1c873933a78dfa3aaae1e0e4c21f` |88 |

Total314 submission-row occurrences,268 final failed observations. No new
historical score. Replays are not counted again as additional failures.

## Registry definitions involved

| Relation | B exact identity | C exact identity |
| --- | --- | --- |
| interval_fee |`56642b075e7d74325b134c01ca848c275e1e91745db7332412fe1aebbcb5af1a` |`cb2f1d3c16e5e8a960cb08d0d3921773f1739b41c31f2e14efe24c3b4d313b9c` |
| pair_envelope |`e229be30d3421988a4384d83b710e771afe84103fcc96e0c4514f9f0d876b3aa` |`6a1e9b08f0a487c2f9e92a8f9b10efb105e51fc447bf04d06f01eed5ee4058a5` |
| echo_charge |`d4278dd3d17c3dfab22892eb5325f11ca3574dffe3c9613cff2f10d3f4eb07d5` |`330bfb7385b5d3a422f1a26a29fe1f2704c9bd6fbbce6121ab913583fad6b0be` |

E3 C calls u/interval_fee, v/interval_fee, sum/pair_envelope in that order;
B calls u/ProxyInterval, v/ProxyInterval, sum/ProxyPair. E4 C calls t/echo_charge
then total/interval_fee; B calls t/ProxyEcho then out/ProxyInterval.
All library definitions have primitive bodies; these are successive composed
regions, not a pair definition internally calling interval or an interval
definition internally calling echo. The failure node path and the argument's
producer path must not be conflated.

## Boundary trace

The existing VM's [seq branch](../../../../experiments/semantic_interpreter/interpreter.py)
(lines443–455,544–546) copies the environment, runs steps, evaluates result, then
wraps its value with sequence start/end. [R6.18 expansion](../../../../experiments/typed_composition_r6_18/composition.py)
(lines366–399) emits a seq per region and substitutes immutable argument refs;
there is no eager argument materialization or transparent compose opcode.
`check` (VM484–486) fails at the declared site's Cell start. The span change occurs
on successful return, not while the callee's original argument checks run.

E3: x[0,1),y[1,2) → end → u region[2,2),v region[2,2) →
pair check at v → offset2. The oracle uses v's arithmetic input y → offset1.
E4: x[0,1),y[1,2) → end → t region[2,2) →
interval check at t → offset2. The flat expression's leftmost operand x supplies
offset0. A failing check does not return a result Cell or partial output.

## Observations and discrepancies

E3 failures:46 selected inputs with x/y passing intervals and x+y+8>245;
TOTAL_HIGH only, expected1/actual2. E4 failures: x77,y0..58 low and y161..189
high, expected0/actual2. Frozen sampling, not complete two-byte-domain proof.
All failed rows' code/stage/status agree with A/X. Successful values/bytes/root
provenance agree over the recorded suite. Raw runtime nodes and output-spans'
node IDs are representation-specific. No new dynamic execution-order trace exists;
static step order and matching first-error observations support bounded precedence.

| Final artifact | Expanded nodes | Work on E3 TOTAL_HIGH | Work on E4 low / high |
| --- | ---: | ---: | ---: |
| E3 A / B / C / X |14 /15 /19 /16 |47 /48 /54 /49 |— |
| E4 A / B / C / X |11 /11 /13 /11 |— |29/33;30/34;32/36;29/33 |

These work differences are real observed envelope differences, although they
are not additional failed exact-work acceptance predicates. X's supplied flat
templates remove composed seq-return boundaries; X participant artifacts are
new primitive roots, not byte-identical normative expansions of C. Original C
expansions retain the nested seq nodes and exhibit the same offset2 as compact
execution. A source-provenance ablation must hold this structure constant or
explicitly qualify a different contract.

The E3-B invalid initial identity and E4-C self-authored attempted revision are
preserved in R6.40 diagnostics; they are not extra sealed acceptance artifacts.
E4-B's post-seal token-budget stop remains an independent protocol limitation.
Neither is repaired or used to relabel the provenance discrepancies.
