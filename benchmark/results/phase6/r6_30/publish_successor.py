"""Publication-only successor resolves first-publication manifest/receipt links."""
import json
import subprocess
import experiment as e

def main():
    e.verify()
    assert e.read('OFFLINE-AUDIT.json')['passed']
    files={};links=[]
    paths=[p for p in e.HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')]
    paths+=[e.HERE.parent/'R6_30-REPORT.md']+[e.ROOT/'docs'/n for n in ('project-overview-r6.30.md','research-log-r6.30.md','decisions-r6.30.md')]
    reserved={(e.HERE/n).resolve() for n in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')}
    for p in paths:
        text=p.read_text(encoding='utf-8')
        if p.suffix=='.json': json.loads(text)
        if p.suffix=='.jsonl':
            for line in text.splitlines(): json.loads(line)
        if p.suffix in ('.md','.py'): assert all(x==x.rstrip() for x in text.splitlines()),p
        assert not e.h.re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bsk-[A-Za-z0-9_-]{20,}',text),p
        if p.suffix=='.md':
            for link in e.h.re.findall(r'\]\(([^)]+)\)',text):
                if not link.startswith(('https:','http:')):
                    target=(p.parent/link.split('#')[0]).resolve(); links.append(target)
                    assert target.exists() or target in reserved,(p,link)
        files[p.relative_to(e.ROOT).as_posix()]=dict(sha256=e.digest(p),bytes=p.stat().st_size)
    diff=subprocess.run(['git','diff','--check'],cwd=e.ROOT,capture_output=True,text=True)
    assert diff.returncode==0
    e.save('PUBLICATION-IDENTITIES.json',dict(timestamp=e.h.now(),files=files))
    e.save('VERIFICATION.json',dict(timestamp=e.h.now(),passed=True,classification=e.read('RESULT.json')['classification'],
        publication_manifest_sha256=e.digest(e.HERE/'PUBLICATION-IDENTITIES.json'),publication_files=len(files),
        protected_count=e.read('BASELINE.json')['protected_count'],protected_mismatches=[],kernel=26,freeze_verified=True,
        JSON_links_whitespace_checked=True,credentials_published=False,git_diff_check=dict(returncode=diff.returncode,stdout=diff.stdout,stderr=diff.stderr),
        P6_A04_acceptance=False,P6_A05_access=False,semantic_implementation_changes=False,stopped=True,
        publisher_successor_reason='Only two self-publication links deferred, then checked after creation; failed first publication retained.'))
    assert all(p.exists() for p in links)
    assert all(e.digest(e.ROOT/p)==v['sha256'] for p,v in files.items())
    e.verify()
    print('Publication verified:',len(files),'files;',len(links),'links;',e.read('BASELINE.json')['protected_count'],'protected identities')

if __name__=='__main__': main()
