"""Record the interrupted pre-exposure gate; no evaluation or retry entry."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from benchmark.results.phase5c.r5_44_review import (
    RESULTS, RUN, Recorder, PROTOCOL, canonical, digest, read, write,
    historical_lock, check_qualification_lock, contamination, authority, boundary)


def record():
    if RUN.exists() or (RESULTS / 'R5_44-classification.json').exists():
        raise ValueError('stopped-run replacement prohibited')
    inherited = read('R5_43-qualification.json')
    result = {
        'primary_classification': 'R5_44_PROTOCOL_HALT',
        'stage': 'before exposure; starting-state verification interrupted',
        'inherited_classification': inherited['primary_classification'],
        'r5_42_classification': read('R5_42-halt-verification.json')['primary_classification'],
        'protocol': PROTOCOL, 'recorder_version': 'recorder_r5_43.py',
        'protocol_sha256': digest((ROOT / 'docs/canonical-evidence-r5.43.md').read_bytes()),
        'recorder_sha256': digest((ROOT / 'benchmark/evaluation/recorder_r5_43.py').read_bytes()),
        'attempted_command': 'Test-Path -LiteralPath \'D:\\Dev\\axiom\\benchmark\\results\\phase5c\' && python benchmark/results/phase5c/r5_44_review.py prepass',
        'tool_timeout_ms': 120000,
        'tool_result': 'shell tool terminated command after exceeding timeout 120000 ms',
        'captured_stdout': 'True\nAxiom validate: ok\n',
        'process_check_after_interruption': 'Get-Process python returned no running Python process',
        'regression_result': 'INCOMPLETE: suite results were not persisted before termination; no pass claim',
        'prepass_artifact_present': (RESULTS / 'R5_44-prepass.json').exists(),
        'recorder_directory_present_at_halt': RUN.exists(),
        'historical_lock': historical_lock('R5_40-implementation-profile-lock.json'),
        'prospective_lock': historical_lock('R5_41-implementation-lock.json'),
        'infrastructure_lock': check_qualification_lock(),
        'frozen_authority': authority(), 'implementation_contamination': contamination(),
        'inherited_qualification_tests': {'passed': 29, 'fresh_reproduction_completed': False},
        'inherited_matrix': inherited['matrix'],
        'fresh_matrix_result': 'NOT ESTABLISHED: gate interrupted before persisted verification',
        'inherited_structure': inherited['independent_structure'],
        'inherited_traceability': inherited['independent_traceability'],
        'inherited_profile_contamination': inherited['independent_profile_contamination'],
        'semantic_count_start': boundary.SCHEMA['core_constructs'],
        'semantic_count_end': boundary.SCHEMA['core_constructs'],
        'authorization': 'user authorizes one dispatch only after successful verification and seal; dispatch gate never reached',
        'starting_baseline_sealed_before_dispatch': False,
        'dispatches_started': 0, 'dispatches_completed': 0,
        'dispatch_start_evidence': None, 'dispatch_completion_evidence': None,
        'total_b02_contracts': 'NOT EVALUATED', 'checked_plans_formed': 'NOT EVALUATED',
        'checked_plan_failures': 'NOT EVALUATED', 'readiness': 'NOT EVALUATED',
        'supplemental_audit': 'NOT EVALUATED', 'admission': 'NOT EVALUATED',
        'compatible_path': 'NOT EVALUATED', 'whole_contract_support': 'NOT EVALUATED',
        'unsupported_requirements': 'NOT EVALUATED; no capability/configuration conclusion',
        'post_exposure_repairs': 0, 'b02_generated': False, 'b02_executed': False,
        'frozen_acceptance_ran': False, 'b03_prospectively_touched': False,
        'b17_exposed': False, 'b17_classified': False, 'phase5c': 'paused',
        'retry_permitted': False,
        'next_gate': 'Separately authorize investigation of pre-exposure verification interruption; no R5.44 retry.'}
    if result['prepass_artifact_present'] or result['recorder_directory_present_at_halt']:
        raise ValueError('unexpected evidence: manual inference of exposure prohibited')
    write('R5_44-halt-verification.json', result)
    RUN.mkdir(exist_ok=False)
    r = Recorder(RUN)
    # This is a sealed HALT record, not the uncompleted experimental baseline.
    r.freeze({'experiment': 'R5.44', 'purpose': 'post-interruption halt accounting only', 'halt_evidence': result},
             [ROOT / 'benchmark/evaluation/recorder_r5_43.py', ROOT / 'docs/canonical-evidence-r5.43.md',
              RESULTS / 'r5_44_review.py', RESULTS / 'r5_44_halt.py', RESULTS / 'R5_44-halt-verification.json'])
    r.write('counts-before', r.counts())
    r.halt('pre-exposure verification command terminated at 120000 ms; starting state not established; no retry')
    r.write('counts-after', r.counts())
    final = r.finish()
    write('R5_44-classification.json', {'primary_classification': 'R5_44_PROTOCOL_HALT', 'recorder': final,
                                      'experimental_baseline': None, 'dispatches': 0})
    print({'classification': 'R5_44_PROTOCOL_HALT', 'counts': r.counts(),
           'historical_lock': result['historical_lock'], 'prospective_lock': result['prospective_lock'],
           'infrastructure_lock': result['infrastructure_lock'],
           'halt_record_baseline': r.read('baseline')['identity']})


if __name__ == '__main__':
    record()
