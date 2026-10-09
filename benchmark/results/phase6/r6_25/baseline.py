"""Verify R6.24 publication and all inherited pins before implementation."""
import os
import subprocess
from common import HERE, ROOT, sha, save, now
import json

def main():
    assert not (HERE / 'BASELINE.json').exists()
    old = HERE.parent / 'r6_24'
    b = json.loads((old / 'BASELINE.json').read_text())
    pub = json.loads((old / 'PUBLICATION-IDENTITIES.json').read_text())
    receipt = json.loads((old / 'VERIFICATION.json').read_text())
    assert receipt['passed'] and receipt['publication_manifest_sha256'] == sha(old / 'PUBLICATION-IDENTITIES.json')
    pins = dict(b['protected_files'])
    pins.update({p: e['sha256'] for p, e in pub['files'].items()})
    for n in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
        p = old / n
        pins[p.relative_to(ROOT).as_posix()] = sha(p)
    assert all(sha(ROOT / p) == h for p, h in pins.items())
    assert len(b['kernel_ledger']['baseline_kernel']) + len(b['kernel_ledger']['preserved_additions']) == 26
    raw = json.loads((old / 'calls/control_tools-result.json').read_text())['message']['tool_calls'][0]
    control = json.loads(json.dumps(raw))
    control['function'].update(name='declare_input', arguments={'definition': 'MetadataControl', 'inputs': []})
    from common import tools
    rejection = tools.Session(['value']).dispatch(control)
    assert rejection['response']['error']['code'] == 'TOOL_SYNTAX'
    weight = __import__('pathlib').Path(r'D:\Software\.ollama\models\blobs\sha256-a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f')
    assert sha(weight) == b['weight_sha256']
    save('BASELINE.json', dict(timestamp=now(), protected_files=pins, protected_count=len(pins), kernel=26,
        kernel_ledger=b['kernel_ledger'], implementations=b['implementations'], weight_sha256=sha(weight),
        weight_bytes=weight.stat().st_size, historical_rejection=rejection, preserved_native_envelope=raw,
        r624_publication_verified=True, implementation_not_started=True,
        available_models=subprocess.run(['ollama', 'list'], capture_output=True, text=True).stdout,
        remote_credential_presence={k: bool(os.environ.get(k)) for k in ('OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'OPENROUTER_API_KEY')},
        model_selection='Existing qwen3:8b selected prospectively: native tools and pinned small local footprint previously verified. Other local models exist but are not selected or tested. No configured remote endpoint supplied.',
        git_status=subprocess.run(['git', 'status', '--short'], capture_output=True, text=True).stdout))
    print('Baseline verified:', len(pins), 'protected identities; kernel26; historical rejection preserved')

if __name__ == '__main__':
    main()
