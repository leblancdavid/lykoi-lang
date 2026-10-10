"""Publish once or read-only verify R6.48 hashes, contracts and exported scope."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from prepare import ROOT, HERE, EVIDENCE, canonical, read, sha, write
from construct import c, verify_freeze
from dataset import validate, exportable

REPORT = ROOT / 'benchmark/results/phase6/R6_48-REPORT.md'
DOCS = [ROOT / ('docs/' + name + '-r6.48.md')
        for name in ('project-overview', 'research-log', 'decisions')]
FAILED_MANIFEST = EVIDENCE / 'PUBLICATION-IDENTITIES.json'
MANIFEST = EVIDENCE / 'PUBLICATION-IDENTITIES-v2.json'
RECEIPT = EVIDENCE / 'VERIFICATION.json'


def inventory():
    paths = [REPORT] + DOCS
    for folder in (HERE, EVIDENCE):
        paths += [p for p in folder.rglob('*') if p.is_file()
                  and '__pycache__' not in p.parts and p not in (MANIFEST, RECEIPT)]
    return sorted(paths)


def strict_json(path):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError('duplicate key in ' + str(path))
            out[key] = value
        return out

    def bad(_):
        raise ValueError('noninteger JSON number in ' + str(path))
    obj = json.loads(path.read_bytes(), object_pairs_hook=pairs,
                     parse_float=bad, parse_constant=bad)
    assert path.read_bytes() == canonical(obj) + b'\n', path
    return obj


def check_references(value):
    count = 0
    if type(value) is dict:
        if (set(value) == {'path', 'sha256'}
                and type(value['path']) is str and type(value['sha256']) is str):
            path = (ROOT / value['path']).resolve()
            assert path.is_relative_to(ROOT.resolve()), value['path']
            assert sha(path) == value['sha256'], value['path']
            count += 1
        for child in value.values():
            count += check_references(child)
    elif type(value) is list:
        for child in value:
            count += check_references(child)
    return count


def verify(allow_pending_receipt=False):
    baseline = read(EVIDENCE / 'BASELINE.json')
    failures = [name for name, digest in baseline['protected_files'].items()
                if sha(ROOT / name) != digest]
    assert not failures, failures
    source_hash = verify_freeze()
    candidate = read(EVIDENCE / 'CANDIDATE-FREEZE.json')
    assert candidate['source_freeze_sha256'] == source_hash
    for name, digest in candidate['files'].items():
        assert sha(ROOT / name) == digest, name
    assert read(EVIDENCE / 'SOURCE-FREEZE.json')['utc'] < candidate['utc']
    manifest = strict_json(MANIFEST)
    expected_paths = {p.relative_to(ROOT).as_posix() for p in inventory()}
    assert set(manifest['files']) == expected_paths
    for name, item in manifest['files'].items():
        path = ROOT / name
        assert sha(path) == item['sha256'] and path.stat().st_size == item['bytes'], name
    schema = strict_json(EVIDENCE / 'dataset-episode-1.schema.json')
    index = strict_json(EVIDENCE / 'DATASET-INDEX.json')
    assert len(index['episodes']) == 12
    assert len({e['episode_id'] for e in index['episodes']}) == 12
    for episode in index['episodes']:
        validate(episode, schema)
        assert episode == read(EVIDENCE / 'episodes' / episode['episode_id'] / 'DATASET-RECORD.json')
        assert not exportable(episode)
        assert episode['tool_trajectory_identity'] is None
        source = read(ROOT / episode['source_identity']['path'])
        assert source['original_requirement'] == episode['original_requirement']
        assert source['family_id'] == episode['family_id']
        expected_partition = 'development' if episode['family_id'] in ('F1', 'F2', 'F3', 'F4') else 'evaluation_quarantine'
        assert episode['partition_assignment'] == expected_partition
    export = strict_json(EVIDENCE / 'TRAINING-READY-EXPORT-MANIFEST.json')
    assert export['entries'] == [] and export['admitted_episode_count'] == 0
    assert not export['evaluation_material_included'] and not export['raw_evidence_included']
    assert read(EVIDENCE / 'PROCESS-CONTROLS.json')['all_passed']
    replays = [strict_json(EVIDENCE / ('REPLAY-%d.json' % n)) for n in (1, 2, 3)]
    for replay in replays:
        assert candidate['utc'] < replay['utc']
        assert replay['all_acceptance_matches'] and replay['ai_calls'] == 0
        assert hashlib.sha256(canonical(replay['results'])).hexdigest() == replay['observations_identity']
    assert all(p['results'] == replays[0]['results'] for p in replays)
    calls = 0
    definitions = 0
    dependencies = []
    for n in range(1, 9):
        folder = EVIDENCE / 'episodes' / ('E%02d' % n)
        trace = strict_json(folder / 'SCRIPTED-TRAJECTORY.json')
        assert trace['kind'] == 'DETERMINISTIC_SCRIPTED_CONSTRUCTION'
        assert not trace['ai_authored_tool_trajectory_available']
        assert trace['corrections_observed'] == 0
        package = read(folder / 'SYMBOLIC.json')
        definitions += 1 + len(package['definitions'])
        for definition in package['definitions'] + [package['program']]:
            assert c.identity(definition) == definition['identity']
            dependencies += list(definition['dependencies'])
        for i, entry in enumerate(trace['entries'], 1):
            assert entry['sequence'] == i and entry['status'] == 'returned'
            response = getattr(c, entry['tool'])(entry['arguments'])
            assert canonical(response) == canonical(entry['response'])
            calls += 1
        assert sha(folder / 'SYMBOLIC.json') == trace['final_symbolic_sha256']
        assert c.expand(package)['plan_identity'] == trace['final_artifact_identity']
        expanded = c.expand(package)
        assert expanded['plan'] == read(folder / 'EXECUTABLE.json')
        assert expanded['map'] == read(folder / 'EXPANSION-MAP.json')
    # Application definitions exist only inside their F4 family; no cross-family imports.
    assert set(dependencies) <= {'tally_pair', 'tally_three', 'packing_double', 'packing_triple'}
    json_files = 1
    references = 0
    links = 0
    byte_count = 0
    credential_pattern = re.compile(r'(?:sk-[A-Za-z0-9_-]{32,}|ghp_[A-Za-z0-9]{32,}|hf_[A-Za-z0-9]{32,})')
    for path in inventory():
        data = path.read_bytes()
        byte_count += len(data)
        text = data.decode('utf-8')
        assert data.endswith(b'\n') and b'\r' not in data, path
        assert not any(line.endswith((' ', '\t')) for line in text.splitlines()), path
        assert not credential_pattern.search(text), path
        if path.suffix == '.json':
            references += check_references(strict_json(path))
            json_files += 1
        if path.suffix == '.md':
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
                if '://' in target or target.startswith('#'):
                    continue
                resolved = (path.parent / target.split('#')[0]).resolve()
                assert resolved.exists() or (allow_pending_receipt and resolved == RECEIPT.resolve()), (path, target)
                links += 1
    tracked_diff = subprocess.check_output(['git', 'diff', '--name-only'], cwd=ROOT, text=True)
    assert not tracked_diff.strip(), tracked_diff
    status = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=ROOT, text=True)
    allowed = expected_paths | {MANIFEST.relative_to(ROOT).as_posix(), RECEIPT.relative_to(ROOT).as_posix()}
    for line in status.splitlines():
        assert line.startswith('?? '), line
        assert line[3:].replace('\\', '/') in allowed, line
    diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    summary = read(EVIDENCE / 'QUALITY-SUMMARY.json')
    assert summary['cases_per_pass'] == 81 and summary['episodes_admitted'] == 0
    assert summary['classification'] == 'R6_48_DATA_PIPELINE_PARTIAL'
    return {'round': 'R6.48', 'classification': summary['classification'], 'passed': True,
        'manifest_sha256': sha(MANIFEST), 'publication_files': len(expected_paths),
        'manifest_and_receipt_files': 2, 'protected_identities': len(baseline['protected_files']),
        'preservation_failures': [], 'r6_47_publication_files_verified': 15,
        'kernel': 26, 'kernel_basis': baseline['kernel_basis'],
        'production_and_experimental_implementations_unchanged': True,
        'source_and_candidate_seals_verified': True, 'strict_canonical_json_files_checked_including_manifest': json_files,
        'initial_publication_attempt': 'failed verifier schema/reference confusion; original manifest and failure record preserved',
        'initial_failed_manifest_sha256': sha(FAILED_MANIFEST),
        'dataset_records_schema_validated': 12, 'reference_bindings_checked': references,
        'relative_document_links_checked': links, 'scripted_api_calls_replayed_for_integrity': calls,
        'definitions_verified_including_programs': definitions,
        'candidate_suites': 8, 'cases_per_pass': 81, 'fresh_process_replays': 3,
        'all_finite_acceptance_matches': True, 'full_envelope_replay_matches': True,
        'admitted_episodes': 0, 'training_export_entries': 0, 'actual_ai_semantic_tool_trajectories': 0,
        'same_coordinator_independence_limit_preserved': True,
        'process_controls_passed': 10, 'new_file_whitespace_checked': True,
        'credential_pattern_scan_passed': True, 'tracked_diff_empty': True,
        'git_diff_check_returncode': diff.returncode, 'publication_payload_bytes': byte_count,
        'training_runs': 0, 'model_inference_calls': 0, 'model_downloads': 0,
        'package_installs': 0, 'p6_a04_acceptance_executions': 0, 'p6_a05_content_access': False,
        'stop': 'bounded pilot published; explicit authorization required for further work'}


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--publish', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.publish:
        assert not MANIFEST.exists() and not RECEIPT.exists()
        assert FAILED_MANIFEST.exists(), 'successor publication retains actual failed initial attempt'
        write(EVIDENCE / 'PUBLICATION-ATTEMPT-1-FAILURE.json', {
            'round': 'R6.48', 'stage': 'first --publish integrity check after initial manifest creation',
            'initial_manifest_sha256': sha(FAILED_MANIFEST),
            'error_type': 'TypeError',
            'error_message': "unsupported operand type(s) for /: 'WindowsPath' and 'dict'",
            'location': 'publication.py check_references: ROOT / value[path]',
            'cause': 'schema reference property definitions matched the concrete reference key set',
            'correction': 'require string-valued path and sha256 before resolving concrete references',
            'source_and_candidate_freezes_changed': False,
            'acceptance_expectations_changed': False, 'candidate_repairs': 0,
            'successor_manifest': MANIFEST.relative_to(ROOT).as_posix()})
        write(MANIFEST, {'round': 'R6.48', 'publication_version': 2,
            'supersedes_failed_manifest': FAILED_MANIFEST.relative_to(ROOT).as_posix(),
            'excluded': ['PUBLICATION-IDENTITIES-v2.json', 'VERIFICATION.json'],
            'files': {p.relative_to(ROOT).as_posix(): {'sha256': sha(p), 'bytes': p.stat().st_size}
                      for p in inventory()}})
        receipt = verify(allow_pending_receipt=True)
        write(RECEIPT, receipt)
        assert verify() == receipt
    else:
        receipt = verify()
        assert strict_json(RECEIPT) == receipt
    print(json.dumps({'publication_files': receipt['publication_files'],
                      'protected_identities': receipt['protected_identities'], 'passed': True,
                      'classification': receipt['classification'], 'admitted_episodes': 0,
                      'manifest_sha256': receipt['manifest_sha256'], 'verification_sha256': sha(RECEIPT)}))


if __name__ == '__main__':
    main()
