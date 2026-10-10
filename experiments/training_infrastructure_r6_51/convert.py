"""Offline, fail-closed conversion of the sealed R6.49 Tier T cohort. No ML calls."""
import copy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'benchmark/results/phase6/r6_51'
OLD = ROOT / 'benchmark/results/phase6/r6_49'
GATES = {'source_and_frc', 'validated_target', 'frozen_acceptance', 'deterministic_replay',
         'stable_provenance', 'no_known_contradiction', 'no_known_evaluation_leakage',
         'owner_authorized_candidate_preparation'}


def strict(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def bad(value):
        raise ValueError('nonfinite JSON')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=bad)


def read(path):
    return strict(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':'), allow_nan=False)


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def verified(ref):
    if type(ref) is not dict or set(ref) != {'path', 'sha256'}:
        raise ValueError('incomplete identity')
    path = (ROOT / ref['path']).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file() or sha(path) != ref['sha256']:
        raise ValueError('identity mismatch or unsafe path')
    return read(path) if path.suffix == '.json' else path.read_text(encoding='utf-8')


def seal_check():
    for round_id in ('r6_49', 'r6_50'):
        folder = ROOT / 'benchmark/results/phase6' / round_id
        manifest = read(folder / 'PUBLICATION-IDENTITIES.json')
        if read(folder / 'VERIFICATION.json')['manifest_sha256'] != sha(folder / 'PUBLICATION-IDENTITIES.json'):
            raise ValueError('publication receipt mismatch')
        for name, record in manifest['files'].items():
            path = ROOT / name
            if sha(path) != record['sha256'] or path.stat().st_size != record['bytes']:
                raise ValueError('publication mismatch: ' + name)
    baseline = read(OLD / 'BASELINE.json')
    for name, digest in baseline['protected_files'].items():
        if sha(ROOT / name) != digest:
            raise ValueError('protected identity mismatch: ' + name)
    accounting = read(ROOT / 'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json')
    if baseline['kernel'] != 26 or accounting['final_count'] != 26 or accounting['additions'] != []:
        raise ValueError('kernel mismatch')
    if read(ROOT / 'benchmark/results/phase6/r6_48/TRAINING-READY-EXPORT-MANIFEST.json')['admitted_episode_count'] != 0:
        raise ValueError('historical zero admission changed')
    groups = {}
    for label, prefix in {'production': 'src/air_compiler/', 'R6.10 VM': 'experiments/semantic_interpreter/',
                          'R6.18 wrapper': 'experiments/typed_composition_r6_18/',
                          'R6.23 adapter': 'benchmark/results/phase6/r6_23/',
                          'R6.25 tool contracts': 'benchmark/results/phase6/r6_25/',
                          'R6.32 registry': 'experiments/lifecycle_r6_32/'}.items():
        groups[label] = sum(name.startswith(prefix) for name in baseline['protected_files'])
        if not groups[label]:
            raise ValueError('missing preservation group: ' + label)
    return {'protected_files': len(baseline['protected_files']), 'verified_preservation_groups': groups, 'kernel': 26,
            'r6_50_manifest_sha256': sha(ROOT / 'benchmark/results/phase6/r6_50/PUBLICATION-IDENTITIES.json'),
            'r6_49_index_sha256': sha(OLD / 'DATASET-INDEX.json'), 'r6_48_original_admissions': 0}


def eligible(entry):
    if entry['tier_t'] != 'T_CANDIDATE_ADMITTED' or entry['tier_e'] != 'NOT_QUALIFIED':
        raise ValueError('not admitted Tier T')
    if entry['partition'] != 'training_development':
        raise ValueError('evaluation/quarantine export forbidden')
    gates = entry['admission_gates']
    if set(gates) != GATES or any(type(v) is not bool or not v for v in gates.values()):
        raise ValueError('failed or missing admission gate')
    if not all(type(entry[k]) is str and entry[k] for k in ('episode_id', 'family_id', 'component')):
        raise ValueError('missing grouping')


def convert_entry(entry):
    eligible(entry)
    direct = entry['direct']
    required = {'SOURCE.json', 'FRC.json', 'ACCEPTANCE.json', 'VALIDATION.json'}
    stateful = entry['component'] == 'PRODUCTION_LOCAL_STATE'
    if entry['component'] not in ('PRODUCTION_LOCAL_STATE', 'STATELESS_READ_CHECK_ENCODE'):
        raise ValueError('unknown semantic profile')
    target_name = 'AI-INTENT.json' if stateful else 'SYMBOLIC.json'
    required.add(target_name)
    if not required <= set(direct):
        raise ValueError('incomplete source record')
    evidence = {name: verified(ref) for name, ref in direct.items()}
    source = evidence['SOURCE.json']
    if not isinstance(source.get('original_requirement'), str) or not source['original_requirement'].strip():
        raise ValueError('missing original requirement')
    if source['episode_id'] != entry['episode_id'].split('/')[1]:
        raise ValueError('episode mismatch')
    if source['family_id'] != entry['family_id'].split('/')[1]:
        raise ValueError('family mismatch')
    valid = evidence['VALIDATION.json']
    if (valid.get('status') != 'VALID' if stateful else valid.get('validation', {}).get('status') != 'valid'):
        raise ValueError('invalid symbolic target')
    vocabulary = read(OUT / 'VOCABULARY.json')['stateful' if stateful else 'stateless']
    input_value = {'requirement': source['original_requirement'], 'semantic_vocabulary': vocabulary,
                   'required_output': target_name + ': one complete JSON object; no markdown or Python'}
    return {'version': 'lykoi-sft-1', 'mode': 'direct', 'episode_id': entry['episode_id'],
            'family_id': entry['family_id'], 'component': entry['component'], 'split': 'training_development',
            'prompt': [{'role': 'system', 'content': 'Construct the declared Lykoi research representation using only the supplied vocabulary.'},
                       {'role': 'user', 'content': dump(input_value)}],
            'completion': [{'role': 'assistant', 'content': dump(evidence[target_name])}],
            'provenance': {'source_refs': direct, 'source_provenance': source,
                           'admission_index_sha256': sha(OLD / 'DATASET-INDEX.json'),
                           'limitations': entry['limitations'], 'target_kind': target_name,
                           'ai_tool_trajectory': False, 'preparation_only': True}}


def partition_guard(records, assignments):
    seen = {}
    for record in records:
        split = assignments.get(record['episode_id'], record['split'])
        for key in (record['family_id'], record['component']):
            if key in seen and seen[key] != split:
                raise ValueError('connected ancestry crosses partitions')
            seen[key] = split
        if split != 'training_development':
            raise ValueError('exposed source cannot become evaluation')


def tool_record(entry):
    eligible(entry)
    # This cohort contains no observed semantic selections/state/typed arguments.
    # A non-null future capture requires a new separately qualified parser, never inference.
    if entry.get('actual_semantic_tool_trajectory') is None:
        raise ValueError('NO_OBSERVED_SEMANTIC_TOOL_DECISION; scripted traces and AI file edits excluded')
    raise ValueError('UNQUALIFIED_NEW_TRAJECTORY_FORMAT; observed state/schema/outcome capture required')


def estimate(text):
    n = len(text.encode('utf-8'))
    return {'utf8_bytes': n, 'estimated_tokens_low': math.ceil(n / 4),
            'estimated_tokens_high': math.ceil(n / 2), 'actual_tokenizer_used': False}


def build():
    baseline = seal_check()
    index = read(OLD / 'DATASET-INDEX.json')
    if index['tier_t_count'] != 10 or index['tier_e_count'] != 0 or len(index['entries']) != 10:
        raise ValueError('cohort mismatch')
    records, excluded, lengths = [], [], []
    seen = set()
    for entry in index['entries']:
        if entry['episode_id'] in seen:
            raise ValueError('duplicate source episode')
        seen.add(entry['episode_id'])
        try:
            record = convert_entry(entry)
            records.append(record)
            parts = entry['direct']
            lengths.append({'episode_id': entry['episode_id'],
                'requirement': estimate(verified(parts['SOURCE.json'])['original_requirement']),
                'target': estimate(record['completion'][0]['content']),
                'prompt_plus_target': estimate(''.join(m['content'] for m in record['prompt'] + record['completion'])),
                'validation_feedback': estimate(dump(verified(parts['VALIDATION.json'])))})
        except (ValueError, KeyError, TypeError) as exc:
            excluded.append({'episode_id': entry['episode_id'], 'mode': 'direct', 'reason': str(exc)})
        try:
            tool_record(entry)
        except ValueError as exc:
            excluded.append({'episode_id': entry['episode_id'], 'mode': 'tool', 'reason': str(exc),
                'ai_edit_capture_available': entry.get('actual_ai_edit_trajectory') is not None,
                'scripted_capture_available': entry.get('scripted_trajectory') is not None})
    partition_guard(records, {})
    return records, {'baseline': baseline, 'direct_records': len(records), 'genuine_tool_records': 0,
        'excluded': excluded, 'sequence_estimates': lengths, 'method': 'UTF8 bytes / 4 to / 2; not tokenizer bounds; add chat-template overhead',
        'independent_evaluation_records': 0, 'training_runs': 0}


def main():
    records, assessment = build()
    OUT.joinpath('DIRECT.jsonl').write_text(''.join(dump(r) + '\n' for r in records), encoding='utf-8', newline='\n')
    OUT.joinpath('TOOL.jsonl').write_text('', encoding='utf-8')
    write(OUT / 'CONVERSION-ASSESSMENT.json', assessment)
    print(json.dumps({'direct': len(records), 'tool': 0, 'excluded': len(assessment['excluded'])}))


if __name__ == '__main__':
    main()
