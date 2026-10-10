"""Freeze authoritative synthetic fixture sources before AI target selection."""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_49'
OLD = ROOT / 'benchmark/results/phase6/r6_48'


def read(path):
    return json.loads(path.read_bytes())


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        f.write(canonical(obj) + b'\n')


def now():
    return datetime.now(timezone.utc).isoformat()


def ref(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}


def baseline():
    protected = dict(read(OLD / 'BASELINE.json')['protected_files'])
    manifest = OLD / 'PUBLICATION-IDENTITIES-v2.json'
    assert read(OLD / 'VERIFICATION.json')['manifest_sha256'] == sha(manifest)
    for name, item in read(manifest)['files'].items():
        assert sha(ROOT / name) == item['sha256'], name
        protected[name] = item['sha256']
    for p in (manifest, OLD / 'VERIFICATION.json'):
        protected[p.relative_to(ROOT).as_posix()] = sha(p)
    assert all(sha(ROOT / p) == h for p, h in protected.items())
    write(OUT / 'BASELINE.json', {'utc': now(), 'protected_files': protected,
        'protected_count': len(protected), 'head': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'initial_status': 'clean before editing', 'kernel': 26,
        'kernel_basis': 'preserved R5.114 accounting and implementation identities, not recount',
        'r6_47_classification': 'R6_47_DATASET_PARTIAL',
        'r6_48_classification': 'R6_48_DATA_PIPELINE_PARTIAL',
        'r6_48_original_admission': 0})


ID = '00000000-0000-4000-8000-000000000001'
CLOCK = '2026-01-01T00:00:00Z'


def fixture(eid):
    staged = eid == 'S02'
    branch = ('hold moves ready to held and opens the seal atomically; reset moves held '
              'to queued and opens the seal atomically; release requires held, then closed seal.'
              if staged else 'release requires ready, then closed seal. There is no hold/reset operation.')
    prose = ('Maintain a local sequential package-release register in records.json. Missing storage '
        'lists as empty without writing. create(label) preserves a nonblank string verbatim, assigns '
        'the supplied valid UUID/UTC provider values and starts phase queued, seal open. '
        'Blank/whitespace labels reject invalid_label without creating storage. '
        'ready requires queued and changes phase to ready. ' + branch +
        ' release changes phase to released. set_seal(value) replaces seal with open or closed. '
        'The invariant is released implies seal closed, so opening a released record rejects invalid_state. '
        'All mutations use id lookup: unknown/missing id rejects not_found before any other checks. '
        'Transition guards check phase before seal: wrong phase is wrong_phase, then open seal is unsealed. '
        'set_seal has no guard: missing or invalid value is invalid_input before invariant validation. '
        'All rejected mutations leave exact storage bytes unchanged; successful changes preserve all '
        'unmentioned fields. list returns full records sorted by created_at then id. Every successful '
        'change is atomically persisted and survives termination and a new process using the same directory. '
        'No operation can leave released. Scope: declared operations, well-formed request objects, '
        'valid provider UUID/time values, initially absent or valid own-format store, one writer, '
        'normal process restarts. Malformed transport, unknown operations, corrupt stores, concurrency '
        'and power-loss recovery are outside this contract.')
    record = {'id': ID, 'created_at': CLOCK, 'label': ' Box ', 'phase': 'queued', 'seal': 'open'}
    cases = []

    def add(op, args, expected, state, rejection=False):
        cases.append({'op': op, 'args': args, 'providers': {'uuid_v4': ID, 'utc_clock': CLOCK},
            'expected': expected, 'expected_records': state,
            'rejection_bytes_unchanged': rejection, 'fresh_process_required': True})

    def err(op, code, args=None):
        add(op, args if args is not None else {'id': ID}, {'error': code}, [dict(record)], True)

    def mutate(op, phase=None, seal=None):
        if phase is not None:
            record['phase'] = phase
        if seal is not None:
            record['seal'] = seal
        args = {'id': ID, 'value': seal} if op == 'set_seal' else {'id': ID}
        add(op, args, {'ok': dict(record)}, [dict(record)])

    add('list', {}, {'ok': []}, [], True)
    for label in ('', ' \t ', '\n'):
        add('create', {'label': label}, {'error': 'invalid_label'}, [], True)
    add('create', {'label': ' Box '}, {'ok': dict(record)}, [dict(record)])
    add('list', {}, {'ok': [dict(record)]}, [dict(record)], True)
    err('set_seal', 'not_found', {'id': 'missing', 'value': 'broken'})
    err('set_seal', 'not_found', {'value': 'broken'})
    err('release', 'not_found', {'id': 'missing'})
    err('release', 'wrong_phase')
    err('set_seal', 'invalid_input', {'id': ID})
    err('set_seal', 'invalid_input', {'id': ID, 'value': 'broken'})
    err('set_seal', 'invalid_input', {'id': ID, 'value': 1})
    mutate('ready', phase='ready')
    err('ready', 'wrong_phase')
    if staged:
        err('release', 'wrong_phase')
        mutate('set_seal', seal='closed')
        mutate('hold', phase='held', seal='open')
        err('hold', 'wrong_phase')
        mutate('set_seal', seal='closed')
        mutate('reset', phase='queued', seal='open')
        err('reset', 'wrong_phase')
        mutate('ready', phase='ready')
        mutate('hold', phase='held', seal='open')
    err('release', 'unsealed')
    mutate('set_seal', seal='closed')
    mutate('release', phase='released')
    err('release', 'wrong_phase')
    err('ready', 'wrong_phase')
    if staged:
        err('hold', 'wrong_phase')
        err('reset', 'wrong_phase')
    err('set_seal', 'invalid_input', {'id': ID, 'value': 'broken'})
    err('set_seal', 'invalid_state', {'id': ID, 'value': 'open'})
    mutate('set_seal', seal='closed')
    add('list', {}, {'ok': [dict(record)]}, [dict(record)], True)
    return prose, cases


def main():
    baseline()
    write(OUT / 'COMMISSIONING.json', {'family_id': 'LOCAL_RELEASE', 'episodes': ['S01', 'S02'],
        'utc': now(), 'commissioner': 'active OpenCode coordinator',
        'independent_commissioning': False, 'independent_acceptance_review': False,
        'authority': 'owner-authorized synthetic research fixture specification',
        'authorization_basis': 'R6.49 user request authorizes bounded data-generation and training-candidate review',
        'training_use_scope': 'research candidate preparation only; actual training not authorized',
        'inherited_context': 'repository guidance and R6.47/R6.48 findings read before commissioning',
        'external_or_pristine_benchmark_material': False,
        'behavioral_difference': 'terminal direct release versus mandatory held stage with atomic reset/open',
        'shared_skeleton': 'R6.16 scalar/mutable production-backed single-record intent profile',
        'ambiguities': [], 'clarification_needed': False})
    paths = [OUT / 'COMMISSIONING.json', HERE / 'PROTOCOL.md',
             ROOT / 'docs/training-data-admission-r6.49.md']
    for eid in ('S01', 'S02'):
        folder = OUT / 'episodes' / eid
        prose, cases = fixture(eid)
        write(folder / 'SOURCE.json', {'episode_id': eid, 'family_id': 'LOCAL_RELEASE',
            'original_requirement': prose, 'source_kind': 'same-coordinator synthetic specification',
            'authoritative_scope': 'this declared research fixture, not a human product request'})
        write(folder / 'FRC.json', {'version': 'lykoi-stateful-pilot-frc-1', 'episode_id': eid,
            'source': ref(folder / 'SOURCE.json'), 'status': 'FROZEN', 'ambiguities': [],
            'operations': ['create', 'list', 'ready', 'release', 'set_seal'] +
                          (['hold', 'reset'] if eid == 'S02' else []),
            'fields': ['id', 'created_at', 'label', 'phase', 'seal'],
            'state_domains': {'phase': ['queued', 'ready', 'released'] + (['held'] if eid == 'S02' else []),
                             'seal': ['open', 'closed']},
            'initial_state': 'absent store, empty list; create queued/open',
            'invariants': ['label nonblank', 'released implies closed seal', 'enum domains'],
            'error_precedence': ['lookup', 'ordered phase guard', 'ordered seal guard',
                                 'input validation', 'staged invariant', 'atomic commit'],
            'rejection': 'identical storage bytes', 'persistence': 'atomic one-store normal restart',
            'output': 'exact full record or {error:code}; list by created_at/id',
            'scope': 'SOURCE original_requirement is the normative closed API and exclusion scope',
            'representability': 'existing R6.16 generator.lower -> scalar_profile + mutable_values.compose',
            'new_semantics': False})
        write(folder / 'ACCEPTANCE.json', {'version': 'stateful-frozen-acceptance-1',
            'episode_id': eid, 'frc': ref(folder / 'FRC.json'), 'cases': cases,
            'oracle_author': 'same coordinator; literal expectations frozen before targets',
            'restart': 'one fresh process per request plus final restart list',
            'invariant_checks': 'every persisted record nonblank/domain-valid/released=>closed'})
        paths += [folder / name for name in ('SOURCE.json', 'FRC.json', 'ACCEPTANCE.json')]
    write(OUT / 'SOURCE-FREEZE.json', {'utc': now(), 'files': {
        p.relative_to(ROOT).as_posix(): sha(p) for p in paths}})
    print(json.dumps({'baseline_verified': read(OUT / 'BASELINE.json')['protected_count'],
        'source_freeze': sha(OUT / 'SOURCE-FREEZE.json'), 'episodes': 2,
        'cases': {e: len(read(OUT / 'episodes' / e / 'ACCEPTANCE.json')['cases']) for e in ('S01', 'S02')}}))


if __name__ == '__main__':
    main()
