# R6.73 — Contrastive semantic binding and decoder qualification

**Final classification: `R6_73_CONTRASTIVE_SUPERVISION_QUALIFIED`.** This AI-free,
CPU-only nonproduction qualification establishes deterministic reconstruction,
verified contrastive supervision and successful adversarial controls. It establishes
no model learning, comparative advantage or generalization. No model was loaded,
and no participant inference, optimizer/scheduler update or training occurred.

## Baseline, freeze and preservation

[Baseline verification](r6_73/BASELINE.json) verifies R6.72 publication/first halt,
R6.71 comparison, R6.70 qualification/decoder, R6.67 adapter, R6.65 scorer, R6.63
demonstrations, R6.66 training configuration and infrastructure, R6.52 assets and
inherited production/experimental identities. Initial git status was clean.
The original pinned base revision is `2e1fd397ee46e1388853d2af2c993145b0f1098a`;
preserved R6.67 adapter content identity is
`7fa3e7bfd5f99dd54caf700d53537c165a1193752d9820b3283423dfc9aef921`.
The historical decoder remains
`f93b261933487a9a95f8fc07339cfb9e902374a5421e4037f009ccf06cc9a01f`.

[Protocol](../../../experiments/contrastive_binding_r6_73/PROTOCOL.md),
[evaluation reservations](r6_73/EVALUATION-RESERVATIONS.json),
[literal expectations](r6_73/ACCEPTANCE-EXPECTATIONS.json) and
[pre-candidate freeze](r6_73/EXPECTATION-FREEZE.json) precede renderer implementation
and candidate execution. Review is **coordinator-only**. A pre-execution negative
operation typo has an [explicit additive amendment](r6_73/EXPECTATION-AMENDMENT-1.json);
original expectations/source/freeze remain intact. No expectations derive from outputs.

Production kernel remains26 by preserved accounting/implementation, not a new recount.
Compiler/lowerer/runtime, VM execution meanings and historical R6.3–R6.72 results are
unchanged. No R6.72 completion, replay inference or rescoring occurred; P6-A04
acceptance0, P6-A05 access false. Historical overview/log/decision files are publication-
pinned (including R6.19), so the current boundary is recorded in additive versioned
supplements rather than rewriting those historical publication identities.

## S11 cause established

[Analysis](r6_73/S11-GRAMMAR-ANALYSIS.md) and
[CPU evidence](r6_73/qualification_2/S11-CPU-ANALYSIS.json): all35 saved token
transitions reproduce exactly. Duplicate decoded dependencies are admitted by the
regex-partial prefix recognizer but rejected only by terminal structural validation.
At the saved prefix only outer `}` remains; its pinned token exists (ID92), yet that
completion fails dependency uniqueness. All94,366 admitted ASCII token continuations
reject, reproducing the empty mask. This is a prefix/terminal consistency defect,
not token absence, tokenizer-boundary mismatch,128-token exhaustion or demonstrated
model reasoning failure. R6.72's original `GRAMMAR_DEAD_END` and downstream
NOT_REACHED classifications remain unchanged.

## Compact decision and authoritative reconstruction

[Versioned specification](../../../experiments/contrastive_binding_r6_73/SPECIFICATION.md)
keeps only operation, ordered tagged operands and explicit dependencies:

```json
{"op":"le","left":{"ref":"used"},"right":{"literal":{"type":"Int64","value":0}},"deps":["used"]}
```

[Renderer](../../../experiments/contrastive_binding_r6_73/reconstruct.py) reuses the
preserved strict implementation in reconstruct_v1.py. It validates syntax/literal
host types and pinned scope, rejects ambiguous identities, delegates operation/type
checking and result derivation to unchanged R6.18 semantics, verifies explicit deps
against the direct reference set, constructs selected/value mechanically and applies
unchanged R6.63 validation/expansion. It does not select, swap or repair operations,
operands or dependencies. Canonical wire-order reconstruction asserts content identity.
No full symbolic package or redundant result type is an assistant target.

The [compact decoder](../../../experiments/contrastive_binding_r6_73/compact_decoder.py)
is a syntax-only finite completion language built from scope references/literals, all
operations and all distinct dependency subsets. It excludes duplicate-dependency dead
states while admitting semantically wrong alternatives. Five languages contain1,734
complete decisions;47,517 token-prefix observations and three exhaustive vocabulary
masks pass. [Every19,500 unique nonterminal prefix](r6_73/qualification_2/PREFIX-EXTENSION-CONTROLS.json)
has a full-decode token-extension witness; terminal states allow EOS only. These are
CPU mechanism controls, not live model-generation results or independent task examples.

## Dataset, contrasts and supervision

[Versioned records](r6_73/qualification_2/TRAINING-RECORDS.json) and
[supervision ledger](r6_73/qualification_2/SUPERVISION-LEDGER.json) contain **54 qualified
decision examples:18 positives and36 explicitly labeled negatives**, in nine contrast
categories/pairs. Identities F01–F09 are frozen, with P1/P2 positives and N1/N2 alternatives:

|Family identity|Requirement-derived distinction|
|---|---|
|F01-add-le|Total versus inclusive comparison; output obligation differs|
|F02-le-eq|Inclusive comparison versus exact match; shared Bool obligation|
|F03-order|Opposite ordered comparisons; asymmetric fixtures|
|F04-distractor|Requested stored quantity versus unrelated same-type reference|
|F05-literal-ref|Fixed zero versus stored baseline; divergent fixture values|
|F06-dependencies|Prior-result/literal versus prior-result pair; direct versus indirect source|
|F07-typed|Int64 zero versus Bool false; invalid mixed typed bindings|
|F08-repeated|Two uses of one identity; one dependency; distinct-operand negatives|
|F09-shared|le versus eq over shared-prefix dependency structure; exact relation matters|

Every record binds requirement/scope/target/action or null rejection identity,
acceptance evidence, family/contrast, label, provenance and training partition.
Invalid negatives have no authoritative reconstructed action: their action identity
is explicitly null and behavior NOT_REACHED. Positive acceptance/action references
are separately retained. Negative reasons are deterministic requirement/validation
feedback, not fabricated AI reasoning.

[18 direct SFT positives](r6_73/qualification_2/SFT-POSITIVES.json) and
[36 corrective SFT records](r6_73/qualification_2/CONTRASTIVE-SFT-POSITIVES.json) are
future training inputs. Corrective user inputs include a labeled incorrect candidate;
assistant targets contain only the correct compact decision. Incorrect decisions never
become positive next-token targets. These54 eligible SFT rows still represent18 underlying
requirements, not54 independent positives or new behavioral families.
The [fully linked SFT-ready dataset](r6_73/qualification_2/SFT-READY.json) carries
all required provenance/action/acceptance/partition fields on every eligible row;
its17 distinct requirement identities disclose the F01/F02 overlap.

## Acceptance and adversarial results

All **18/18** positive reconstructions are deterministic and accepted by unchanged
R6.65 scorer/assembler; **54/54** frozen positive fixtures pass unchanged VM execution.
Scopes are byte-preserved. Repeating the CPU qualification after the serialization-
order correction reproduces the same authoritative action identities; repetitions
are not additional examples or independent observations.

Negative classifications: **4 schema rejections,18 semantic rejections,14 valid-but-wrong
decisions**. Twelve of the14 valid wrong decisions fail at least one behavioral fixture.
The two F09 wrong-relation negatives pass all their functional fixtures but fail the
exact requirement-derived operation. Shared prefix adjusted=echo+1 masks this relation
distinction; functional agreement alone is deliberately not called full acceptance.
Commutative operand-order expectations remain structural rather than behaviorally proven.

[Adversarial verification](r6_73/qualification_2/ADVERSARIAL-VERIFICATION.json): **26/26
controls pass**:16 schema rejections,7 semantic rejections,1 valid-but-behaviorally-wrong
reversed comparison, and2 legal controls (repeated operands and native Int64 overflow
acceptance-as-rejection). Unknown operation, missing/tag-ambiguous operands, malformed
JSON/duplicate keys/NaN, extra fields, invalid typed literals/overflow literals, missing
references, absent/incorrect/duplicate deps, unsorted deps, duplicate scope identities,
parameter/prior collisions, incompatible operations and unlisted literals are covered.
The reversed comparison is never silently corrected. Runtime overflow remains native
`OVERFLOW`; this adds no execution meaning.

## Token lengths and leakage limitations

[Pinned tokenizer measurements](r6_73/qualification_2/TOKENIZATION.json) verify all54
decisions:20–32 content tokens (positive targets21–32),304–385 full chat-sequence tokens.
[Corrective records](r6_73/qualification_2/CORRECTIVE-TOKENIZATION.json):21–32 content
tokens,363–444 full sequence tokens. Completion+EOS is trainable; prompts/post-EOS
newline masked. All90 measured rows round-trip exactly, none truncate and none exceed2048.
The pinned tokenizer identity is
`c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539`.

[Leakage assessment](r6_73/LEAKAGE-AND-INDEPENDENCE.md): all expectations are coordinator-
reviewed synthetic development evidence. Reserved evaluation families have no published
solutions, but independent withholding is unavailable: future evaluation is exploratory.
F01/F02 share one le case; shared prefix/renaming controls are correlated and not new
behavioral families. Scope result obligations narrow operations, and correction prompts
provide a training-only scaffold. No generalization or unaided learning is established.

## Failures preserved, publication and next step

[Preparation failures](r6_73/PREPARATION-FAILURES.json),
[first qualification failure](r6_73/QUALIFICATION-ATTEMPT-1.json) and
[supplement import failure](r6_73/SUPPLEMENT-PREPARATION-FAILURE.json) remain retained.
The first CPU qualification passed reconstruction/behavior/adversarial/S11/tokenization,
then failed compact target membership because sorted-loaded JSON was serialized in a
different wire order. Version2 mechanically canonicalizes that envelope only, preserving
every semantic choice; archived source hashes match the original implementation freeze.
Fresh successor outputs are in qualification_2; no first evidence was overwritten.

[Publication identities](r6_73/PUBLICATION-IDENTITIES.json) and
[verification](r6_73/VERIFICATION.json) bind original and successor sources/evidence,
report/spec/design and versioned documentation. Fresh-process checks repeat baseline
identity verification, freeze/source identities, syntax, local links, record references,
credential-pattern/whitespace checks, additive scope and `git diff --check`.

**A fresh-adapter experiment is justified as a bounded prospective test**, not immediate
execution. [One proposed protocol](r6_73/FRESH-ADAPTER-PROTOCOL.md) uses the original base,
18 direct+36 corrective records, explicit deps/compact targets,54-update maximum216-
presentation QLoRA budget, frozen base diagnostics and identical paired evaluation.
It does not presume the previous20-step configuration optimal. Smallest next step:
separately authorize CPU-only integration into the existing R6.66 masked-completion
infrastructure, sampling/schedule/worker freeze and coordinator-disclosed evaluation
realization/review. Neutral inference and training require later explicit authorization.

**Stopped after bounded qualification and publication. Await explicit owner authorization
before additional dataset generation, participant inference, training or evaluation.**
