"""Fresh, bounded R5.48 qualification; no benchmark request dispatch entry.

Receipts bind a partial observed v2 identity and are explicitly non-reusable for
production. Unresolved material closure prevents a production certificate.
"""

import ast
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from benchmark.evaluation import execution_identity_r5_48 as identity
from benchmark.evaluation import ai_independence_r5_48 as independence
from benchmark.evaluation import infrastructure_lock_r5_47 as successor
from benchmark.evaluation import preexposure_r5_45 as prior
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, ProtocolFailure

OUTPUT = ROOT / 'benchmark/results/phase5c/R5_48-evidence'
LOCK = ROOT / 'benchmark/results/phase5c/R5_47-infrastructure-lock-v2.json'


def write(name, value):
    security.persist(OUTPUT / (name + '.json'), value)


def read(name):
    return loads((OUTPUT / (name + '.json')).read_bytes())


def definitions():
    stages = {'harness-' + p.stem: ['suite', 'benchmark/harness', p.name, True]
              for p in sorted((ROOT / 'benchmark/harness').glob('test*.py'))}
    stages.update({
        'application': ['suite', 'tests', 'test*.py', False],
        'focused': ['suite', 'benchmark/harness', 'test_optional_support_r5_41.py', True],
        'recorder': ['suite', 'benchmark/harness', 'test_canonical_evidence_r5_43.py', True],
        'certificate': ['suite', 'benchmark/evaluation', 'test_preexposure_r5_45.py', False],
        'security': ['suite', 'benchmark/evaluation', 'test_security_r5_47.py', False],
        'publication': ['suite', 'benchmark/evaluation', 'test_environment_snapshot.py', False],
        'execution-v2': ['suite', 'benchmark/evaluation', 'test_execution_identity_r5_48.py', False],
        'coherence': ['coherence'], 'locks': ['locks'], 'inventory': ['inventory'],
        'validate': ['command', 'validate'], 'safety': ['command', 'safety'],
        'diff': ['diff']})
    return stages


def boundary():
    from benchmark.results.phase5c.r5_47_qualification import inherited
    value = inherited()
    current = successor.verify(ROOT, successor.reload(LOCK))
    if current['identity'] != identity.BASELINE or current['members'] != 1065:
        raise ProtocolFailure('unexpected successor baseline')
    quarantine = loads((ROOT / 'benchmark/results/phase5c/R5_46-evidence/quarantine.json').read_bytes())
    value['quarantined_receipt_changes'] = [n for n, h in quarantine['receipts_sha256'].items()
        if digest((ROOT / 'benchmark/results/phase5c/R5_46-evidence' / n).read_bytes()) != h]
    if value['quarantined_receipt_changes']:
        raise ProtocolFailure('quarantined evidence changed')
    value['successor'] = current
    value['successful'] = value['core_semantics'] == 30 and value['contamination']['valid']
    return value


def inventory():
    imports = independence.imports(ROOT)
    core_external = sorted({name.split('.')[0] for names in imports.values() for name in names if name and not name.startswith('.')})
    provider = re.compile(r'(?i)openai|anthropic|google[ _-]?ai|gemini|opencode|chatgpt|claude|api[_-]?key|inference|gpt[-_ ]')
    matches = []
    # Publish locations/categories only. No matched text or configuration values.
    for directory, dirs, files in os.walk(ROOT):
        dirs[:] = [n for n in dirs if n not in {'.git', '__pycache__'}]
        for name in files:
            path = Path(directory) / name
            relative = path.relative_to(ROOT).as_posix()
            if relative.startswith(identity.OUTPUT) or path.suffix not in {'.py', '.json', '.md', '.jsonc', '.toml', '.yaml', '.yml', '.txt'}:
                continue
            if provider.search(path.read_text(encoding='utf-8', errors='replace')):
                if relative.startswith(('src/', 'generated/', 'air/')):
                    domain = 'LANGUAGE_CORE' if relative.startswith('src/') else 'PROGRAM_DECLARED'
                elif relative.startswith('benchmark/'):
                    domain = 'OPTIONAL_TOOLING'
                else:
                    domain = 'DEVELOPMENT_AUTHORING'
                matches.append({'path': relative, 'domain': domain,
                                'participation': 'reference/configuration evidence; no value published'})
    semantic_imports = set()
    for path in sorted((ROOT / 'benchmark/semantic').glob('*.py')):
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, ast.Import):
                semantic_imports.update(a.name.split('.')[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
                semantic_imports.add(node.module.split('.')[0])
    nonstandard = sorted(semantic_imports - sys.stdlib_module_names - {'benchmark', 'air_compiler'})
    return {'successful': not nonstandard and not any(m['domain'] in {'LANGUAGE_CORE', 'PROGRAM_DECLARED'} for m in matches),
            'classification_scope': 'repository textual provider references and direct import dependencies; not remote agent config',
            'core_direct_imports': imports, 'core_external_roots': core_external,
            'core_nonstdlib_dependencies': sorted(set(core_external) - sys.stdlib_module_names),
            'semantic_external_roots': sorted(semantic_imports), 'semantic_nonstdlib_dependencies': nonstandard,
            'provider_reference_locations': matches,
            'considered_environment': [{'name': n, 'domain': identity.classify_variable(n)} for n in sorted(os.environ)],
            'resolved_packages_policy': 'no third-party core imports; installed unrelated distributions excluded',
            'dependencies': [
                {'component': 'Lykoi source/schema/deterministic semantic rules', 'domain': 'LANGUAGE_CORE'},
                {'component': 'CPython and actually imported standard-library/native implementations', 'domain': 'BUILD_EXECUTION'},
                {'component': 'declared model, argv, durable state, clock and ID providers', 'domain': 'PROGRAM_DECLARED'},
                {'component': 'Git identity/lock inspection and external benchmark oracle/recorder', 'domain': 'OPTIONAL_TOOLING'},
                {'component': 'Git resolved executable for this qualification', 'domain': 'BUILD_EXECUTION'},
                {'component': 'OpenAI/Anthropic/Google/model/OpenCode/editor/IDE credentials and configuration', 'domain': 'DEVELOPMENT_AUTHORING'},
                {'component': 'unrelated installed packages/hostname/username/machine serial', 'domain': 'IRRELEVANT'},
                {'component': 'native closure, descendant imports, Git helpers and mutable context ownership', 'domain': 'UNKNOWN'}],
            'execution_identity_complete': False, 'production_certificate_qualified': False}


def worker(name):
    definition = definitions()[name]
    kind = definition[0]
    if kind == 'suite':
        from benchmark.results.phase5c.r5_38_review import run_suite
        result = run_suite(*definition[1:])
        result.pop('output')
        result['failures'] = [r['test'] for r in result['failures']]
        result['errors'] = [r['test'] for r in result['errors']]
    elif kind == 'locks':
        result = boundary()
    elif kind == 'inventory':
        result = inventory()
    elif kind == 'coherence':
        from benchmark.results.phase5c.r5_41_review import matrix
        from benchmark.harness.test_optional_support_r5_41 import setup
        from benchmark.semantic import profile_audit_r5_41 as audit
        app, spec, state, config = setup()
        configuration = {'transport': spec, 'state': state, 'launch': config}
        reference = 'benchmark/harness/test_optional_support_r5_41.py'
        traces = [{'path': p, 'value': v, 'artifact': reference,
                   'sha256': digest((ROOT / reference).read_bytes()), 'clause': 'setup',
                   'interpretation': 'Independent declared shape and public mapping.'}
                  for p, v in audit.leaves(configuration)]
        first, second = matrix(), matrix()
        saved = loads((ROOT / 'benchmark/results/phase5c/R5_41-independent-coherence-matrix.json').read_bytes())
        result = {'profiles': len(first['profiles']), 'rows': len(first['rows']),
                  'canonical_equal': canonical(first) == canonical(saved),
                  'deterministic': canonical(first) == canonical(second),
                  'structure': audit.structure(configuration),
                  'traceability': audit.traceability(configuration, traces, ROOT, {reference}),
                  'contamination': audit.contamination(configuration)}
        result['successful'] = (result['profiles'] == 16 and result['rows'] == 84 and
            result['canonical_equal'] and result['deterministic'] and result['structure']['valid'] and
            result['traceability']['valid'] and not result['contamination'])
    else:
        command = ['git', 'diff', '--check'] if kind == 'diff' else [sys.executable, '-B', '-S', '-m', 'air_compiler.cli', definition[1], 'air/task_manager.json']
        p = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30)
        result = {'successful': p.returncode == 0, 'exit': p.returncode, 'output_withheld': True}
    # Bind observed resolved imports for each stage, without implying completeness.
    observed = identity.observed(ROOT, os.environ)
    result['resolved_import_observation'] = observed['dependencies']
    write(name + '-worker', result)
    if not result['successful']:
        raise SystemExit(1)


def capture():
    # Load the same inspector dependencies before every coordinator capture.
    # Worker imports are separately observed and cannot widen coordinator state.
    boundary()
    return identity.observed(ROOT, os.environ)


def initialize():
    if OUTPUT.exists():
        existing = {p.name for p in OUTPUT.iterdir()}
        permitted = {'starting-boundary.json', 'initialization-publication-rejection.json',
                     'host-environment-domains.json'}
        if not existing <= permitted or 'starting-boundary.json' not in existing:
            raise ProtocolFailure('initialization replacement prohibited')
        if canonical(read('starting-boundary')) != canonical(boundary()):
            raise ProtocolFailure('initial boundary changed')
        if 'initialization-publication-rejection.json' not in existing:
            write('initialization-publication-rejection', {
                'stage_started': False, 'state_frozen': False, 'secret_published': False,
                'reason': 'credential-named domain map rejected before publication; use name/domain rows',
                'superseded_construction_only': True})
        else:
            write('capture-publication-rejection', {
                'stage_started': False, 'state_frozen': False, 'secret_published': False,
                'reason': 'stdlib module named token rejected as credential field; resolved identities now typed rows',
                'superseded_construction_only': True})
    else:
        OUTPUT.mkdir(exist_ok=False)
        write('starting-boundary', boundary())
    if not (OUTPUT / 'host-environment-domains.json').exists():
        write('host-environment-domains', {'variables': [{'name': n, 'domain': identity.classify_variable(n)} for n in sorted(os.environ)],
                                          'values_published': False,
                                          'identity_policy': 'only sanitized child execution controls are included; ambient host values excluded'})
    frozen = capture()
    write('state', frozen)
    write('definitions', definitions())
    print({'observed_identity': frozen['identity'], 'stages': len(definitions()),
           'unresolved_material_groups': len(frozen['unknown'])})


def halt(reason):
    if not (OUTPUT / 'quarantine.json').exists():
        write('quarantine', {'primary_classification': 'R5_48_PROTOCOL_HALT',
                            'reason_category': reason, 'all_receipts_quarantined': True,
                            'reusable_pass_evidence': False, 'b02_exposure': 0,
                            'receipts': {p.name: digest(p.read_bytes()) for p in sorted(OUTPUT.glob('*.json'))}})
    raise ProtocolFailure('R5.48 protocol halt; details withheld')


def batch():
    if (OUTPUT / 'quarantine.json').exists():
        raise ProtocolFailure('halted investigation cannot resume')
    frozen = read('state')
    if canonical(capture()) != canonical(frozen):
        halt('observed material state drift before batch')
    started = time.monotonic()
    for name, definition in definitions().items():
        if (OUTPUT / (name + '.json')).exists():
            continue
        remaining = 90 - (time.monotonic() - started)
        if remaining < 30:
            break
        before = capture()
        mechanism = digest(canonical(definition))
        write(name + '-attempt', prior.stage(identity.bridge(frozen)['identity'], name, 'INCOMPLETE',
              {'successful': False, 'reason': 'started; no completion receipt'}, mechanism))
        command = [sys.executable, '-B', '-S', str(Path(__file__).resolve()), 'worker', name]
        status, telemetry = prior.bounded(command, ROOT, identity.isolated_environment(os.environ, ROOT), min(70, remaining - 5))
        # Never publish arbitrary subprocess output, command paths or diagnostics.
        supervision = {n: telemetry[n] for n in ('elapsed_seconds', 'allowed_seconds', 'successful')}
        after = capture()
        if canonical(before) != canonical(after) or canonical(before) != canonical(frozen):
            halt('observed material state drift during stage')
        path = OUTPUT / (name + '-worker.json')
        result = loads(path.read_bytes()) if status == 'PASS' and path.exists() else {'successful': False}
        result.update({'supervision': supervision, 'production_reusable': False})
        if status == 'PASS' and result['successful']:
            receipt = identity.stage(before, after, name, result, mechanism)
        else:
            receipt = prior.stage(identity.bridge(frozen)['identity'], name, status,
                                  {'successful': False, 'supervision': supervision}, mechanism)
        write(name, receipt)
        print({'stage': name, 'status': receipt['status'], 'seconds': telemetry['elapsed_seconds']}, flush=True)
        if receipt['status'] != 'PASS':
            halt('verification failure or incomplete stage')
    print({'completed': sum((OUTPUT / (n + '.json')).exists() for n in definitions()),
           'required': len(definitions())})


def final():
    if (OUTPUT / 'quarantine.json').exists():
        raise ProtocolFailure('halted investigation cannot qualify')
    frozen, current = read('state'), capture()
    if canonical(frozen) != canonical(current):
        halt('observed material state drift at final boundary')
    stages = {n: prior.reload(OUTPUT / (n + '.json')) for n in definitions()}
    for name, receipt in stages.items():
        prior.check_stage(receipt, identity.bridge(frozen), name,
                          {'stages': {n: digest(canonical(d)) for n, d in definitions().items()}})
    harness = [r['result'] for n, r in stages.items() if n.startswith('harness-')]
    counts = {'discovered': sum(r['discovered'] for r in harness),
              'passed': sum(r['passed'] for r in harness),
              'skipped': sum(len(r['skipped']) for r in harness)}
    if counts != {'discovered': 429, 'passed': 393, 'skipped': 36}:
        halt('restricted harness denominator changed')
    result = {'primary_classification': 'R5_48_EXECUTION_STATE_IDENTITY_GAP',
              'classification_policy': 'prospective descriptive gap label; user halt/failure list was absent',
              'ai_independence': 'SUPPORTED_WITHIN_INSPECTED_AND_TESTED_CORE_SCOPE',
              'execution_identity_version': identity.PROTOCOL, 'observed_identity': frozen['identity'],
              'unresolved_material_dependencies': frozen['unknown'],
              'production_certificate_issued': False, 'production_toctou_qualified': False,
              'synthetic_certificate_and_final_check': 'fresh v2 suite includes assembly, mutation rejection and one-pass fixture',
              'stages': {n: r['identity'] for n, r in stages.items()}, 'stage_count': len(stages),
              'restricted_harness': counts, 'regressions': {n: stages[n]['result'] for n in
                  ('application', 'focused', 'recorder', 'certificate', 'security', 'publication', 'execution-v2', 'coherence', 'validate', 'safety', 'diff')},
              'locks': boundary(), 'full_regression_pass_established': True,
              'evidence_reusable_for_production': False, 'core_semantics': 30,
              'b02': {n: 0 for n in ('reservations', 'dispatches', 'checked_plans', 'readiness',
                                   'audit', 'admission', 'static_support', 'generation', 'execution', 'frozen_acceptance')},
              'b03_prospectively_touched': False, 'b17_exposed': False, 'b17_classified': False,
              'phase5c': 'paused', 'rotation_status': 'ROTATION_STATUS_EXTERNAL_OR_UNVERIFIED'}
    write('summary', result)
    print({'classification': result['primary_classification'], 'harness': counts,
           'stages': len(stages), 'production_certificate': False})


def final_integrity():
    frozen, current = read('state'), capture()
    if canonical(frozen) != canonical(current):
        halt('reporting changed observed execution state')
    p = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True)
    if p.returncode:
        raise ProtocolFailure('final diff check failed')
    result = {'successful': True, 'observed_identity_unchanged': True, 'locks': boundary(),
              'evidence': {p.name: digest(p.read_bytes()) for p in sorted(OUTPUT.glob('*.json'))},
              'reporting_files': {n: digest((ROOT / n).read_bytes()) for n in
                  ('docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md',
                   'docs/ai-independence-r5.48.md',
                   'benchmark/results/phase5c/R5_48-EXECUTION-STATE-AND-AI-INDEPENDENCE.md')},
              'diff_check_exit': p.returncode, 'production_certificate_issued': False}
    write('final-integrity', result)
    print({'final_integrity': 'PASS', 'observed_identity': frozen['identity']})


if __name__ == '__main__':
    try:
        {'initialize': initialize, 'batch': batch, 'worker': lambda: worker(sys.argv[2]),
         'final': final, 'final-integrity': final_integrity}[sys.argv[1]]()
    except Exception:
        print('R5.48 qualification operation failed; raw diagnostics withheld', file=sys.stderr)
        raise SystemExit(1)
