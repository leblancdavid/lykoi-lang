# R6.11 exploratory comparative development pilot — protocol 1

## Authority and question

The owner's R6.11 request authorizes this bounded pilot and publication, with no
language improvement. Question: on identical contracts, how do acceptance,
authoring reliability and development effort compare? This prospective protocol
does not amend any historical protocol or invoke its approval/controller gates.

## Selection and scope

Four standalone synthetic requirements are specified in TASKS.md before authoring:
pair aggregation, bounded sample validation, ordered ticket selection, configuration
interpretation. Two separately frozen extensions test incremental maintenance.
No CFG66, DSV66, BXC66 or curated external task is scored. No P6-A04 acceptance
or P6-A05 access. No exact tailored implementation of these task contracts is known;
generic operation examples and historical research are already exposed.

Selection is by the same session with knowledge of both capability inventories.
These are independently specified *standalone tasks*, not independently sourced
requirements. Capability-aware selection and small synthetic domains bias this
pilot. Independent sourcing in the stronger experimental sense is unmet.
Byte inputs exercise recognition unavailable in the production normal profiles;
the Lykoi track must use the explicitly labeled R6.10 experimental VM for all four.
Production suitability is a static profile assessment, not a scored failed attempt.
This pilot cannot answer the production-toolchain efficiency question.

## Freeze and shared inputs

Before implementation, freeze SHA-256 identities for this protocol, TASKS.md,
ACCEPTANCE.json, run.py and transport.py, plus four shared FRC envelopes generated
from task sections by the existing FormalRequirementContract-0.1 validator.
Envelope validation is bookkeeping, not fidelity review, coverage or approval.
Both tracks receive identical task sections and acceptance access, common transport,
and task-relevant language documentation. Modification requirements and tests are
frozen now, released after each base pair passes. Their content is already visible
to this session; anticipation cannot be excluded. No post-result oracle edits.

## Tracks, budgets and chronology

Model: session-reported OpenAI openai/gpt-6.1-sol (model gpt-6.1-sol).
Reasoning configuration is inherited and not exposed; same session throughout.
Conventional Python uses standard library. Experimental authoring produces explicit
semantic-plan-1 JSON, with no Python behavior callbacks. transport.py only converts
hex/bytes and projects declared observations from either result; it does not solve
task behavior. VM is pinned and not edited. No mandatory provider dependency.

Order: T1 conventional first, T2 experimental first, T3 conventional first,
T4 experimental first; modification T2 conventional first, T4 experimental first.
Each task/track has a clean distinct directory and start record before authoring.
Cap: 15 minutes wall time per task/track/stage, one initial candidate and at most
two repairs, one full acceptance opportunity per attempt, process timeout 10s.
Pass ends authoring; otherwise repair or stop at cap. Equal nominal token ceiling
8,000 per track/stage is **not enforceable or measurable by the available harness**.
Actual tokens/API cost remain null, not estimated from characters or code size.
Reported elapsed time is start-record to evaluation completion, including tool
latency and interleaved session overhead, not pure model thinking or CPU time.

Artifacts, starts, commands, outcomes, hashes, first attempts and every repair are
retained. Development-step ledger supplements these records. The harness's full
internal reasoning/token stream and complete external transcript cannot be exported;
repository evidence is an artifact/command record, not complete interaction telemetry.

## Separation and interpretation

Directories and subprocesses do not enforce cognitive, filesystem or provider
context separation. The common author context necessarily remembers both tracks;
the second author can be contaminated even without opening the other file.
No track is instructed to read the other implementation. Both see acceptance
expectations because this is same-agent exploratory evidence. R6.9's fail-closed
review dispatcher is not called or bypassed. No independence claim is made.

Mandatory classification for executed runs in this environment:
R6_11_EXPLORATORY_COMPARISON_ONLY. If execution cannot finish, report partial/halt
instead, with downstream NOT_REACHED. No statistical superiority, production success,
minimum-kernel or generality claim follows from this small pilot.

## Observations and taxonomy

Acceptance compares full ordered JSON values or exact error code/byte offset;
VM provenance/work/node/stage are supplementary diagnostics, not scored outputs.
Modification acceptance is original suite plus new cases. Report base and new-case
denominators, regression failures, repairs and first-attempt success separately.
Record language/profile capability limitations, AI authoring mistakes, interpreter/
compiler failures, infrastructure/tooling failures and ambiguities as separate axes.
Correctness takes precedence over time or tokens. Maintenance is observed only as
bounded extension/regression behavior, not general long-term maintainability.

## Preservation and stop

Pin current production src/schema/air/generated/tools, historical R6.3–R6.10,
experimental VM, Phase 5 harness/evaluation/conventional files and kernel accounting.
Never read curated source trees for inventory. Verify frozen historical publication
hashes, fresh production validation/safety, VM regression checks, acceptance replay,
publication file hashes and git diff --check. Publication manifest excludes itself.
Stop after reporting. Further benchmark expansion or semantic work needs owner approval.
