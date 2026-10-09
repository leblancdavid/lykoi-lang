"""AI-free measurement/provenance/publication, with no provider dispatch path."""
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import sys
from preflight import ROOT, HERE, OUT, load, save, raw, sha

sys.path.insert(0, str(ROOT / 'experiments/lifecycle_r6_32'))
from lifecycle import Registry, Journal, c

CLASSIFICATION = 'R6_36_AI_LIFECYCLE_SUPPORTED'
REPORT = ROOT / 'benchmark/results/phase6/R6_36-REPORT.md'


def usage(parts):
    result = dict(input=0, output=0, reasoning=0, cache_read=0, cache_write=0, total=0)
    for part in parts:
        tokens = part['tokens']
        for key in ('input', 'output', 'reasoning', 'total'):
            result[key] += tokens[key]
        for key in ('read', 'write'):
            result['cache_' + key] += tokens['cache'][key]
    return result


def records():
    author = load(OUT / 'AUTHORING-RESULT.json')
    closed = load(OUT / 'AUTHORING-CLOSED.json')
    preflight = load(OUT / 'PREFLIGHT-RESULT.json')
    replay = load(OUT / 'REPLAY.json')
    functional = load(OUT / 'FUNCTIONAL.json')
    original = load(OUT / 'ORIGINAL-ACCEPTANCE.json')
    assert author['status'] == 'LIFECYCLE_COMPLETED_AWAITING_REPLAY'
    assert closed['child_processes_terminated']
    assert functional['all_passed'] and original['all_passed']
    assert load(OUT / 'REPLAY-INTEGRITY.json')['passed']
    assert len(replay['runs']) == 3 and len({r['observations_sha256'] for r in replay['runs']}) == 1
    artifacts = {k: load(OUT / (k + '.json')) for k in ('old', 'new', 'a', 'b', 'a_new')}
    provenance = []
    for number, keys in ((1, ['old']), (2, ['a', 'b']), (3, ['new']), (4, ['a_new'])):
        proposal = load(OUT / 'calls' / f'{number:02}' / 'PROPOSAL.json')
        for key, definition in zip(keys, proposal['definitions']):
            assert c.seal(definition) == artifacts[key], 'Semantic artifact differs from model proposal'
            provenance.append(dict(artifact=key, proposal_call=number,
                identity=artifacts[key]['identity'], raw_sha256=sha(OUT / (key + '.json')),
                only_mechanical_seal=True))
    old, new = artifacts['old'], artifacts['new']
    assert (old['name'], old['params'], old['result_type']) == (new['name'], new['params'], new['result_type'])
    assert new['steps'][:len(old['steps'])] == old['steps']
    assert new['order'][:len(old['order'])] == old['order']
    # The immutable predecessor's exact checks/sites/order remain in the successor.
    checks = [s['node'] for s in old['steps'] if s['node']['op'] == 'check']
    assert [node['code'] for node in checks] == ['X_NEGATIVE', 'Y_NEGATIVE', 'SUM_LIMIT']
    assert [node['site'] for node in checks] == [{'ref': 'x'}, {'ref': 'y'}, {'ref': 'x'}]
    state = Registry(OUT / 'registry').read()['state']
    migration = load(OUT / 'calls/05/PROPOSAL.json')
    assert migration == load(OUT / 'MIGRATION.json')
    assert state['migrations'][0]['decisions'] == migration['decisions']
    save(OUT / 'PROVENANCE.json', dict(passed=True, artifacts=provenance,
        exact_model_authored_semantics=True, exact_migration_proposal=True,
        signature_preserved=True, original_checks_error_sites_order_preserved=True,
        coordinator_semantic_repairs=0, expansion_maps_in='FUNCTIONAL.json'))
    journal = Journal(OUT / 'telemetry').recover()['events']
    counts = Counter(e['kind'] for e in journal)
    timing = {kind: sum(e['data'].get('tool_seconds', 0) for e in journal if e['kind'] == kind)
              for kind in ('admission', 'retrieval')}
    calls = closed['calls']
    parts = [part for call in calls for part in call['step_finishes']]
    measurements = dict(preflight_CLI_invocations=1, lifecycle_model_CLI_invocations=len(calls),
        total_participant_CLI_invocations=1+len(calls), lifecycle_model_steps=len(parts),
        participant_tool_calls=sum(call['participant_tool_calls'] for call in calls),
        broker_admission_calls=counts['admission'], broker_retrieval_calls=counts['retrieval'],
        broker_migration_calls=counts['migration'], telemetry_event_counts=dict(counts),
        correction_turns=len(author['rejected_proposals']), coordinator_semantic_repairs=0,
        preflight_usage=usage(preflight['step_finishes']), authoring_usage=usage(parts),
        combined_participant_usage=usage(preflight['step_finishes']+parts),
        preflight_wall_seconds=preflight['wall_seconds'],
        preflight_inventory_freeze_request_seconds=preflight['total_preflight_seconds'],
        authoring_CLI_wall_seconds=sum(call['wall_seconds'] for call in calls),
        authoring_lifecycle_including_export_seconds=author['wall_seconds'],
        registry_admission_seconds=timing['admission'], retrieval_seconds=timing['retrieval'],
        migration_seconds=None, migration_timing_missing_reason='Unchanged registry migration has no tool_seconds field',
        original_validation_expansion_seconds=sum(v['validation_seconds'] for v in original['expansions'].values()),
        final_validation_expansion_seconds=sum(v['validation_seconds'] for v in functional['expansions'].values()),
        validation_overlap_note='Admission includes validation; expansion is part of acceptance; intervals overlap',
        original_acceptance=dict(passed=original['passed'], total=original['total'], wall_seconds=original['wall_seconds']),
        final_acceptance=dict(passed=functional['passed'], total=functional['total'], wall_seconds=functional['wall_seconds']),
        replay_runs=replay['runs'], replay_model_calls=0,
        provider_errors=[], runtime_errors=[], coordinator_retries=0,
        provider_HTTP_attempts=None, effective_reasoning=None, effective_authentication=None,
        billing_USD=None, opencode_reported_cost_counter=sum(p['cost'] for p in parts),
        reported_cost_is_not_billing_attestation=True, purchases=0,
        coordinator_model_tokens=None, fully_costed_workflow_seconds=None,
        missing_measurements=['Provider HTTP-attempt count', 'Effective authentication/endpoint',
            'Effective reasoning attestation', 'Actual subscription/billing cost', 'Migration isolated timing',
            'Coordinator tokens and fully costed preparation/publication effort'])
    save(OUT / 'MEASUREMENTS.json', measurements)
    save(OUT / 'RESULT.json', dict(round='R6.36', classification=CLASSIFICATION,
        linked_predecessors=['R6.33', 'R6.34', 'R6.35'], corrected_configuration_access_worked=True,
        effective_OAuth_route_attested=False, neutral_gate_passed=True, four_tools_discovered=True,
        lifecycle_completed=True, AI_independent_replay_passed=True,
        functional_passed=functional['passed'], functional_total=functional['total'],
        authoring_calls=len(calls), correction_turns=0, semantic_repairs=0,
        selected_roots=load(OUT / 'DEPENDENCY-IMPACT.json')['expectation']['selected_roots'],
        kernel=26, P6_A04_acceptance=False, P6_A05_access=False,
        H1_H2_study=False, stopped_after_one_attempt_and_publication=True))
    save(OUT / 'REDACTION.json', dict(credential_stores_read=False, credential_headers_accessed=False,
        credentials_published=False, raw_stderr_published=False,
        structured_events_and_export='Credential-bearing fields recursively omitted; encoded JSON sanitized',
        provider_route_evidence='Allowlisted safe host/path only; unavailable in this capture',
        global_environment_or_OpenCode_modified=False))
    print(json.dumps(measurements, indent=2))


def paths():
    result = [p for base in (HERE, OUT) for p in base.rglob('*') if p.is_file()
              and '__pycache__' not in p.parts and p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')]
    return sorted(result + [REPORT] + [ROOT / ('docs/' + stem + '-r6.36.md')
        for stem in ('project-overview', 'research-log', 'decisions')])


def checks():
    pins = load(OUT / 'BASELINE.json')['protected_files']
    for name, pin in pins.items():
        assert 'p6_a05' not in name.lower().replace('-', '_')
        assert sha(ROOT / name) == pin, name
    for freeze in ('PREFLIGHT-FREEZE.json', 'LIFECYCLE-FREEZE.json'):
        for name, pin in load(OUT / freeze)['inputs'].items():
            assert sha(ROOT / name) == pin, name
    for path in paths():
        text = path.read_text(encoding='utf-8')
        assert not any(line.endswith((' ', '\t')) for line in text.splitlines()), path
        if path.suffix == '.json':
            json.loads(text)
        if path.suffix == '.jsonl':
            for line in text.splitlines():
                json.loads(line)
        if path.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if '://' not in link and not link.startswith('#'):
                    assert (path.parent / link.split('#')[0]).resolve().exists(), (path, link)
        assert not re.search(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}', text), path
        assert not re.search(r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', text), path
        assert not re.search(r'"set-cookie"\s*:\s*"(?!<REDACTED_RESPONSE_CREDENTIAL>)', text), path
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    assert not subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=ROOT, text=True).strip()
    assert load(OUT / 'RESULT.json')['classification'] == CLASSIFICATION
    return dict(protected_identities_verified=len(pins), all_freezes_verified=True,
        tracked_files_unchanged=True, additive_whitespace=True, relative_links=True,
        credential_scan_passed=True, git_diff_check=True)


def publish(verify=False):
    checked = checks()
    manifest_path = OUT / 'PUBLICATION-IDENTITIES.json'
    if not verify:
        save(manifest_path, dict(round='R6.36', classification=CLASSIFICATION,
            files={p.relative_to(ROOT).as_posix(): dict(sha256=sha(p), bytes=p.stat().st_size) for p in paths()}))
        save(OUT / 'VERIFICATION.json', dict(round='R6.36', passed=True, kernel=26,
            classification=CLASSIFICATION, checks=checked, publication_files=len(paths()),
            manifest_sha256=sha(manifest_path), stopped_after_publication=True))
    receipt = load(OUT / 'VERIFICATION.json')
    assert receipt['passed'] and receipt['checks'] == checked
    assert receipt['manifest_sha256'] == sha(manifest_path)
    entries = load(manifest_path)['files']
    assert set(entries) == {p.relative_to(ROOT).as_posix() for p in paths()}
    for name, meta in entries.items():
        assert sha(ROOT / name) == meta['sha256'] and (ROOT / name).stat().st_size == meta['bytes']
    print('R6.36 publication verified:', checked['protected_identities_verified'],
          'protected identities;', len(paths()), 'publication files;', CLASSIFICATION)


if __name__ == '__main__':
    if sys.argv[1] == 'records':
        records()
    else:
        publish(verify=sys.argv[1] == 'verify')
