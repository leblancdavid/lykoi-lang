"""Final prospective content, history, whitespace and scope audit."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
s=importlib.util.spec_from_file_location('audit105_pins',OUT/'R5_105-generic.py')
generic=importlib.util.module_from_spec(s); s.loader.exec_module(generic)


def main():
    lock=json.loads((OUT/'R5_105-GENERIC-LOCK-2.json').read_text(encoding='utf-8'))
    first=json.loads((OUT/'R5_105-GENERIC-LOCK.json').read_text(encoding='utf-8'))
    verification=json.loads((OUT/'R5_105-GENERIC-FINAL-VERIFICATION.json').read_text(encoding='utf-8'))
    synthetic=json.loads((OUT/'R5_105-SYNTHETIC-FINAL-EVIDENCE.json').read_text(encoding='utf-8'))
    comparison=json.loads((OUT/'R5_105-COMPARISON.json').read_text(encoding='utf-8'))
    corpus=json.loads((OUT/'R5_105-CORPUS-LOCK.json').read_text(encoding='utf-8'))
    tracked=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()
    new=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
    changed=sorted(set(tracked+new))
    allowed={'AGENTS.md','README.md','benchmark/README.md','docs/agent-workflow.md','docs/decisions.md','docs/project-overview.md','docs/research-log.md',
        'docs/typed-input-values-v1.md','src/air_compiler/input_values.py','src/air_compiler/mutable_runtime.py','src/air_compiler/mutable_values.py',
        'src/lykoi_pipeline/mutable_profile.py','src/lykoi_workspace/mutable_schema.py','src/lykoi_workspace/input_corpus.py','tests/test_input_values.py'}
    scope_bad=[p for p in changed if p not in allowed and not p.startswith('benchmark/results/phase5c/R5_105-')]
    whitespace=[]
    for p in changed:
        text=(ROOT/p).read_text(encoding='utf-8')
        whitespace.extend(dict(path=p,line=i) for i,line in enumerate(text.splitlines(),1) if line.rstrip()!=line)
    diff=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
    checks=dict(final_implementation_lock_intact=generic.implementation_pins()==lock['implementation'],
        history_preserved_across_both_locks=generic.history_pins()==lock['history']==first['history'],
        verification_passed=verification['all_pass'] and verification['tests']==348,
        synthetic_all_passed=all(r['first_blocker']=='SUCCESS' for r in synthetic['cases']) and synthetic['external_invocations']==132,
        all_twenty_source_captures_intact=all(hashlib.sha256((OUT/('R5_105-'+case+'-CANDIDATE.json')).read_bytes()).hexdigest()==pin for case,pin in corpus['cases'].items()) and len(corpus['cases'])==20,
        corpus_binds_final_lock=corpus['implementation_lock_sha256']==hashlib.sha256((OUT/'R5_105-GENERIC-LOCK-2.json').read_bytes()).hexdigest(),
        final_lock_precedes_transfer=datetime.datetime.fromisoformat(lock['utc'])<datetime.datetime.fromisoformat(corpus['utc']),
        transfer_distribution_correct=comparison['distribution']['SUCCESS']==8 and comparison['distribution']['STRUCTURAL']==9 and comparison['distribution']['BDI']==1 and comparison['distribution']['FORMALIZATION']==2,
        scope_correct=not scope_bad,whitespace_clean=diff.returncode==0 and not whitespace,
        no_benchmark_ids_in_changed_product=all(not re.search(r'\bB\d{2}\b',(ROOT/p).read_text(encoding='utf-8')) for p in changed if p.startswith('src/')))
    report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),all_pass=all(checks.values()),checks=checks,
        changed_paths=changed,out_of_scope=scope_bad,whitespace=whitespace,git_diff_check=dict(exit=diff.returncode,stdout=diff.stdout,stderr=diff.stderr),
        tests=verification['tests'],synthetic_external_invocations=synthetic['external_invocations'],transfer_external_invocations=comparison['external_invocations'],
        distribution=comparison['distribution'],scope='R5.105 only; final generic lock 2 unchanged since before first transfer result; R5.104 and history preserved')
    generic.publish('R5_105-FINAL-AUDIT.json',report)
    print(json.dumps(dict(all_pass=report['all_pass'],checks=checks,tests=report['tests'],synthetic_external_invocations=132,transfer_external_invocations=report['transfer_external_invocations']),indent=2))
    assert report['all_pass']


if __name__=='__main__': main()
