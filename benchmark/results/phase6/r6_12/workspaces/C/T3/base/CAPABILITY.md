# T3 BASE — static capability assessment

Outcome: CAPABILITY_GAP / XOR_AND_PAYLOAD_REORDER_UNAVAILABLE.
No candidate or acceptance execution. This is not an observed runtime rejection.

Required obligations: contract 2 checks XOR(tag,length,payload) for every original
record before trailing/transform checks; contract 3 reverses tag-1 payloads and
sorts tag-2 payloads preserving multiplicity; contract 4 recomputes XOR and totals.

Frozen evidence: CONTRACT-1.md 43–60, 64–83; interpreter.py EXPRS/CODECS 55–59,
expr 266–316, codecs 318–384, map/select 489–513, emit 524–532.
There is no XOR/bit extraction codec or expression, byte-index expression,
reverse/sort node, list permutation/concatenation, or accumulated reduction.
`bytes_check` validates membership only; `bytes` codec copies exact bytes;
uint8/uint16be perform only fixed unsigned conversion. `each` emits original order.

Bounded subsets considered: 90-byte input and eight records fit limits. Fixed atoms,
checked dynamic take, count-repeat, end and ordered checks can describe much of
the binary validation skeleton. Pruning can use select on nonempty payloads with
equality to false; retained count can use length. This task is not blocked merely
by binary input or small payloads. Reversal could theoretically unroll lengths
0–8 with separate byte bindings and reverse emits, and sorting could theoretically
use a finite comparator network. XOR is also mathematically a finite table; its
absence is not an irreducibility proof. But the frozen API cannot parameterize
rules to reuse such transformations, index dynamic byte/list values, or fold their
results. Exhaustive XOR operand pairs require 65536 relations before multi-byte
composition; bit-decomposition/comparator-network alternatives need explicit
branch/update/construction stages alongside the parser within the 64-node and
2048-expression plan bounds. No complete within-bound composition was identified.
Transport XOR, reversal, sorting, or payload summation would solve central behavior
and is prohibited; hex byte conversion alone is permitted. No partial success is
scored and no acceptance-specific table or Python fallback is authored.
