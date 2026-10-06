"""Final preservation, change-scope, stage-accounting and publication checks."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
ALLOWED={
    'AGENTS.md','README.md','benchmark/README.md','docs/agent-workflow.md','docs/project-overview.md','docs/decisions.md','docs/research-log.md',
    'docs/existing-semantic-composition-v1.md',
    'src/air_compiler/profiles.py','src/air_compiler/creation_provider_runtime.py',
    'src/lykoi_pipeline/author_worker.py','src/lykoi_pipeline/contracts.py','src/lykoi_pipeline/controller.py','src/lykoi_pipeline/plans.py',
    'src/lykoi_pipeline/query_profile.py','src/lykoi_pipeline/scalar_profile.py','src/lykoi_pipeline/composition_profile.py','src/lykoi_pipeline/model_profile.py',
    'src/lykoi_workspace/scalar_schema.py','src/lykoi_workspace/workspace.py',
    'tests/test_existing_composition.py','tests/test_fresh_typed_corpus.py',
}


def main():
    fresh=json.loads((OUT/'R5_103-FINAL-EVIDENCE.json').read_text(encoding='utf-8'))
    summary=json.loads((OUT/'R5_103-SUMMARY.json').read_text(encoding='utf-8'))
    tests=json.loads((OUT/'R5_103-FINAL-VERIFICATION.json').read_text(encoding='utf-8'))
    initial=json.loads((OUT/'R5_103-INITIAL-EVIDENCE.json').read_text(encoding='utf-8'))
    checks={}
    checks['history_pins_match_initial_and_final']=initial['history_pins']==fresh['history_pins'] and all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==pin for p,pin in fresh['history_pins'].items())
    checks['all_twenty_fresh']=len(fresh['cases'])==20 and {r['case'] for r in fresh['cases']}=={f'B{i:02d}' for i in range(1,21)}
    checks['exact_candidates_match_final_frc']=all(json.loads((OUT/f"R5_103-{r['case']}-CANDIDATE.json").read_text(encoding='utf-8'))['exact_frc']==r['formalization']['contract'] for r in fresh['cases'])
    checks['source_authority_files_unchanged']=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==pin for r in fresh['cases'] for p,pin in r['candidate']['source_files'].items())
    checks['baseline_model_unchanged']=all(r['candidate']['domains']['baseline_model_sha256']==hashlib.sha256((ROOT/'air/task_manager.json').read_bytes()).hexdigest() for r in fresh['cases'])
    checks['first_blocker_distribution_complete']=sum(fresh['distribution'].values())==20 and fresh['distribution']==summary['distribution']
    checks['current_tests_pass']=tests['all_pass'] and tests['tests']==328
    checks['successful_cases_have_actual_external_artifacts']=True
    checks['unexecuted_stages_not_reached']=True
    for r in fresh['cases']:
        stages=r['stages']; keys=list(stages)
        # JSON serialization sorts controller maps, so use the specified stage order.
        order=('FORMALIZATION','STRUCTURAL','BDI','ADEQUACY','REPRESENTATION','AUTHORING','COMPILATION','RUNTIME','BEHAVIORAL_VERIFICATION')
        if r['first_blocker']=='SUCCESS':
            artifacts=r['audit']['artifacts']; types={a['type'] for a in artifacts.values()}
            checks['successful_cases_have_actual_external_artifacts'] &= {'model','target','verification','plan','v1','adequacy','bdi'}<=types and all(stages[s]=='PASS' for s in order[1:])
            verification=artifacts[r['terminal']['verification']]['content']
            checks['successful_cases_have_actual_external_artifacts'] &= verification['outcome']=='BEHAVIORALLY_VERIFIED' and all(s['passed'] for c in verification['cases'] for s in c['steps'])
        else:
            index=order.index(r['first_blocker'])
            checks['unexecuted_stages_not_reached'] &= stages[r['first_blocker']]=='BLOCKED' and all(stages[s]=='NOT_REACHED' for s in order[index+1:])
    for name in ('R5_101-CURRENT-EVIDENCE.json','R5_102-TRANSFER-EVIDENCE.json','R5_103-INITIAL-EVIDENCE.json'):
        prior={r['case']:r for r in json.loads((OUT/name).read_text(encoding='utf-8'))['cases']}
        changed=[r['case'] for r in fresh['cases'] if prior[r['case']]['first_blocker']!=r['first_blocker']]
        checks[name+'_expected_changes']=changed==(['B01','B04'] if '101-' in name else ['B01'] if '102-' in name else [])
    whitespace=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
    tracked=subprocess.run(['git','diff','--name-only'],cwd=ROOT,capture_output=True,text=True)
    untracked=subprocess.run(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,capture_output=True,text=True)
    paths=sorted(set(tracked.stdout.splitlines()+untracked.stdout.splitlines()))
    checks['git_diff_check']=whitespace.returncode==0
    checks['change_scope']=tracked.returncode==0 and untracked.returncode==0 and all(p in ALLOWED or p.startswith('benchmark/results/phase5c/R5_103-') for p in paths)
    checks['untracked_whitespace']=all(all(line==line.rstrip() for line in (ROOT/p).read_text(encoding='utf-8').splitlines()) and (ROOT/p).read_bytes().endswith(b'\n') for p in untracked.stdout.splitlines())
    # Product code contains no benchmark-ID dispatch or source-word interpretation.
    new_product=['src/lykoi_pipeline/composition_profile.py','src/lykoi_pipeline/model_profile.py','src/air_compiler/creation_provider_runtime.py']
    import re
    checks['no_case_dispatch']=all(not re.search(r'\bB(?:0[1-9]|1[0-9]|20)\b',(ROOT/p).read_text(encoding='utf-8')) for p in new_product)
    result=dict(checks=checks,all_pass=all(checks.values()),changed_paths=paths,whitespace_stderr=whitespace.stderr,
        distribution=fresh['distribution'],classification=summary['classification'],history_pins=fresh['history_pins'],
        pins={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths if not p.endswith('R5_103-FINAL-AUDIT.json')},
        scope='Preservation/artifact/scope checks, not model/runtime/transport qualification')
    with (OUT/'R5_103-FINAL-AUDIT.json').open('x',encoding='utf-8',newline='\n') as stream: json.dump(result,stream,indent=2); stream.write('\n')
    print(json.dumps(checks,indent=2)); assert result['all_pass']


if __name__=='__main__': main()
