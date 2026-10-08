"""Read-only R6.2 identity/scope checks; optional exclusive evidence publication."""
import json
import subprocess
import sys
from pathlib import Path

from benchmark.results.phase6.r6_1.prepare import (
    ROOT, digest, git, implementation_snapshot, load, sha, validate, verify_source,
)

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'r6_1'
CLASSIFICATION = 'R6_2_P6_A04_LITERAL_INPUT_CLARIFICATION_REQUIRED'


def verify():
    provenance, source = verify_source()
    frc = load(OLD / 'FRC-CANDIDATE.json')
    plan = load(OLD / 'ACCEPTANCE-PLAN-CANDIDATE.json')
    assert validate(frc) == 'ec79136bf1c1bcee109e9d739299bd594587029c6b70203fcac1a768edc801a0'
    assert digest(plan) == '97da6d516f08f45f77462cfd6d6f54f7a944dc2d86a0b92899c7fdc0ff438d59'
    assert frc['source']['text'] == source['body'] and frc['review'] is None
    assert all(not issue['resolved'] for issue in frc['issues'])
    assert plan['frc']['canonical_sha256'] == validate(frc)
    assert not plan['approved'] and not plan['sealed'] and plan['native_plan'] is None
    assert {o['id'] for o in frc['obligations']} == {o for c in plan['checks'] for o in c['obligations']}
    assert all(c['status'] == 'CONDITIONAL_NOT_RUN' and c['source_quote'] in source['body'] for c in plan['checks'])
    assert all(c['expected']['selected_expectation'] is None for c in plan['checks'][2:])
    old_ids = load(OLD / 'IDENTITIES.json')
    assert sha(OLD / 'FRC-CANDIDATE.json') == old_ids['frc_file_sha256']
    assert sha(OLD / 'ACCEPTANCE-PLAN-CANDIDATE.json') == old_ids['acceptance_plan_file_sha256']
    for name, expected in old_ids['review_files_sha256'].items():
        assert sha(OLD / name) == expected
    snapshot = load(OLD / 'SNAPSHOT.json')
    assert implementation_snapshot() == snapshot['implementation_manifest']
    assert digest(implementation_snapshot()) == snapshot['implementation_identity']
    allowed = {'AGENTS.md', 'README.md', 'benchmark/README.md', 'docs/project-overview.md',
               'docs/agent-workflow.md', 'docs/research-log.md', 'docs/decisions.md',
               'benchmark/results/phase6/R6_2-REPORT.md'}
    changed = git('diff', '--name-only', 'HEAD').splitlines()
    untracked = git('ls-files', '--others', '--exclude-standard').splitlines()
    assert all(p in allowed or p.startswith('benchmark/results/phase6/r6_2/') for p in changed + untracked)
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    for name in changed + untracked:
        assert all(line == line.rstrip() for line in (ROOT / name).read_text(encoding='utf-8').splitlines()), name
    record = {
        'round': 'R6.2', 'classification': CLASSIFICATION,
        'git_commit': git('rev-parse', 'HEAD'), 'git_tree': git('rev-parse', 'HEAD^{tree}'),
        'initial_git_status': 'CLEAN; checked before source reading or edits',
        'source_capture_sha256': provenance['source']['sha256'],
        'title_utf8_sha256': provenance['title_utf8_sha256'],
        'body_utf8_sha256': provenance['body_utf8_sha256'],
        'source_provenance_sha256': sha(HERE.parent / 'r5_116a/P6-A04-provenance.json'),
        'frc_source_record_canonical_sha256': digest(frc['source']),
        'preserved_frc_canonical_sha256': validate(frc),
        'preserved_acceptance_canonical_sha256': digest(plan),
        'implementation_identity': snapshot['implementation_identity'],
        'review_files_sha256': {n: sha(HERE / n) for n in ('SOURCE-EVIDENCE.md', 'HUMAN-REVIEW.md')},
        'revised_frc': 'NOT_PRODUCED: material input authority unresolved',
        'revised_acceptance': 'NOT_PRODUCED: no fixed eligible-input oracle justified',
        'checks': {k: 'PASS' for k in ('source_identity', 'preserved_candidate_validity',
                  'conditional_acceptance_integrity', 'historical_preservation_scope',
                  'implementation_unchanged', 'whitespace_change_scope')},
        'historical_preservation_basis': 'Clean starting HEAD; all tracked changes and untracked additions constrained to R6.2 evidence/minimal status files',
        'approved': False, 'sealed': False, 'research_receipt': None,
        'acceptance_executions': 0, 'evaluation_stages': 'NOT_RUN',
    }
    if '--publish' in sys.argv:
        with (HERE / 'IDENTITIES.json').open('x', encoding='utf-8', newline='\n') as out:
            out.write(json.dumps(record, indent=2) + '\n')
    else:
        assert load(HERE / 'IDENTITIES.json') == record
    print(json.dumps(record, indent=2))
    if '--source' in sys.argv:
        print(source['body'])


if __name__ == '__main__':
    verify()
