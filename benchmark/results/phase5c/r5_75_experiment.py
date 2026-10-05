"""R5.75 structured pre-exposure verification; no protected-content access.

Uses the unchanged qualified runner. A failed prerequisite is terminal.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import phase5_runner_v2 as r

OLD = ROOT / 'benchmark/results/phase5c/R5_74-qualified-evidence'
OUT = ROOT / 'benchmark/results/phase5c/R5_75-evidence'
TRUSTED = 'e9a84957429452ed56138c181143294f9236b86518646346e14f2415cd93c692'


def write(name, value):
    r.persist(OUT / (name + '.json'), r.seal(value))


def preexposure():
    r.require(OUT.parent.is_dir() and not OUT.exists(), 'fresh R5.75 evidence required')
    OUT.mkdir()
    (OUT / 'actual-ledger').mkdir()
    boundary = r.Boundary(ROOT)
    checks = {}
    with boundary.active():
        try:
            state = r.current_state(ROOT)
            r.persist(OUT / 'state.json', state)
            inherited = r.load(OLD / 'state.json')
            r.verify(inherited)
            checks['current_state'] = {'observed': state['identity'], 'inherited': inherited['identity'],
                                       'matches': state == inherited}
            r.require(state == inherited, 'R5.74 CurrentState identity mismatch')
            health = r.load(OLD / 'health.json')
            r.require(r.health_record(state, health['results']) == health, 'inherited health invalid')
            for stage in r.HEALTH_STAGES:
                row = r.load(OLD / ('health-' + stage + '.json'))
                r.require(r.verify(row) == health['results'][stage] and row['protected_read_attempts'] == 0,
                          'inherited health stage mismatch')
            checks['generic_health'] = {'identity': health['identity'], 'status': 'PASS_INHERITED',
                                       'contamination': health['results']['matrix-schema-trace-contamination']}
            summary = r.load(OLD / 'summary.json')
            r.verify(summary)
            r.require(summary['classification'] == 'R5_74_ACTUAL_HELDOUT_PATH_QUALIFIED',
                      'inherited qualification missing')
            for pin in summary['artifact_pins']:
                r.require(pin['path'] not in r.RESOURCE_PATHS, 'protected artifact pin read prohibited')
                r.require(r.digest((ROOT / pin['path']).read_bytes()) == pin['sha256'], 'qualification pin mismatch')
            checks['qualification_artifact_pins'] = 'PASS'
            commitment = r.benchmark_commitment(ROOT)
            r.require(commitment == r.load(OLD / 'b02-metadata-eligibility.json')['benchmark']
                      and r.eligible(commitment, r.ACTUAL_HELD_OUT, TRUSTED), 'trusted B02 metadata mismatch')
            r.persist(OUT / 'commitment.json', commitment)
            checks['commitment'] = commitment
            checks['frozen_pins'] = {name: row['commitment'] for name, row in commitment['resources'].items()
                                     if row['frozen']}
            ledgers = [OUT / 'actual-ledger', OLD / 'b02-ledger',
                       ROOT / 'benchmark/results/phase5c/R5_74-evidence/b02-ledger',
                       ROOT / 'benchmark/results/phase5c/R5_72-qualified-evidence/actual-ledger']
            for path in ledgers:
                r.require(r.Ledger(path).status() == 'zero', 'prior actual ledger nonzero')
            checks['ledgers'] = {str(path): 'zero' for path in ledgers}
            ledger = r.Ledger(OUT / 'actual-ledger')
            frozen = r.freeze(state, commitment, health, ledger)
            r.persist(OUT / 'freeze.json', frozen)
            checks['experiment_freeze'] = frozen
            checks['runner'] = state['runner']
            checks['semantic_count'] = state['semantic_count']
            command = [sys.executable, '-B', '-S', '-m', 'benchmark.evaluation.phase5_runner_v2', 'preflight',
                       '--mode', r.ACTUAL_HELD_OUT, '--trusted-identity', TRUSTED,
                       '--freeze', str(OUT / 'freeze.json'), '--commitment', str(OUT / 'commitment.json'),
                       '--state', str(OUT / 'state.json'), '--ledger', str(ledger.directory)]
            result = subprocess.run(command, cwd=ROOT, env=r.controlled_environment(ROOT),
                                    capture_output=True, timeout=30)
            checks['structured_invocation'] = {'argv': command, 'returncode': result.returncode,
                                                'stdout': result.stdout.decode(), 'stderr': result.stderr.decode()}
            r.require(result.returncode == 0, 'qualified structured preflight failed')
            write('preexposure', {'status': 'PASS', 'checks': checks, 'protected_read_attempts': boundary.attempts,
                                 'controller': r.digest(Path(__file__).read_bytes())})
            print(json.dumps({'preexposure': 'PASS', 'state': state['identity']}))
        except (r.Rejected, OSError, KeyError, ValueError, subprocess.SubprocessError) as exc:
            write('terminal', {'classification': 'R5_75_PREEXPOSURE_HALT', 'reason': str(exc),
                              'checks': checks, 'protected_read_attempts': boundary.attempts,
                              'accounting': {name: 0 for name in ('read_attempts', 'content_reads', 'authorizations',
                                  'opening_reservations', 'openings', 'exposures', 'observation_dispatches',
                                  'observation_completions', 'generation', 'execution', 'frozen_acceptance', 'repair')},
                              'controller': r.digest(Path(__file__).read_bytes())})
            print(json.dumps({'classification': 'R5_75_PREEXPOSURE_HALT', 'reason': str(exc)}))


def observe_once():
    """One qualified dispatch of existing static consumers; no generation/execution."""
    from benchmark.semantic import current_pipeline as pipeline
    from benchmark.semantic import readiness_r5_41 as readiness
    from benchmark.semantic import profile_audit_r5_41 as audit
    from benchmark.semantic import application_boundary_r5_41 as boundary_api
    from benchmark.semantic.refined_generator_r5_28 import canonical, sha
    r.require(not (OUT / 'terminal.json').exists(), 'terminal R5.75 cannot resume')
    pre = r.load(OUT / 'preexposure.json')
    r.verify(pre)
    r.require(pre['status'] == 'PASS', 'pre-exposure verification missing')
    state, commitment, frozen = (r.load(OUT / (name + '.json')) for name in ('state', 'commitment', 'freeze'))
    ledger = r.Ledger(OUT / 'actual-ledger')
    guard = r.Boundary(ROOT)
    with guard.active():
        r.require(r.current_state(ROOT) == state and r.benchmark_commitment(ROOT) == commitment,
                  'last preauthorization identity drift')
        r.authorization_preflight(frozen, commitment, ledger, state, r.ACTUAL_HELD_OUT, TRUSTED)
        r.require(r.health_record(state, r.load(OLD / 'health.json')['results'])['identity'] == frozen['health'],
                  'last health linkage drift')
        write('callback-binding', {'controller': r.digest(Path(__file__).read_bytes()),
                                   'state': state['identity'], 'freeze': frozen['identity'],
                                   'static_consumers': ['current_pipeline.checked', 'readiness_r5_41.inspect',
                                       'profile_audit_r5_41.inspect', 'application_boundary_r5_41.support_report',
                                       'application_boundary_r5_41.aggregate'],
                                   'prior_accounting': pre['protected_read_attempts'],
                                   'generation': False, 'execution': False, 'acceptance': False, 'repair': False})
        grant = r.authorize(frozen, commitment, ledger, state, r.ACTUAL_HELD_OUT, TRUSTED)
        r.persist(OUT / 'authorization.json', grant)
    counts = {'read_attempts': 0, 'content_reads': 0, 'openings': 0, 'observation_dispatches': 0}

    def opener():
        # Exactly the precommitted set. Text representation is specified by the
        # pre-existing authority, not chosen in response to a digest mismatch.
        policy = r.metadata(ROOT, next(iter(r.METADATA)))
        opened = {}
        counts['openings'] += 1
        for name, row in sorted(policy['members'].items()):
            if row['classification'] != 'SEALED':
                continue
            counts['read_attempts'] += 1
            raw = (ROOT / name).read_bytes()
            counts['content_reads'] += 1
            r.require(row['representation_kind'] == 'utf8-lf-text', 'unsupported committed representation')
            raw = raw.replace(b'\r\n', b'\n')
            r.require(r.digest(raw) == commitment['resources'][row['resource']]['commitment'],
                      'opened commitment mismatch')
            opened[row['resource']] = raw
        write('opening-verification', {'freeze': frozen['identity'], 'benchmark': commitment['identity'],
            'resources': {name: r.digest(raw) for name, raw in opened.items()},
            'frozen_pins': pre['checks']['frozen_pins'], 'status': 'PASS', **counts})
        write('exposure', {'event': 'B02_EXPOSED', 'permanent': True, 'freeze': frozen['identity'],
                           'benchmark': commitment['identity'], **counts})
        return opened

    def evaluator(opened):
        counts['observation_dispatches'] += 1
        # Whole frozen documents are decoded together, never clause-probed.
        documents = {name: json.loads(raw) for name, raw in opened.items()
                     if name not in ('frozen-request',) and not name.startswith('sealed-test-module-')}
        write('opened-static-documents', {'request': opened['frozen-request'].decode('utf-8'),
                                          'documents': documents, 'benchmark': commitment['identity']})
        apps = [value for value in documents.values() if isinstance(value, dict)
                and set(value) == {'id', 'state', 'operations'}]
        # Select the single latest precommitted semantic application by resource
        # metadata, never repair or select based on a support result.
        app_keys = [name for name, value in documents.items() if value in apps]
        chosen = next((name for name in app_keys if 'r540' in name), None)
        if chosen is None:
            r.require(len(app_keys) == 1, 'unambiguous frozen application selection unavailable')
            chosen = app_keys[0]
        app = documents[chosen]
        configurations = [value for value in documents.values() if isinstance(value, dict)
                          and {'transport', 'state', 'launch'} <= set(value)]
        r.require(len(configurations) == 1, 'unambiguous frozen profile configuration unavailable')
        config = configurations[0]
        obligation_document = documents['obligation-fixture-r540']
        obligations = (obligation_document['obligations'] if isinstance(obligation_document, dict)
                       else obligation_document)
        r.require(isinstance(obligations, list), 'frozen obligation list unavailable')
        manifest = {'application': sha(canonical(app)), 'generation': 'r575-static-only'}
        # This is one whole-document readiness invocation. Its operation records
        # include CheckedPlans and rejection evidence under stable document paths.
        ready = readiness.inspect(app, config['transport'], config['state'], config['launch'], obligations)
        audited = audit.inspect(app, config)
        compatible = boundary_api.support_report(app, config['transport'], config['state'], config['launch'], manifest)
        try:
            admitted = boundary_api.aggregate(app, config['transport'], config['state'], config['launch'], manifest)
            admission = {'status': 'ADMITTED', 'aggregate': admitted}
        except (ValueError, KeyError, TypeError) as exc:
            admission = {'status': 'REJECTED', 'reason': str(exc)}
        operations = ready['operations']
        formed = [name for name, value in operations.items() if value['status'] == 'SUPPORTED']
        rejected = {name: value for name, value in operations.items() if name not in formed}
        supported = (ready['status'] == 'READY' and audited['status'] == 'SUPPORTED'
                     and compatible['status'] == 'SUPPORTED' and admission['status'] == 'ADMITTED')
        return {'contract_count': len(app['operations']), 'boundary_obligation_count': len(obligations),
            'request': opened['frozen-request'].decode('utf-8'), 'selected_application': chosen,
            'checked_plans': {'attempted': len(app['operations']), 'formed': len(formed),
                              'rejected': len(rejected), 'formed_operations': formed, 'rejections': rejected},
            'readiness': ready, 'audit': audited, 'admission': admission, 'compatible_path': compatible,
            'whole_contract_static_views': 'SUPPORTED' if supported else 'UNSUPPORTED',
            'whole_contract_coverage': 'REQUIRES_REPORT_CORRESPONDENCE_ASSESSMENT',
            'generation': 0, 'execution': 0, 'frozen_acceptance': 0, 'repair': 0}

    try:
        result = r.observe(frozen, commitment, grant, ledger, lambda: r.current_state(ROOT),
                           lambda: r.benchmark_commitment(ROOT), opener, evaluator)
        post = r.post_check(frozen, commitment, ledger, lambda: r.current_state(ROOT),
                            lambda: r.benchmark_commitment(ROOT))
        write('observation', {'result': result, 'post_check': post, 'counts': counts,
                              'observation_completions': 1, 'semantic_count': 30,
                              'controller': r.digest(Path(__file__).read_bytes()),
                              'replay_prevention': {'events': [e['transition'] for e in ledger.events()],
                                  'second_authorization': 'REJECTS_NONZERO_LEDGER',
                                  'second_opening': 'REJECTS_EVENT_COUNT_BEFORE_OPENER',
                                  'second_observation': 'REJECTS_EVENT_COUNT_BEFORE_DISPATCH'}})
        print(json.dumps({'static_views': result['whole_contract_static_views'], 'post_check': post,
                          'counts': counts, 'observation_completions': 1}))
    except (r.Rejected, OSError, KeyError, ValueError, TypeError) as exc:
        events = ledger.events()
        reason = str(exc)
        classification = ('R5_75_BENCHMARK_COMMITMENT_FAILURE' if 'commitment mismatch' in reason else
                          'R5_75_PROTOCOL_HALT' if 'drift' in reason else 'R5_75_OBSERVATION_INDETERMINATE')
        write('terminal', {'classification': classification, 'reason': reason, 'counts': counts,
                          'ledger_status': ledger.status(), 'events': [e['transition'] for e in events],
                          'post_state': r.current_state(ROOT)['identity'], 'semantic_count': 30,
                          'observation_completions': sum(e['transition'] == 'COMPLETED' for e in events),
                          'generation': 0, 'execution': 0, 'frozen_acceptance': 0, 'repair': 0,
                          'controller': r.digest(Path(__file__).read_bytes())})
        print(json.dumps({'classification': classification, 'reason': reason, 'counts': counts}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['preexposure', 'observe'])
    args = parser.parse_args()
    {'preexposure': preexposure, 'observe': observe_once}[args.command]()
