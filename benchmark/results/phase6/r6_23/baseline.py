"""Read-only historical/local identity check before adapter implementation."""
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
WEIGHT = 'a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f'
DIGEST = '500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41'


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def main():
    destination = HERE / 'BASELINE.json'
    assert not destination.exists()
    old = HERE.parent / 'r6_22'
    pins = json.loads((old / 'BASELINE.json').read_text())['protected_files'].copy()
    publications = []
    superseded = []
    for folder in [ROOT / 'experiments/typed_composition_r6_18'] + [HERE.parent / ('r6_' + str(n)) for n in range(19, 23)]:
        manifest = folder / 'PUBLICATION-IDENTITIES.json'
        pub = json.loads(manifest.read_text())
        for name, entry in pub['files'].items():
            current = sha(ROOT / name)
            if current != entry['sha256']:
                assert folder.name == 'typed_composition_r6_18'
                assert name in ('AGENTS.md', 'README.md', 'benchmark/README.md', 'docs/agent-workflow.md',
                                'docs/project-overview.md', 'docs/research-log.md', 'docs/decisions.md'), name
                assert pins.get(name) == current, name
                superseded.append(dict(path=name, historical_sha256=entry['sha256'],
                    preserved_current_sha256=current, reason='shared guidance superseded before R6.19'))
            else:
                pins[name] = entry['sha256']
        for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
            p = folder / name
            pins[p.relative_to(ROOT).as_posix()] = sha(p)
        publications.append(dict(path=manifest.relative_to(ROOT).as_posix(), sha256=sha(manifest), files=len(pub['files'])))
    assert all(sha(ROOT / p) == h for p, h in pins.items())
    ledger = json.loads((HERE.parent / 'r6_19/BASELINE.json').read_text())['kernel_ledger']
    assert len(ledger['baseline_kernel']) + len(ledger['preserved_additions']) == 26
    blob = Path(r'D:\Software\.ollama\models\blobs') / ('sha256-' + WEIGHT)
    assert sha(blob) == WEIGHT
    version = subprocess.run(['ollama', '--version'], capture_output=True, text=True, timeout=30)
    inventory = dict(cli_version=dict(returncode=version.returncode, stdout=version.stdout, stderr=version.stderr),
        weight_sha256=WEIGHT, weight_bytes=blob.stat().st_size, expected_digest=DIGEST,
        proposed_configuration=dict(temperature=0, seed=623, num_ctx=8192, num_predict=2048, top_k=20, top_p=.95, repeat_penalty=1),
        effective_context='R6.22 historical8192; current live context verified after qualification load')
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        def api(path, data=None):
            req = urllib.request.Request('http://127.0.0.1:11434' + path,
                data=json.dumps(data).encode() if data else None, headers={'Content-Type': 'application/json'})
            with opener.open(req, timeout=15) as r:
                return json.load(r)
        inventory['version'] = api('/api/version')
        assert inventory['version']['version'] == '0.35.0'
        inventory['selected'] = next(m for m in api('/api/tags')['models'] if m['name'] == 'qwen3:8b')
        assert inventory['selected']['digest'] == DIGEST
        show = api('/api/show', dict(model='qwen3:8b'))
        inventory.update(model_info=show['model_info'], parameters=show['parameters'], template=show['template'])
    except OSError as e:
        inventory['desktop_api_unavailable'] = str(e)
    result = dict(timestamp=datetime.now(timezone.utc).isoformat(), publications=publications,
        protected_files=pins, protected_count=len(pins), mismatches=[], historical_guidance_supersessions=superseded,
        kernel=26, kernel_ledger=ledger,
        vm_sha256=sha(ROOT / 'experiments/semantic_interpreter/interpreter.py'),
        wrapper_sha256=sha(ROOT / 'experiments/typed_composition_r6_18/composition.py'),
        inventory=inventory, preserved_r6_22_halt=sha(old / 'HALT.json'),
        git_status=subprocess.run(['git', 'status', '--short'], capture_output=True, text=True).stdout,
        implementation_not_started=True)
    destination.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('Baseline verified', len(pins), 'protected identities; kernel26; version', inventory.get('version'))


if __name__ == '__main__':
    main()
