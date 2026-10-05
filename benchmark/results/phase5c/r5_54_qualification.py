"""Fresh successor/capsule/certificate preflight; fail closed before observation.

Uses existing R5.51 mechanisms unchanged. No request loader, B02 evaluation,
historical evidence reuse, or certificate-policy adapter is provided.
"""

from collections import Counter
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import authority_r5_53 as authority
from benchmark.evaluation import checkout_r5_52 as checkout
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, ProtocolFailure

RESULTS = ROOT / 'benchmark/results/phase5c'
OUT = Path(os.environ.get('LYKOI_R551_EVIDENCE', str(RESULTS / 'R5_54-evidence'))).resolve()
WORK = Path('C:/Users/lblan/AppData/Local/Temp/opencode/r554-cooperative-workspace')
TRUSTED = '5dd2e7e645c1736f23a80bff755d347da5688cc9e8b7f7df515bd7110d1534ea'
EXPERIMENT = 'R5.54-fresh-production-tier2-qualification-v1'
DRIVER = 'benchmark/results/phase5c/r5_54_qualification.py'
BASELINE = 'benchmark/results/phase5c/R5_53-authority-successor-v1.json'

BLOCKED = (
    'restricted-harness', 'compiler-application', 'r541-focused', 'recorder',
    'certificate-mechanisms', 'security', 'methodology', 'tier2-mechanisms',
    'ai-independence', 'git-independent-core', 'matrix-coherence', 'schema',
    'traceability', 'dependency-review', 'validation', 'safety',
    'production-pre-observation', 'synthetic-reservation', 'synthetic-dispatch',
    'synthetic-completion', 'post-observation', 'second-observation-prevention',
    'no-repair-enforcement', 'secret-safety-regressions',
)


def write(name, value):
    security.persist(OUT / (name + '.json'), value)


def read(name):
    raw = (OUT / (name + '.json')).read_bytes()
    value = loads(raw)
    if raw != canonical(value) + b'\n':
        raise ProtocolFailure('noncanonical R5.54 evidence')
    return value


def boundary():
    # Historical result inputs are consumed by regression fixtures. Outputs remain
    # in the original checkout, outside this dedicated input/import/discovery tree.
    from benchmark.results.phase5c.r5_51_qualification import boundary as original
    policy = original()
    policy['scopes']['evaluator'].append(DRIVER)
    policy['scopes']['authority'].extend([BASELINE, 'docs/authority-successor-r5.53.md'])
    policy['production_authority_successor'] = TRUSTED
    policy['purpose'] = 'R5.54 production qualification only; synthetic observation only after certification'
    policy['checkout_interpretation'] = 'R5.53 repository identity; physical capsule and separate representation receipt'
    return policy


def capture():
    tool = shutil.which('git')
    version = subprocess.check_output([tool, '--version'], timeout=10).decode().strip()
    resolved = tier.dependency('git', version, tool, 'experimental content/index and provenance inspection only')
    return tier.capture(WORK, boundary(), tier.controlled_environment(os.environ, WORK), tools=[resolved])


def anchor():
    baseline = authority.reload(WORK / BASELINE)
    assert baseline['identity'] == TRUSTED
    tree = checkout.tree(WORK, baseline['head'])
    blobs = checkout.blobs(WORK, [r['blob'] for r in baseline['members'].values() if r['blob']])
    repository = {}
    for name, row in baseline['members'].items():
        if row['blob'] is None:
            assert name in baseline['authorized_additions'] and row['mode'] == '100644'
            data = (WORK / name).read_bytes()
        else:
            assert tree[name] == {'mode': row['mode'], 'blob': row['blob']}
            data = blobs[row['blob']]
        repository[name] = {'content': data, 'mode': row['mode'], 'blob': row['blob']}
    representation = authority.verify(WORK, baseline, repository, trusted_identity=TRUSTED)
    metadata = {k: v for k, v in baseline.items() if k not in ('members', 'identity', 'protocol')}
    assert authority.build(repository, metadata) == baseline
    assert authority.reload(WORK / BASELINE) == baseline
    assert subprocess.run(['git', '--no-replace-objects', 'merge-base', '--is-ancestor',
                           baseline['head'], 'HEAD'], cwd=WORK, timeout=10, capture_output=True).returncode == 0
    adjudication = loads((WORK / 'benchmark/results/phase5c/R5_53-evidence/adjudication.json').read_bytes())
    assert digest(canonical(adjudication)) == baseline['reconciliation_sha256']
    decision = (WORK / 'docs/authority-successor-r5.53.md').read_bytes()
    assert digest(decision) == baseline['decision_sha256']
    for row in adjudication['files']:
        assert row['historical_preimage_status'] == 'HISTORICAL_PREIMAGE_UNAVAILABLE'
        assert row['disposition'] == 'CURRENT_STATE_PROVEN_AUTHORIZED'
        assert not row['frozen_behavioral_authority']
        assert baseline['members'][row['path']]['sha256'] == row['current_repository_sha256']
        for link in row['current_provenance']:
            if link['kind'] == 'decision':
                data = decision
            else:
                data = checkout.git(WORK, 'show', link['source'])
            assert digest(data) == link['source_sha256']
    historical = []
    for previous in baseline['predecessors']:
        data = (WORK / 'benchmark/results/phase5c' / previous['path']).read_bytes()
        assert digest(data) == previous['raw_sha256']
        assert previous['historical_physical_status'] == 'FAIL'
        lock = loads(data)
        assert subprocess.run(['git', '--no-replace-objects', 'merge-base', '--is-ancestor',
                               lock['head'], baseline['head']], cwd=WORK,
                              timeout=10, capture_output=True).returncode == 0
        matches = sum(digest((WORK / n).read_bytes()) == h for n, h in lock['files'].items())
        assert matches == 145
        historical.append({'path': previous['path'], 'status': 'FAIL', 'matching': matches,
                           'members': len(lock['files']), 'production_requirement': False})
    for name, pin in baseline['frozen_authority'].items():
        assert digest(repository[name]['content']) == pin
    attrs = checkout.attributes(WORK, sorted(repository))
    assert all(r['filter'] == 'unspecified' and r['working-tree-encoding'] == 'unspecified'
               for r in attrs.values())
    controls = subprocess.run(['git', 'config', '--show-origin', '--get-regexp',
                              r'core\.(autocrlf|eol|safecrlf|attributesfile)'], cwd=WORK,
                             capture_output=True, timeout=10)
    assert controls.returncode in (0, 1)
    write('checkout-representation', {'receipt': representation, 'attributes': attrs,
                                    'effective_eol_settings': controls.stdout.decode(),
                                    'capsule_physical_bytes_are_separate': True})
    return {'successful': True, 'authority_successor': TRUSTED, 'members': len(repository),
            'canonical_reload': True, 'deterministic_reproduction': True, 'ancestry': True,
            'provenance_links': True, 'frozen_pins': baseline['frozen_authority'],
            'checkout_relationships': dict(Counter(r['relationship'] for r in representation['members'].values())),
            'historical_locks': historical, 'historical_failures_preserved': True,
            'historical_preimages_recovered': 0, 'current_versions_authorized': 8}


def initialize():
    assert OUT.parent.is_dir() and not OUT.exists() and WORK.parent.is_dir() and not WORK.exists()
    OUT.mkdir()
    # Snapshot every pre-existing benchmark evidence file, including all 81 R5.51
    # receipts; never overwrite or publish into a historical round's directory.
    historical = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes())
                  for p in (ROOT / 'benchmark/results').rglob('*') if p.is_file()
                  and OUT not in p.parents and '__pycache__' not in p.parts
                  and p.name != Path(__file__).name}
    write('initial', {'historical': historical, 'b02_exposure': 0, 'core_semantics': 30})
    materialization = tier.Workspace.materialize(ROOT, WORK, boundary()['scopes'])
    # Initial snapshot was included as an untracked relevant result input; all
    # subsequent original-checkout output stays outside the captured workspace.
    write('materialization', materialization)
    print({'materialized_files': len(materialization['files']), 'b02_exposure': 0})


def qualify():
    assert not (OUT / 'summary.json').exists()
    workspace = tier.Workspace(WORK, OUT / 'production-gate', EXPERIMENT)
    workspace.evidence.mkdir(exist_ok=False)
    marker = workspace.enter()
    before = capture()
    write('capsule', before)
    anchor_result = anchor()
    after = capture()
    assert before == after == loads(canonical(before))
    write('authority', tier.receipt(before, after, EXPERIMENT, 'authority',
                                   digest(canonical({'driver': DRIVER, 'stage': 'authority'})), 'PASS', anchor_result))
    write('capsule-verification', {'status': 'PASS', 'identity': before['identity'],
                                  'deterministic_capture': True, 'canonical_round_trip': True,
                                  'platform': before['platform'], 'production_qualified': False})
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    from benchmark.results.phase5c.r5_43_qualification import contamination
    findings = contamination()
    assert findings['findings'] == [] and SCHEMA['core_constructs'] == 30
    policy = {'experiment': EXPERIMENT, 'infrastructure': TRUSTED,
              'semantic_count': 30, 'canonical_protocol': tier.CANONICAL_PROTOCOL,
              'authority': before['roles']['authority'], 'authority_successor': TRUSTED,
              'recorder': before['policy']['recorder'],
              'stages': {n: digest(canonical({'driver': DRIVER, 'stage': n})) for n in tier.REQUIRED},
              'required_locks': {'authority_successor': TRUSTED}}
    results = {'identity': {'successful': True, 'semantic_count': SCHEMA['core_constructs']},
               'locks': {'successful': True, 'required_lock_state': policy['required_locks'],
                         'authority_verification_receipt': read('authority')['identity']},
               'contamination': {'successful': True, 'findings': findings['findings']},
               'workspace': {'successful': True, 'dedicated': marker['dedicated']}}
    evidence = {n: tier.receipt(before, capture(), EXPERIMENT, n, policy['stages'][n], 'PASS', r)
                for n, r in results.items()}
    for name, value in evidence.items():
        write('preflight-' + name, value)
    # Actual compatibility preflight, NOT a claim of complete regression receipts.
    # Correct successor identity cannot be admitted by the existing fixed policy.
    try:
        tier.certificate(before, evidence, policy)
    except ProtocolFailure as error:
        reason = str(error)
    else:
        raise ProtocolFailure('unexpected successor certificate acceptance')
    assert reason == 'certificate policy incomplete or incompatible'
    # Isolate the second constraint: keeping the old implementation identity does
    # not admit the successor lock set either. Never claim old locks passed.
    compatibility = {**policy, 'infrastructure': tier.INFRASTRUCTURE}
    try:
        tier.certificate(before, evidence, compatibility)
    except ProtocolFailure as error:
        lock_reason = str(error)
    else:
        raise ProtocolFailure('unexpected successor lock-set acceptance')
    assert lock_reason == 'required locks not established'
    after = capture()
    assert before == after
    failure = {'successful': False, 'reason': reason, 'lock_set_probe_reason': lock_reason,
               'policy': policy, 'receipts': evidence,
               'implementation_infrastructure_pin': tier.INFRASTRUCTURE,
               'required_implementation_lock_names': ['historical', 'prospective', 'infrastructure'],
               'regression_receipts_complete': False, 'production_certificate_issued': False,
               'smallest_failure': 'existing certificate cannot express qualified R5.53 successor authority',
               'no_historical_lock_pass_claimed': True}
    write('certificate', tier.receipt(before, after, EXPERIMENT, 'certificate',
                                    digest((WORK / 'benchmark/evaluation/tier2_r5_51.py').read_bytes()), 'FAIL', failure))
    write('terminal-stop', {'status': 'FAIL', 'reason': failure['smallest_failure'],
                            'reservation': 0, 'dispatch': 0, 'completion': 0,
                            'repair_permitted': False, 'retry_permitted': False, 'b02_exposure': 0})
    stages = {'authority-successor': 'PASS', 'historical-preservation': 'PASS',
              'capsule-capture': 'PASS', 'checkout-representation': 'PASS',
              'workspace-setup': 'PASS', 'semantic-count': 'PASS', 'contamination': 'PASS',
              'production-certificate-compatibility': 'FAIL',
              **{n: 'INCOMPLETE' for n in BLOCKED}}
    write('summary', {'primary_classification': 'R5_54_PRODUCTION_CERTIFICATE_GAP',
                      'stages': stages, 'capsule': before['identity'], 'authority': TRUSTED,
                      'required_receipts_complete': False, 'production_qualified': False,
                      'production_certificate_issued': False, 'synthetic_observations_completed': 0,
                      'b02_exposure': 0, 'core_semantics': 30, 'phase5c': 'paused',
                      'blocked_reason': 'qualification stopped on fresh certificate compatibility failure',
                      'publication': 'all new structured evidence guarded before persistence; no raw worker logs'})
    print({'classification': 'R5_54_PRODUCTION_CERTIFICATE_GAP', 'reason': failure['smallest_failure'],
           'capsule': before['identity'], 'production_observations': 0})


def final():
    initial = read('initial')
    differences = [n for n, h in initial['historical'].items() if digest((ROOT / n).read_bytes()) != h]
    assert not differences
    assert capture() == read('capsule')
    artifacts = {}
    for path in OUT.rglob('*.json'):
        raw = path.read_bytes()
        value = loads(raw)
        assert raw == canonical(value) + b'\n'
        security.safe_bytes(value)
        artifacts[path.relative_to(OUT).as_posix()] = digest(raw)
    result = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, timeout=10)
    assert result.returncode == 0
    assert not list((OUT / 'production-gate').glob('*reservation*'))
    assert not list((OUT / 'production-gate').glob('*observation*'))
    write('final-integrity', {'status': 'PASS', 'historical_files_unchanged': len(initial['historical']),
                             'evidence_sha256': artifacts, 'capsule_unchanged': True,
                             'git_diff_check': 'PASS', 'b02_exposure': 0,
                             'production_qualification': False, 'synthetic_observations_completed': 0})
    print({'integrity': 'PASS', 'historical_files_unchanged': len(initial['historical']),
           'git_diff_check': 'PASS'})


if __name__ == '__main__':
    {'initialize': initialize, 'qualify': qualify, 'final': final}[sys.argv[1]]()
