# T4 modification — Absence-conditional replacement

Terminal: `PRODUCTION_BYTE_SLICE_SPLICE_PROFILE_GAP`, static assessment.

Modification clauses 1 and 3 retain every original obligation, including complete
shape validation, all-patch bounds before match decisions, original-coordinate
slices, mismatch-before-conflict precedence, applied-pair conflict ordering,
length-changing assembly and original-index observations. Thus they remove none
of the original production byte-slice/splice/assembly interface blockers recorded
in `../base/CAPABILITY.md` and GAP.json.

The new absent branch applies precisely on old != original slice; equality skips,
including empty old. Applied absent patches consume len(old) original bytes and
insert new bytes without mismatch rejection. The **negation is supported**:
`docs/typed-predicates-v1.md:11–25` defines NOT eq and typed whole-value operands;
`71–84` describes original-record guards and staged observations. Extending an enum
and composing NOT equality would be plausible if the original slice were already
bound by a permitted production operation. The base assessment identifies that
missing dynamic slice binding (`predicate_runtime.py:5–11`, `predicates.py:49–96`),
plus missing runtime span assembly (`mutable_values.py:51–84`,
`references.py:216–242`). Host computation of the slice or replacement is central
behavior. This stage adds no demonstrated irreducible boolean meaning; it retains
the byte binding/assembly gaps and extends their use to a complement condition.
Existing decoded integer endpoints, boolean interval comparisons and row ordering
remain useful subsets, not complete executions of this contract.

All 8 new frozen cases were read after start: absent apply/skip, empty-old skip,
bounds rejection, applied conflict, skipped non-conflict, length-changing assembly
with original-index order, and existing always mismatch precedence. These are
expected observations only. Original 16 and new 8 cases remain `NOT_REACHED`;
zero semantic candidates, compilation/evaluation attempts, repairs or tests.
Regression count/rate is unavailable without a successful base observation and
execution. No host patch algorithm or shape validator was authored. This is a
static current production profile finding, not an observed runtime/compiler
failure, regression, or abstract kernel impossibility claim.

Own base records are preserved. Reads: own base CAPABILITY.md/GAP.json, own base
contract, assigned modification contract/acceptance and current typed-predicates
documentation. Exact UTC boundaries/elapsed are in START.json/GAP.json; session
read and command disclosure is in `../../MODIFICATIONS.md`.
