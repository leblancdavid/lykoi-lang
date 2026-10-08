# R6.4 native execution capability inventory and gaps

Evidence is static inspection of the unchanged repository, bound by file SHA-256 and
line-numbered excerpts in [STATIC-EVIDENCE.json](STATIC-EVIDENCE.json). No projection,
BDI, adequacy, V1, authoring, validation/lowering of a candidate, installation or oracle
stage was invoked. "Demonstrated" below means demonstrated repository/interface facts
or verified identities, not newly demonstrated P6-A04 behavior.

## Existing capabilities and their limits

| Area | Demonstrated existing capability | Boundary for this contract | Evidence |
| --- | --- | --- | --- |
| Research authority | Offline exact-bound receipts, content provenance; local path does not need controller or AI credentials | R6.4 approves investigation only; does not appoint an execution evaluator or permit `execute` | `src/lykoi_research/local.py:24-87,116-187`; authorization/receipt |
| Kernel | Records, fields, finite sequences, literals, predicates, selection, bounded transforms, transitions, typed authority, durable state, atomic commit, finite reachability, checked arithmetic/time | 26 constructs are an accounting vocabulary, not proof of arbitrary parsing or package-management expressiveness | `R5_114-KERNEL-ACCOUNTING.json:4-79` |
| Exact input representation | String-like scalar values and verbatim pipelines can retain an already supplied declaration | Storing the string does not interpret setup.py/requirements, construct dependency metadata or resolve a wheel | `mutable_values.py:45-85,211-231` |
| Pure value processing | Pipelines allow verbatim, trim, stable deduplication with staged validation; records/predicates can compare explicit data | No validated string slicing/tokenization/grammar evaluation, URL-to-artifact interpretation or wheel metadata decoder in this normal profile | Same excerpts; `profiles.py:40-96` |
| Abstract dependency data | Finite records/references/reachability can describe already supplied finite relationships | Does not ingest the approved binary wheel or build metadata, implement package version/tag/name rules or perform dependency installation | Kernel inventory; `profiles.py:135-170` |
| External capabilities | Validator admits JSON-file storage, UUID, UTC clock and read/write authority over declared JSON storage | Typed authority is not an arbitrary executable callback. No binary-file/archive/build/package-install capability is accepted | `validator.py:134-156`; `creation_provider_runtime.py:1-46`; `atomic_state.py:49-60` |
| Durable/atomic effects | Validated records written through JSON serialization and single-file replacement | Installing payload files and dist-info into a venv is not that JSON-state operation. Atomic JSON commit cannot silently become a filesystem installation transaction | `runtime_template.py:120-150` |
| Structural path | Qualified mutable/model/composed/scalar/query profile dispatch; generic fallback retains external-effect channels | Approved relations have no selected qualified package profile. Generic `effects` captures observability, not executable install semantics; generic invariant/transition mapping absent | `contracts.py:15-91`; approved FRC |
| Native lowering | Closed `LykoiProgram-1` profile dispatch or validated legacy generator | No package subject lowering or arbitrary Python/command plugin branch. No faithfully lowered subject identity exists | `profiles.py:40-96,135-170` |
| Plan binding | `external-cli-plan-1` case identities/coverage and bounded JSON fixture checks | Approved plan has `native_plan: null`, no native version/cases/coverage/limitations shape; cannot pass acceptance binding if that stage is reached | `local.py:158-168`; `plans.py:12,54-129`; approved plan |
| External process verification | Fresh case directories, generated target/controlled host, return/stdout/stderr/JSON-state comparisons | Host interpreter `-I -S`, empty env, ten-second timeout; no pinned target venv, absolute fixture root, wheel staging, pip activation or target-site inspection adapter | `pipeline.py:20-107` |
| Fixed observations | Before-state absence, unchanged inputs/wheel hashes; report selection; distribution and installed payload inspection are specified | Observer is prepared, not exercised or calibrated in R6.4. Report metadata is subject-produced evidence, not independently trusted parsing/resolution proof | `r6_3/observe.py:14-54`; `ACCEPTANCE-PROCEDURE.md:44-99` |

## Classified limitations

| ID | Classification | Concrete limitation and consequence | Supporting evidence / confidence |
| --- | --- | --- | --- |
| S1 | Semantic capability gap | Native accepted operations cannot interpret the arbitrary requirement string/setup workflow into package metadata. Verbatim/trim/predicates on provided values cannot stand in for the required parser. | Closed transformation and profile branches above. High confidence in current implementation boundary; no theorem about eventual abstract-kernel expressiveness. |
| S2 | Semantic capability gap | No validated operation/capability for binary artifact reading, ZIP/wheel metadata/payload interpretation, building containing-package metadata, or installing files/distributions into a venv. | Closed capability validator and JSON write implementation. Concrete end-to-end semantic/runtime gap, beyond an acceptance harness omission. |
| S3 | Semantic capability gap | No qualified native package structural/V1/author/lowering path binds the seven approved obligations to executable package behavior. | `contracts.py:15-91`, `profiles.py:40-96`; FRC retains invariant/effects/transition relations without a package profile. Static expectation only; no measured native blocker code/stage. |
| I1 | Execution infrastructure gap | Fixed plan cannot be supplied directly as the native execution payload. A later binding must retain all expectations, source/fixture/observer hashes and traceability, with separate exact approval. | Approved `native_plan: null`; `local.py:158-168`; native plan schema/interface. |
| I2 | Execution infrastructure gap | Verifier cannot stage this binary fixture, execute an identified subject through `pip install --verbose .` in the pinned venv, or invoke an independent target-venv observer with required environment/report channels. | JSON fixture allowlist; host `sys.executable -I -S`, `env={}`, fresh relative case directory, fixed timeout. |
| I3 | Execution infrastructure gap | Existing subprocess isolation is cooperative, not filesystem/network/process containment. PIP_NO_INDEX does not enforce the specified disabled network or contain setup.py/build execution. | `pipeline.py:57-84`; procedure network requirement. No enforcement adapter demonstrated. |
| F1 | Fixture/environment gap | Approved Ubuntu 24.04 x86_64 / ordinary CPython 3.13.1 environment, fresh venv, absolute space path and wheelhouse are not provisioned by this round. Recording host is Windows; no eligible run established. | Host observation in IDENTITY-PROVENANCE; fixture/procedure. No container/VM availability claim or machine qualification requirement. |
| F2 | Fixture/environment gap | Seven wheel identities were inspected in memory in R6.3, but local staging, bootstrap, offline access and versions are not demonstrated. Version constraints/tags do not prove usable setup. | `r6_3/prepare.py:46-64,95-141`; fixture `fixture_execution: NOT_RUN`. No current network retrieval or package execution. |
| E1 | Unresolved evidence gap | Abstract kernel composition sufficiency, layer responsibility (pip vs build backend) and legitimate semantics/adapter partition remain unproven. No candidate exists. | No generic grammar/byte/effect composition proof; no candidate authoring. Source failure context is not causal diagnosis. |
| E2 | Unresolved evidence gap | Observer/report availability, absence-control calibration and evidence independence have not been empirically verified. Parsing uses unchanged input plus report Requires-Dist substring; resolution uses installer report and direct_url; these are not independent traces of internal algorithms. | `observe.py:22-54`; fixed procedure. Installed payload hashes offer stronger independent state evidence, but no observations obtained. |
| E3 | Unresolved evidence gap | Repeatable pass/fail outcomes and safe execution of this fixture have not been demonstrated. Package build/install can introduce timestamps/paths/bytecode; pinned inputs are not byte-identical output guarantees. | All four checks NOT_RUN; no replay or containment validation. Exact command-success evidence must be retained outside the observer. |

## What can be independently verified, once separately authorized?

- **Parsing:** the fixed plan observes unchanged input and produced containing dependency
  metadata. This can corroborate successful metadata generation; it does not localize
  parsing to a particular layer or authenticate report contents. The observer's substring
  predicate is the approved predicate; this assessment does not strengthen it.
- **Resolution:** verify selected local path/hash in the report and installed direct_url,
  corroborated by exact installed payload bytes. The report/direct_url remain producer-owned
  provenance channels; observer ownership and byte inspection are separate.
- **Containing installation:** independently inspect target-venv distribution/version and
  empty my_module.py, paired with externally captured command outcome.
- **Dependency installation:** independently record initial absence and final version/payload
  correspondence. The observer has separate before/after modes but does not itself retain
  the before receipt or command outcome; a future verifier must bind both into the same run.

Neither generated stdout declaring PASS nor a forged install report alone may establish
success. Missing evidence is a limitation under the unchanged plan. Independent observation
means separate execution/evidence ownership, not cognitively independent preparation: this
round and the original expectations use the same agent/model. No oracle was run.

## Design hypotheses (not implemented capabilities)

Existing records, explicit identities, predicates, reference graphs and bounded operations
could model already decoded dependency/artifact data and immutable manifests. Existing
authority concepts could describe allowed resources. Reusing these does **not** license
undeclared byte/grammar/package effects or prove that all required transformations compose.
The smallest general typed artifact/resource-effect interface, or general parsing composition,
must be investigated on non-package examples before any claim of kernel-preserving closure.
Additional backend adapters would still need validated meaning, authority and failure rules.

Calling stock pip, setuptools/packaging, a hand-written parser or wheel installer behind a
generated JSON command would make that conventional code the semantic implementation of the
missing behavior. A verifier may bootstrap tools and independently inspect files; it must not
repair/normalize input, preinstall pipefunc or construct subject output. No existing-semantics-only
native execution approach has been demonstrated. Harness repairs alone cannot close S1-S3.
