# Reproducing the read-only census

R6.47 used Python standard-library JSON parsing/hash/set/count operations only.
It did not import the VM, wrapper, adapter, registry, generators or scorers. A
temporary analysis script ran outside the workspace and printed results; only
documentation and JSON receipts are published here. This recipe defines the exact
selection and counting algorithm, independently of an execution or training runner.

From the repository root, these Python statements reproduce the selected count and
operation counts. They read only the listed historical JSON files. No files are
written, no model/library is loaded, no acceptance is executed.

```python
import json
from pathlib import Path
from collections import Counter

root = Path('.')
selected = {}

def collect(value, found):
    if isinstance(value, dict):
        required = {'identity', 'params', 'steps', 'result_type', 'order'}
        if required <= value.keys():
            found.setdefault(value['identity'], value)
        for child in value.values():
            collect(child, found)
    elif isinstance(value, list):
        for child in value:
            collect(child, found)

sources = []
for round_number in (36, 37):
    for name in ('old', 'new', 'a', 'b', 'a_new'):
        sources.append(root / f'benchmark/results/phase6/r6_{round_number}/{name}.json')
for round_number in (38, 39):
    for task in (1, 2, 3):
        sources.append(root / f'benchmark/results/phase6/r6_{round_number}/T{task}-A/registry/000005.json')
for task, snapshot in ((1, '000001'), (2, '000002'), (3, '000002')):
    sources.append(root / f'benchmark/results/phase6/r6_40/D{task}/registry/{snapshot}.json')
for task in range(1, 7):
    sources.append(root / f'benchmark/results/phase6/r6_40/E{task}-A/registry/000001.json')
for path in sources:
    collect(json.loads(path.read_text(encoding='utf-8')), selected)

counts = Counter()
def count(value):
    if isinstance(value, dict):
        if 'op' in value:
            counts[value['op']] += 1
        for key, child in value.items():
            if key in ('ref', 'const', 'add', 'le', 'eq'):
                counts['expr:' + key] += 1
            count(child)
    elif isinstance(value, list):
        for child in value:
            count(child)
for definition in selected.values():
    count(definition)
print(len(selected), dict(counts))
```

Expected:49 definitions; check63,value41,atom51,compose24,end30 and expression
ref348,const89,add83,le61,eq2. These fingerprints are exact identity deduplication,
not semantic-equivalence or alpha-equivalence proof. Example deduplication is at the
requirement episode level in INVENTORY.md, with all sibling conditions/stages grouped.
The17 rows, not the49 identity keys, define the positive-source count.

For the broader92-ID census, use the same `collect` function over `*.json` recursively
within exactly r6_36,r6_37,r6_38,r6_39,r6_40. Skip filenames beginning `BASELINE`,
`PUBLICATION-IDENTITIES.json`, `EXPORT.json`, and files larger than5,000,000 bytes.
Build a fresh `found` per round and an exact-ID union across rounds. The inclusion
rule is intentional: it is a scoped materialized-definition census, not a search
through all provider exports or giant observation archives. Counts/file denominators
are in ANALYSIS-RECEIPT.json. Equivalent definitions repeated under distinct pins can
still occur in this artifact count; no semantic diversity is inferred from92.

For preservation: start with r6_46/BASELINE.json `protected_files`, union each
r6_46/PUBLICATION-IDENTITIES.json `files[path].sha256`, then add that manifest and
VERIFICATION.json themselves. Require5,239 unique paths, compare SHA256 of current
bytes and verify the predecessor receipt's `manifest_sha256`. No P6-A05 content path
is present in this inherited union. Check new publication manifest separately and
bind its SHA256 in the new receipt. Historical receipts are not rewritten or rerun.
