"""Read-only identity inventory, before R6.24 tool implementation."""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

def main():
    assert not (HERE / 'BASELINE.json').exists()
    prior = HERE.parent / 'r6_23'
    old = json.loads((prior / 'BASELINE.json').read_text())
    pins = old['protected_files'].copy()
    pub = json.loads((prior / 'PUBLICATION-IDENTITIES.json').read_text())
    pins.update({p: e['sha256'] for p, e in pub['files'].items()})
    for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
        p = prior / name
        pins[p.relative_to(ROOT).as_posix()] = sha(p)
    mismatches = [p for p, h in pins.items() if sha(ROOT / p) != h]
    assert not mismatches, mismatches
    assert len(old['kernel_ledger']['baseline_kernel']) + len(old['kernel_ledger']['preserved_additions']) == 26
    weight = Path(r'D:\Software\.ollama\models\blobs\sha256-a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f')
    assert sha(weight) == weight.name[7:]
    version = subprocess.run(['ollama', '--version'], capture_output=True, text=True, timeout=30)
    result = dict(timestamp=datetime.now(timezone.utc).isoformat(), protected_files=pins,
        protected_count=len(pins), mismatches=mismatches, kernel=26, kernel_ledger=old['kernel_ledger'],
        historical_guidance_supersessions=old['historical_guidance_supersessions'],
        implementations={p: sha(ROOT / p) for p in ['experiments/semantic_interpreter/interpreter.py',
            'experiments/typed_composition_r6_18/composition.py', 'benchmark/results/phase6/r6_23/adapter.py']},
        prior_abort_evidence={f'r6_{n}/{name}': sha(HERE.parent / f'r6_{n}' / name)
            for n in (21, 23) for name in ('HALT.json', 'FAILURE-ANALYSIS.json')},
        weight_sha256=sha(weight), weight_bytes=weight.stat().st_size,
        ollama_cli=dict(returncode=version.returncode, stdout=version.stdout, stderr=version.stderr),
        inference_configuration=dict(model='qwen3:8b', temperature=0, seed=624, num_ctx=8192,
            num_predict=384, top_k=20, top_p=.95, repeat_penalty=1, think=False,
            interface='native /api/chat tools; no forced JSON format'),
        context_note='metadata40960; requested8192; effective context checked on loaded model and runtime log',
        implementation_not_started=True,
        git_status=subprocess.run(['git', 'status', '--short'], capture_output=True, text=True).stdout)
    (HERE / 'BASELINE.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('Verified', len(pins), 'protected identities; kernel26; baseline precedes implementation')

if __name__ == '__main__':
    main()
