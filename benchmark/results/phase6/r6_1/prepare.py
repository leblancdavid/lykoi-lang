"""Finite R6.1 artifact recorder/verifier. No evaluation or test execution.

Generated JSON is retained research evidence, exclusively created; this is not
an approval service, controller, execution harness or semantic extension.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

from benchmark.evaluation.formal_requirements_r5_80 import digest, validate
from lykoi_research.local import implementation_snapshot

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CURATION = HERE.parent / 'r5_116a'
SOURCE_ID = 'P6-A04/pypa/pip#13139/preserved-body'
GUIDANCE = {'AGENTS.md', 'README.md', 'benchmark/README.md',
            'docs/project-overview.md', 'docs/agent-workflow.md',
            'docs/research-log.md', 'docs/decisions.md'}
REPORT = 'benchmark/results/phase6/R6_1-REPORT.md'
PREFIX = 'benchmark/results/phase6/r6_1/'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, encoding='utf-8').strip()


def save(name, value):
    with (HERE / name).open('x', encoding='utf-8', newline='\n') as out:
        out.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def verify_source():
    p = load(CURATION / 'P6-A04-provenance.json')
    assert (p['repository'], p['issue_number'], p['selection_order']) == ('pypa/pip', 13139, 4)
    assert p['source']['sha256'] == '811cd95034444011f50e13572ebd10c810692b9e26b6355863d1aae3aa1af747'
    for key in ('source', 'issue_api', 'search', 'repository_capture', 'repository_ref_capture', 'acceptance'):
        row = p[key]
        assert row['path'].startswith(('captures/pypa__pip/', 'acceptance/P6-A04'))
        assert sha(CURATION / row['path']) == row['sha256'], key
    s = load(CURATION / p['source']['path'])
    issue = load(CURATION / p['issue_api']['path'])
    repo = load(CURATION / p['repository_capture']['path'])
    ref = load(CURATION / p['repository_ref_capture']['path'])
    for field in ('title', 'body'):
        assert s[field] == issue[field]
        assert hashlib.sha256(s[field].encode('utf-8')).hexdigest() == p[field + '_utf8_sha256']
    assert s['title'] == p['original_title']
    for field, saved in (('number', 'issue_number'), ('id', 'issue_numeric_id'),
                         ('node_id', 'issue_node_id'), ('html_url', 'issue_url'),
                         ('created_at', 'issue_created_at'), ('updated_at', 'issue_updated_at'),
                         ('author_association', 'author_association')):
        assert issue[field] == p[saved]
    assert issue['user']['login'] == p['author_login']
    assert issue['user']['id'] == p['author_numeric_id']
    assert (repo['full_name'], repo['id'], repo['node_id']) == (
        p['repository'], p['repository_numeric_id'], p['repository_node_id'])
    assert ref['object']['sha'] == p['repository_revision_at_retrieval']
    receipt = load(CURATION / 'captures/pypa__pip/candidate-01-issue.receipt.json')
    assert receipt['url'] == 'https://api.github.com/repos/pypa/pip/issues/13139'
    assert receipt['http_status'] == 200 and receipt['sha256'] == p['issue_api']['sha256']
    assert receipt['retrieved_utc'] == p['retrieved_utc']
    assert receipt['policy_commit'] == 'c840083469efc9f94920ebce41103a51092ac915'
    search = load(CURATION / p['search']['path'])
    assert any(row['id'] == p['issue_numeric_id'] and row['number'] == p['issue_number']
               and row['html_url'] == p['issue_url'] for row in search['items'])
    return p, s


def snapshot():
    manifest = implementation_snapshot()
    assert git('rev-parse', 'HEAD') == 'de9f1b67cc614e76e090766434096696e78089d2'
    save('SNAPSHOT.json', {
        'round': 'R6.1', 'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'git_commit': git('rev-parse', 'HEAD'), 'git_tree': git('rev-parse', 'HEAD^{tree}'),
        'initial_git_status': '', 'initial_status_basis': 'First shell command before source reads: git status --short, clean',
        'recording_git_status': git('status', '--short'),
        'chronology': 'Initial Git identity/clean status recorded before P6-A04 access. Full implementation manifest recorded after source reading and before candidate construction; unchanged HEAD content, not a separately timed pre-access manifest.',
        'implementation_manifest': manifest, 'implementation_identity': digest(manifest),
        'kernel_concepts': 26, 'canonical_model': '0.3', 'compiler': '0.3.0',
        'historical_exposed_successes': '16/20 B01-B20; retained, not rerun',
        'local_execution_path': 'R5.120A; unused',
        'model': 'openai/gpt-6.1-sol via OpenCode; session-reported',
        'fresh_tests': 'NOT_RUN: preparation only; no broad qualification',
        'source_exposure': 'Previously exposed curation source; same-agent/model preparation; not blinded or held-out',
        'preserved_source_provenance_sha256': sha(CURATION / 'P6-A04-provenance.json')})


def build():
    p, s = verify_source()
    quote = '`pip` should correctly parse the `install_requires` and install the local wheel, even if its path contains spaces.'
    requirement = 'pipefunc-0.46.0-py3-none-any.whl @ file://$(pwd)/my folder/pipefunc-0.46.0-py3-none-any.whl'
    condition = 'A04-Q1/Q2 input interpretation resolved; accessible genuine source wheel and compatible fixture prerequisites satisfied'
    obligations = []
    for oid, basis, parents, kind, statement, parameters in [
        ('A04-E1', 'STATED', [], 'invariant', 'Parse the approved source-grounded install_requires local-wheel requirement despite a space in its path.',
         {'input_type': 'setup.py install_requires requirement string', 'condition': condition, 'required_observation': 'Requirement identifies the intended local wheel without space-caused parsing rejection'}),
        ('A04-E2', 'STATED', [], 'effects', 'Install the specified local wheel as a dependency of the containing package.',
         {'input_type': 'LocalWheelArtifact + containing package + install invocation', 'condition': condition, 'postcondition_type': 'InstalledEnvironment', 'required_observation': 'Specified local-wheel distribution installed in target environment'}),
        ('A04-I1', 'NECESSARY_IMPLICATION', ['A04-E1'], 'invariant', 'The path space alone must not cause the reported parsing/metadata-generation failure for the approved input.',
         {'condition': condition, 'forbidden_observation': 'Expected end or semicolon (after URL and whitespace) rejection solely because of the path space', 'error_text_policy': 'No byte-exact diagnostic requirement; substantive parsing success required'}),
        ('A04-I2', 'NECESSARY_IMPLICATION', ['A04-E2'], 'effects', 'Install from the designated local wheel, not an unrelated or remote substitute.',
         {'condition': condition, 'artifact_identity': 'Source-designated local wheel; later fixture digest required', 'required_observation': 'Installed dependency corresponds to that wheel', 'network_policy': 'No general no-network requirement'}),
        ('A04-I3', 'NECESSARY_IMPLICATION', ['A04-E1', 'A04-E2'], 'transition', 'The source containing-package installation must complete when other prerequisites are satisfied; parser success alone is insufficient.',
         {'input_type': 'pip install --verbose .', 'precondition': condition, 'postcondition': 'my-local-package 0.1.0 and its designated local dependency installed', 'observation': 'Successful installation outcome and independent installed-state inspection'})]:
        obligations.append({'id': oid, 'basis': basis, 'source_quote': quote, 'derived_from': parents,
                            'relation': {'kind': kind, 'parameters': parameters}, 'statement': statement})
    issues = [
        {'id': 'A04-Q1', 'category': 'AMBIGUITY', 'description': 'Must the raw space in the source file URL be accepted unchanged, or may the approved input encode the space? Encoding is not silently delegated.',
         'affects': [o['id'] for o in obligations], 'alternatives': ['Accept the source raw-space URL unchanged', 'Require a legitimately clarified encoded URL; revise source/contract identities'],
         'witness': {'source_quote': requirement, 'observable_difference': 'Raw-space fixture succeeds versus rejection with only encoded input eligible'}, 'resolved': False},
        {'id': 'A04-Q2', 'category': 'AMBIGUITY', 'description': 'Is the wheel-filename token before @ intentionally required, or may an authoritative clarification replace it with the wheel project name? The source does not establish its validity.',
         'affects': [o['id'] for o in obligations], 'alternatives': ['Retain exact wheel-filename token and require the specified artifact installation', 'Use a clarified project-name token; new linked candidate needed'],
         'witness': {'source_quote': requirement, 'observable_difference': 'Exact original requirement accepted versus original rejected and only corrected name accepted'}, 'resolved': False}]
    frc = {'schema_version': 'FormalRequirementContract-0.1', 'contract_id': 'R6.1/P6-A04/candidate', 'revision': 1,
           'source': {'id': SOURCE_ID, 'text': s['body'], 'sha256': p['body_utf8_sha256'], 'classification': 'PUBLIC'},
           'context': {'scope': 'Research-only source-grounded local-wheel installation delta, conditional on input clarification; no approval or pip implementation.',
                       'domains': {'repository': p['repository'], 'issue': p['issue_number'], 'title': s['title'],
                                   'source_capture_sha256': p['source']['sha256'], 'source_provenance_sha256': sha(CURATION / 'P6-A04-provenance.json'),
                                   'retrieved_utc': p['retrieved_utc'], 'exact_requirement_before_shell_interpolation': requirement,
                                   'source_environment': 'pip 24.3.1; Python 3.13.1; macOS and Ubuntu reported',
                                   'inherited_context': 'Preserved title/body only. No packaging standard, conventional pip behavior, linked issue or fix imported.'},
                       'assumptions': ['Accessible genuine local wheel and otherwise satisfiable containing-package installation are fixture prerequisites, not inferred guarantees for malformed wheels or unrelated dependency failures.',
                                       'The reproduction shell expands $(pwd) before setup.py execution; replacing that placeholder with the working directory preserves the source recipe, not an encoding/name correction.'], 'component_authority': None},
           'obligations': obligations, 'issues': issues,
           'unspecified': ['Exact setuptools/build-backend versions, immutable wheel bytes and transitive dependency fixtures are absent; pin legitimate compatible fixtures before any executable plan approval.',
                           'Failure is observed in setup.py egg_info; source diagnostics attribute it to the package/subprocess. No causal pip-layer fix or permission to bypass backend validation follows.',
                           'No exact exit integer, full verbose output, error wording, rollback, network prohibition, Windows support, restart or arbitrary invalid-input behavior is specified.',
                           'No source-defined universal pip compatibility matrix, no-space control output or unrelated package preservation guarantee.'],
           'implementation_choices': ['Internal algorithm, language, data structures and organization are delegated subject to approved observable behavior.',
                                      'Parser/build/installer responsibility may be chosen without changing the required end-to-end input/output contract; no particular layer is mandated.',
                                      'Fixture absolute directory and observation method may vary faithfully; URL spelling and requirement-name acceptance are material, not implementation freedoms.'],
           'lineage': [], 'formalizer': 'OpenCode/openai/gpt-6.1-sol/R6.1/same-agent-candidate', 'review': None}
    commitment = validate(frc)
    save('FRC-CANDIDATE.json', frc)
    checks = []
    for tid, ids, inputs, observation, expected, effects, error in [
        ('A04-T1', ['A04-E1', 'A04-I1'], ['Exact source setup.py with shell-expanded working directory and raw-space local file URL', 'Accessible source-designated wheel under my folder', 'pip install --verbose .'],
         'Requirement parsing and metadata preparation outcome', 'No space-caused parsing rejection for the clarified accepted input', 'Parsing alone does not establish installation; T2 observes target state', 'Reported requirement parsing/metadata failure must not occur solely due to the space'),
        ('A04-T2', ['A04-E2', 'A04-I2', 'A04-I3'], ['T1 source recipe in isolated target environment with all other prerequisites satisfied', 'Locally pinned source-designated wheel; no preinstalled dependency masking installation'],
         'Install outcome and independently inspected containing-package/dependency state and local-artifact correspondence', 'Containing package my-local-package 0.1.0 and designated local wheel installed; no remote or wrong-artifact substitute', 'Target environment gains containing package and designated dependency; source files need no modification to satisfy the accepted-input branch', 'No successful verdict from parsing alone; unrelated errors have no invented expected outcomes'),
        ('A04-T3', ['A04-E1', 'A04-I1', 'A04-E2', 'A04-I2', 'A04-I3'], ['Compare original raw-space URL with a space-encoded URL while holding artifact and name constant'],
         'Which input is required to parse and install', None, 'Installation effects required only for a clarified eligible input', 'No pass/fail expectation for the excluded spelling without authority'),
        ('A04-T4', ['A04-E1', 'A04-E2', 'A04-I1', 'A04-I2', 'A04-I3'], ['Compare original wheel-filename token before @ with an authoritatively clarified project-name token while holding URL/artifact constant'],
         'Which name spelling is required to parse and select/install the wheel', None, 'Correct designated artifact required in either clarified successful branch', 'No rejection or success oracle for the alternate name is supplied by the issue')]:
        checks.append({'id': tid, 'obligations': ids, 'source_quote': quote if tid in ('A04-T1', 'A04-T2') else requirement,
                       'inputs': inputs, 'observable': observation, 'expected': {'selected_expectation': expected, 'condition': 'Resolve A04-Q1 and A04-Q2 and pin fixture prerequisites',
                       'alternatives': [i['alternatives'] for i in issues] if expected is None else []},
                       'state_effects': effects, 'error_behavior': error, 'status': 'CONDITIONAL_NOT_RUN'})
    plan = {'candidate_id': 'R6.1/P6-A04/acceptance-candidate/1', 'purpose': 'research-evaluation-only',
            'status': 'CANDIDATE_CLARIFICATION_REQUIRED_NOT_EXECUTABLE', 'fixed_before_authoring': True, 'expectation_basis': 'preserved-source',
            'source': {'id': SOURCE_ID, 'capture_sha256': p['source']['sha256'], 'body_sha256': p['body_utf8_sha256']},
            'frc': {'candidate_id': frc['contract_id'], 'revision': 1, 'canonical_sha256': commitment},
            'independence': {'generated_implementation_access': False, 'review_context': 'SAME_AGENT', 'same_model': True,
                             'cognitive_independence': 'NOT_ESTABLISHED', 'role_separation': 'Unregistered source-only preparation; no verifier credential fabricated'},
            'checks': checks, 'fixture': {'prerequisites': frc['context']['assumptions'],
                                        'unfixed': 'Wheel URL preserved, not fetched. Wheel/backend/dependency hashes and compatible versions not provided; must be fixed before executable acceptance.',
                                        'reported_platforms': ['macOS', 'Ubuntu'], 'platform_limit': 'Reported environments are source context, not an exhaustive platform guarantee'},
            'preservation_requirements': ['Keep the designated local artifact and containing-package recipe in the exact-input interpretation; accepting a different package is not success.',
                                         'Retain the intended path including its space and local-wheel selection; no renaming directory as a workaround.',
                                         'No blanket no-space/invalid-requirement/unrelated pip behavior is inferred; controlled comparisons are conditional, not invented regression oracles.'],
            'coverage_limitations': ['Four proposed groups, all conditional, zero executed; not a complete executable research_plan.',
                                     'No universal package-manager correctness, pip backend responsibility, upstream endorsement or held-out generalization established.',
                                     'Same-agent/model source interpretation; acceptance independent of generated software, not independent cognition.',
                                     'No native payload; clarified exact expectations and fixture identities require a newly bound plan/review before approval or evaluation.'],
            'native_plan': None, 'approved': False, 'sealed': False}
    save('ACCEPTANCE-PLAN-CANDIDATE.json', plan)
    save('SOURCE-VERIFICATION.json', {'status': 'PASS', 'provenance': p, 'provenance_file_sha256': sha(CURATION / 'P6-A04-provenance.json'),
                                    'method': 'Saved capture/raw issue/repository/ref/search hashes and issue/title/body/author identity equality; no network access',
                                    'revision_limit': p['source_revision_basis'], 'newer_content_or_solution_access': False})


def verify():
    p, s = verify_source()
    snap = load(HERE / 'SNAPSHOT.json')
    assert git('rev-parse', 'HEAD') == snap['git_commit']
    assert implementation_snapshot() == snap['implementation_manifest']
    assert digest(implementation_snapshot()) == snap['implementation_identity']
    assert sha(CURATION / 'P6-A04-provenance.json') == snap['preserved_source_provenance_sha256']
    frc = load(HERE / 'FRC-CANDIDATE.json')
    fid = validate(frc)
    assert frc['source']['text'] == s['body'] and frc['review'] is None
    assert [i['id'] for i in frc['issues']] == ['A04-Q1', 'A04-Q2']
    plan = load(HERE / 'ACCEPTANCE-PLAN-CANDIDATE.json')
    assert plan['frc']['canonical_sha256'] == fid
    assert plan['source']['capture_sha256'] == p['source']['sha256']
    assert plan['source']['body_sha256'] == p['body_utf8_sha256']
    assert plan['fixed_before_authoring'] and plan['expectation_basis'] == 'preserved-source'
    assert plan['approved'] is False and plan['sealed'] is False and plan['native_plan'] is None
    assert {o['id'] for o in frc['obligations']} == {o for c in plan['checks'] for o in c['obligations']}
    assert len({c['id'] for c in plan['checks']}) == len(plan['checks']) == 4
    for c in plan['checks']:
        assert c['source_quote'] in s['body'] and c['status'] == 'CONDITIONAL_NOT_RUN'
        assert c['inputs'] and c['observable'] and c['state_effects'] and c['error_behavior']
    assert all(c['expected']['selected_expectation'] is None for c in plan['checks'][2:])
    changed = git('diff', '--name-only', 'HEAD').splitlines()
    untracked = git('ls-files', '--others', '--exclude-standard').splitlines()
    assert all(p in GUIDANCE or p == REPORT or p.startswith(PREFIX) for p in changed + untracked), (changed, untracked)
    # Git compares all preserved tracked history without opening any other source.
    assert not git('diff', '--name-only', 'HEAD', '--', 'src', 'schema', 'air', 'generated', 'tests',
                   'benchmark/evaluation', 'benchmark/harness', 'benchmark/conventional', 'benchmark/requirements',
                   'benchmark/results/phase5c', 'benchmark/results/phase6/r5_*', 'benchmark/results/phase6/R5*')
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    for name in untracked:
        lines = (ROOT / name).read_text(encoding='utf-8').splitlines()
        assert all(line == line.rstrip() for line in lines), name
    identities = {'source_capture_sha256': p['source']['sha256'], 'title_utf8_sha256': p['title_utf8_sha256'],
                  'body_utf8_sha256': p['body_utf8_sha256'], 'frc_source_record_canonical_sha256': digest(frc['source']),
                  'frc_canonical_sha256': fid, 'frc_file_sha256': sha(HERE / 'FRC-CANDIDATE.json'),
                  'acceptance_plan_canonical_sha256': digest(plan), 'acceptance_plan_file_sha256': sha(HERE / 'ACCEPTANCE-PLAN-CANDIDATE.json'),
                  'review_files_sha256': {n: sha(HERE / n) for n in ('HUMAN-REVIEW.md', 'MATERIAL-CLARIFICATION.md')},
                  'frc_envelope': 'VALID_NOT_APPROVED', 'historical_preservation': 'PASS_GIT_UNCHANGED',
                  'implementation_unchanged': True, 'external_checks_executed': 0,
                  'classification': 'R6_1_P6_A04_RESEARCH_REVIEW_PREPARED'}
    identities['research_approval_preparation'] = {
        'model': 'R5.118A research-evaluation-only; R5.120A available for separately authorized local execution',
        'decision_recipient': 'Project owner, explicitly named by current user instruction',
        'decision': 'NOT_GIVEN', 'approved': False, 'sealed': False,
        'material_questions': ['A04-Q1', 'A04-Q2'],
        'evaluator': 'NOT_DESIGNATED; bind in subsequent exact approval',
        'source_identity': identities['frc_source_record_canonical_sha256'],
        'frc_identity': fid, 'acceptance_identity': identities['acceptance_plan_canonical_sha256'],
        'review_file_sha256': identities['review_files_sha256']['HUMAN-REVIEW.md'],
        'requires_new_identities_before_execution': 'Resolve material questions and fix compatible fixture/executable acceptance; preserve this preparation',
        'upstream_maintainer_approval_required': False, 'production_authorized': False}
    if '--publish' in sys.argv:
        save('IDENTITIES.json', identities)
    else:
        assert load(HERE / 'IDENTITIES.json') == identities
    print(json.dumps(identities, indent=2))


if __name__ == '__main__':
    {'snapshot': snapshot, 'build': build, 'verify': verify}[sys.argv[1]]()
