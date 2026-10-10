# Independent commissioning protocol — R6.50 / version 1

Status: neutral commissioning package, **UNASSIGNED / NOT_QUALIFIED**.
No new human requirement, human acceptance approval or independent family exists
in this round. The owner authorized design; that statement does not appoint an
independent requirement author or approve a behavioral contract.

## Roles and permitted inputs

| Role | Input access | Obligations |
| --- | --- | --- |
| Human commissioner | Neutral brief and domain experience | Distinct from implementation agent; author original requirements without candidate code, generated targets, historical task solutions or acceptance outputs |
| Independent acceptance reviewer | Original source, clarification record and public interface specification | Separate from implementation authors and commissioner; derive expectations before implementations, disclose prior exposure/conflicts |
| Custodian | Source, review and sealed evaluation assets | Administer custody and release, no training-data production |
| Implementation participants | Released source/FRC and common public interface only | No hidden acceptance, reference implementation or sibling material |
| Training producers | Training-development allowlist only | No evaluation-family sources, solutions, acceptance or trajectories |

Human role identities and dated declarations must be supplied by the people
themselves. An AI cannot self-appoint, sign for them or infer their approval.
Independent acceptance review may use deterministic tooling, but the reviewer
must take responsibility for source fidelity and independently fixed outcomes.

## Neutral brief for one family

Commission one original **bounded local-stateful application family** with a
sequential public API and observable state. Describe intended users, operations,
valid and invalid inputs, outputs, lifecycle, invariants, effects, normal process
restart, ordering and authority assumptions. Do not request a particular algorithm,
kernel construct, implementation skeleton or existing release-workflow variant.
Specify whether concurrency, crash recovery and external effects are included.
The commissioner chooses the domain; none is claimed to have been chosen here.
Record gaps faithfully if the fixed production profile cannot represent it.

Ask for a structurally distinct sibling in that broad family, privately through
the custodian. See [custody protocol](CUSTODIAN-WITHHOLDING.md). Both episodes remain
evaluation-only; commissioning one public episode does not authorize training on it.

## Ordered procedure and evidence

1. Appoint actual humans and custodian; obtain conflict/prior-access disclosures
   and input inventories. No candidate implementations may be consulted.
2. Commissioner writes source with authorship/time/rights evidence. Custodian
   records exact UTF-8 bytes, SHA256 and byte length before formalization.
3. Reviewer maps each obligation to observations, including rejection/no-effect,
   boundaries, conflicting invalid inputs, state histories and restart. Maintain
   an obligation-to-case matrix; mutation controls challenge weak acceptance.
4. Record ambiguity ID, source quotation, competing readings, exact commissioner
   response and resulting source/FRC revision. Unanswered material ambiguity blocks
   freeze. Reviewer independently confirms alignment; never resolve from outputs.
5. Freeze source, FRC, acceptance expectations, harness, provider assumptions,
   observation normalization, budgets and review statements together. Signed human
   receipts bind hashes; hashes establish integrity, not human independence.
6. Establish custody before release; freeze scorer and first-result policy. Release
   the primary source/FRC only to evaluation participants after training freeze.
   Hidden tests and reference solutions remain custodian-only.
7. Record first exposure, first terminal result and native blocker. Preserve failed
   candidates and NOT_REACHED stages. Subsequent clarification/repair becomes a
   linked post-exposure round; do not replace the first result or secretly fix tests.

Require evidence of independent review and controlled access, not just a role name
or a fresh AI conversation. Capability assessment follows source freeze and cannot
retroactively reshape the commissioner’s task. If representation fails, preserve a
capability gap and the original contract.

## This round's stop

Commissioner: unavailable/unappointed. Reviewer: unavailable/unappointed.
Frozen new requirement/acceptance identities: **none**. Commissioned families: **0**.
The procedure is designed; its independence is not empirically qualified.
