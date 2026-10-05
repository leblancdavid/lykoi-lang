"""Bounded R5.53 provenance investigation. Authority inputs are hash-only.

Search actual project bytes, never reconstruct a missing historical preimage.
No B02 subject parser, readiness, admission, reservation or dispatch is used.
"""

from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import authority_r5_53 as authority
from benchmark.evaluation import checkout_r5_52 as check
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation.recorder_r5_43 import canonical

RESULTS = ROOT / 'benchmark/results/phase5c'
OUT = RESULTS / 'R5_53-evidence'
TEMP = Path('C:/Users/lblan/AppData/Local/Temp/opencode')
LOCKS = {'historical': 'R5_40-implementation-profile-lock.json',
         'prospective': 'R5_41-implementation-lock.json',
         'r547': 'R5_47-infrastructure-lock-v2.json'}
REPORTS = {
    'r5.33': 'R5_33-CROSS-SHAPE-STATE-EVOLUTION.md',
    'r5.35': 'R5_35-GENERIC-TRANSPORT-BOUNDARY-COMPLETION.md',
    'r5.38': 'R5_38-NULLABLE-DOMAIN-WHOLE-CONTRACT-COHERENCE.md',
    'r5.39': 'R5_39-REFINEMENT-DEPENDENCY-WHOLE-CONTRACT-BOUNDARY-CLOSURE.md'}
ROLES = {
    'R5_24-type-matrix.json': ('GENERATED_EVIDENCE', 'Prospective capability matrix; consumed by readiness metadata, not frozen oracle', True),
    'current_pipeline.py': ('COMPILER_RUNTIME', 'Current application assembly and checked-plan entry', True),
    'input_binding_r5_32.py': ('PROFILE_SUPPORT', 'Typed public input decoder and validation', True),
    'public_binding_r5_32.py': ('PROFILE_SUPPORT', 'Checked public metadata and independent binding challenge', True),
    'refined_evidence_r5_28.py': ('BENCHMARK_INFRASTRUCTURE', 'Independent semantic conformance verifier', True),
    'refined_generator_r5_28.py': ('COMPILER_RUNTIME', 'Checked lowering/emission', True),
    'refined_runtime_r5_28.py': ('COMPILER_RUNTIME', 'Generated application persistence/runtime', True),
    'unified_types_r5_27.py': ('SEMANTIC_CORE', 'Authoritative prospective type analyzer and CheckedPlan', True)}


def write(name, value):
    security.persist(OUT / (name + '.json'), value)


def read(name):
    return json.loads((OUT / (name + '.json')).read_bytes())


def initialize():
    OUT.mkdir(exist_ok=False)
    names = [p for p in (ROOT / 'benchmark/results').rglob('*') if p.is_file()
             and '__pycache__' not in p.parts and OUT not in p.parents
             and p.name != Path(__file__).name]
    write('initial', {'head': check.git(ROOT, 'rev-parse', 'HEAD').decode().strip(),
        'historical': {p.relative_to(ROOT).as_posix(): check.sha(p.read_bytes()) for p in names},
        'b02_exposure': 0})


def investigate():
    inventory = json.loads((RESULTS / 'R5_52-inventory-v3.json').read_bytes())
    rows = [r for r in inventory['locks']['infrastructure']['members'] if r['class'] == 'UNCLASSIFIED']
    if len(rows) != 8 or {Path(r['path']).name for r in rows} != set(ROLES):
        raise ValueError('unexpected unresolved scope')
    expected = {r['path']: r['authority_sha256'] for r in rows}
    # All objects (including unreachable/index-only blobs), not merely path log.
    listing = check.git(ROOT, 'cat-file', '--batch-all-objects', '--batch-check=%(objectname) %(objecttype) %(objectsize)').decode().splitlines()
    blobs = [line.split()[0] for line in listing if line.split()[1] == 'blob']
    matches = {n: [] for n in expected}
    for start in range(0, len(blobs), 64):
        for blob, data in check.blobs(ROOT, blobs[start:start + 64]).items():
            digest = check.sha(data)
            for name, pin in expected.items():
                if digest == pin:
                    matches[name].append({'blob': blob, 'raw_sha256': digest})
    reachable = check.git(ROOT, 'rev-list', '--all', 'HEAD').decode().splitlines()
    reflog = check.git(ROOT, 'reflog', '--all', '--format=%H').decode().splitlines()
    commits = sorted(set(reachable + reflog))
    trees = {commit: check.tree(ROOT, commit) for commit in commits}
    current_tree = check.tree(ROOT, 'HEAD')
    objects = check.blobs(ROOT, [t[n]['blob'] for t in trees.values() for n in expected if n in t])
    fsck = subprocess.run(['git', 'fsck', '--full', '--no-reflogs', '--unreachable'], cwd=ROOT, capture_output=True, timeout=60)
    if fsck.returncode:
        raise ValueError('Git object integrity failure')
    copies = []
    # Explicit existing project diagnostic copies only. Never inspect unrelated
    # interpreter distribution, credentials, OpenCode configuration or history.
    locations = [TEMP / n for n in ('r531-lf', 'r532-lf', 'r551-cooperative-workspace', 'r552-clean-lf')]
    archives = []
    for archive in sorted((ROOT / 'benchmark/results').rglob('*.tar')):
        member_rows = []
        with tarfile.open(archive) as tar:
            for item in tar.getmembers():
                # Inspect names only for all other members, including B02.
                name = item.name.removeprefix('./')
                for target, pin in expected.items():
                    if item.isfile() and (name == target or name.endswith('/' + target)):
                        data = tar.extractfile(item).read()
                        member_rows.append({'path': target, 'member': item.name, 'sha256': check.sha(data), 'exact': check.sha(data) == pin})
        archives.append({'path': archive.relative_to(ROOT).as_posix(), 'sha256': check.sha(archive.read_bytes()),
                         'candidate_members': member_rows})
    result = []
    for row in rows:
        name, pin = row['path'], row['authority_sha256']
        current = objects[current_tree[name]['blob']]
        history = check.git(ROOT, 'log', '--format=%H %s', '--', name).decode().splitlines()
        last_commit, round_name = history[0].split(' ', 1)
        report = REPORTS[round_name]
        report_data = check.git(ROOT, 'show', last_commit + ':benchmark/results/phase5c/' + report)
        witnesses = []
        for location in locations:
            p = location / name
            if p.is_file():
                data = p.read_bytes()
                witnesses.append({'source': location.name + ':' + name, 'sha256': check.sha(data),
                                  'exact_preimage': check.sha(data) == pin,
                                  'current_repository_content_equal': check.normalize(data) == current})
        copies.extend(witnesses)
        candidates = [(commit + ':' + name, objects[t[name]['blob']]) for commit, t in trees.items() if name in t]
        candidates += [(str(location / name), (location / name).read_bytes()) for location in locations if (location / name).is_file()]
        recovered = authority.exact_preimage(pin, candidates)
        # A digest match elsewhere is not sufficient without path context.
        if matches[name] and not recovered:
            raise ValueError('uncontextualized matching object requires manual review')
        occurrences = []
        for p in sorted(RESULTS.glob('*lock*.json')):
            value = json.loads(p.read_bytes())
            if value.get('files', {}).get(name) == pin:
                occurrences.append({'path': p.relative_to(ROOT).as_posix(), 'head': value.get('head'), 'sha256': check.sha(p.read_bytes())})
        first = next((line for line in reversed(check.git(ROOT, 'log', '--format=%H %s', '--', *[o['path'] for o in occurrences]).decode().splitlines())
                      if any(o['path'] in trees[line.split()[0]] for o in occurrences)), None)
        criticality, role, affects = ROLES[Path(name).name]
        lock_contexts = []
        for occurrence in occurrences:
            head = occurrence['head']
            if head and name in check.tree(ROOT, head):
                at_lock = check.git(ROOT, 'show', head + ':' + name)
                lock_contexts.append({'lock': occurrence['path'], 'head': head,
                                      'repository_sha256': check.sha(at_lock), 'current_content_equal': at_lock == current})
        result.append({'path': name, 'role': role, 'criticality': criticality,
            'text_binary_generated': 'UTF-8 JSON generated capability evidence' if name.endswith('.json') else 'UTF-8 Python authored infrastructure',
            'historical_sha256': pin, 'current_raw_sha256': check.sha((ROOT / name).read_bytes()),
            'current_repository_sha256': check.sha(current), 'current_blob': current_tree[name]['blob'],
            'checkout_relation': authority.materialization(current, (ROOT / name).read_bytes(), 'utf8-lf-text'),
            'history': history, 'first_known_lock_commit': first, 'lock_membership': occurrences,
            'lock_head_repository_witnesses': lock_contexts,
            'historical_preimage': recovered, 'historical_preimage_status': 'HISTORICAL_PREIMAGE_RECOVERED' if recovered else 'HISTORICAL_PREIMAGE_UNAVAILABLE',
            'object_matches': matches[name], 'diagnostic_copies': witnesses,
            'change_record': {'path': 'benchmark/results/phase5c/' + report, 'commit': last_commit, 'sha256': check.sha(report_data)},
            'can_affect_behavior': affects, 'frozen_behavioral_authority': False})
    write('investigation', {'head': read('initial')['head'], 'files': result,
        'source_search': {'reachable_commits': len(reachable), 'reflog_commits': len(set(reflog)),
            'combined_commits': len(commits), 'all_objects': len(listing), 'all_blobs_raw_hashed': len(blobs),
            'object_inventory_sha256': check.sha(canonical(listing)), 'fsck_exit': fsck.returncode,
            'unreachable_objects': fsck.stdout.decode().splitlines(), 'diagnostic_paths': [str(p) for p in locations],
            'archive_inventory': archives, 'index': check.git(ROOT, 'ls-files', '-s', '--', *expected).decode().splitlines(),
            'scope': 'All available local objects/refs/reflogs/index, tracked archives, lock records and existing project diagnostic copies; no remote fetch or unavailable external backups attested'},
        'historical_exact_preimages_recovered': sum(r['historical_preimage'] is not None for r in result),
        'b02_exposure': 0, 'core_semantics': 30})
    print(json.dumps({'files': [{k: r[k] for k in ('path', 'historical_sha256', 'current_repository_sha256', 'first_known_lock_commit', 'history', 'criticality', 'historical_preimage_status')} for r in result],
                      'sources': {k: v for k, v in read('investigation')['source_search'].items() if k not in ('archive_inventory', 'index')}}, indent=2))


def qualify():
    investigation = read('investigation')
    head = investigation['head']
    if check.git(ROOT, 'rev-parse', 'HEAD').decode().strip() != head:
        raise ValueError('investigation HEAD drift')
    decision_path = 'docs/authority-successor-r5.53.md'
    decision = (ROOT / decision_path).read_bytes()
    for label in ('application', 'test_authority_r5_53-v2', 'test_reproducibility_boundary_r5_50',
                  'test_tier2_r5_51', 'test_checkout_r5_52'):
        if not read(label)['successful']:
            raise ValueError('required focused check failed')
    for label in ('coherence', 'core-count', 'implementation-contamination', 'dependencies', 'validate', 'safety'):
        if not read(label + '-worker')['successful']:
            raise ValueError('required static check failed')
    if not read('supplemental-source-search')['exact_preimages_unavailable']:
        raise ValueError('supplemental recovery requires review')
    rows = []
    for row in investigation['files']:
        data = check.git(ROOT, 'show', head + ':' + row['path'])
        if check.sha(data) != row['current_repository_sha256']:
            raise ValueError('investigated content drift')
        change = row['change_record']
        source = check.git(ROOT, 'show', change['commit'] + ':' + change['path'])
        if check.sha(source) != change['sha256']:
            raise ValueError('change evidence drift')
        evidence = [
            {'kind': 'git', 'source': head + ':' + row['path'], 'source_sha256': check.sha(data), 'current_sha256': check.sha(data)},
            {'kind': 'change-record', 'source': change['commit'] + ':' + change['path'], 'source_sha256': check.sha(source), 'current_sha256': check.sha(data)},
            {'kind': 'decision', 'source': decision_path, 'source_sha256': check.sha(decision), 'current_sha256': check.sha(data)}]
        # Decisions name exact repository identities, not just plausible behavior.
        if row['path'].encode() not in decision or check.sha(data).encode() not in decision:
            raise ValueError('decision does not bind current member')
        disposition = authority.adjudicate(row['historical_sha256'], data, row['criticality'], evidence, recovered=row['historical_preimage'])
        if disposition not in ('CURRENT_STATE_PROVEN_AUTHORIZED', 'HISTORICAL_PREIMAGE_RECOVERED'):
            raise ValueError('successor ineligible')
        rows.append({**row, 'current_provenance': evidence, 'disposition': disposition})
    adjudication = {'files': rows, 'eligible': True, 'basis': decision_path, 'decision_sha256': check.sha(decision),
                    'historical_locks_requalified': False, 'b02_exposure': 0, 'core_semantics': 30}
    write('adjudication', adjudication)
    tree = check.tree(ROOT, head)
    names = set(json.loads((RESULTS / LOCKS['r547']).read_bytes())['files'])
    # Explicit forward scope: established implementation/evaluator plus new R5.48–
    # R5.53 mechanisms and versioned policies. Result evidence is enumerated only
    # where already in the predecessor; future capsule captures add their inputs.
    names.update(n for n in tree if n.startswith(('src/', 'schema/', 'air/', 'generated/', 'benchmark/semantic/', 'benchmark/evaluation/', 'benchmark/harness/')))
    names.update(n for n in tree if n.startswith('docs/') and n.endswith('.md') and n not in ('docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md'))
    objects = check.blobs(ROOT, [tree[n]['blob'] for n in names])
    repository = {n: {**tree[n], 'content': objects[tree[n]['blob']]} for n in sorted(names)}
    # New mechanism/policy files are explicitly content-bound additions, not Git
    # history claims. Publication does not require a commit by the agent.
    additions = ['benchmark/evaluation/authority_r5_53.py', 'benchmark/evaluation/test_authority_r5_53.py',
                 'benchmark/results/phase5c/r5_53_adjudicate.py', decision_path]
    for n in additions:
        data = (ROOT / n).read_bytes()
        repository[n] = {'content': data, 'mode': '100644', 'blob': None}
    attributes = check.attributes(ROOT, sorted(repository))
    if any(r['filter'] != 'unspecified' or r['working-tree-encoding'] != 'unspecified'
           for r in attributes.values()):
        raise ValueError('unsupported checkout filter/encoding')
    write('checkout-controls', {'attributes': attributes,
        'conversion_policy': 'exact repository bytes or declared LF/CRLF pair expansion; bare CR rejected',
        'effective_eol_settings': subprocess.run(['git', 'config', '--show-origin', '--get-regexp',
            r'core\.(autocrlf|eol|safecrlf|attributesfile)'], cwd=ROOT, capture_output=True, timeout=10).stdout.decode(),
        'b02_exposure': 0})
    predecessors = [{'path': p, 'raw_sha256': check.sha((RESULTS / p).read_bytes()),
                     'historical_physical_status': 'FAIL', 'repository_semantics_retroactive': False} for p in LOCKS.values()]
    frozen = json.loads((RESULTS / 'R5_52-inventory-v3.json').read_bytes())['frozen_pins']
    pins = {}
    for row in frozen:
        data = check.git(ROOT, 'show', head + ':' + row['path'])
        if check.sha(data) != row['authority_sha256']:
            raise ValueError('frozen behavioral authority gap')
        pins[row['path']] = row['authority_sha256']
    baseline = authority.build(repository, {'head': head, 'predecessors': predecessors,
        'reconciliation_sha256': check.sha(canonical(adjudication)), 'decision_sha256': check.sha(decision),
        'frozen_authority': pins, 'authorized_additions': additions,
        'scope': 'Enumerated successor authority and infrastructure; not a complete execution capsule',
        'historical_physical_failures_preserved': True, 'core_semantics': 30, 'b02_exposure': 0})
    destination = RESULTS / 'R5_53-authority-successor-v1.json'
    security.persist(destination, baseline)
    loaded = authority.reload(destination)
    if loaded != baseline or authority.build(repository, {k: v for k, v in baseline.items() if k not in ('members', 'identity', 'protocol')}) != baseline:
        raise ValueError('nondeterministic successor')
    checkout = authority.verify(ROOT, loaded, repository, trusted_identity=baseline['identity'])
    write('checkout', checkout)
    # Independent raw reader verifies each authority digest and permitted physical
    # relationship without build()/verify(), and independently recomputes ID.
    if check.sha(canonical({k: v for k, v in loaded.items() if k != 'identity'})) != baseline['identity']:
        raise ValueError('independent identity rejection')
    for n, r in repository.items():
        p = (ROOT / n).read_bytes()
        member = loaded['members'][n]
        if check.sha(r['content']) != member['sha256'] or (p != r['content'] and
            not (member['kind'] == 'utf8-lf-text' and p.replace(b'\r\n', b'\n') == r['content'])):
            raise ValueError('independent member rejection')
    for p in predecessors:
        if check.sha((RESULTS / p['path']).read_bytes()) != p['raw_sha256']:
            raise ValueError('predecessor drift')
    for p in LOCKS.values():
        h = json.loads((RESULTS / p).read_bytes())['head']
        if subprocess.run(['git', 'merge-base', '--is-ancestor', h, head], cwd=ROOT).returncode:
            raise ValueError('ancestry failure')
    write('qualification', {'identity': baseline['identity'], 'members': len(repository), 'canonical_reload': True,
        'deterministic_reproduction': True, 'independent_member_integrity': True, 'authority_identities': pins,
        'ancestry_verified': True, 'checkout_relationships': dict(Counter(r['relationship'] for r in checkout['members'].values())),
        'historical_failures_preserved': True, 'production_tier2_qualified': False, 'r554_eligible_start': True,
        'b02_exposure': 0, 'core_semantics': 30, 'phase5c': 'paused'})
    previous_rows = {r['path']: r for r in json.loads((RESULTS / 'R5_52-inventory-v3.json').read_bytes())['locks']['infrastructure']['members']}
    unresolved = {r['path']: r for r in rows}
    transitions = []
    for n, member in baseline['members'].items():
        if n not in previous_rows:
            transitions.append({'path': n, 'category': 'EXPLICIT_SCOPE_ADDITION', 'repository_sha256': member['sha256'],
                                'git_provenance': head + ':' + n if member['blob'] else 'R5.53 explicit addition'})
        else:
            old = previous_rows[n]
            if old['authority_sha256'] != member['sha256']:
                category = ('CURRENT_STATE_PROVEN_AUTHORIZED' if n in unresolved else
                            'R5_50_AUTHORIZED_METHODOLOGY_CHANGE' if n == 'benchmark/README.md' else
                            'R5_52_PROVEN_REPRESENTATION_IDENTITY_TRANSITION')
                transitions.append({'path': n, 'category': category,
                    'historical_physical_sha256': old['authority_sha256'], 'repository_sha256': member['sha256'],
                    'r552_class': old['class'], 'historical_status_changed': False})
    write('authorized-transitions', {'baseline': baseline['identity'], 'rows': transitions,
                                   'b02_exposure': 0, 'historical_content_diff_claimed_for_missing_preimages': False})
    print({'baseline': baseline['identity'], 'members': len(repository), 'b02_exposure': 0})


def supplemental():
    investigation = read('investigation')
    targets = {r['path']: r['historical_sha256'] for r in investigation['files']}
    main = {line.split()[0] for line in check.git(ROOT, 'cat-file', '--batch-all-objects',
            '--batch-check=%(objectname) %(objecttype)').decode().splitlines()}
    records = []
    found = []
    for location in ('r531-lf', 'r532-lf', 'r551-cooperative-workspace', 'r552-clean-lf'):
        root = TEMP / location
        p = subprocess.run(['git', 'rev-parse', '--git-dir'], cwd=root, capture_output=True, timeout=10)
        if p.returncode:
            records.append({'location': location, 'git_database_available': False})
            continue
        listing = check.git(root, 'cat-file', '--batch-all-objects', '--batch-check=%(objectname) %(objecttype)').decode().splitlines()
        extra = [line.split()[0] for line in listing if line.split()[1] == 'blob' and line.split()[0] not in main]
        for start in range(0, len(extra), 64):
            for blob, data in check.blobs(root, extra[start:start + 64]).items():
                for n, h in targets.items():
                    if check.sha(data) == h:
                        found.append({'location': location, 'blob': blob, 'path_requires_context_review': n})
        records.append({'location': location, 'git_database_available': True, 'objects': len(listing),
                        'additional_blobs_raw_hashed': len(extra)})
    patches = []
    for name in ('r532-new.patch', 'r532-tracked.patch'):
        data = (TEMP / name).read_bytes()
        patches.append({'path': name, 'sha256': check.sha(data),
            'member_headers': [line for line in data.decode().splitlines() if line.startswith(('diff --git', '+++ '))],
            'exact_preimage': any(check.sha(data) == h for h in targets.values()),
            'interpretation': 'R5.32 patch fragments, not complete historical authority files; no application/reconstruction attempted'})
    write('supplemental-source-search', {'diagnostic_git_databases': records, 'patch_backups': patches,
        'matches_requiring_review': found, 'exact_preimages_unavailable': not found,
        'b02_exposure': 0})
    print({'additional_sources': records, 'matches': len(found)})


def worker(directory, pattern, label=None):
    from benchmark.results.phase5c.r5_38_review import run_suite
    result = run_suite(directory, pattern, restrictions=directory == 'benchmark/harness')
    result.pop('output')
    label = label or ('application' if directory == 'tests' else Path(pattern).stem)
    write(label, result)
    print({label: {k: result[k] for k in ('discovered', 'passed')},
           'skips': len(result['skipped']), 'failures': len(result['failures']), 'errors': len(result['errors'])})


def static():
    from benchmark.results.phase5c import r5_51_qualification as driver
    driver.OUTPUT = OUT
    for stage in ('coherence', 'core-count', 'implementation-contamination', 'dependencies', 'validate', 'safety', 'diff'):
        driver.worker(stage)
    security_rows = []
    for n in ('.gitignore', 'benchmark/evaluation/security_r5_47.py', 'benchmark/evaluation/infrastructure_lock_r5_47.py'):
        data = (ROOT / n).read_bytes()
        historical = check.git(ROOT, 'show', 'c75cc65:' + n)
        if check.normalize(data) != historical:
            raise ValueError('security correction drift')
        security_rows.append({'path': n, 'repository_sha256': check.sha(historical), 'preserved': True})
    write('security-preservation', {'members': security_rows, 'b02_exposure': 0})
    inventory = json.loads((RESULTS / 'R5_52-inventory-v3.json').read_bytes())
    statuses = {}
    for key, name in LOCKS.items():
        lock = json.loads((RESULTS / name).read_bytes())
        matches = sum(check.sha((ROOT / n).read_bytes()) == h for n, h in lock['files'].items())
        old_key = 'infrastructure' if key == 'r547' else key
        original = inventory['locks'][old_key]['members']
        unchanged = all(check.sha((ROOT / r['path']).read_bytes()) == r['checkout_sha256'] for r in original)
        statuses[key] = {'raw_matches': matches, 'members': len(lock['files']), 'status': 'FAIL',
                         'r552_physical_members_unchanged': unchanged}
        if not unchanged:
            raise ValueError('historical input drift; reopen relevant evidence')
    write('historical-lock-status', statuses)


def final():
    initial = read('initial')
    if any(check.sha((ROOT / n).read_bytes()) != h for n, h in initial['historical'].items()):
        raise ValueError('historical evidence mutation')
    from benchmark.evaluation.preexposure_r5_45 import unseal
    summary = json.loads((RESULTS / 'R5_51-evidence/summary.json').read_bytes())
    for n, h in summary['receipts'].items():
        row = json.loads((RESULTS / 'R5_51-evidence' / (n + '.json')).read_bytes())
        unseal(row)
        if row['identity'] != h:
            raise ValueError('receipt drift')
    if subprocess.run(['git', 'diff', '--check'], cwd=ROOT).returncode:
        raise ValueError('diff check failed')
    write('final-integrity', {'protected_historical_files_unchanged': len(initial['historical']),
        'r551_receipts_preserved': len(summary['receipts']), 'diff_check': 'PASS', 'b02_exposure': 0,
        'core_semantics': 30, 'phase5c': 'paused', 'production_certificate_issued': False,
        'artifact_sha256': {p.relative_to(ROOT).as_posix(): check.sha(p.read_bytes()) for p in
            [*OUT.glob('*.json'), RESULTS / 'R5_53-authority-successor-v1.json',
             RESULTS / 'R5_53-UNRESOLVED-AUTHORITY-PROVENANCE-AND-SUCCESSOR-BASELINE-ADJUDICATION.md',
             ROOT / 'docs/authority-successor-r5.53.md', ROOT / 'docs/project-overview.md',
             ROOT / 'docs/decisions.md', ROOT / 'docs/research-log.md']},
        'primary_classification': 'R5_53_SUCCESSOR_PROVENANCE_QUALIFIED'})


if __name__ == '__main__':
    if sys.argv[1] == 'worker':
        worker(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    else:
        {'initialize': initialize, 'investigate': investigate, 'qualify': qualify,
         'supplemental': supplemental, 'static': static, 'final': final}[sys.argv[1]]()
