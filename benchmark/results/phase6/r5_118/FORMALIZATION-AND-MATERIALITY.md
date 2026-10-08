# P6-A02 formalization, materiality and authority review

One source-only interpretation and same-agent reconciliation, not independent review.
Applicable existing rules: FRC v0.1 sections 3–4 and 6; R5.85 question-selection
policy section 4; Phase 6 protocol first-attempt approval/authority rules.
No compiler capability query was used to select the requirement's meaning.

## Complete source accounting

Offsets are half-open Unicode character offsets in the exact body, including CRLF.
The separate title is preserved in provenance and candidate context.

| Fragment | Disposition |
| --- | --- |
| `### Problem` (0–11) | Heading only; no behavior |
| `.internal is officially revered by [ICANN](https://www.icann.org/en/board-activities-and-meetings/materials/approved-resolutions-special-meeting-of-the-icann-board-29-07-2024-en#section2.a) and [IETF](https://datatracker.ietf.org/doc/draft-davies-internal-tld/) for private use.` (15–293) | Reporter rationale, verbatim wording retained; linked contents not verified or made normative |
| `Please consider allow *.internal wildcard TLS certificates.` (294–353) | A02-E1; A02-I1 derived; A02-Q1 authority review |
| Title `Allow *.internal wildcard TLS certificate` | Same requested change; not an additional obligation |

The offset boundaries are checked in the publication receipt; no source fragment
is discarded because of language support. A02-I1 derives from A02-E1: categorical
rejection of the requested identity in every otherwise admissible scenario would
make the requested allowance impossible. This does not imply accepting an untrusted,
expired or otherwise invalid certificate or specifying a particular trust algorithm.

## WHAT, inputs/outputs and frame

**Requested delta:** allow the literal wildcard TLS certificate identity
`*.internal` in curl; stop excluding it solely for that wildcard identity.
Input surface: TLS connection attempt with destination hostname, presented
certificate identity and applicable verification configuration. Observation:
certificate allowance versus verification rejection attributable to that identity.
HTTP contents, byte-exact diagnostics and exit values are not requested.
No durable state effects or migration/restart requirements are given.

**Explicit preservation:** none. The source does not enumerate surrounding behavior
to retain. It is a change request against an existing application, not a request to
replace TLS policy wholesale. Other validation is outside the requested delta;
this is a scope limitation, not a fabricated source statement guaranteeing every
other curl behavior unchanged. Concrete inherited behavior must be source/context
bound for any later oracle, not filled from model memory or fixing implementation.

**Material constraints:** target curl; wildcard identity exactly `*.internal`;
TLS certificate allowance. Private-use rationale is attributed, not independently
validated. No backend, algorithm, internal representation or code organization is
mandated. Internal implementation choices can vary subject to the approved behavior.
No observable trust bypass, new flag, multi-label rule or other-TLD exception is delegated.

## Materiality disposition

The curated acceptance questions are reviewed afresh as candidate questions, not
binding findings that every missing detail is a blocker.

| Missing detail | Disposition and rationale |
| --- | --- |
| Exact error text/code or HTTP response | Not material to requested categorical allowance; no source demand for those bytes |
| Algorithms, internal matching helper, test organization | Legitimate internal freedom subject to behavior; no clarification needed |
| Curl/backend/TLS versions | No source-defined version matrix; absence alone does not make the change incoherent. Actual integration scope must be approved before implementation |
| SAN versus common name, trust/expiry handling | Not a request to redesign these policies. Do not disable validation or invent new identity rules; later fixtures require authorized inherited context |
| `host.internal`, `internal`, `a.b.internal` matching | Plausible distinctions for a future oracle, but the request does not say to expand wildcard grammar. No concrete match/non-match result is claimed here. Review the adopted existing matcher/context rather than demanding a complete TLS respecification |
| Default versus opt-in activation | Source does not explicitly delegate a new switch. The bounded candidate does not invent one; owner adoption/scope approval is required |
| ICANN/IETF policy text | Rationale only under this exact-source-only round; no further lookup or unverified policy supplied |

No definite source conflict or unresolved material behavioral choice is demonstrated
within the bounded delta. This is a **candidate materiality judgment**, awaiting the
required independent review. It is not proof of complete executable-contract adequacy.
If an approved interface admits additional behavior, adequacy must revisit that behavior;
this round cannot use narrow candidate scope to silently discard an admitted obligation.

## Exact unresolved authority decision

**A02-Q1:** Will the legitimate source owner or appointed independent benchmark owner
approve this exact interpretation as the adopted bounded exception, identify the
applicable inherited verification context/scope, and supply the required content-bound
review/approval? No such receipt, clarification answer or human approval exists.

The user authorized evaluation and expressly retained the current approval process;
that is not approval of this subsequently produced FRC or a grant to implement it.
The public reporter's request is not upstream acceptance. No source-authorized policy
grants this agent approval rights. Independent source reconciliation is unavailable;
same-agent reconciliation remains labeled as such.

**Sufficiency:** enough to draft a coherent source-bound bounded-change candidate;
not enough to claim a complete, reviewed, owner-approved FRC or fixed independent oracle.
The first blocker is **FRC_REVIEW_APPROVAL / REQUIRED_APPROVAL_UNAVAILABLE**,
separate from semantic incompleteness. The existing Phase 6 outcome
**NEEDS_CLARIFICATION** covers unavailable required approval. No semantic capability
finding is justified, and structural coverage must not run to bypass this boundary.
