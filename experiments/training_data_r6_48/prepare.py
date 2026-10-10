"""Freeze source-side R6.48 records before any candidate construction (stdlib only)."""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'benchmark/results/phase6/r6_48'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError('immutable output already exists: ' + str(path))
    path.write_bytes(canonical(value) + b'\n')


def read(path):
    return json.loads(path.read_bytes())


def protected():
    files = dict(read(ROOT / 'benchmark/results/phase6/r6_46/BASELINE.json')['protected_files'])
    for round_id in ('46', '47'):
        folder = ROOT / ('benchmark/results/phase6/r6_' + round_id)
        manifest = read(folder / 'PUBLICATION-IDENTITIES.json')
        receipt = read(folder / 'VERIFICATION.json')
        assert receipt['manifest_sha256'] == sha(folder / 'PUBLICATION-IDENTITIES.json')
        for name, item in manifest['files'].items():
            assert sha(ROOT / name) == item['sha256'], name
            files[name] = item['sha256']
        for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
            path = folder / name
            files[path.relative_to(ROOT).as_posix()] = sha(path)
    failures = [name for name, digest in files.items() if sha(ROOT / name) != digest]
    assert not failures, failures
    return files


PROVENANCE = {
    'commissioner': 'same OpenCode coordinator as formalizer and artifact-script author',
    'source_kind': 'new synthetic human-style requirement, not a human-authored request',
    'independent_commissioning': False,
    'independent_acceptance_review': False,
    'repository_exposure': True,
    'inherited_context': 'AGENTS.md and R6.47 findings visible before commissioning',
    'provider_hidden_context_exclusion': 'unattested',
    'limitations': ['capability-aware coordinator', 'no independent custodian',
                    'no externally authoritative behavioral approval'],
}


def ok(data, value, role='program'):
    return {'input_hex': bytes(data).hex(), 'expected': {
        'status': 'success', 'value': value, 'output_hex': value.to_bytes(2, 'big').hex(),
        'consumed': len(data), 'provenance': {'span': [0, len(data)], 'origins': []}},
        'kind': 'positive_or_boundary'}


def no(data, code, offset, role, stage='validation', kind='negative_or_precedence'):
    return {'input_hex': bytes(data).hex(), 'expected': {'status': 'reject',
        'error': {'code': code, 'offset': offset, 'role': role, 'stage': stage,
                  'path': None, 'expected': []}}, 'kind': kind}


def generic(cases, width):
    cases.append(no([], 'TRUNCATED', 0, 'a', 'structure', 'empty_input'))
    valid = next(c for c in cases if c['expected']['status'] == 'success')
    data = list(bytes.fromhex(valid['input_hex']))
    cases.append(no(data + [99], 'TRAILING', width, 'complete', 'structure', 'trailing_input'))
    cases.append({'input_hex': valid['input_hex'], 'limits': {'work': 0},
                  'expected': {'status': 'reject', 'error': {
                      'code': 'WORK_LIMIT', 'offset': 0, 'role': 'program',
                      'stage': 'limit', 'path': None, 'expected': []}, 'work': 0},
                  'kind': 'logical_work_boundary'})
    return cases


def specifications():
    return [
        ('F1', 'capacity_and_weight', [
            ('E01', 'At the parcel intake, read exactly two unsigned byte weights. Return their sum as a two-byte big-endian integer. Reject totals above 120 as CAPACITY at the first weight. Read both weights before checking capacity, and check capacity before rejecting trailing data.',
             ['read a', 'read b', 'sum=a+b', 'sum<=120 else CAPACITY at a', 'end', 'emit sum'],
             generic([ok([0, 0], 0), ok([40, 80], 120), ok([1, 118], 119),
                      no([60, 61], 'CAPACITY', 0, 'capacity'), no([255, 255, 1], 'CAPACITY', 0, 'capacity'),
                      no([40], 'TRUNCATED', 1, 'b', 'structure')], 2)),
            ('E02', 'The route quote reads two unsigned bytes: fragile weight and ordinary weight. Charge twice the fragile weight plus ordinary weight. Return a two-byte big-endian quote. Reject quotes above 600 as QUOTE at the fragile weight, after reading both bytes but before trailing-data rejection. Exactly two bytes are required.',
             ['read a', 'read b', 'twice=a+a', 'quote=twice+b', 'quote<=600 else QUOTE at a', 'end', 'emit quote'],
             generic([ok([0, 0], 0), ok([255, 90], 600), ok([255, 89], 599), ok([0, 255], 255),
                      no([255, 91], 'QUOTE', 0, 'capacity'), no([255, 255, 1], 'QUOTE', 0, 'capacity'),
                      no([1], 'TRUNCATED', 1, 'b', 'structure')], 2)),
        ]),
        ('F2', 'binary_safety_constraints', [
            ('E03', 'Read exactly two byte flags for redundant safety sensors. Each flag must be 0 or 1. Validate the first flag before reading the second; validate the second next, then require the two flags to agree. Use FLAG_A, FLAG_B and DISAGREE respectively, located at the relevant flag (DISAGREE at the first). Return the first flag as UInt16BE. Perform trailing-data rejection last.',
             ['read a', 'a<=1 else FLAG_A', 'read b', 'b<=1 else FLAG_B', 'a==b else DISAGREE at a', 'end', 'emit a'],
             generic([ok([0, 0], 0), ok([1, 1], 1), no([0, 1], 'DISAGREE', 0, 'agreement'),
                      no([1, 0, 9], 'DISAGREE', 0, 'agreement'), no([2], 'FLAG_A', 0, 'flag_a'),
                      no([2, 2], 'FLAG_A', 0, 'flag_a'), no([0, 2], 'FLAG_B', 1, 'flag_b'),
                      no([0], 'TRUNCATED', 1, 'b', 'structure')], 2)),
            ('E04', 'Read exactly two byte flags for a transfer interlock. First read both bytes, then reject invalid first or second flags (values over 1) in that order as FLAG_A or FLAG_B. Require exactly one flag to be set; reject equal flags as INTERLOCK at the first byte. Return the sum as UInt16BE, and check trailing data after all constraints.',
             ['read a', 'read b', 'a<=1 else FLAG_A', 'b<=1 else FLAG_B', 'sum=a+b', 'sum==1 else INTERLOCK at a', 'end', 'emit sum'],
             generic([ok([0, 1], 1), ok([1, 0], 1), no([0, 0], 'INTERLOCK', 0, 'agreement'),
                      no([1, 1, 9], 'INTERLOCK', 0, 'agreement'), no([2], 'TRUNCATED', 1, 'b', 'structure'),
                      no([2, 2], 'FLAG_A', 0, 'flag_a'), no([0, 2], 'FLAG_B', 1, 'flag_b')], 2)),
        ]),
        ('F3', 'ordered_protocol_validation', [
            ('E05', 'A gauge frame begins with byte version 7 and then a byte count at most 12. Reject a wrong version immediately as VERSION at byte 0, before attempting to read count. Reject excessive counts as COUNT at byte 1 before checking for trailing data. Require exactly two bytes and return count as UInt16BE.',
             ['read a', 'a==7 else VERSION', 'read b', 'b<=12 else COUNT', 'end', 'emit b'],
             generic([ok([7, 0], 0), ok([7, 12], 12), ok([7, 11], 11),
                      no([8], 'VERSION', 0, 'version'), no([8, 99, 3], 'VERSION', 0, 'version'),
                      no([7, 13, 9], 'COUNT', 1, 'count'), no([7], 'TRUNCATED', 1, 'b', 'structure')], 2)),
            ('E06', 'Read exactly three bytes: low, high and reading. Read all three before any check. Reject low greater than high as WINDOW at low; otherwise reject reading below low as BELOW at reading, then reject reading above high as ABOVE at reading. Perform trailing-data rejection last. Return reading as UInt16BE.',
             ['read a', 'read b', 'read c', 'a<=b else WINDOW at a', 'a<=c else BELOW at c', 'c<=b else ABOVE at c', 'end', 'emit c'],
             generic([ok([0, 255, 0], 0), ok([0, 255, 255], 255), ok([4, 4, 4], 4),
                      no([5, 4, 0, 9], 'WINDOW', 0, 'window'), no([5, 9, 4], 'BELOW', 2, 'below'),
                      no([5, 9, 10, 9], 'ABOVE', 2, 'above'),
                      no([5], 'TRUNCATED', 1, 'b', 'structure'), no([5, 4], 'TRUNCATED', 2, 'c', 'structure')], 3)),
        ]),
        ('F4', 'dependency_composition', [
            ('E07', 'A three-lane tally reads exactly three byte counts before calculation. The tally must be authored using an explicit reusable two-argument sum definition, and a nested three-argument aggregation definition that calls it twice with pinned dependencies. Reject a final total over 300 as TOTAL at the first input byte. Return the tally as UInt16BE and check trailing input after the total check.',
             ['read a', 'read b', 'read c', 'total=compose aggregate(a,b,c)', 'total<=300 else TOTAL at a', 'end', 'emit total'],
             generic([ok([0, 0, 0], 0), ok([100, 100, 100], 300), ok([99, 100, 100], 299),
                      no([100, 100, 101], 'TOTAL', 0, 'capacity'), no([255, 255, 255, 1], 'TOTAL', 0, 'capacity'),
                      no([1], 'TRUNCATED', 1, 'b', 'structure'), no([1, 2], 'TRUNCATED', 2, 'c', 'structure')], 3)),
            ('E08', 'The packing score reads two byte quantities before calculation and returns twice the first plus three times the second as UInt16BE. Author a reusable doubling definition and a tripling definition that composes doubling and adds its input once more. The program must compose both pinned definitions. Reject scores above 1000 as SCORE at the first byte, before trailing-data rejection. Exactly two bytes are required.',
             ['read a', 'read b', 'd=compose double(a)', 't=compose triple(b)', 'score=d+t', 'score<=1000 else SCORE at a', 'end', 'emit score'],
             generic([ok([0, 0], 0), ok([200, 200], 1000), ok([199, 200], 998), ok([0, 255], 765),
                      no([201, 200], 'SCORE', 0, 'capacity'), no([255, 255, 9], 'SCORE', 0, 'capacity'),
                      no([1], 'TRUNCATED', 1, 'b', 'structure')], 2)),
        ]),
        ('F5', 'reservation_lifecycle', [
            ('E09', 'Build a persistent equipment reservation service. Reservations expire after a day. Only an authorized operator may renew one. Keep an audit record and make retries safe.',
             ['What defines a day and expiry equality?', 'What authenticates an operator?',
              'What is the idempotency key and conflict behavior?', 'Which rejection wins for expired unauthorized retries?'], None),
            ('E10', 'Build a durable waitlist that promotes the next eligible member when a reservation is cancelled. Never overbook, preserve fairness and retain history through restart.',
             ['What is eligibility and which ordering defines fairness?', 'Who may cancel?',
              'Is promotion atomic with cancellation?', 'What errors and historical migration rules apply?'], None),
        ]),
        ('F6', 'distributed_effect_authority', [
            ('E11', 'Two independent offline hosts must contend for one shared physical actuator. With no communication, no shared storage and no preallocated exclusive owner, either host may acquire it when alone, but simultaneous requests must allow exactly one grant and exactly one physical activation. Rejections are BUSY, no rejected request may activate the actuator, and committed grants survive both hosts restarting. Grant authority must be established by the execution system, not a supplied actor string.',
             ['single-host grant', 'simultaneous exactly-one grant', 'exactly-one physical activation',
              'BUSY without activation', 'restart retains owner', 'execution-established authority'], []),
            ('E12', 'Provide an exactly-once bank transfer between two independently controlled remote ledgers despite arbitrary network loss and process crashes. Accept only an authenticated owner of the debit account. AUTH must precede FUNDS rejection. A successful receipt is issued only after both durable remote balances commit; neither one-sided commit nor a duplicate debit is permitted. No cooperative transaction service or idempotency facility is supplied by either remote ledger.',
             ['authenticated owner', 'AUTH before FUNDS', 'two remote commits before receipt',
              'no one-sided commit', 'no duplicate debit after crash'], []),
        ]),
    ]


def main():
    assert not EVIDENCE.exists(), 'round already prepared'
    identities = protected()
    baseline = {'round': 'R6.48', 'head': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'initial_git_status': 'clean',
        'kernel': 26, 'kernel_basis': 'preserved R5.114 accounting; no independent recount',
        'protected_files': identities, 'protected_count': len(identities),
        'r6_47_classification_preserved': 'R6_47_DATASET_PARTIAL',
        'initial_preservation_failures': [], 'r6_47_publication_files_verified': 15}
    write(EVIDENCE / 'BASELINE.json', baseline)
    partition = {'version': 'lykoi-family-partition-1', 'development': ['F1', 'F2', 'F3', 'F4'],
                 'evaluation_quarantine': ['F5', 'F6'], 'classification': 'PROCESS_DEMONSTRATION_ONLY',
                 'custodian_held': False, 'coordinator_has_seen_all_requirements': True,
                 'training_export_gate': 'TRAINING_ADMITTED only; no evaluation artifacts or transcripts',
                 'cross_family_shared_symbol_policy': 'no shared application definitions across families',
                 'shared_format_and_runtime': 'public foundation allowed; arithmetic/check scaffold overlaps require audit'}
    write(EVIDENCE / 'PARTITION-PLAN.json', partition)
    for fid, name, episodes in specifications():
        write(EVIDENCE / 'commissioning' / (fid + '.json'), {
            'family_id': fid, 'name': name, 'episodes': [e[0] for e in episodes],
            'provenance': PROVENANCE, 'selection_basis': 'behavioral structure and requested coverage; new synthetic requests',
            'not_selected_by_existing_example_lookup': True,
            'capability_blind_selection': False, 'partition': 'development' if fid < 'F5' else 'evaluation_quarantine'})
        for eid, source, obligations, cases in episodes:
            folder = EVIDENCE / 'episodes' / eid
            write(folder / 'SOURCE.json', {'episode_id': eid, 'family_id': fid,
                'original_requirement': source, 'provenance': PROVENANCE})
            unresolved = cases is None
            write(folder / 'FRC.json', {'version': 'lykoi-pilot-frc-1', 'episode_id': eid,
                'source_sha256': sha(folder / 'SOURCE.json'),
                'status': 'CLARIFICATION_REQUIRED' if unresolved else 'FROZEN',
                'ordered_obligations': [] if unresolved else obligations,
                'ambiguities': obligations if unresolved else [],
                'clarification': 'unavailable; no answers inferred' if unresolved else 'none identified within explicit synthetic source scope',
                'behavioral_authority': 'synthetic coordinator-authored source, not external human approval',
                'semantic_profile': 'NOT_SELECTED' if unresolved else ('production-and-experimental-capability-assessment' if fid == 'F6' else 'typed-composition-1'),
                'mutable_state_expectations': 'NOT_REACHED' if unresolved else ('remote durable state required' if fid == 'F6' else 'none; stateless bytes-to-UInt16BE function'),
                'foundation_spec': 'experiments/typed_composition_r6_18/SEMANTICS-1.md'})
            write(folder / 'ACCEPTANCE.json', {'version': 'lykoi-pilot-acceptance-1', 'episode_id': eid,
                'frc_sha256': sha(folder / 'FRC.json'),
                'status': 'NOT_FROZEN_CLARIFICATION_REQUIRED' if unresolved else ('OBLIGATIONS_ONLY_NO_EXECUTABLE_ORACLE' if fid == 'F6' else 'FROZEN_FINITE_SUITE'),
                'review': 'same coordinator; candidate-output-independent derivation, no independent reviewer',
                'authoritative_sources': ['SOURCE.json', 'FRC.json', 'experiments/typed_composition_r6_18/SEMANTICS-1.md', 'experiments/semantic_interpreter/interpreter.py'],
                'cases': cases or [], 'required_state_obligations': obligations if fid == 'F6' else [],
                'provenance_policy': 'success root consumed span and empty scalar origins; failures retain normative offset/stage and artifact-resolved role',
                'logical_work_policy': 'work=0 rejection independently expected; full envelopes including work must match on three fresh-process replays; other exact work not independently predicted',
                'finite_tests_not_universal_correctness': True})
    frozen = {p.relative_to(ROOT).as_posix(): sha(p) for p in EVIDENCE.rglob('*.json')}
    write(EVIDENCE / 'SOURCE-FREEZE.json', {'version': 'lykoi-pilot-freeze-1',
        'utc': datetime.now(timezone.utc).isoformat(), 'stage': 'before construction code and candidate execution',
        'files': frozen, 'implementation_authorization': 'owner R6.48 authorization, conditional on per-episode frozen complete contracts; E01-E08 released only',
        'blocked': ['E09', 'E10'], 'assessment_only': ['E11', 'E12'],
        'independent_qualification': False})
    print(json.dumps({'protected': len(identities), 'sources': 12, 'complete_frc': 10,
                      'executable_acceptance_suites': 8, 'frozen_files': len(frozen)}))


if __name__ == '__main__':
    main()
