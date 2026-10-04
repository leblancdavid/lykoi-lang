"""Security reconciliation only; no request dispatch or identity qualification."""

import json
import io
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[3]
RESULTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import infrastructure_lock_r5_47 as successor
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads

DOCS = {'docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md'}
NEW_CODE = {'benchmark/evaluation/security_r5_47.py',
            'benchmark/evaluation/infrastructure_lock_r5_47.py',
            'benchmark/evaluation/test_security_r5_47.py',
            'benchmark/results/phase5c/r5_47_qualification.py',
            'docs/security-evidence-r5.47.md'}

# Scan-only adjudication of independently reviewed non-authentication literals.
# These exceptions NEVER relax the publication guard or exempt entire files.
COMMAND_WORDS = {'create', 'list', 'list-high', 'migrate', 'complete', 'delete', 'list-overdue'}
ADMIN_PROSE = {
    'exactly one whole-contract static pass; no generation/execution/acceptance/repair',
    'readiness, supplemental audit and aggregate admission through the unchanged R5.41 shared compatible-path model',
    'user authorizes one dispatch only after successful verification and seal; dispatch gate never reached'}
FIXTURE_WORDS = {'synthetic-api-value', 'synthetic-password', 'synthetic-credential',
                 'synthetic-private-git-value', 'synthetic-recorder-value'}


def reviewed_scan(content, name):
    text = content.decode('utf-8', errors='replace')
    adjudications = []
    def literal(match):
        field, value = match[1], match[2]
        category = None
        if field == 'token' and value in COMMAND_WORDS:
            category = 'CLI lexical token, not authentication'
        elif field == 'authorization' and value in ADMIN_PROSE:
            category = 'administrative prose, not authentication'
        elif name in {'benchmark/evaluation/test_environment_snapshot.py',
                      'benchmark/evaluation/test_execution_identity_r5_46.py',
                      'benchmark/evaluation/test_security_r5_47.py'} and value in FIXTURE_WORDS:
            category = 'reviewed synthetic fixture literal'
        if category:
            adjudications.append(category)
            return match[0].replace(value, security.REDACTED)
        return match[0]
    text = security.ASSIGNMENT.sub(literal, text)
    if name.endswith('schema/axiom-v0.2.schema.json'):
        # Exact schema declaration, not a raw credential or general exception.
        text = text.replace('"token": {"type": "string"}', '"token": "[REDACTED]"')
        adjudications.append('CLI token schema declaration, not authentication')
    return security.scan_content(text.encode()), sorted(set(adjudications))


def git(*args):
    p = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    if p.returncode:
        raise ValueError('Git inspection failed; output withheld')
    return p.stdout


def read(name):
    return loads((RESULTS / name).read_bytes())


def write(name, value):
    security.persist(RESULTS / name, value)


def names():
    return sorted(set(git('ls-files', '--cached', '--others', '--exclude-standard', '-z').decode().strip('\0').split('\0')))


def blobs(entries):
    ids = list(dict.fromkeys(oid for oid, name in entries))
    p = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                       input=('\n'.join(ids) + '\n').encode(), capture_output=True)
    if p.returncode:
        raise ValueError('blob inspection failed')
    content, offset, result = p.stdout, 0, {}
    for oid in ids:
        end = content.index(b'\n', offset)
        header = content[offset:end].split()
        size = int(header[2])
        offset = end + 1
        if header[1] == b'blob':
            result[oid] = content[offset:offset + size]
        offset += size + 1
    return result


def scan():
    """Never return blob contents, credential hashes, or matched substrings."""
    findings, adjudications = [], []
    counts = {}
    def check(scope, label, content):
        counts[scope] = counts.get(scope, 0) + 1
        categories, reviewed = reviewed_scan(content, label)
        if reviewed:
            adjudications.append({'scope': scope, 'location': label, 'categories': reviewed})
        if categories:
            findings.append({'scope': scope, 'location': label, 'diagnostics': categories})
        if label.endswith(('.tar', '.tar.gz', '.tgz')):
            with tarfile.open(fileobj=io.BytesIO(content), mode='r:*') as archive:
                for member in archive.getmembers():
                    if member.isfile():
                        check(scope, label + '::' + member.name, archive.extractfile(member).read())
    for name in names():
        check('working_tree', name, (ROOT / name).read_bytes())
    index = git('ls-files', '--stage', '-z').decode().strip('\0').split('\0')
    entries = []
    for entry in index:
        meta, name = entry.split('\t', 1)
        mode, oid, stage = meta.split()
        if mode == '160000' or stage != '0':
            raise ValueError('unsupported index state')
        entries.append((oid, name))
    contents = blobs(entries)
    for oid, name in entries:
        check('index', name, contents[oid])
    refs = git('for-each-ref', '--format=%(refname)').decode().splitlines()
    objects = git('rev-list', '--objects', '--all', 'HEAD').decode().splitlines()
    entries = [(row.split(' ', 1)[0], row.partition(' ')[2]) for row in objects]
    contents = blobs(entries)
    for oid, name in entries:
        if oid in contents:
            check('reachable_history_all_refs', name or oid, contents[oid])
    ignored = git('ls-files', '--others', '--ignored', '--exclude-standard', '-z').decode().strip('\0').split('\0')
    ignored = [n for n in ignored if n]
    # Caches are not sharing candidates; still scan physical ignored files so
    # local secret artifacts can be reported categorically without their bytes.
    for name in ignored:
        check('ignored_local', name, (ROOT / name).read_bytes())
    return {'counts': counts, 'refs_scanned': refs, 'findings': findings, 'adjudications': adjudications,
            'remote_policy': 'locally available remote-tracking refs scanned; server/unfetched history not attested',
            'rotation_status': 'ROTATION_STATUS_EXTERNAL_OR_UNVERIFIED',
            'reflog_policy': 'unreachable/reflog objects are not intended sharing history; never publish them'}


def diagnostic_scan():
    # Diagnostic categories and filenames only; no file text or exception dump.
    result = scan()
    result['adjudications'] = len(result['adjudications'])
    print(json.dumps(result, indent=2))


def regression(stage):
    from benchmark.results.phase5c.r5_38_review import run_suite
    definitions = {
        'harness': ('benchmark/harness', 'test*.py', True),
        'application': ('tests', 'test*.py', False),
        'focused': ('benchmark/harness', 'test_optional_support_r5_41.py', True),
        'recorder': ('benchmark/harness', 'test_canonical_evidence_r5_43.py', True),
        'certificate': ('benchmark/evaluation', 'test_preexposure_r5_45.py', False),
        'publication': ('benchmark/evaluation', 'test_environment_snapshot.py', False),
        'security': ('benchmark/evaluation', 'test_security_r5_47.py', False)}
    definitions['security-final'] = definitions['security']
    if stage in definitions:
        # Historical test output stays in memory; publication gets structured
        # counts/IDs only, never tracebacks or arbitrary captured subprocess text.
        result = run_suite(*definitions[stage])
        result.pop('output')
        result['failures'] = [r['test'] for r in result['failures']]
        result['errors'] = [r['test'] for r in result['errors']]
    elif stage == 'coherence':
        from benchmark.results.phase5c.r5_41_review import matrix
        from benchmark.harness.test_optional_support_r5_41 import setup
        from benchmark.semantic import profile_audit_r5_41 as audit
        app, spec, state, config = setup()
        configuration = {'transport': spec, 'state': state, 'launch': config}
        reference = 'benchmark/harness/test_optional_support_r5_41.py'
        traces = [{'path': path, 'value': value, 'artifact': reference,
                   'sha256': digest((ROOT / reference).read_bytes()), 'clause': 'setup',
                   'interpretation': 'Independent declared shape and public mapping.'}
                  for path, value in audit.leaves(configuration)]
        first, second = matrix(), matrix()
        result = {'profiles': len(first['profiles']), 'rows': len(first['rows']),
                  'canonical_equal': canonical(first) == canonical(read('R5_41-independent-coherence-matrix.json')),
                  'deterministic': canonical(first) == canonical(second),
                  'structure': audit.structure(configuration),
                  'traceability': audit.traceability(configuration, traces, ROOT, {reference}),
                  'contamination': audit.contamination(configuration)}
        result['successful'] = (result['profiles'] == 16 and result['rows'] == 84 and
            result['canonical_equal'] and result['deterministic'] and result['structure']['valid'] and
            result['traceability']['valid'] and not result['contamination'])
    else:
        command = ['git', 'diff', '--check'] if stage == 'diff' else [sys.executable, '-m', 'air_compiler.cli', stage, 'air/task_manager.json']
        p = subprocess.run(command, cwd=ROOT, env={**os.environ, 'PYTHONPATH': 'src'}, capture_output=True)
        result = {'successful': p.returncode == 0, 'exit': p.returncode,
                  'output_withheld': True}
    write('R5_47-regression-' + stage + '.json', result)
    if not result['successful']:
        raise ValueError('regression failed; details withheld')


def inherited():
    from benchmark.results.phase5c.r5_43_qualification import historical_lock, contamination
    from benchmark.results.phase5c.r5_42_review import authority
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    old = read('R5_43-infrastructure-lock.json')
    body = {k: v for k, v in old.items() if k != 'identity'}
    differences = [name for name, expected in old['files'].items()
                   if digest((ROOT / name).read_bytes()) != expected]
    if digest(canonical(body)) != old['identity'] or differences != ['.gitignore']:
        raise ValueError('unexplained infrastructure drift')
    classifications = {
        'R5_42-halt-verification.json': 'R5_42_PROTOCOL_HALT',
        'R5_44-halt-verification.json': 'R5_44_PROTOCOL_HALT',
        'R5_45-evidence/classification.json': 'R5_45_STATE_IDENTITY_GAP',
        'R5_46-evidence/classification.json': 'R5_46_PROTOCOL_HALT'}
    for name, expected in classifications.items():
        if read(name)['primary_classification'] != expected:
            raise ValueError('historical outcome mutation')
    if SCHEMA['core_constructs'] != 30:
        raise ValueError('semantic scope intrusion')
    return {'historical': historical_lock('R5_40-implementation-profile-lock.json'),
            'prospective': historical_lock('R5_41-implementation-lock.json'),
            'predecessor': {'identity': old['identity'], 'identity_valid': True,
                            'members': len(old['files']), 'matching': len(old['files']) - 1,
                            'differences': differences},
            'authority': authority(), 'contamination': contamination(),
            'historical_classifications': classifications, 'core_semantics': 30}


def members():
    return [name for name in names() if name not in DOCS and
            not Path(name).name.startswith('R5_47-') and '/R5_47-' not in name]


def category(name):
    if name in NEW_CODE:
        return 'R5.47 secret-safe infrastructure/qualification code and policy'
    if name in {'benchmark/evaluation/environment_snapshot.py',
                'benchmark/evaluation/test_environment_snapshot.py',
                'benchmark/results/phase5c/R5_45-SECURITY-REDACTION.md'}:
        return 'security remediation'
    if name in {'benchmark/evaluation/execution_identity_r5_46.py',
                'benchmark/evaluation/test_execution_identity_r5_46.py'}:
        return 'retained unqualified R5.46 research; no promotion or execution'
    if name in {'benchmark/evaluation/preexposure_r5_45.py',
                'benchmark/evaluation/test_preexposure_r5_45.py',
                'docs/preexposure-r5.45.md'}:
        return 'preserved R5.45 synthetic-only infrastructure; production gap retained'
    if name.startswith('benchmark/results/phase5c/R5_43-'):
        return 'preserved predecessor qualification evidence'
    for version in ('44', '45', '46'):
        if (name.startswith('benchmark/results/phase5c/R5_' + version + '-') or
                name in {'benchmark/results/phase5c/r5_' + version + suffix
                         for suffix in ('_review.py', '_halt.py', '_qualification.py', '_finalize.py')}):
            return 'preserved historical R5.' + version + ' stopped/gap evidence and orchestration'
    raise ValueError('unexplained addition: ' + name)


def metadata():
    predecessor = read('R5_43-infrastructure-lock.json')
    current = members()
    additions = sorted(set(current) - set(predecessor['files']))
    audit = {name: {'change': 'added', 'category': category(name)} for name in additions}
    audit['.gitignore'] = {'change': 'modified', 'category': 'security remediation; local .env ignores with example/sample exceptions',
                           'before_sha256': predecessor['files']['.gitignore'],
                           'after_sha256': digest((ROOT / '.gitignore').read_bytes())}
    if set(predecessor['files']) - set(current):
        raise ValueError('predecessor member removed')
    return {'protocol': 'lykoi-infrastructure-lock-r5.47-v2',
            'head': git('rev-parse', 'HEAD').decode().strip(),
            'predecessor_identity': predecessor['identity'],
            'reason': 'intentional security correction and prospective secret-safe publication boundary',
            'authorized_differences': audit,
            'permitted_updates': sorted(DOCS), 'permitted_outputs': 'R5_47-* reconciliation evidence only',
            'unqualified_research_policy': 'R5.46 prototype preserved as unqualified; R5.48 separately authorized',
            'scope': 'repository physical bytes only; not execution identity or a production certificate'}


def unchanged_inherited():
    changes = git('diff', '--name-only', 'HEAD', '--').decode().splitlines()
    if set(changes) - DOCS:
        raise ValueError('inherited bytes modified')
    unknown = set(names()) - set(git('ls-files', '-z').decode().strip('\0').split('\0'))
    unexpected = {n for n in unknown if n not in NEW_CODE and not Path(n).name.startswith('R5_47-')}
    if unexpected:
        raise ValueError('unexplained new candidate file')


def freeze():
    unchanged_inherited()
    boundary = inherited()
    if not (RESULTS / 'R5_47-starting-boundary.json').exists():
        write('R5_47-starting-boundary.json', boundary)
    lock = successor.manifest(ROOT, members(), metadata())
    write('R5_47-infrastructure-lock-v2.json', lock)
    print(successor.verify(ROOT, successor.reload(RESULTS / 'R5_47-infrastructure-lock-v2.json')))


def qualify():
    unchanged_inherited()
    lock = read('R5_47-infrastructure-lock-v2.json')
    checks = successor.verify(ROOT, lock)
    reproduced = successor.manifest(ROOT, members(), metadata())
    if canonical(reproduced) != canonical(lock):
        raise ValueError('successor manifest unstable')
    # Independent comprehension, not the manifest implementation.
    independent = {**metadata(), 'files': {n: digest((ROOT / n).read_bytes()) for n in members()}}
    if digest(canonical(independent)) != lock['identity']:
        raise ValueError('independent identity mismatch')
    mutations = []
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for name in ('.gitignore', 'benchmark/evaluation/security_r5_47.py'):
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            content = (ROOT / name).read_bytes()
            path.write_bytes(content)
            fixture = successor.manifest(root, [name], {'protocol': 'r5.47-disposable-mutation-probe'})
            path.write_bytes(content + b'\n# synthetic mutation\n')
            rejected = False
            try:
                successor.verify(root, fixture)
            except ValueError:
                rejected = True
            path.write_bytes(content)
            successor.verify(root, fixture)
            mutations.append({'member': name, 'mismatch_rejected': rejected, 'restored': True})
    if not all(m['mismatch_rejected'] for m in mutations):
        raise ValueError('mutation not detected')
    stages = ('harness', 'application', 'focused', 'recorder', 'certificate', 'publication',
              'security-final', 'coherence', 'validate', 'safety', 'diff')
    regressions = {stage: read('R5_47-regression-' + stage + '.json') for stage in stages}
    if not all(r['successful'] for r in regressions.values()) or len(regressions['harness']['skipped']) != 36:
        raise ValueError('regression/firewall qualification failed')
    scanned = scan()
    write('R5_47-repository-scan.json', scanned)
    if scanned['findings']:
        raise ValueError('secret scan has unresolved findings')
    boundary = inherited()
    # The original redacted snapshot must STILL fail its historical identity.
    from benchmark.evaluation.preexposure_r5_45 import unseal
    invalidated = False
    try:
        unseal(read('R5_45-evidence/state.json'))
    except ValueError:
        invalidated = True
    if not invalidated or not read('R5_46-evidence/quarantine.json')['all_stage_evidence_quarantined']:
        raise ValueError('historical disposition lost')
    result = {'primary_classification': 'R5_47_SECURITY_RECONCILIATION_QUALIFIED',
              'boundary': boundary, 'successor_lock': checks,
              'canonical_reload_and_independent_reproduction': True, 'mutation_probes': mutations,
              'regressions': regressions, 'scan_counts': scanned['counts'],
              'unresolved_scan_findings': 0, 'rotation_status': 'ROTATION_STATUS_EXTERNAL_OR_UNVERIFIED',
              'redacted_r5_45_seal_still_invalid': invalidated,
              'r5_46_receipts_still_quarantined': True, 'r5_46_prototype_qualified': False,
              'production_certificate_issued': False, 'core_semantics': 30,
              'b02': {n: 0 for n in ('reservations', 'dispatches', 'static_evaluations', 'checked_plans',
                                   'readiness', 'audit', 'admission', 'generation', 'execution', 'frozen_acceptance')},
              'b03_prospectively_touched': False, 'b17_exposed': False, 'b17_classified': False, 'phase5c': 'paused'}
    successor.verify(ROOT, lock)
    write('R5_47-qualification.json', result)
    print({'primary_classification': result['primary_classification'], 'successor_lock': checks})


def final_integrity():
    unchanged_inherited()
    lock = read('R5_47-infrastructure-lock-v2.json')
    verified = successor.verify(ROOT, lock)
    if canonical(successor.manifest(ROOT, members(), metadata())) != canonical(lock):
        raise ValueError('final membership drift')
    scan_result = scan()
    if scan_result['findings']:
        raise ValueError('final scan unresolved')
    diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True)
    if diff.returncode:
        raise ValueError('final diff failure')
    report = {'successor': verified, 'inherited': inherited(), 'diff_check_exit': diff.returncode,
              'scan_counts': scan_result['counts'], 'unresolved_findings': 0,
              'artifacts': {p.relative_to(ROOT).as_posix(): digest(p.read_bytes())
                            for p in sorted(RESULTS.glob('R5_47-*')) if p.is_file()}}
    write('R5_47-final-integrity.json', report)
    print({'final_integrity': 'PASS', 'successor': verified})


def main():
    command = sys.argv[1]
    if command == 'scan':
        diagnostic_scan()
    elif command == 'regression':
        regression(sys.argv[2])
    elif command == 'freeze':
        freeze()
    elif command == 'qualify':
        qualify()
    elif command == 'final-integrity':
        final_integrity()
    else:
        raise ValueError('unknown security reconciliation command')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('R5.47 check failed; raw diagnostics withheld', file=sys.stderr)
        raise SystemExit(1)
