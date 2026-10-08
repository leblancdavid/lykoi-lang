# A03-Q1 — inherited ACL rule processing

**Resolved sufficiently for a bounded research interpretation**, using pre-issue
public documentation rather than a fabricated maintainer answer. Original R5.119
ambiguity and candidate remain unchanged. New context supplies the rule that the
reporter explicitly did not know. It does not establish that Redis maintainers
accepted the feature or its compatibility consequences.

## Evidence and inference

Pinned Redis documentation at `redis/redis-doc` revision
`7277deb0a858a6384d8a069fc654c61fcda32b34`, dated `2022-01-02T16:21:04Z`, predates
issue creation `2025-01-10T10:22:51Z`. See [exact extracts/provenance](INHERITED-EVIDENCE.json).

- D1-Q1 / D2-Q1: rules apply left-to-right.
- D1-Q2–Q5 / D2-Q2–Q4: explicit command rules and category expansions add/remove
  commands from the same allowed-command list. No independent explicit-grant priority.
- D1-Q6: overlapping categories can remove commands a preceding category added.
- Thus a category removal can remove an earlier explicit grant; an explicit denial
  does not defeat a later applicable category grant. These are deductions from the
  documented rule, not observations of a modified server.
- D2-Q5: `-@all` starts each case without allowed commands. Cases use fresh users,
  one ordinary rule list, no selectors/modules/subcommand/first-argument grants.
- D3-Q1/Q3: SELECT chooses a zero-based database on a connection; new connections
  start on DB0. D3-Q2 bounds probes to non-cluster environments.

The original source reports SELECT absent from @read/@write. D1-Q7 describes the
old key-interaction category boundary, consistent with that report. The old-membership
column below uses that reporter-bound membership premise; it is not an independently
executed membership inventory or a claim about every release.

## Required cases and reversed order

All suffixes follow `-@all`; normal user activation/authentication/key setup is
otherwise valid. The only membership change is adding SELECT to both categories.

| ACL suffix | Inherited rule with source-reported old membership | After requested membership addition, same rule | Change? | New policy choice? |
| --- | --- | --- | --- | --- |
| `+select +@read -@write` | Allow: explicit grant is untouched by old categories | **Deny**: final -@write removes SELECT | Yes | No |
| `+@read -@write +select` | Allow: final explicit grant | **Allow**: final explicit grant restores SELECT | No | No |
| `-select +@read` | Deny: category lacks SELECT | **Allow**: later +@read adds SELECT | Yes | No |
| `+@read -select` | Deny: final explicit removal | **Deny**: final explicit removal | No | No |
| `+@read -@write` | Deny: neither category changes SELECT | **Deny**: last applicable category removes SELECT | No | No |
| `-@write +@read` | Deny: neither category changes SELECT | **Allow**: last applicable category adds SELECT | Yes | No |
| `+@write -@read` | Deny: neither category changes SELECT | **Deny**: last applicable category removes SELECT | No | No |
| `-@read +@write` | Deny: neither category changes SELECT | **Allow**: last applicable category adds SELECT | Yes | No |
| `-select +@write` | Deny: category lacks SELECT | **Allow**: later +@write adds SELECT | Yes | No |
| `+@write -select` | Deny: final explicit removal | **Deny**: final explicit removal | No | No |
| `+select +@write -@read` | Allow: explicit grant untouched by old categories | **Deny**: final -@read removes SELECT | Yes | No |
| `+@write -@read +select` | Allow: final explicit grant | **Allow**: final explicit grant restores SELECT | No | No |

Every row is derived from D1-Q1–Q6 / D2-Q1–Q5 plus original E1/E2 and the
source-reported old-membership premise. No row is a runtime result. A later allowed
SELECT must select the requested valid database; a denied command is not authorized
to execute a selection. Exact wire error text remains outside this bounded contract.

## Preservation boundary and authority

Adopt the user-preferred narrow interpretation because the source requests category
membership, not a new processor, and independent documentation supplies the ordinary
processor. Preserve **rule-processing semantics**, not every previous final permission
under changed membership. The source warns of the very denied outcome now determined
by those inherited rules; it does not require a SELECT-specific compatibility exception.

The experiment therefore accepts `+select +@read -@write` losing SELECT permission
as a consequence of the requested membership addition. Preserving that old allowance
would require an additional permission-precedence policy unsupported by this source.
Do not introduce it. Preserve existing other category memberships and other commands'
processing within the narrow ACL delta; no unrelated key/authentication/persistence
changes are authorized. Broad application equivalence is not claimed.

**No material Q1 choice remains within this declared documented-rule scope.**
Nonblocking limitations: unknown reporter server version, no runtime confirmation,
no later-release matrix, no selectors/first-argument grants/modules/cluster scope,
and no universal compatibility/rollout guarantee. If a later attempt targets a
different ACL-rule family or conflicting version behavior, it needs new context and
review, not extrapolation from this record. Feature adoption remains a human research
approval decision. This evidence does not certify upstream intent or product approval.
