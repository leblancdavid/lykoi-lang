# R6.31 — Read-only publication verification recipe

The [publication manifest](PUBLICATION-IDENTITIES.json) binds all R6.31 report,
protocol, inventory and additive guidance files by raw SHA256 and byte length.
It excludes itself and [verification receipt](VERIFICATION.json) to avoid recursive
hashes. The receipt binds the manifest. Baseline anchors bind the inherited complete
preservation maps; no historical execution is needed for integrity verification.

From repository root, a standard-library Python verifier can perform the following
read-only checks (run Python with this code as input; no application imports):

```python
from pathlib import Path
import hashlib, json, re, subprocess
root = Path.cwd()
folder = root / 'benchmark/results/phase6/r6_31'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
baseline = json.loads((folder / 'BASELINE.json').read_text())
for p, h in baseline['anchors'].items():
    assert sha(root / p) == h, p
previous = json.loads((root / 'benchmark/results/phase6/r6_30/BASELINE.json').read_text())
publication = json.loads((root / 'benchmark/results/phase6/r6_30/PUBLICATION-IDENTITIES.json').read_text())
pins = dict(previous['protected_files'])
pins.update({p: v['sha256'] for p, v in publication['files'].items()})
pins = {p: h for p, h in pins.items() if not re.search(r'P6[-_]A05', p, re.I)}
assert len(pins) == baseline['protected_identity_count']
for p, h in pins.items():
    assert sha(root / p) == h, p
ledger = previous['kernel_ledger']
assert len(ledger['baseline_kernel']) + len(ledger['preserved_additions']) == 26
manifest = json.loads((folder / 'PUBLICATION-IDENTITIES.json').read_text())
receipt = json.loads((folder / 'VERIFICATION.json').read_text())
assert sha(folder / 'PUBLICATION-IDENTITIES.json') == receipt['manifest_sha256']
for p, identity in manifest['files'].items():
    path = root / p
    assert sha(path) == identity['sha256'], p
    assert path.stat().st_size == identity['bytes'], p
    text = path.read_text(encoding='utf-8')
    assert all(line.rstrip() == line for line in text.splitlines()), p
    if path.suffix == '.json':
        json.loads(text)
    if path.suffix == '.md':
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if '://' not in target and not target.startswith('#'):
                assert (path.parent / target.split('#')[0]).exists(), (p, target)
subprocess.run(['git', 'diff', '--check'], check=True)
print('R6.31 publication and 1,752 preservation identities verified; kernel26')
```

During initial publication additionally verify `git diff --exit-code`: all tracked
bytes remain unchanged, with only additive untracked R6.31 documents. After a future
commit that condition is no longer a claim about untracked status; the pinned byte
and preservation checks remain applicable. Check actual status and file scope too.
JSON validity includes manifest/receipt parsing; both excluded files receive their
own whitespace checks. Verify receipt's stated checks against actual command output,
not from Boolean fields alone. No credentials or provider configuration is needed.

Publication integrity is not functional acceptance, independent review, semantic
qualification or an empirical H1/H2 result. No historical tests are rerun here.
