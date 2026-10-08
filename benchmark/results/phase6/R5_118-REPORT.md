# R5.118 — P6-A02 first external requirement evaluation

**`R5_118_P6_A02_FIRST_EVALUATION_COMPLETE`**

**`P6_A02_FIRST_RESULT = NEEDS_CLARIFICATION`**

First blocker: **FRC_REVIEW_APPROVAL / REQUIRED_APPROVAL_UNAVAILABLE**.
This is an approval/authority boundary, separately reported from semantic
incompleteness. No definite material behavioral ambiguity was established in
the bounded requested delta. That candidate judgment is not independent approval
or a claim of executable-contract adequacy.

## Evidence and chronology

1. [Fresh snapshot](r5_118/SNAPSHOT.md) recorded before P6-A02 access. Initial dirty
   R5.117 publication work became externally committed `0934907` during collection;
   stable pre-access commit `09349071c6c63154bcbe82e02e6f2fd2d002ab3c`, clean tree.
   All implementation/test subtrees match Phase 5; kernel 26; versions/profiles/model
   recorded. Validation/safety and **34 fresh baseline regression passes**.
2. [Exact source verification](r5_118/SOURCE-VERIFICATION.md): access after
   `2026-10-08T14:27:14.7693623Z`; twelve checks passed at
   `2026-10-08T14:27:48.529174+00:00`. Exact preserved `curl/curl#15914`, reporter
   ttc0419, title/body and physical source/API/provenance-referenced hashes matched.
3. [Source-bound candidate](r5_118/FRC-CANDIDATE.json) and
   [formalization/materiality](r5_118/FORMALIZATION-AND-MATERIALITY.md): A02-E1/A02-I1,
   complete source fragment accounting and A02-Q1 required approval decision.
4. [Reached-stage evidence](r5_118/PIPELINE-EVIDENCE.md): existing FRC validator ran
   once at `2026-10-08T14:30:03.024599+00:00`; valid candidate envelope, commitment
   `6ad06b722f465a884d428a762282e539972705f00ab6d5a24023f9dab66e328a`.
5. [Immutable first result](r5_118/P6_A02_FIRST_RESULT.json) persisted immediately
   afterward, before report/status publication. Publication receipt binds its bytes.

Material is **externally authored, procedurally selected evaluation material**,
not independently blinded or pristine held-out. Prior curation exposure remains.
Manual same-agent candidate/reconciliation is explicitly distinguished from independent
review, live provider calls, owner approval and controller-issued authority.

## Requested change and preservation

The exact title is **“Allow *.internal wildcard TLS certificate”**. The body asks
**“Please consider allow *.internal wildcard TLS certificates.”** Its ICANN/IETF
private-use rationale is preserved, including “revered”; links were not opened.

Requested observable delta: allow the wildcard identity `*.internal` in curl's TLS
certificate handling rather than reject it solely for that identity, in an otherwise
admissible authorized verification scenario. Inputs are a TLS connection attempt,
destination hostname, certificate identity and verification configuration. The output
surface is allowance or verification rejection, not a particular HTTP body or diagnostic.
No state effect, migration, audit or restart requirement is supplied.

**Existing behavior explicitly required to remain unchanged: none.** The source does
not state a global preservation frame. A bounded software-change request need not
respecify its surrounding application. Nor does it authorize wholesale replacement
of hostname/trust policy. Other verification conditions are outside the requested
delta, not newly supplied exact security rules or a invented universal frame.

Internal algorithms, representations, helper structure and test organization are
legitimately unconstrained subject to the approved observable requirement. No concrete
hostname matches, default/option activation, trust bypass, other-TLD expansion, backend
matrix or error values were selected on the reporter's behalf.

## Materiality and required approval

Missing exact errors, HTTP output, internal implementation detail and platform/version
enumeration are not automatically clarification blockers. SAN/common-name treatment,
trust conditions and hostname examples require authoritative inherited context for a
later oracle; their absence does not itself prove that a bounded change is incoherent.
The candidate does not use conventional curl behavior or model memory as authority.
The curation readiness label/questions are preserved, not mechanically promoted into
an evaluation finding that all omissions are material ambiguities.

No demonstrated material conflict in the requested delta remains. **A02-Q1** is the
unavailable required independent/source-owner or appointed benchmark-owner approval
of this exact interpretation, adopted scope and applicable inherited context.
The user authorized this evaluation while retaining the current approval process;
no approval of the subsequently generated candidate, independent reviewer receipt,
owner clarification or scoped implementation grant was supplied. The issue reporter
is not asserted to be an upstream approver. No approval or answer was fabricated.

Formalization therefore produced a coherent, source-bound, envelope-valid **candidate**,
but not a complete independently reviewed/owner-approved/sealed FRC. Independent
source reconciliation and fixed approved acceptance remain unavailable. The existing
Phase 6 NEEDS_CLARIFICATION outcome includes unavailable required approval. This
manual outcome is not a fabricated controller DISPUTED result.

## Pipeline and behavioral evidence

Reached: fresh snapshot, source verification, candidate formalization, same-agent
source reconciliation, materiality/authority review and blocked FRC approval boundary.

**FRC sealing, structural coverage, BDI, adequacy, V1, Lykoi authoring, compilation,
external behavioral verification: NOT_REACHED.** No unsupported-stage finding is
inferred for an unexecuted stage. Zero P6-A02 acceptance cases/external invocations;
no generated executable or approved independent oracle. All requested executable
behavior remains unverified. Regression passes do not establish P6-A02 behavior.

## Preservation and interpretation

Lykoi semantics, 26-concept kernel, profiles, mappings, compiler/backend, model,
generated software and prompts are unchanged. Implementation identities match the
baseline; R5.117 result/evidence and all R5.116A curation artifacts remain unchanged.
No repair, model switch, outcome retry or P6-A03–P6-A05 inspection/evaluation.
Immutability is procedural and hash-bound; no filesystem write protection or new
evaluation-agent Git commit is claimed. Integrity checks are publication checks,
not a requirement rerun.

**Finding:** the process can distinguish a bounded real-world delta from an imagined
need for a full application specification, while retaining the separate approval gate.
This is one external first attempt with one authority halt, zero behavioral trials.
It does not establish semantic coverage, backend suitability, executable generalization,
curl compatibility, upstream acceptance, kernel minimality or need for a new concept.
No downstream concept/composition was exercised; capability cause remains unknown.

**Next:** obtain legitimate content-bound owner/benchmark approval and independent
source reconciliation of the bounded delta and inherited context; fix source-derived
acceptance independently before authoring. Any further attempt must be separately
authorized and linked to this immutable first result. No repair or P6-A03 access here.

## Completion answers

1. **Exact source verified?** Yes; exact saved revision, hashes and identities matched.
2. **Observable change?** Allow `*.internal` wildcard certificate identity; no categorical
   rejection solely for that identity in an otherwise admissible authorized scenario.
3. **Explicit preservation?** None stated; no whole-curl preservation contract invented.
4. **Delegated implementation choices?** Internal algorithms/representation/organization;
   no new observable TLS policy or activation choice is silently delegated.
5. **Material ambiguities?** None demonstrated for the bounded delta. Adopted scope and
   authoritative inherited verification context await approval for a concrete contract/oracle.
6. **Formalization sufficient?** Coherent, valid candidate; not a complete approved FRC.
7. **Implementation authority?** No; required review/owner approval unavailable.
8. **Stages reached?** Snapshot/source/candidate/reconciliation/materiality and approval boundary.
9. **First terminal result?** NEEDS_CLARIFICATION at FRC_REVIEW_APPROVAL, authority cause.
10. **External verification?** No; zero requirement invocations.
11. **Lykoi unchanged?** Yes; implementation baseline and 26 concepts preserved.
12. **Real-world handling finding?** Bounded-change interpretation and authority separation;
    downstream semantic/behavioral generalization remains untested.
13. **Next?** Legitimate approval, independent context/acceptance review, then only a separately
    authorized linked attempt. Stop after this first result.
