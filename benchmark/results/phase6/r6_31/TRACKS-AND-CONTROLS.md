# R6.31 — Track and control definitions

Track labels are scoped to their hypothesis. H1-C is the experimental composition
system; H2-C is the production stateful semantic pipeline. Report them explicitly.

## H1: required six conditions

| ID | Author artifact, vocabulary and execution |
| --- | --- |
| H1-A | Direct standard-library Python; ordinary helper functions may be designed in development and frozen. Common transport/types/error contract, no Lykoi imports. |
| H1-B | Fixed lean structured intent, deterministic ordinary Python generator, schema/name/order checks and conventional checked arithmetic/guards. No Lykoi graph/type/expansion validator. Fixed grammar; inline task expressions allowed. |
| H1-L0 | Fixed primitive-only Lykoi; identical R6.18/R6.23 machinery to L1, no reusable library. Task-local definitions allowed but unavailable to future tasks. |
| H1-L1 | L0 plus AI-discovered, development-admitted, frozen reusable compositions. No vocabulary writes in evaluation. |
| H1-LH | Same machinery/retrieval as L1, human-designed macros using the same development requirements, without seeing AI library or evaluation tasks. |
| H1-LX | Same discovered L1 bodies/applicability documentation, furnished as hygienically expanded templates rather than named compose calls. Fresh independent authors assemble task programs; never copy L1 task solutions. |

All six receive identical behavioral requirements, public examples, selftest
opportunities, budgets and model configuration. Tool/schema documentation differs
only for actual workflow. Transport performs decoding/projection, not task decisions.
Expose those common checks in the attribution ledger: B/A checked arithmetic and
guards can prevent the same failures as C. Fixed intent must not be deliberately
weakened by omitting equivalent checks already in its generator/runtime.

H1-A/L1/LH libraries: at most4 entries,64 total authored body steps (Python helper
AST statement count separately), nesting at most3, and16KiB canonical library+
index+documentation. In an executable compact packet, library plus task-local
definitions must stay within7 authored definitions plus generic HostEntry, and all
inherited package/step/depth/byte/node bounds still apply. A portable library cannot
require otherwise unsupported parameter or call semantics. Equal caps do not imply
equal useful capacity across languages.

LH must match L1's **actual** entry count and total symbolic body-step count, within
10% (or one step, whichever larger), parameter arity/type multiset and maximum
nesting; library exposure token count within10%. Independent human design happens
first under the same caps; a deterministic selection/padding rule, frozen before
development, selects a matching subset from its sealed ranked pool. Padding is
documentation only, never new behavior. If no match exists, retain LH results but
mark capacity matching unavailable; do not claim discovery attribution. If L1 is
empty, LH's matched library is empty and H1 has no discovery-transfer witness.
Report uncapped human pool cost too; no uncharged search for a winning comparator.

LX includes every L1 body, unused entries and equivalent documentation. It may use
the same deterministic type/lexical retrieval with a template response. Fetch
instantiates only caller-specified literal/ref substitutions and hygienic names;
the author decides applicability and order. All expansion/search cost is counted.
If expanded exposure exceeds frozen limits, mark the ablation constrained, not
evidence for AI discovery. A/LH get the same development effort opportunity as L1;
B/L0 may spend it on practice/testing but gain no cross-task adaptive definitions.

## Attribution contrasts

- L1 vs L0: value of extra reusable compositions, not uniquely AI discovery.
- L1 vs LH: AI-selected versus ordinary human-selected macro reuse at matched
  capacity; required for any adaptive attribution.
- L1 vs LX: compact references/retrieval versus the same discovered meaning in
  expanded form; equal outcomes mean semantic selection can still matter, but
  compact syntax itself is not established as necessary.
- L0/LH/L1 vs B: incremental symbolic machinery under comparable requirements.
- All vs A: practical workflow utility, including inherited tooling and new setup.
  A's helpers prevent a comparison against artificially reuse-free Python.

## H2: three main tracks

| ID | Editable authoritative artifact and checks |
| --- | --- |
| H2-A | Existing equivalent Python application; modify source/helpers and state rules. Ordinary syntax, runtime, test and call-graph tools permitted. |
| H2-B | Existing fixed declarative stateful intent; deterministic independent Python generator/runtime through R6.16 pattern. Same grammar as C; existing structural checks/invariant guards preserved. |
| H2-C | Same intent interface lowered to genuine existing production typed mutation/predicate semantics and deterministic Python backend. No task-specific Python implements guards/transitions in the facade. |

C does not receive H1's learned library: H2 tests symbolic modification separately
from discovery. Immutable storage objects may get successor revisions; **in-place**
means the deployed existing operation changes under the same public endpoint and
state identity, not overwriting preserved research bytes. Consumers must point to
the new revision where required. Generated Python is regenerated, never hand-edited.

Record a check matrix with rows for shape, types, references, effects, runtime
invariants, ordering and impact, columns A/B/C, actual implementation identities
and first blocking stage. If B performs an equivalent check, credit it equally.
For suspected C-only benefit, replay the saved defective candidate through all
applicable validators after scores freeze. Optional matched B-check control can
measure an additional generic check only in a separately frozen successor, not an
outcome-informed repair to the primary comparison. Workflow advantage and unique
semantic advantage are different claims.
