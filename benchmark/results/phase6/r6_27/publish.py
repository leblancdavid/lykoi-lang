"""Offline publication verification; no inference and no historical edits."""
import json
import re
import subprocess
import sys
from common import HERE, ROOT, read, save, sha, now

def verify():
    pins = read('BASELINE.json')['protected_files']
    mismatches = [p for p, h in pins.items() if sha(ROOT/p) != h]
    assert not mismatches, mismatches
    for round_name in ('r6_25', 'r6_26'):
        directory = HERE.parent/round_name
        manifest = directory/'PUBLICATION-IDENTITIES.json'
        receipt = json.loads((directory/'VERIFICATION.json').read_text())
        assert receipt['publication_manifest_sha256']==sha(manifest)
        assert all(sha(ROOT/p)==identity['sha256'] for p,identity in json.loads(manifest.read_text())['files'].items())
    ledger = json.loads((HERE.parent/'r6_25/BASELINE.json').read_text())['kernel_ledger']
    assert len(ledger['baseline_kernel'])+len(ledger['preserved_additions'])==26
    assert all(sha(HERE/n)==h for n,h in read('PRE-INFERENCE-FREEZE-5.json')['files'].items())
    tests={}
    for name, directory, pattern, expected in (
        ('neutral_exposure', HERE, 'test_exposure.py', 6),
        ('frozen_transport', HERE.parent/'r6_25', 'test_transport.py', 17)):
        proc = subprocess.run([sys.executable,'-m','unittest','discover','-s','.','-p',pattern,'-v'],cwd=directory,capture_output=True,text=True,encoding='utf-8')
        assert proc.returncode==0 and f'Ran {expected} tests' in proc.stderr, proc.stderr
        tests[name]=dict(methods=expected,passed=True,stdout=proc.stdout,stderr=proc.stderr,model_calls=0)
    save('TESTS.json',tests)
    from collect import rows
    from bridge import definitions
    original = json.loads((HERE.parent/'r6_26/TOOLS.json').read_text())
    expected = [dict(name=t['function']['name'],description=t['function']['description'],inputSchema=t['function']['parameters']) for t in original]
    original_list = next(r['response']['result']['tools'] for r in rows('ORIGINAL') if r['request']['method']=='tools/list')
    assert original_list==expected
    annotated_list = next(r['response']['result']['tools'] for r in rows('ANNOTATED') if r['request']['method']=='tools/list')
    assert annotated_list==definitions('exact')
    neutral_list = next(r['response']['result']['tools'] for r in rows('EXACT-LIVE-3') if r['request']['method']=='tools/list')
    assert neutral_list==definitions('exact-neutral')
    for actual, frozen in zip(annotated_list, expected):
        if actual['name']=='apply_operation':
            assert set(actual['inputSchema'])=={'oneOf','type'}
            assert actual['inputSchema']['oneOf']==frozen['inputSchema']['oneOf']
        else:
            assert actual==frozen
    for label, count, failures in (('SYNTHETIC-LIVE-3',11,1),('EXACT-LIVE-3',4,0)):
        assert read(label+'/DELIVERY.json')['matches_requested']
        calls=[r for r in rows(label) if r['request']['method']=='tools/call']
        assert len(calls)==count and sum(r['response']['result']['isError'] for r in calls)==failures
        assert all(r['response']['result'].get('structuredContent',{}).get('inert') for r in calls if not r['response']['result']['isError'])
    assert read('BRIDGE-CONTROLS/RESULT.json')==dict(valid=6,invalid=36,all_matched=True,model_calls=0,semantic_dispatches=0)
    assert read('RESULT.json')['classification']=='R6_27_TOOL_EXPOSURE_QUALIFIED'
    # No semantic dispatcher, evaluator, frozen tasks or executable artifact path
    # exists in the bridge. Source guard supplements recorded inert responses.
    bridge = (HERE/'bridge.py').read_text()
    assert 'Session(' not in bridge and '.dispatch(' not in bridge
    assert not list(HERE.rglob('ARTIFACT.json')) and not list(HERE.rglob('SYMBOLIC-PACKET.json'))
    sources = [p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')]
    sources += [HERE.parent/'R6_27-REPORT.md']
    sources += [ROOT/'docs'/n for n in ('project-overview-r6.27.md','research-log-r6.27.md','decisions-r6.27.md')]
    files={}
    for p in sorted(sources):
        text=p.read_text(encoding='utf-8')
        if p.suffix=='.json':
            json.loads(text)
        if p.suffix=='.jsonl':
            for line in text.splitlines():
                json.loads(line)
        if p.suffix in ('.py','.md','.mjs'):
            assert all(line==line.rstrip() for line in text.splitlines()), str(p)
        if p.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if link.startswith(('http:','https:')):
                    continue
                target=(p.parent/link.split('#')[0]).resolve()
                if target.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json'):
                    assert target.exists(), str(target)
        assert not re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bsk-[A-Za-z0-9_-]{20,}',text), str(p)
        files[p.relative_to(ROOT).as_posix()]=dict(sha256=sha(p),bytes=p.stat().st_size)
    diff=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
    assert diff.returncode==0, diff.stderr
    # Untracked publication files do not participate in git diff; whitespace is
    # independently checked above rather than claiming diff alone covers them.
    save('PUBLICATION-IDENTITIES.json',dict(timestamp=now(),files=files))
    save('VERIFICATION.json',dict(timestamp=now(),passed=True,classification=read('RESULT.json')['classification'],kernel=26,
         protected_count=len(pins),protected_mismatches=[],R6_25_R6_26_publication_verified=True,
         original_schema_identity_verified=True,only_root_type_schema_delta=True,original_validation_authoritative=True,
         provider_metadata_separate=True,final_pre_inference_freeze_verified=True,neutral_test_methods=6,transport_test_methods=17,
         synthetic_positive_calls=10,synthetic_malformed_rejections=1,exact_inert_calls=4,stdio_valid=6,stdio_invalid=36,
         byte_exact_final_prompt_delivery=True,semantic_dispatches=0,scored_exposure=False,programs_constructed=0,
         P6_A04_acceptance=False,P6_A05_access=False,credentials_published=False,JSON_links_whitespace_checked=True,
         git_diff_check=dict(returncode=diff.returncode,stdout=diff.stdout,stderr=diff.stderr),
         publication_files=len(files),publication_manifest_sha256=sha(HERE/'PUBLICATION-IDENTITIES.json'),inference_calls_during_publication=0,stopped=True))
    assert all(sha(ROOT/p)==identity['sha256'] for p,identity in read('PUBLICATION-IDENTITIES.json')['files'].items())
    assert all(sha(ROOT/p)==h for p,h in pins.items())
    print('R6_27_TOOL_EXPOSURE_QUALIFIED;',len(files),'publication files;',len(pins),'protected identities; tests6+17; kernel26')

if __name__=='__main__':
    verify()
