"""Finite preparation and offline identity checks; no semantic or install execution."""
import copy
import hashlib
import io
import json
from datetime import datetime, timezone
from email.parser import BytesParser
from pathlib import Path
import subprocess
import sys
import urllib.request
import zipfile

from benchmark.results.phase6.r6_1.prepare import (
    ROOT, digest, git, implementation_snapshot, load, sha, validate, verify_source,
)
from benchmark.evaluation.formal_requirements_r5_80 import check_revision

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'r6_1'
STATEMENT = ('For P6-A04 (pypa/pip#13139), I authorize the following bounded research '
             'clarification, without claiming pip maintainer intent. Q1: Require the '
             'exact raw-space file:// URL from the preserved issue. Q2: Require the '
             'exact wheel-filename token before @ from the preserved issue.')
REQUIREMENT = 'pipefunc-0.46.0-py3-none-any.whl @ file://$(pwd)/my folder/pipefunc-0.46.0-py3-none-any.whl'
WORKDIR = '/tmp/lykoi-r6-3-p6-a04'
WHEEL_URL = ('https://files.pythonhosted.org/packages/67/d2/'
             '3eb2021d2e0329c96c92f78e98c92bc9dbdfa94b647ddbf9f625567aa8db/'
             'pipefunc-0.46.0-py3-none-any.whl')
CLASSIFICATION = 'R6_3_P6_A04_CLARIFIED_RESEARCH_CONTRACT_READY'


def save(name, value):
    if (HERE / name).exists():
        assert load(HERE / name) == value, 'Refuse to overwrite existing evidence: ' + name
        return
    with (HERE / name).open('x', encoding='utf-8', newline='\n') as out:
        out.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def fetch(url):
    with urllib.request.urlopen(url, timeout=90) as response:
        return response.read()


def wheel_record(url, filename, role, expected=None):
    data = fetch(url)
    identity = hashlib.sha256(data).hexdigest()
    if expected:
        assert identity == expected
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        metadata_name, = [n for n in archive.namelist()
                          if n.endswith('.dist-info/METADATA') and n.count('/') == 1]
        metadata = archive.read(metadata_name)
        header = BytesParser().parsebytes(metadata)
        payload = {n: hashlib.sha256(archive.read(n)).hexdigest()
                   for n in archive.namelist() if not n.endswith('/') and '.dist-info/' not in n}
    return {'filename': filename, 'url': url, 'sha256': identity, 'size': len(data),
            'role': role, 'distribution': header['Name'], 'version': header['Version'],
            'requires_python': header['Requires-Python'],
            'requires_dist': header.get_all('Requires-Dist', []),
            'metadata_sha256': hashlib.sha256(metadata).hexdigest(),
            'installed_payload_sha256': payload,
            'inspection': 'ZIP metadata/payload hashes only; no package execution or solution inspection'}


def build():
    p, source = verify_source()
    prior = load(OLD / 'FRC-CANDIDATE.json')
    assert validate(prior) == 'ec79136bf1c1bcee109e9d739299bd594587029c6b70203fcac1a768edc801a0'
    now = datetime.now(timezone.utc).isoformat()
    if (HERE / 'HUMAN-CLARIFICATION.json').exists():
        now = load(HERE / 'HUMAN-CLARIFICATION.json')['recorded_at_utc']
    original = {'id': prior['source']['id'], 'capture_sha256': p['source']['sha256'],
                'body_sha256': p['body_utf8_sha256'], 'source_record_sha256': digest(prior['source']),
                'provenance_sha256': sha(HERE.parent / 'r5_116a/P6-A04-provenance.json')}
    clarification = {
        'id': 'R6.3/P6-A04/human-clarification/1', 'human_statement': STATEMENT,
        'decisions': {'A04-Q1': 'Accept exact raw-space file:// URL after source shell expansion.',
                      'A04-Q2': 'Accept exact wheel-filename token before @.'},
        'original_source': original,
        'previous_candidate': {'contract_id': prior['contract_id'], 'revision': 1,
                               'canonical_sha256': digest(prior)},
        'recorded_at_utc': now,
        'timestamp_basis': 'Agent observation/recording time; human message has no supplied signing timestamp.',
        'purpose': 'bounded-local-research-only',
        'conversation_provenance': {'speaker': 'Project owner, as identified by user instruction',
            'message_heading': 'R6.3 — P6-A04 Human-Clarified FRC and Acceptance Plan',
            'location': 'Section 1. Exact human clarification, current user message in this OpenCode conversation',
            'session_identifier': 'Not supplied by harness', 'attribution': 'Conversation provenance only; not cryptographic authentication'},
        'artifact_approval': 'NOT_GIVEN; exact revised artifacts require a subsequent human interaction',
        'pip_maintainer_endorsement': False, 'production_authorized': False,
    }
    save('HUMAN-CLARIFICATION.json', clarification)
    designated = wheel_record(WHEEL_URL, 'pipefunc-0.46.0-py3-none-any.whl', 'designated-source-dependency',
                              'bd1bc99a9788f01d218d83a0389ebb17e740b0cab60e7ac57d8d3c0d51f28181')
    artifacts = [designated]
    for name, version, filename in [
        ('pip', '24.3.1', 'pip-24.3.1-py3-none-any.whl'),
        ('setuptools', '75.6.0', 'setuptools-75.6.0-py3-none-any.whl'),
        ('wheel', '0.45.1', 'wheel-0.45.1-py3-none-any.whl'),
        ('cloudpickle', '3.1.0', 'cloudpickle-3.1.0-py3-none-any.whl'),
        ('networkx', '3.4.2', 'networkx-3.4.2-py3-none-any.whl'),
        ('numpy', '2.2.1', 'numpy-2.2.1-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl'),
    ]:
        url = f'https://pypi.org/pypi/{name}/{version}/json'
        release_bytes = fetch(url)
        release = json.loads(release_bytes)
        row, = [r for r in release['urls'] if r['filename'] == filename]
        artifact = wheel_record(row['url'], filename,
                                'bootstrap-tool' if name in ('pip', 'setuptools', 'wheel') else 'transitive-prerequisite',
                                row['digests']['sha256'])
        artifact['release_metadata'] = {'url': url, 'response_sha256': hashlib.sha256(release_bytes).hexdigest()}
        artifacts.append(artifact)
    exact = REQUIREMENT.replace('$(pwd)', WORKDIR)
    setup = ('from setuptools import setup\n\nsetup(\n'
             '    name="my-local-package",\n    version="0.1.0",\n'
             f'    install_requires=[\n        "{exact}"\n    ],\n'
             '    py_modules=["my_module"],\n)\n')
    fixture = {'id': 'R6.3/P6-A04/fixture/1', 'original_source': original,
        'human_clarification_sha256': digest(clarification), 'recorded_at_utc': now,
        'containing_package': {'name': 'my-local-package', 'version': '0.1.0', 'module': 'my_module',
            'setup_py_utf8': setup, 'setup_py_sha256': hashlib.sha256(setup.encode()).hexdigest(),
            'my_module_py_utf8': '', 'my_module_py_sha256': hashlib.sha256(b'').hexdigest()},
        'requirement_before_shell_expansion': REQUIREMENT, 'requirement_after_shell_expansion': exact,
        'absolute_workdir': WORKDIR, 'local_wheel_path': WORKDIR + '/my folder/' + designated['filename'],
        'environment': {'python': 'CPython 3.13.1, non-free-threaded', 'platform': 'Ubuntu 24.04 Linux x86_64, glibc >= 2.17',
            'target': 'Fresh venv without system site packages', 'build_backend': 'setuptools 75.6.0 with wheel 0.45.1',
            'installer_baseline': 'pip 24.3.1',
            'compatibility_basis': 'Declared Python support and wheel tags inspected; ordinary setup.py/build compatibility only, not proof of clarified syntax acceptance.',
            'execution_subject': 'Later separately authorized candidate must handle this exact declaration through the containing-package workflow; stock baseline is not claimed to pass.',
            'scope': 'Version/platform constraints are research fixture choices, not machine qualification or a universal compatibility contract'},
        'artifacts': artifacts,
        'dependency_isolation': {'preinstall_allowed': ['pip', 'setuptools', 'wheel', 'cloudpickle', 'networkx', 'numpy'],
            'must_be_absent_before': ['pipefunc', 'my-local-package'], 'extras': [],
            'wheelhouse_excludes': ['pipefunc'], 'network_during_install': 'disabled as a fixture control, not a product requirement',
            'reason': 'Satisfy only unrelated prerequisites; designated dependency must be installed by the containing-package command.'},
        'source_dictated': ['containing name/version/module', 'wheel URL/filename', 'my folder', 'dependency template', 'pip install --verbose .'],
        'research_choices': ['absolute workdir', 'Linux platform', 'tool/transitive versions', 'venv isolation', 'offline wheelhouse', 'observation procedure'],
        'fixture_execution': 'NOT_RUN; artifacts fetched in memory for identity/metadata only, no installation/build',
        'remaining_material_identity_limitations': [],
    }
    save('FIXTURE-MANIFEST.json', fixture)
    frc = copy.deepcopy(prior)
    frc['revision'] = 2
    composite = source['body'] + '\n\n--- R6.3 project-owner bounded research clarification (not pip maintainer intent) ---\n' + STATEMENT
    frc['source'] = {'id': 'R6.3/P6-A04/preserved-source-plus-human-clarification', 'text': composite,
                     'sha256': hashlib.sha256(composite.encode()).hexdigest(), 'classification': 'PUBLIC'}
    frc['context']['scope'] = 'Bounded research: exact reported declaration must parse, resolve the designated local wheel and install both distributions through containing-package installation. No artifact approval.'
    frc['context']['domains'].update({'artifact_id': 'R6.3/P6-A04/frc/2', 'original_source': original,
        'human_clarification_sha256': digest(clarification), 'fixture_manifest_sha256': digest(fixture),
        'authority_partition': 'Original five obligations: preserved issue. H1/H2: project-owner research clarification only.'})
    condition = 'Exact source declaration after shell expansion; pinned R6.3 fixture with other prerequisites satisfied'
    for obligation in frc['obligations']:
        params = obligation['relation']['parameters']
        for key in ('condition', 'precondition'):
            if key in params:
                params[key] = condition
        if obligation['id'] == 'A04-I2':
            params['artifact_identity'] = designated['sha256']
            params['required_observation'] = 'Resolve exact local path/digest and install payload corresponding to that wheel'
        frc['lineage'].append({'change': 'meaning_change', 'previous': [obligation['id']], 'current': [obligation['id']],
            'reason': 'Preserve source obligation; refine prior conditional domain with attributed Q1/Q2 clarification and pinned fixture.'})
    for oid, description in [('A04-H1', 'Accept the exact raw-space file:// URL from the preserved declaration; no input percent-encoding.'),
                             ('A04-H2', 'Accept the exact pipefunc-0.46.0-py3-none-any.whl token before @; no input project-name substitution.')]:
        frc['obligations'].append({'id': oid, 'basis': 'STATED', 'source_quote': STATEMENT, 'derived_from': [],
            'relation': {'kind': 'invariant', 'parameters': {'condition': condition, 'authority': 'Human research clarification, not upstream intent',
                'exact_input': exact, 'required_observation': description}}, 'statement': description})
    frc['issues'] = []
    frc['context']['domains']['resolved_questions'] = clarification['decisions']
    frc['unspecified'][0] = 'Pinned execution fixture is a research choice; no empirical installation/backend success yet. Native package-install acceptance integration is not supplied by this preparation.'
    frc['implementation_choices'][-1] = 'Internal layers and algorithms delegated; fixed fixture and exact input may not be corrected, wheel substituted or dependency preinstalled.'
    frc['formalizer'] = 'OpenCode/openai/gpt-6.1-sol/R6.3/same-agent-candidate'
    fid = validate(frc)
    check_revision(prior, frc)
    save('FRC-CANDIDATE.json', frc)
    plan = {'id': 'R6.3/P6-A04/fixed-acceptance/1', 'purpose': 'local-research-only',
        'status': 'FIXED_EXPECTATIONS_NOT_RUN_NOT_APPROVED', 'fixed_before_authoring': True,
        'original_source': original, 'human_clarification_sha256': digest(clarification),
        'frc': {'contract_id': frc['contract_id'], 'revision': 2, 'canonical_sha256': fid},
        'fixture_manifest_sha256': digest(fixture),
        'executable_procedure_file': 'ACCEPTANCE-PROCEDURE.md',
        'executable_procedure_sha256': sha(HERE / 'ACCEPTANCE-PROCEDURE.md'),
        'observation_program_sha256': sha(HERE / 'observe.py'),
        'checks': [
            {'id': 'A04-PARSE', 'obligations': ['A04-E1', 'A04-I1', 'A04-H1', 'A04-H2'],
             'expected': 'Exact unchanged setup input is accepted, dependency metadata prepared without syntax error; metadata identifies the local dependency.',
             'evidence': 'Input byte hashes before/after, containing metadata Requires-Dist and completed metadata stage in install report; no separately normalized parser probe.'},
            {'id': 'A04-RESOLVE', 'obligations': ['A04-I2'],
             'expected': 'Report selects pipefunc 0.46.0 from exact local file path and SHA-256 pinned in fixture.',
             'evidence': 'Installer report download_info URL and archive_info hashes; fail closed if unavailable.'},
            {'id': 'A04-CONTAINING-INSTALL', 'obligations': ['A04-I3'],
             'expected': 'Containing installation command succeeds and my-local-package 0.1.0/my_module is observable in target venv.',
             'evidence': 'Command successful outcome and independent importlib.metadata observation.'},
            {'id': 'A04-DEPENDENCY-INSTALL', 'obligations': ['A04-E2', 'A04-I2'],
             'expected': 'Previously absent pipefunc becomes installed at 0.46.0; installed payload hashes match designated wheel.',
             'evidence': 'Independent pre/post distribution inventory, direct_url local provenance, payload byte comparisons.'},
        ],
        'negative_controls': [{'id': 'A04-N0', 'kind': 'observer/fixture sanity, not extra pip semantics',
            'procedure': 'Before command, assert containing and designated dependency absent; post-state success predicates cannot pass on this fresh environment.',
            'expected': 'Both absent, therefore no successful behavioral verdict before installation.'}],
        'excluded_controls': 'No invented malformed wheel, missing-file, encoded-URL or normalized-name success/rejection oracle; neither alternate spelling is an eligible substitute.',
        'verdict': 'PASS only if all four checks pass in the same exact-input run; parsing alone insufficient. Missing observations/setup incompatibility are recorded limitations, not success.',
        'independence': 'Source plus human clarification fixed before authoring; same agent/model, not cognitively independent. No generated software accessed.',
        'native_plan': None,
        'integration_limit': 'Executable shell/observation procedure is fixed; existing native local verifier has no bound package-install payload here. No claim of native execution readiness; later integration needs separate authorization and exact identity approval, without changing expectations.',
        'approved': False, 'sealed': False, 'execution_receipt': None,
    }
    save('ACCEPTANCE-PLAN.json', plan)
    save('SOURCE-VERIFICATION.json', {'original_source': original, 'provenance': p,
        'status': 'PASS', 'newer_issue_or_solution_access': False,
        'network_scope': 'Only source-designated wheel and pinned fixture package release metadata/wheel bytes; no fixing PR/commit or other source.',
        'recorded_at_utc': now})


def verify():
    p, source = verify_source()
    clarification = load(HERE / 'HUMAN-CLARIFICATION.json')
    fixture = load(HERE / 'FIXTURE-MANIFEST.json')
    frc = load(HERE / 'FRC-CANDIDATE.json')
    plan = load(HERE / 'ACCEPTANCE-PLAN.json')
    prior = load(OLD / 'FRC-CANDIDATE.json')
    assert clarification['human_statement'] == STATEMENT
    assert clarification['original_source']['capture_sha256'] == p['source']['sha256']
    assert clarification['previous_candidate']['canonical_sha256'] == validate(prior)
    datetime.fromisoformat(clarification['recorded_at_utc'])
    assert frc['source']['text'] == source['body'] + '\n\n--- R6.3 project-owner bounded research clarification (not pip maintainer intent) ---\n' + STATEMENT
    fid = validate(frc)
    revision = check_revision(prior, frc)
    assert not frc['issues'] and frc['review'] is None
    assert {o['id'] for o in frc['obligations']} == {o for c in plan['checks'] for o in c['obligations']}
    assert len(frc['obligations']) == 7 and len(plan['checks']) == 4
    assert plan['frc']['canonical_sha256'] == fid
    assert plan['human_clarification_sha256'] == fixture['human_clarification_sha256'] == digest(clarification)
    assert plan['fixture_manifest_sha256'] == frc['context']['domains']['fixture_manifest_sha256'] == digest(fixture)
    assert plan['executable_procedure_sha256'] == sha(HERE / 'ACCEPTANCE-PROCEDURE.md')
    assert plan['observation_program_sha256'] == sha(HERE / 'observe.py')
    assert not plan['approved'] and not plan['sealed'] and plan['execution_receipt'] is None
    assert fixture['requirement_before_shell_expansion'] == REQUIREMENT
    assert fixture['requirement_after_shell_expansion'] == REQUIREMENT.replace('$(pwd)', WORKDIR)
    package = fixture['containing_package']
    assert hashlib.sha256(package['setup_py_utf8'].encode()).hexdigest() == package['setup_py_sha256']
    assert fixture['requirement_after_shell_expansion'] in package['setup_py_utf8']
    assert fixture['artifacts'][0]['url'] == WHEEL_URL and WHEEL_URL in source['body']
    assert fixture['artifacts'][0]['sha256'] == 'bd1bc99a9788f01d218d83a0389ebb17e740b0cab60e7ac57d8d3c0d51f28181'
    assert [a['distribution'].lower() for a in fixture['artifacts']] == ['pipefunc', 'pip', 'setuptools', 'wheel', 'cloudpickle', 'networkx', 'numpy']
    assert not fixture['remaining_material_identity_limitations']
    for artifact in fixture['artifacts']:
        assert len(artifact['sha256']) == 64 and artifact['url'].startswith('https://files.pythonhosted.org/')
        assert artifact['installed_payload_sha256'] and artifact['version'] and artifact['filename']
    snapshot = load(OLD / 'SNAPSHOT.json')
    assert implementation_snapshot() == snapshot['implementation_manifest']
    assert digest(implementation_snapshot()) == snapshot['implementation_identity']
    old_ids = load(OLD / 'IDENTITIES.json')
    assert sha(OLD / 'FRC-CANDIDATE.json') == old_ids['frc_file_sha256']
    assert sha(OLD / 'ACCEPTANCE-PLAN-CANDIDATE.json') == old_ids['acceptance_plan_file_sha256']
    for name, expected in old_ids['review_files_sha256'].items():
        assert sha(OLD / name) == expected
    r62 = HERE.parent / 'r6_2'
    for name, expected in load(r62 / 'IDENTITIES.json')['review_files_sha256'].items():
        assert sha(r62 / name) == expected
    allowed = {'AGENTS.md', 'README.md', 'benchmark/README.md', 'docs/project-overview.md',
               'docs/agent-workflow.md', 'docs/research-log.md', 'docs/decisions.md',
               'benchmark/results/phase6/R6_3-REPORT.md'}
    changed = git('diff', '--name-only', 'HEAD').splitlines()
    untracked = git('ls-files', '--others', '--exclude-standard').splitlines()
    assert all(n in allowed or n.startswith('benchmark/results/phase6/r6_3/') for n in changed + untracked)
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    for name in changed + untracked:
        assert all(line == line.rstrip() for line in (ROOT / name).read_text(encoding='utf-8').splitlines()), name
    record = {'round': 'R6.3', 'classification': CLASSIFICATION,
        'git_commit': git('rev-parse', 'HEAD'), 'git_tree': git('rev-parse', 'HEAD^{tree}'),
        'initial_git_status': 'CLEAN, checked before edits/source reads',
        'source_capture_sha256': p['source']['sha256'], 'implementation_identity': snapshot['implementation_identity'],
        'canonical_sha256': {name: digest(load(HERE / name)) for name in
            ('HUMAN-CLARIFICATION.json', 'FRC-CANDIDATE.json', 'ACCEPTANCE-PLAN.json', 'FIXTURE-MANIFEST.json')},
        'files_sha256': {name: sha(HERE / name) for name in
            ('HUMAN-CLARIFICATION.json', 'FRC-CANDIDATE.json', 'ACCEPTANCE-PLAN.json', 'FIXTURE-MANIFEST.json',
             'SOURCE-VERIFICATION.json', 'ACCEPTANCE-PROCEDURE.md', 'observe.py', 'HUMAN-REVIEW.md', 'prepare.py')},
        'report_sha256': sha(HERE.parent / 'R6_3-REPORT.md'),
        'revision_consistency': revision,
        'checks': {k: 'PASS' for k in ('exact_source_provenance', 'exact_clarification', 'frc_envelope',
            'acceptance_bindings', 'fixture_identity_completeness', 'historical_preservation', 'unchanged_implementation', 'whitespace_scope')},
        'frc_approval': 'NOT_GIVEN', 'research_receipt': None, 'evaluation_stages': 'NOT_RUN',
        'acceptance_executions': 0, 'native_execution_integration': 'NOT_PREPARED; disclosed limitation, no infrastructure expansion'}
    if '--publish' in sys.argv:
        save('IDENTITIES.json', record)
    else:
        assert load(HERE / 'IDENTITIES.json') == record
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    {'build': build, 'verify': verify}[sys.argv[1]]()
