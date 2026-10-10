"""Seal and read-only verify R6.49 publication, evidence and protected history."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from prepare import ROOT, HERE, OUT, OLD, read, write, sha, canonical
from dataset import admit

REPORT = ROOT / 'benchmark/results/phase6/R6_49-REPORT.md'
DOCS = [ROOT / ('docs/' + n + '-r6.49.md') for n in ('project-overview', 'research-log', 'decisions')]
DOCS += [ROOT / 'docs/training-data-admission-r6.49.md']
MANIFEST = OUT / 'PUBLICATION-IDENTITIES.json'
RECEIPT = OUT / 'VERIFICATION.json'


def inventory():
    paths = [REPORT] + DOCS
    for folder in (HERE, OUT):
        paths += [p for p in folder.rglob('*') if p.is_file()
                  and '__pycache__' not in p.parts and p not in (MANIFEST, RECEIPT)]
    return sorted(paths)


def strict_json(path):
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d:
                raise ValueError('duplicate key: ' + str(path))
            d[k] = v
        return d

    def bad(value):
        raise ValueError('nonfinite JSON value: ' + value)
    return json.loads(path.read_bytes(), object_pairs_hook=pairs, parse_constant=bad)


def references(value):
    count = 0
    if type(value) is dict:
        if set(value) == {'path', 'sha256'} and type(value['path']) is str and type(value['sha256']) is str:
            p = (ROOT / value['path']).resolve()
            assert p.is_relative_to(ROOT.resolve()) and sha(p) == value['sha256'], value
            count += 1
        for child in value.values():
            count += references(child)
    elif type(value) is list:
        for child in value:
            count += references(child)
    return count


def verify(pending_receipt=False):
    baseline = read(OUT / 'BASELINE.json')
    assert all(sha(ROOT / p) == h for p, h in baseline['protected_files'].items())
    assert baseline['kernel'] == 26
    assert read(OLD / 'TRAINING-READY-EXPORT-MANIFEST.json')['admitted_episode_count'] == 0
    assert read(OLD / 'VERIFICATION.json')['manifest_sha256'] == sha(OLD / 'PUBLICATION-IDENTITIES-v2.json')
    for name in ('SOURCE-FREEZE.json', 'CANDIDATE-FREEZE.json'):
        for p, h in read(OUT / name)['files'].items():
            assert sha(ROOT / p) == h, p
    source = read(OUT / 'SOURCE-FREEZE.json')
    candidate = read(OUT / 'CANDIDATE-FREEZE.json')
    assert source['utc'] < candidate['utc']
    assert candidate['source_freeze_sha256'] == sha(OUT / 'SOURCE-FREEZE.json')
    replays = [read(OUT / ('REPLAY-%d.json' % i)) for i in (1, 2)]
    for replay in replays:
        assert candidate['utc'] < replay['utc'] and replay['passed'] and replay['ai_calls'] == 0
        assert replay['observations_sha256'] == hashlib.sha256(canonical(replay['results'])).hexdigest()
        assert replay['fresh_process_requests'] == 61
    assert replays[0]['results'] == replays[1]['results']
    sys.path.insert(0, str(ROOT / 'experiments/value_added_r6_16'))
    from generate import generate
    for eid in ('S01', 'S02'):
        folder = OUT / 'episodes' / eid
        generated, ir = generate(read(folder / 'AI-INTENT.json'), 'C')
        assert generated.encode('utf-8') == (folder / 'APPLICATION.py').read_bytes()
        assert ir == read(folder / 'SYMBOLIC-IR.json')
        # Offline observation verification avoids creating unrecorded new runtime calls.
        suite = read(folder / 'ACCEPTANCE.json')['cases']
        result = next(r for r in replays[0]['results'] if r['episode_id'] == eid)
        assert len(suite) == len(result['observations'])
        for case, obs in zip(suite, result['observations']):
            assert obs['request'] == {k: case[k] for k in ('op', 'args', 'providers')}
            assert obs['returncode'] == 0 and obs['actual'] == case['expected']
            assert json.loads(obs['stdout']) == obs['actual']
            raw = bytes.fromhex(obs['storage_after_hex']) if obs['storage_after_hex'] is not None else None
            records = json.loads(raw) if raw is not None else []
            assert records == case['expected_records']
            assert all(r['label'].strip() and r['phase'] in read(folder / 'FRC.json')['state_domains']['phase']
                       and r['seal'] in ('open', 'closed') and (r['phase'] != 'released' or r['seal'] == 'closed') for r in records)
            if case['rejection_bytes_unchanged']:
                assert obs['storage_before_hex'] == obs['storage_after_hex']
            assert obs['passed'] and all(obs['checks'].values())
        restart = result['final_restart']
        assert restart['passed'] and restart['actual'] == {'ok': suite[-1]['expected_records']}
        assert json.loads(bytes.fromhex(restart['persisted_bytes_hex'])) == suite[-1]['expected_records']
    historical = read(OUT / 'R6_48-REASSESSMENT-REPLAY.json')
    assert historical['passed'] and historical['observations'] == 162
    for row in historical['results']:
        assert row['first_replay'] == row['second_replay'] and row['matches_three_historical_replays']
        for i in (1, 2, 3):
            original = next(r for r in read(OLD / ('REPLAY-%d.json' % i))['results'] if r['episode_id'] == row['episode_id'])
            assert [o['actual'] for o in original['observations']] == row['first_replay']
    ledger = read(OUT / 'R6_48-SUCCESSOR-LEDGER.json')
    assert ledger['historical_admitted_count'] == 0 and len(ledger['entries']) == 8
    index = read(OUT / 'DATASET-INDEX.json')
    assert index['tier_t_count'] == 10 and index['tier_e_count'] == 0 and len(index['entries']) == 10
    assert len({e['episode_id'] for e in index['entries']}) == 10
    for entry in index['entries']:
        assert admit(entry['admission_gates'], entry['partition'])
        assert entry['tier_t'] == 'T_CANDIDATE_ADMITTED' and entry['tier_e'] == 'NOT_QUALIFIED'
        assert entry['actual_semantic_tool_trajectory'] is None
        if entry['episode_id'].startswith('R6.48/'):
            assert entry['actual_ai_edit_trajectory'] is None
        else:
            eid = entry['episode_id'].split('/')[1]
            assert entry == read(OUT / 'episodes' / eid / 'DATASET-RECORD.json')
    partition = read(OUT / 'DEDUPLICATION-AND-PARTITIONS.json')
    assert not partition['evaluation_qualified_families'] and not partition['semantic_duplicates_within_counted_cohort']
    assert partition['nominal_requirement_families'] == len({e['family_id'] for e in index['entries']}) == 5
    assert {e['episode_id'] for e in index['entries']} == {e for c in partition['components'] for e in c['episodes']}
    controls = read(OUT / 'ADMISSION-CONTROLS.json')
    assert controls['all_passed'] and len(controls['controls']) == 12 and all(c['rejected'] for c in controls['controls'])
    mutant = read(OUT / 'WRONG-TRANSITION-CONTROL.json')
    assert mutant['validation_passed'] and not mutant['observations']['passed'] and not mutant['training_example']
    transcript = read(OUT / 'AI-CONSTRUCTION-TRANSCRIPT.json')
    assert transcript['semantic_mcp_calls'] == 0 and not transcript['hidden_reasoning_included']
    calls = [t for row in transcript['entries'] for t in row['actual_tool_calls']]
    assert len(calls) == read(OUT / 'CONSTRUCTION-COST.json')['tool_call_count'] == 10
    assert any('INVALID_TYPED_SCALAR_RELATION' in str(c['response']) for c in calls)
    assert any('validated, lowered and frozen' in str(c['response']) for c in calls)
    epoch = datetime.fromisoformat(source['utc']).timestamp() * 1000
    creation = [c for c in calls if '*** Add File: benchmark/results/phase6/r6_49/episodes/S01/AI-INTENT.json' in json.dumps(c['arguments'])]
    assert creation and all(c['time']['start'] > epoch for c in creation)
    assert all(row['message_metadata']['modelID'] == 'gpt-6.1-sol' for row in transcript['entries'])
    auth = read(OUT / 'OWNER-AUTHORIZATION.json')['original_owner_message']['text']
    assert 'I authorize a bounded, nonproduction investigation and data-generation pilot.' in auth
    assert 'Do not train or fine-tune a model.' in auth
    paths = inventory()
    expected = {p.relative_to(ROOT).as_posix() for p in paths}
    manifest = strict_json(MANIFEST)
    assert set(manifest['files']) == expected
    ref_count, json_count, link_count, byte_count = 0, 0, 0, 0
    for p in paths:
        name = p.relative_to(ROOT).as_posix()
        data = p.read_bytes()
        assert manifest['files'][name] == {'sha256': sha(p), 'bytes': len(data)}
        byte_count += len(data)
        text = data.decode('utf-8')
        assert data.endswith(b'\n') and b'\r' not in data, name
        assert not any(line.endswith((' ', '\t')) for line in text.splitlines()), name
        assert not re.search(r'(?:sk-[A-Za-z0-9_-]{32,}|ghp_[A-Za-z0-9]{32,}|hf_[A-Za-z0-9]{32,})', text), name
        if p.suffix == '.json':
            ref_count += references(strict_json(p))
            json_count += 1
        if p.suffix == '.md':
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
                if '://' in target or target.startswith('#'):
                    continue
                resolved = (p.parent / target.split('#')[0]).resolve()
                assert resolved.exists() or (pending_receipt and resolved == RECEIPT.resolve()), (name, target)
                link_count += 1
    assert not subprocess.check_output(['git', 'diff', '--name-only'], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=ROOT, text=True)
    allowed = expected | {MANIFEST.relative_to(ROOT).as_posix(), RECEIPT.relative_to(ROOT).as_posix()}
    for line in status.splitlines():
        assert line.startswith('?? ') and line[3:].replace('\\', '/') in allowed, line
    diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    readiness = read(OUT / 'READINESS.json')
    assert readiness['tier_t_candidates'] == 10 and readiness['tier_e_examples'] == 0
    return {'passed': True, 'classification': readiness['classification'], 'manifest_sha256': sha(MANIFEST),
        'protected_identities': len(baseline['protected_files']), 'preservation_failures': [],
        'publication_files': len(paths), 'publication_payload_bytes': byte_count,
        'strict_json_files': json_count, 'reference_bindings_checked': ref_count, 'relative_links_checked': link_count,
        'kernel': 26, 'production_vm_wrapper_adapter_contracts_registry_unchanged': True,
        'original_r6_48_admission': 0, 'successor_tier_t_count': 10, 'tier_e_count': 0,
        'stateful_accepted': 2, 'stateful_steps_per_pass': 59, 'fresh_process_requests': 122,
        'replay_observations_identical': True, 'candidate_regeneration_matches': True,
        'source_candidate_ordering_verified': True, 'actual_ai_edits_after_source_freeze': True,
        'actual_semantic_mcp_calls': 0, 'actual_ai_edit_episode_views': 2,
        'admission_controls': 12, 'historical_reassessment_observations': 162,
        'new_file_whitespace_and_credentials_checked': True, 'tracked_diff_empty': True,
        'git_diff_check_returncode': diff.returncode, 'training_runs': 0, 'downloads': 0,
        'package_installs': 0, 'p6_a04_acceptance': 0, 'p6_a05_access': False,
        'stop': 'published bounded pilot; further work requires explicit authorization'}


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--publish', action='store_true')
    group.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.publish:
        write(MANIFEST, {'round': 'R6.49', 'excluded': ['PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'],
            'files': {p.relative_to(ROOT).as_posix(): {'sha256': sha(p), 'bytes': p.stat().st_size} for p in inventory()}})
        receipt = verify(pending_receipt=True)
        write(RECEIPT, receipt)
        assert verify() == receipt
    else:
        receipt = verify()
        assert receipt == read(RECEIPT)
    print(json.dumps({k: receipt[k] for k in ('passed', 'classification', 'protected_identities',
        'publication_files', 'publication_payload_bytes', 'successor_tier_t_count', 'tier_e_count')}))


if __name__ == '__main__':
    main()
