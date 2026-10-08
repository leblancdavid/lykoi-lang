"""Offline R6.4 publication checks only; never invoke semantic/execution stages."""
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from benchmark.results.phase6.r6_1.prepare import (
    ROOT, digest, git, implementation_snapshot, load, sha, verify_source,
)

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / 'r6_3'
EXPECTED = {
    'HUMAN-CLARIFICATION.json': '232fef22356ed5b743c0e3e572c69c76ed6669ff7dcceab7989c5e7fbc9d48d8',
    'FRC-CANDIDATE.json': 'aa2af92cf77073f1f42a70065d64135d211bf7bc6889aeeb4a033ce3aa449aba',
    'ACCEPTANCE-PLAN.json': '2ec947565b95dbed28bf5096aa945dbf528c1bdaf2763a99cc95f7da587f0dc4',
    'FIXTURE-MANIFEST.json': 'd3f38f5cdcf4aac2602e83ce66de6b227200f7e12185a42f2d3ece83efb4c6e1',
}
GUIDANCE = {'AGENTS.md', 'README.md', 'benchmark/README.md',
            'docs/project-overview.md', 'docs/agent-workflow.md',
            'docs/research-log.md', 'docs/decisions.md'}
EVIDENCE = {
    'src/lykoi_research/local.py': [(24, 31), (38, 58), (132, 187)],
    'src/lykoi_pipeline/contracts.py': [(15, 91)],
    'src/lykoi_pipeline/plans.py': [(12, 13), (54, 129)],
    'src/lykoi_pipeline/pipeline.py': [(20, 107)],
    'src/air_compiler/profiles.py': [(40, 96), (135, 170)],
    'src/air_compiler/validator.py': [(134, 156)],
    'src/air_compiler/mutable_values.py': [(45, 85), (211, 231)],
    'src/air_compiler/runtime_template.py': [(120, 150)],
    'src/air_compiler/creation_provider_runtime.py': [(1, 46)],
    'src/air_compiler/atomic_state.py': [(49, 60)],
    'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json': [(1, 80)],
    'benchmark/results/phase6/r6_3/ACCEPTANCE-PROCEDURE.md': [(8, 42), (44, 107)],
    'benchmark/results/phase6/r6_3/observe.py': [(14, 54)],
}


def save(name, value):
    path = HERE / name
    if path.exists():
        assert load(path) == value, 'Refuse evidence overwrite: ' + name
    else:
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def verify():
    provenance, source = verify_source()  # confined to preserved P6-A04 captures
    artifacts = {name: load(PREVIOUS / name) for name in EXPECTED}
    identities = {name: digest(value) for name, value in artifacts.items()}
    assert identities == EXPECTED
    human, frc, plan, fixture = [artifacts[n] for n in EXPECTED]
    prior = load(HERE.parent / 'r6_1/FRC-CANDIDATE.json')
    assert prior['source']['text'] == source['body']
    original = {'id': prior['source']['id'], 'capture_sha256': provenance['source']['sha256'],
                'body_sha256': provenance['body_utf8_sha256'],
                'source_record_sha256': digest(prior['source']),
                'provenance_sha256': sha(HERE.parent / 'r5_116a/P6-A04-provenance.json')}
    for value in (human, plan, fixture):
        assert value['original_source'] == original
    assert frc['context']['domains']['original_source'] == original
    assert frc['source']['text'].startswith(source['body'] + '\n\n')
    assert frc['source']['text'].endswith(human['human_statement'])
    assert hashlib.sha256(frc['source']['text'].encode()).hexdigest() == frc['source']['sha256']
    assert frc['revision'] == 2 and plan['frc']['revision'] == 2
    assert plan['frc']['canonical_sha256'] == EXPECTED['FRC-CANDIDATE.json']
    for value in (plan, fixture, frc['context']['domains']):
        assert value['human_clarification_sha256'] == EXPECTED['HUMAN-CLARIFICATION.json']
    for value in (plan, frc['context']['domains']):
        assert value['fixture_manifest_sha256'] == EXPECTED['FIXTURE-MANIFEST.json']
    assert plan['native_plan'] is None
    for name, key in [('ACCEPTANCE-PROCEDURE.md', 'executable_procedure_sha256'),
                      ('observe.py', 'observation_program_sha256')]:
        assert sha(PREVIOUS / name) == plan[key]
    manifest = implementation_snapshot()
    assert manifest == load(HERE.parent / 'r6_1/SNAPSHOT.json')['implementation_manifest']
    assert load(ROOT / 'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json')['final_count'] == 26
    changed = git('diff', '--name-only', 'HEAD').splitlines()
    staged = git('diff', '--cached', '--name-only').splitlines()
    untracked = git('ls-files', '--others', '--exclude-standard').splitlines()
    allowed = lambda p: p in GUIDANCE or p == 'benchmark/results/phase6/R6_4-REPORT.md' or p.startswith('benchmark/results/phase6/r6_4/')
    assert all(allowed(p) for p in changed + staged + untracked), 'Out-of-scope change'
    inventory = {}
    for name, ranges in EVIDENCE.items():
        lines = (ROOT / name).read_text(encoding='utf-8').splitlines()
        inventory[name] = {'file_sha256': sha(ROOT / name), 'excerpts': [
            {'first_line': start, 'last_line': end, 'text': '\n'.join(lines[start-1:end])}
            for start, end in ranges]}
    return identities, original, manifest, inventory, provenance


def publish():
    identities, original, manifest, inventory, provenance = verify()
    now = (load(HERE / 'RESEARCH-APPROVAL-RECEIPT.json')['recorded_at_utc']
           if (HERE / 'RESEARCH-APPROVAL-RECEIPT.json').exists()
           else datetime.now(timezone.utc).isoformat())
    save('RESEARCH-APPROVAL-RECEIPT.json', {
        'version': 'R6.4-research-approval-receipt-1', 'requirement': 'P6-A04/pypa/pip#13139',
        'recorded_at_utc': now,
        'timestamp_basis': 'Agent UTC recording time, not a human signing timestamp',
        'human_statement_file': 'AUTHORIZATION.md', 'human_statement_utf8_sha256': sha(HERE / 'AUTHORIZATION.md'),
        'statement_preservation': 'User message text retained; line endings normalized to LF',
        'provenance': 'Project owner user message headed R6.4 in current OpenCode conversation; no session identifier supplied; conversation attribution, not cryptographic authentication or pip maintainer endorsement',
        'approved_artifacts_canonical_sha256': identities,
        'conditional_identity_and_provenance_verification': 'PASS',
        'scope': 'Exact artifact approval and bounded static native-readiness investigation/publication only',
        'execution_authorized': False, 'production_authorized': False,
        'local_execution_receipt_created': False,
        'receipt_boundary': 'This records research approval, not local-research-receipt-1; no named execution evaluator or experiment permission inferred',
        'implementation_snapshot_sha256': digest(manifest), 'kernel_constructs': 26,
    })
    save('IDENTITY-PROVENANCE.json', {
        'round': 'R6.4', 'recorded_at_utc': now, 'artifact_identities': identities,
        'original_source': original, 'preserved_provenance': provenance,
        'composite_source_identity': digest(load(PREVIOUS / 'FRC-CANDIDATE.json')['source']),
        'source_and_clarification_bindings': 'PASS', 'procedure_and_observer_bindings': 'PASS',
        'historical_artifacts': 'Unchanged; old approval/status fields remain historical, superseding approval recorded separately',
        'git_head': git('rev-parse', 'HEAD'), 'git_tree': git('rev-parse', 'HEAD^{tree}'),
        'initial_git_status': '', 'initial_status_basis': 'First R6.4 tool command: git status --short, clean',
        'implementation_manifest': manifest, 'implementation_identity': digest(manifest),
        'matches_r6_1_implementation_manifest': True,
        'recording_host': {'system': platform.system(), 'python': platform.python_version(), 'machine': platform.machine()},
        'fixture_environment': 'Not provisioned or executed; recording host is not the approved Linux fixture',
        'semantic_stages': 'NOT_RUN', 'behavioral_acceptance_executions': 0,
        'verification': 'Offline hashes/provenance, artifact bindings, static code excerpts, implementation equality and Git change scope only',
    })
    save('STATIC-EVIDENCE.json', {'method': 'Read-only static inspection; no semantic pipeline invocation', 'files': inventory})
    publications = ['AUTHORIZATION.md', 'record.py', 'RESEARCH-APPROVAL-RECEIPT.json',
                    'IDENTITY-PROVENANCE.json', 'STATIC-EVIDENCE.json', 'CAPABILITY-INVENTORY.md']
    save('PUBLICATION-IDENTITIES.json', {'canonical_sha256': {n: digest(load(HERE / n)) for n in publications if n.endswith('.json')},
        'byte_sha256': {n: sha(HERE / n) for n in publications},
        'report_byte_sha256': sha(HERE.parent / 'R6_4-REPORT.md'),
        'classification': 'R6_4_LYKOI_SEMANTIC_GAP'})
    print('PASS: exact approval/source/bindings, static evidence, implementation/kernel and change scope; acceptance executions 0')


if __name__ == '__main__':
    if sys.argv[1:] == ['publish']:
        publish()
    elif sys.argv[1:] == ['verify']:
        verify()
        pub = load(HERE / 'PUBLICATION-IDENTITIES.json')
        for name, expected in pub['byte_sha256'].items():
            assert sha(HERE / name) == expected
        for name, expected in pub['canonical_sha256'].items():
            assert digest(load(HERE / name)) == expected
        assert sha(HERE.parent / 'R6_4-REPORT.md') == pub['report_byte_sha256']
        print('PASS: publication identities and preservation; no execution')
    else:
        raise SystemExit('Use publish or verify; neither executes the experiment')
