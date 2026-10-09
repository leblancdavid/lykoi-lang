"""Publish/verify the access-blocked successor; never dispatch authoring."""
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from preflight import ROOT, HERE, OUT, TEMP, EXE, sha, load, save, raw, redact

REPORT = ROOT / 'benchmark/results/phase6/R6_34-REPORT.md'
EXCLUDED = {OUT / 'PUBLICATION-IDENTITIES.json', OUT / 'VERIFICATION.json'}


def final_records():
    preflight = load(OUT / 'PREFLIGHT-RESULT.json')
    assert preflight['status'] == 'PROVIDER_ACCESS_BLOCKED'
    assert not preflight['participant_requirement_exposure']
    calls = preflight['calls']
    assert len(calls) == 1 and not calls[0]['passed']
    error = calls[0]['errors'][0]['error']['data']
    assert error['statusCode'] == 429
    assert json.loads(error['responseBody'])['error']['code'] == 'credit_balance_exhausted'
    session_id = calls[0]['session_ids'][0]
    start = time.perf_counter()
    export = subprocess.run([EXE, 'export', session_id], cwd=TEMP, capture_output=True, timeout=60)
    assert export.returncode == 0, 'Session export failed'
    session = redact(json.loads(export.stdout))
    save(OUT / 'SESSION-EXPORT.json', session)
    raw(OUT / 'SESSION-EXPORT.stderr.txt', export.stderr)
    save(OUT / 'AUTHORING-CLOSED.json', dict(utc=datetime.now(timezone.utc).isoformat(),
        authoring_started=False, participant_task_exposure=False, session_id=session_id,
        preflight_process_terminated=True, no_further_model_calls=True,
        completed_semantic_model_responses=0))
    stages = ('configuration_freeze', 'proposal', 'admission', 'retrieval', 'two_callers',
              'base_validation_execution', 'modification_exposure', 'successor',
              'CallerA_migration', 'CallerB_retention', 'functional_acceptance', 'AI_independent_replay')
    save(OUT / 'RESULT.json', dict(round='R6.34', classification='R6_34_PROVIDER_ACCESS_BLOCKED',
        linked_predecessor='R6.33', R6_33_classification_unchanged='R6_33_PROTOCOL_HALT',
        terminal_stage='neutral_model_access_preflight', provider='openai', model='gpt-6.1-sol',
        variant='high', http_status=429, error_type='insufficient_quota',
        error_code='credit_balance_exhausted', lifecycle={s: 'NOT_REACHED' for s in stages},
        authoring_model_calls=0, AI_authored_artifacts=0, semantic_repairs=0,
        kernel=26, P6_A04_acceptance=False, P6_A05_access=False,
        other_configured_provider_access='NOT_TESTED; no universal unavailability claim',
        stopped_after_one_bounded_preflight=True))
    save(OUT / 'SUCCESSOR-FREEZE-STATUS.json', dict(status='NOT_REACHED',
        reason='Conditional model/tool access gate failed; no lifecycle configuration frozen',
        preflight_configuration_frozen=True, task_requirements_sent=False,
        frozen_R6_33_inputs_preserved=True, coordinator_task_text_exposure=True,
        coordinator_exposure_source='Historical pilot.py read; no independent or blind coordinator claim'))
    save(OUT / 'REGISTRY-ARTIFACT-STATUS.json', dict(status='NOT_REACHED',
        registry_initialized=False, registry_admissions=0, retrievals=0, migrations=0,
        predecessor=None, successor=None, CallerA=None, CallerB=None,
        reason='No semantic model response; no placeholder definitions or executable substitutes created'))
    save(OUT / 'FUNCTIONAL-STATUS.json', dict(status='NOT_REACHED', passed=None, total=None,
        validation_seconds=None, registry_overhead_seconds=None,
        acceptance_criteria_modified=False, dependency_map_modified=False,
        reason='No authored executable; unchanged frozen expectations never executed'))
    save(OUT / 'REPLAY.json', dict(status='NOT_REACHED', replay_process_executed=False,
        model_calls=0, executable_artifacts=0, executed_observations=0,
        comparison_results=None, reason='No saved executable artifacts exist to replay',
        authoring_closed_receipt_sha256=sha(OUT / 'AUTHORING-CLOSED.json')))
    info = session.get('info', {})
    save(OUT / 'MEASUREMENTS.json', dict(preflight_CLI_invocations=1,
        authoring_model_calls=0, completed_model_responses=0, participant_tool_calls=0,
        semantic_tool_calls=0, correction_turns=0, transport_failed_invocations=1,
        preflight_CLI_wall_seconds=calls[0]['wall_seconds'],
        preflight_inventory_freeze_and_request_wall_seconds=preflight['total_wall_seconds'],
        session_export_wall_seconds=time.perf_counter()-start,
        provider_HTTP_attempts=None, provider_API_cost_USD=None,
        input_tokens=None, output_tokens=None, reasoning_tokens=None, cached_tokens=None,
        usage_missing_reason='No provider step_finish; failed-session counters are unpopulated, not measured zero usage',
        exported_session_counters=info.get('tokens'), exported_cost_counter=info.get('cost'),
        provider_effective_reasoning=None, provider_effective_tool_schema=None,
        validation_seconds=None, registry_overhead_seconds=None, replay_seconds=None,
        downstream_timing_status='NOT_REACHED', coordinator_model_tokens=None,
        fully_costed_workflow_seconds=None, spending_metering_available=False,
        spending_limit_enforced=False, purchases=0,
        limitations='CLI internal HTTP retries and billing unmetered; process deadline enforced; no lifecycle permitted'))
    save(OUT / 'REDACTION.json', dict(policy='Credential-bearing response fields redacted recursively before publication',
        raw_semantic_error_preserved=True, credential_originals_published=False,
        original_unredacted_stream_retained=False,
        note='Captured JSON events and session export retain error body/status; response cookie values omitted',
        transcript_files=['preflight-01/stdout.jsonl', 'SESSION-EXPORT.json']))


def paths():
    candidates = [REPORT] + list(OUT.rglob('*')) + list(HERE.rglob('*'))
    candidates += [ROOT / ('docs/' + stem + '-r6.34.md')
        for stem in ('project-overview', 'research-log', 'decisions')]
    return sorted({p for p in candidates if p.is_file() and '__pycache__' not in p.parts and p not in EXCLUDED})


def checks(publishing=False):
    base = load(OUT / 'BASELINE.json')
    for name, pin in base['protected_files'].items():
        assert sha(ROOT / name) == pin, name
    for round_id in ('32', '33'):
        folder = ROOT / ('benchmark/results/phase6/r6_' + round_id)
        assert sha(folder / 'PUBLICATION-IDENTITIES.json') == load(folder / 'VERIFICATION.json')['manifest_sha256']
        for name, meta in load(folder / 'PUBLICATION-IDENTITIES.json')['files'].items():
            assert sha(ROOT / name) == meta['sha256'] and (ROOT / name).stat().st_size == meta['bytes'], name
    for name, pin in load(ROOT / 'benchmark/results/phase6/r6_33/FREEZE.json')['inputs'].items():
        assert sha(ROOT / name) == pin, name
    for name, pin in load(OUT / 'PREFLIGHT-FREEZE.json')['inputs'].items():
        assert sha(ROOT / name) == pin, name
    result = load(OUT / 'RESULT.json')
    assert result['classification'] == 'R6_34_PROVIDER_ACCESS_BLOCKED'
    assert set(result['lifecycle'].values()) == {'NOT_REACHED'}
    assert (OUT / 'preflight-01/prompt.txt').read_text() == 'Reply exactly NEUTRAL_OK. Do not call tools.'
    for p in paths():
        text = p.read_text(encoding='utf-8')
        assert not any(line.endswith((' ', '\t')) for line in text.splitlines()), p
        if p.suffix == '.json':
            json.loads(text)
        if p.suffix == '.jsonl':
            for line in text.splitlines():
                json.loads(line)
        if p.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if '://' not in target and not target.startswith('#'):
                    resolved = (p.parent / target.split('#')[0]).resolve()
                    assert resolved.exists() or (publishing and resolved in EXCLUDED), (p, target)
        assert not re.search(r'"set-cookie"\s*:\s*"(?!<REDACTED_RESPONSE_CREDENTIAL>)', text), p
        assert not re.search(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}', text), p
    diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    assert not subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=ROOT, text=True).strip()
    return dict(protected_identities_verified=len(base['protected_files']),
        R6_32_publication_files_verified=1262, R6_33_publication_files_verified=31,
        historical_HTTP429_preserved=True, R6_33_freeze_verified=True,
        preflight_freeze_verified=True, tracked_files_unchanged=True,
        git_diff_check=True, additive_whitespace=True, relative_links=True,
        credential_response_fields_redacted=True)


def main():
    mode = sys.argv[1]
    if mode == 'records':
        final_records()
        print('R6.34 terminal records saved; no authoring dispatched')
        return
    checked = checks(publishing=mode == 'publish')
    if mode == 'publish':
        save(OUT / 'PUBLICATION-IDENTITIES.json', dict(round='R6.34',
            classification='R6_34_PROVIDER_ACCESS_BLOCKED', hash_algorithm='SHA256 raw bytes',
            excluded_self_referential_files=sorted(p.relative_to(ROOT).as_posix() for p in EXCLUDED),
            files={p.relative_to(ROOT).as_posix(): dict(sha256=sha(p), bytes=p.stat().st_size) for p in paths()}))
        save(OUT / 'VERIFICATION.json', dict(round='R6.34', passed=True, kernel=26,
            classification='R6_34_PROVIDER_ACCESS_BLOCKED', checks=checked,
            publication_files=len(paths()), manifest_sha256=sha(OUT / 'PUBLICATION-IDENTITIES.json'),
            P6_A04_acceptance=False, P6_A05_access=False, stopped_after_publication=True))
    elif mode == 'verify':
        receipt = load(OUT / 'VERIFICATION.json')
        manifest = load(OUT / 'PUBLICATION-IDENTITIES.json')
        assert receipt['passed'] and receipt['checks'] == checked
        assert receipt['manifest_sha256'] == sha(OUT / 'PUBLICATION-IDENTITIES.json')
        assert set(manifest['files']) == {p.relative_to(ROOT).as_posix() for p in paths()}
        for name, meta in manifest['files'].items():
            assert sha(ROOT / name) == meta['sha256'] and (ROOT / name).stat().st_size == meta['bytes'], name
    else:
        raise ValueError('records, publish or verify')
    print('R6.34 integrity verified:', checked['protected_identities_verified'],
          'protected identities;', len(paths()), 'publication files; kernel26')


if __name__ == '__main__':
    main()
