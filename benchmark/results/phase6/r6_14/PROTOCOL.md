# R6.14 finite-relation construction — protocol 1

Owner authorization: bounded R6.14 construction on unchanged R6.10 VM. Provider-neutral
Python standard library; no provider calls, delegation, VM/production edits or external
task acceptance. Same-agent implementation-aware research, not independent qualification.

## Frozen acceptance definitions (before construction)

- XOR8: exact integers a,b in [0,255], result bitwise XOR in [0,255]. All 65,536 pairs.
- ADDMOD8: same input domain, result (a+b) modulo 256. All 65,536 pairs.
- PARITY8: exact integer a in [0,255], result number of set bits modulo 2. All 256 inputs.
- Host oracle may use Python bitwise/arithmetic operations, but VM execution may only
  consume ordinary plan data. Builders may enumerate finite tables; no runtime callbacks.
- Native VM interface consumes bytes, not arbitrary Python integers. A transparent
  boundary adapter checks arity then exact integer type then range, returning MISSING,
  TYPE or RANGE with argument index, before bytes serialization. It performs no relation
  computation, bit decomposition or lookup. Test both adapter and native VM, distinguish
  boundary rejection from VM semantic rejection. Raw shortage => TRUNCATED; trailing =>
  TRAILING. Native non-bytes => INPUT_TYPE.
- Invalid arguments: missing each argument, extras; -1,-256,256,65535; True,False,
  1.0,"1",None,[],{} in each position, plus both invalid for precedence. Deterministic
  rejection with no published prefix. Successful exact integer value and exact bytes.
- Malformed plans: unknown opcode, duplicate node ID, undeclared ref, cyclic rule,
  overlapping prefixes, over64 nodes, over16 depth, over2048 expression visits.
- Exhaust every work cutoff below successful work for (0,0),(255,255),(85,170) and
  parity 0,255,85; expect WORK_LIMIT and exact work=cutoff. Also input/output/depth
  exhaustion and invalid limit vector. Three repeats of negative/resource results.

## Fixed attempt and execution budget

At most six attempts: historical naive XOR8 lookup comparison; byte-bit projection +
selection-cardinality XOR8; ADDMOD8 checked addition/conditional subtraction; PARITY8
Boolean equality fold; oversized expression-chain negative; oversized structural-chain
negative. Preserve all plans/errors/timeouts. No adaptive replacement attempts or budget
expansion. Construction deadline 600 seconds from builder start, each construction
subprocess capped at 120 seconds. Historical baseline verification precedes this budget.

Measurement session: 900 seconds total child dispatch deadline, maximum 180 seconds per
child except naive lookup validation 10 seconds. Direct subprocess timeout kills/waits
child; no descendants created. Coordinator dispatch deadline is cooperative, not hard
whole AI-session containment. Record partial progress every 4096 valid pairs and on
cooperative deadline; hard timeout preserves most recent checkpoint. No universal
claim without complete valid-domain execution. No rerun of exhausted acceptance.

## Measurement procedure

Plans are serialized JSON trees: count structural nodes separately from expressions,
prefix bytes and validator traversals. Canonical serialized bytes and published pretty
bytes, structural and expression nesting, rule invocation depth, repeated expressions,
shared rule calls recorded. Count actual validate() walk/expression/prefix-pair visits
using sys.setprofile in a separate run; time validation WITHOUT profiling (5 repeats).
Counters are physical traversal events, not VM runtime work. Do not edit validator.

Exhaustive native runtime uses original Machine/run/plain/provenance after one original
validate, matching execute's nontext valid-byte/default-limit path including encode.
This avoids repeating validation 65,536 times, NOT a new VM or semantic operation.
Cross-check against public execute at deterministic boundary grid {0,1,15,16,127,128,
254,255} (parity all 256); report public API end-to-end time separately. Native exhaustive
pass charges all original runtime events, includes value/provenance/output comparison;
no tracing during timed exhaustive run. Lexicographic inputs, SHA256 digest of inputs,
values, outputs, work. Three full runtime passes per relation for determinism, including
all success envelopes. Record work min/max/sum/histogram and wall time per pass.

Memory: tracemalloc separate 256-case deterministic sample, original public execute;
peak Python traced allocations includes validation/runtime, excludes process RSS and
native allocator. RSS only if platform API available, explicitly label scope. No
asymptotic inference from these finite observations. Record interpreter/OS/CPU/clock,
GC settings, timestamps, script and plan identities. No authoring-token/cost comparison.

Freeze this protocol and baseline hashes before writing builders/plans. Freeze builder,
runner and plans before acceptance. Run 82 VM, 22 compiler, 9 application, 3 baseline,
10 R6.13 scorer regression methods, production validate/safety and git diff --check.
Verify protected/history hashes before and after. Publish classification, limitations,
failed attempts and proposed next experiment; stop pending explicit owner authorization.
