"""Round-local serialization/admission gate; no execution primitives."""
import copy
import hashlib
from collections import Counter

from prepare import ROOT, EVIDENCE, canonical, read, sha, write
from construct import c, verify_freeze
from replay import compare

STATUSES = ['TRAINING_ADMITTED', 'VALIDATED_LIMITED_EVIDENCE', 'CAPABILITY_GAP',
            'REQUIREMENT_CLARIFICATION_REQUIRED', 'ACCEPTANCE_GAP',
            'IMPLEMENTATION_FAILURE', 'PROVENANCE_OR_LEAKAGE_GAP']


def schema():
    reference = {'type': 'object', 'required': ['path', 'sha256'], 'additionalProperties': False,
                 'properties': {'path': {'type': 'string'}, 'sha256': {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}}}
    nullable_ref = {'oneOf': [{'$ref': '#/$defs/reference'}, {'type': 'null'}]}
    properties = {
        'schema_version': {'const': 'lykoi-training-episode-1'},
        'episode_id': {'type': 'string', 'pattern': '^E[0-9]{2}$'},
        'family_id': {'type': 'string', 'pattern': '^F[1-6]$'},
        'original_requirement': {'type': 'string'},
        'source_identity': {'$ref': '#/$defs/reference'},
        'formal_requirement_contract': {'$ref': '#/$defs/reference'},
        'semantic_profile': {'type': 'string'},
        'symbolic_artifact_identity': nullable_ref,
        'executable_artifact_identity': nullable_ref,
        'tool_trajectory_identity': nullable_ref,
        'scripted_trajectory_identity': nullable_ref,
        'acceptance_identity': {'$ref': '#/$defs/reference'},
        'validation_status': {'enum': ['VALID', 'NOT_REACHED', 'NOT_REPRESENTABLE']},
        'replay_evidence': {'type': 'array', 'items': {'$ref': '#/$defs/reference'}},
        'provenance_classification': {'const': 'SAME_COORDINATOR_EXPOSED'},
        'partition_assignment': {'enum': ['development', 'evaluation_quarantine']},
        'admission_status': {'enum': STATUSES},
        'technical_status': {'enum': STATUSES},
        'admission_blockers': {'type': 'array', 'items': {'type': 'string'}},
    }
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema',
            '$id': 'urn:lykoi:training-episode:1', 'title': 'Lykoi training episode 1',
            'type': 'object', 'required': list(properties), 'additionalProperties': False,
            'properties': properties, '$defs': {'reference': reference}}


def validate(value, spec, root=None):
    """Validate exactly the JSON Schema keywords used in this version, stdlib only."""
    import re
    root = root or spec
    if '$ref' in spec:
        assert spec['$ref'] == '#/$defs/reference'
        return validate(value, root['$defs']['reference'], root)
    if 'oneOf' in spec:
        matches = 0
        for branch in spec['oneOf']:
            try:
                validate(value, branch, root)
                matches += 1
            except ValueError:
                pass
        if matches != 1:
            raise ValueError('oneOf')
    kinds = {'object': dict, 'array': list, 'string': str, 'null': type(None)}
    if 'type' in spec and type(value) is not kinds[spec['type']]:
        raise ValueError('type')
    if 'const' in spec and (type(value) is not type(spec['const']) or value != spec['const']):
        raise ValueError('const')
    if 'enum' in spec and value not in spec['enum']:
        raise ValueError('enum')
    if 'pattern' in spec and not re.fullmatch(spec['pattern'], value):
        raise ValueError('pattern')
    if type(value) is dict and 'properties' in spec:
        if not set(spec.get('required', [])) <= set(value):
            raise ValueError('required')
        if spec.get('additionalProperties') is False and set(value) - set(spec['properties']):
            raise ValueError('additionalProperties')
        for key, item in value.items():
            if key in spec['properties']:
                validate(item, spec['properties'][key], root)
    if type(value) is list and 'items' in spec:
        for item in value:
            validate(item, spec['items'], root)


def reference(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)}


def exportable(episode):
    # The status label alone cannot waive the independent-evidence gate.
    return (episode['admission_status'] == 'TRAINING_ADMITTED'
            and episode['partition_assignment'] == 'development'
            and episode['validation_status'] == 'VALID'
            and not episode['admission_blockers']
            and episode['provenance_classification'] != 'SAME_COORDINATOR_EXPOSED')


def controls(s):
    checks = []
    package = read(EVIDENCE / 'episodes/E01/SYMBOLIC.json')
    for label, code, change in [
        ('tampered_content_identity', 'IDENTITY', lambda p: p['program'].update(identity='0' * 64)),
        ('wrong_declared_type', 'TYPE', lambda p: p['program']['steps'][0].update(type='Bool')),
        ('missing_exact_dependencies', 'DEPENDENCY', lambda p: p['program']['steps'][2].update(deps=[])),
    ]:
        p = copy.deepcopy(package)
        change(p)
        result = c.diagnose(p)
        checks.append({'control': label, 'expected_code': code, 'actual': result,
                       'passed': result['status'] == 'reject' and result['diagnostic']['code'] == code})
    replay = read(EVIDENCE / 'REPLAY-1.json')['results'][0]['observations'][0]['actual']
    case = read(EVIDENCE / 'episodes/E01/ACCEPTANCE.json')['cases'][0]
    changed = copy.deepcopy(replay)
    changed['value'] += 1
    differences = compare(case['expected'], changed, 'program/' + package['program']['identity'])
    checks.append({'control': 'wrong_success_value_rejected_by_scorer', 'passed': bool(differences), 'differences': differences})
    negative = read(EVIDENCE / 'REPLAY-1.json')['results'][0]['observations'][3]['actual']
    negative_case = read(EVIDENCE / 'episodes/E01/ACCEPTANCE.json')['cases'][3]
    changed = copy.deepcopy(negative)
    changed['error']['offset'] += 1
    differences = compare(negative_case['expected'], changed, 'program/' + package['program']['identity'])
    checks.append({'control': 'wrong_error_provenance_rejected', 'passed': bool(differences), 'differences': differences})
    changed = copy.deepcopy(replay)
    changed['work'] += 1
    checks.append({'control': 'logical_work_change_breaks_complete_replay_identity',
                   'passed': canonical(changed) != canonical(replay)})
    invalid = {'episode_id': 'E01'}
    try:
        validate(invalid, s)
        rejected = False
    except ValueError:
        rejected = True
    checks.append({'control': 'incomplete_dataset_record_rejected', 'passed': rejected})
    identity_failures = []
    for name, digest in read(EVIDENCE / 'SOURCE-FREEZE.json')['files'].items():
        if sha(ROOT / name) != digest:
            identity_failures.append(name)
    checks.append({'control': 'source_acceptance_partition_unchanged_after_execution', 'passed': not identity_failures,
                   'failures': identity_failures})
    return checks


def main():
    verify_freeze()
    passes = [read(EVIDENCE / ('REPLAY-%d.json' % n)) for n in (1, 2, 3)]
    identical = len({p['observations_identity'] for p in passes}) == 1
    assert identical
    s = schema()
    write(EVIDENCE / 'dataset-episode-1.schema.json', s)
    episodes = []
    for n in range(1, 13):
        eid = 'E%02d' % n
        folder = EVIDENCE / 'episodes' / eid
        source = read(folder / 'SOURCE.json')
        frc = read(folder / 'FRC.json')
        executed = n <= 8
        matches = executed and all(p['results'][n - 1]['all_acceptance_matches'] for p in passes)
        technical = ('VALIDATED_LIMITED_EVIDENCE' if matches else 'IMPLEMENTATION_FAILURE') if executed else (
            'REQUIREMENT_CLARIFICATION_REQUIRED' if n <= 10 else 'CAPABILITY_GAP')
        blockers = ['independent commissioning unavailable', 'independent acceptance review unavailable',
                    'same-coordinator repository/evaluation exposure']
        if n > 8:
            blockers.append(technical)
        episode = {
            'schema_version': 'lykoi-training-episode-1', 'episode_id': eid, 'family_id': source['family_id'],
            'original_requirement': source['original_requirement'],
            'source_identity': reference(folder / 'SOURCE.json'),
            'formal_requirement_contract': reference(folder / 'FRC.json'),
            'semantic_profile': frc['semantic_profile'],
            'symbolic_artifact_identity': reference(folder / 'SYMBOLIC.json') if executed else None,
            'executable_artifact_identity': reference(folder / 'EXECUTABLE.json') if executed else None,
            'tool_trajectory_identity': None,
            'scripted_trajectory_identity': reference(folder / 'SCRIPTED-TRAJECTORY.json') if executed else None,
            'acceptance_identity': reference(folder / 'ACCEPTANCE.json'),
            'validation_status': 'VALID' if executed else ('NOT_REACHED' if n <= 10 else 'NOT_REPRESENTABLE'),
            'replay_evidence': [reference(EVIDENCE / ('REPLAY-%d.json' % k)) for k in (1, 2, 3)] if executed else [],
            'provenance_classification': 'SAME_COORDINATOR_EXPOSED',
            'partition_assignment': 'development' if n <= 8 else 'evaluation_quarantine',
            'admission_status': 'PROVENANCE_OR_LEAKAGE_GAP' if matches else technical,
            'technical_status': technical, 'admission_blockers': blockers,
        }
        validate(episode, s)
        write(folder / 'DATASET-RECORD.json', episode)
        if n > 8:
            gap = {'episode_id': eid, 'status': technical, 'candidate_constructed': False,
                   'acceptance_execution': 'NOT_REACHED', 'production_candidate_attempted': False,
                   'experimental_candidate_attempted': False}
            if n <= 10:
                gap.update({'missing_decisions': frc['ambiguities'], 'clarification_answers': None,
                            'production_capability_verdict': 'NOT_ASSESSED; source incomplete, not a language gap'})
            else:
                gap.update({'gap': 'No distributed commit, physical-device effect adapter or authenticating execution source in current profiles',
                    'basis': [reference(ROOT / 'docs/atomic-durable-history-v1.md'),
                              reference(ROOT / 'docs/prewrite-conditional-composition-v1.md'),
                              reference(ROOT / 'experiments/typed_composition_r6_18/SEMANTICS-1.md')],
                    'production_backed': 'bounded one-store durable state and externally asserted trusted-context binding only',
                    'experimental_profile': 'stateless UInt8 reads, ordered checks, arithmetic and UInt16BE output',
                    'secondary_gap': 'ACCEPTANCE_GAP: no distributed/physical test harness or executable frozen expectations',
                    'specification_limitation': 'strong availability/exactly-once constraints under absent coordination may be mutually unachievable; no whole-language impossibility proof',
                    'supported_subrelations_not_whole_requirement_success': True})
            write(folder / 'DISPOSITION.json', gap)
        episodes.append(episode)
    write(EVIDENCE / 'DATASET-INDEX.json', {'schema_version': 'lykoi-training-episode-1', 'episodes': episodes,
                                         'raw_research_records_not_training_release': True})
    checks = controls(s)
    forged = copy.deepcopy(episodes[0])
    forged['admission_status'] = 'TRAINING_ADMITTED'
    checks.append({'control': 'forged_admission_label_cannot_bypass_provenance', 'passed': not exportable(forged)})
    evaluation = copy.deepcopy(forged)
    evaluation['partition_assignment'] = 'evaluation_quarantine'
    evaluation['admission_blockers'] = []
    evaluation['provenance_classification'] = 'INDEPENDENT'  # gate negative control only, never a record
    checks.append({'control': 'evaluation_record_cannot_enter_training_export', 'passed': not exportable(evaluation)})
    write(EVIDENCE / 'PROCESS-CONTROLS.json', {'controls': checks, 'all_passed': all(x['passed'] for x in checks),
                                             'mutants_are_negative_controls_not_failed_candidates': True})
    admitted = [e for e in episodes if exportable(e)]
    assert not admitted
    write(EVIDENCE / 'TRAINING-READY-EXPORT-MANIFEST.json', {
        'version': 'lykoi-training-export-1', 'status': 'EMPTY_NO_EPISODES_ADMITTED',
        'dataset_schema': reference(EVIDENCE / 'dataset-episode-1.schema.json'),
        'entries': [], 'admitted_episode_count': 0, 'raw_evidence_included': False,
        'evaluation_material_included': False, 'credentials_or_private_provider_metadata_included': False,
        'nonempty_training_export_authorized': False})
    write(EVIDENCE / 'ADMISSION-LEDGER.json', {'round': 'R6.48', 'entries': [
        {k: e[k] for k in ('episode_id', 'family_id', 'partition_assignment', 'admission_status',
                          'technical_status', 'validation_status', 'admission_blockers')} for e in episodes],
        'counts': dict(Counter(e['admission_status'] for e in episodes)),
        'technical_counts': dict(Counter(e['technical_status'] for e in episodes)),
        'precedence': 'incomplete source first, then whole-contract capability, then implementation, then admission provenance; secondary blockers retained'})
    patterns = set()
    operations = Counter()
    expressions = Counter()
    definitions = 0
    steps = 0
    for e in episodes[:8]:
        p = read(ROOT / e['symbolic_artifact_identity']['path'])
        definitions += 1 + len(p['definitions'])
        pattern = []
        for d in p['definitions'] + [p['program']]:
            steps += len(d['steps'])
            pattern.append([s['node']['op'] for s in d['steps']])
            for st in d['steps']:
                operations[st['node']['op']] += 1
            def visit(x):
                if type(x) is dict:
                    for key, val in x.items():
                        if key in ('add', 'le', 'eq', 'ref', 'const'):
                            expressions[key] += 1
                        visit(val)
                elif type(x) is list:
                    for val in x:
                        visit(val)
            visit(d)
        patterns.add(canonical(pattern))
    coverage = {
        'typed_arithmetic': {'episodes': ['E01', 'E02', 'E04', 'E07', 'E08'], 'status': 'FINITE_EXECUTION'},
        'boolean_constraints': {'episodes': ['E03', 'E04'], 'status': 'FINITE_EXECUTION_EXPLICIT_BOOL_LOCALS'},
        'ordered_checks': {'episodes': ['E01', 'E02', 'E03', 'E04', 'E05', 'E06', 'E07', 'E08'], 'status': 'FINITE_EXECUTION'},
        'dependency_composition': {'episodes': ['E07', 'E08'], 'status': 'FINITE_EXECUTION_PINNED_NESTED_DEFINITIONS'},
        'invalid_input': {'episodes': ['E01', 'E02', 'E03', 'E04', 'E05', 'E06', 'E07', 'E08'], 'status': 'FINITE_EXECUTION'},
        'error_precedence': {'episodes': ['E01', 'E02', 'E03', 'E04', 'E05', 'E06', 'E07', 'E08'], 'status': 'FINITE_EXECUTION_MIXED_INVALID_CASES'},
        'state_transitions': {'episodes': ['E09', 'E10', 'E11', 'E12'], 'status': 'SOURCE_ATTEMPT_ONLY_NO_EXECUTION'},
        'invariants': {'episodes': ['E01', 'E02', 'E03', 'E04', 'E06', 'E07', 'E08'], 'status': 'PURE_CHECK_CONSTRAINTS_ONLY; durable invariants NOT_REACHED'},
        'persistence': {'episodes': ['E09', 'E10', 'E11', 'E12'], 'status': 'SOURCE_ATTEMPT_ONLY_NO_EXECUTION'},
        'effects_and_authority': {'episodes': ['E09', 'E10', 'E11', 'E12'], 'status': 'SOURCE_ATTEMPT_ONLY_NO_EXECUTION'},
    }
    write(EVIDENCE / 'SEMANTIC-COVERAGE.json', {'matrix': coverage, 'stored_operations': dict(operations),
        'expression_occurrences': dict(expressions), 'definitions_including_programs': definitions,
        'stored_steps': steps, 'distinct_operation_sequence_shapes': len(patterns),
        'shape_count_is_not_independent_requirement_count': True,
        'production_kernel': 26, 'production_executed_episodes': 0,
        'experimental_executed_episodes': 8, 'public_foundation_shared': True})
    observations = passes[0]['results']
    total = sum(len(r['observations']) for r in observations)
    successes = sum(o['actual']['status'] == 'success' for r in observations for o in r['observations'])
    raw_files = [p for p in EVIDENCE.rglob('*') if p.is_file()]
    write(EVIDENCE / 'QUALITY-SUMMARY.json', {
        'classification': 'R6_48_DATA_PIPELINE_PARTIAL', 'families_commissioned': 6,
        'independently_commissioned_families': 0, 'episodes_commissioned': 12,
        'episodes_complete_frozen_frc': 10, 'episodes_pending_frc_clarification': 2,
        'episodes_represented': 8, 'episodes_finite_accepted': sum(r['all_acceptance_matches'] for r in observations),
        'episodes_admitted': 0, 'episodes_rejected_or_blocked_for_admission': 12,
        'executable_acceptance_suites': 8, 'independently_reviewed_acceptance_suites': 0,
        'cases_per_pass': total, 'success_cases_per_pass': successes, 'rejection_cases_per_pass': total - successes,
        'fresh_process_passes': 3, 'total_observations': total * 3,
        'full_envelope_replay_identical': identical,
        'replay_identity': passes[0]['observations_identity'],
        'first_candidate_acceptance_failures': sum(not r['all_acceptance_matches'] for r in observations),
        'observed_candidate_corrections': 0, 'actual_ai_semantic_tool_trajectories': 0,
        'deterministic_scripted_trajectories': 8, 'scripted_trace_calls': sum(len(read(
            EVIDENCE / 'episodes' / ('E%02d' % n) / 'SCRIPTED-TRAJECTORY.json')['entries']) for n in range(1, 9)),
        'broad_executed_behavioral_patterns': 4, 'distinct_operation_sequence_shapes': len(patterns),
        'process_controls': len(checks), 'process_controls_pass': all(x['passed'] for x in checks),
        'raw_evidence_bytes_before_summary_and_publication': sum(p.stat().st_size for p in raw_files),
        'formalization_and_review_time': 'not individually metered; no independent review cost measured',
        'pipeline_ready_to_scale': False, 'training_runs': 0, 'downloads': 0, 'installs': 0,
        'p6_a04_acceptance_executions': 0, 'p6_a05_access': False,
    })
    assert all(x['passed'] for x in checks)
    print(read(EVIDENCE / 'QUALITY-SUMMARY.json'))


if __name__ == '__main__':
    main()
