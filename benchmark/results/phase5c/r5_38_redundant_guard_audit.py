"""Independent post-lock optional regression audit; no emission or B02 analysis."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import types as python_types

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from benchmark.semantic import nullable_study_r5_38 as study
from benchmark.semantic import unified_types_r5_27 as current
from benchmark.results.phase5c.r5_38_review import verify_lock


def audit():
    model = study.application()
    contract = model['operations']['reviewed']
    selection = contract['branches'][0]['value']
    predicate = selection['select']['where']['and']
    predicate.append(copy.deepcopy(predicate[1]))
    contract['branches'][0]['value'] = {'order': {'source': selection, 'keys': ['reviewed', 'code']}}
    source = subprocess.check_output(['git', 'show',
        '428a3409ea4d47a57a9fc9e5a94af2595d98ec43:benchmark/semantic/unified_types_r5_27.py'], cwd=ROOT, text=True)
    baseline = python_types.ModuleType('r538_optional_baseline')
    sys.modules[baseline.__name__] = baseline
    exec(compile(source, '<historical optional analyzer>', 'exec'), baseline.__dict__)
    baseline.checked_plan(contract).assert_invariants()
    try:
        current.checked_plan(contract).assert_invariants()
        diagnostic = None
    except ValueError as exc:
        diagnostic = str(exc)
    nullable = study.application()['operations']['ordered']
    order = nullable['branches'][0]['value']['order']
    guard = order['source']['select']['where']
    order['source']['select']['where'] = {'and': [guard, copy.deepcopy(guard)]}
    try:
        current.checked_plan(nullable).assert_invariants()
        nullable_diagnostic = None
    except ValueError as exc:
        nullable_diagnostic = str(exc)
    record = {'version': 'R5.38', 'source': model, 'baseline_accepts': True,
        'current_accepts': diagnostic is None, 'diagnostic': diagnostic,
        'classification': 'OPTIONAL_REDUNDANT_GUARD_ORDERING_REGRESSION' if diagnostic else 'NO_REGRESSION',
        'nullable_redundant_guard': {'source': nullable, 'current_accepts': nullable_diagnostic is None,
                                     'diagnostic': nullable_diagnostic},
        'lock': verify_lock(), 'generated': False, 'b02_analyzed_again': False}
    (Path(__file__).parent / 'R5_38-redundant-guard-audit.json').write_bytes((json.dumps(record, indent=2) + '\n').encode())
    print(json.dumps({k: v for k, v in record.items() if k != 'source'}, indent=2))


if __name__ == '__main__':
    audit()
