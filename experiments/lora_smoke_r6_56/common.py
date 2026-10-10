"""Frozen nonproduction R6.56 settings and deterministic diagnostic scorer."""
import copy
import ctypes
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'benchmark/results/phase6/r6_56'
STORE = Path(r'C:\Users\lblan\AppData\Local\Temp\opencode\lykoi-r6-52')
ARTIFACTS = STORE / 'r6-56'
PYTHON = STORE / 'venv/Scripts/python.exe'
sys.path.insert(0, str(ROOT / 'experiments/training_setup_r6_52'))
import qualify as q52
from setup import sha


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n',
                            encoding='utf-8', newline='\n')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def identity(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def rows():
    all_rows = [json.loads(s) for s in (ROOT / 'benchmark/results/phase6/r6_51/DIRECT.jsonl').read_text().splitlines()]
    return [next(r for r in all_rows if r['episode_id'] == f'R6.48/E{i:02d}') for i in range(1, 7)]


def load_composition():
    spec = importlib.util.spec_from_file_location('r56_composition', ROOT / 'experiments/typed_composition_r6_18/composition.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rss(pid):
    # Win32 WorkingSetSize: external process resident working set, not virtual memory.
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
            (n, ctypes.c_size_t) for n in ('PeakWorkingSetSize', 'WorkingSetSize', 'QuotaPeakPagedPoolUsage',
            'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage', 'QuotaNonPagedPoolUsage',
            'PagefileUsage', 'PeakPagefileUsage')]
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    handle = kernel.OpenProcess(0x0400 | 0x0010, False, pid)
    if not handle:
        return None
    try:
        result = Counters()
        result.cb = ctypes.sizeof(result)
        if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(result), result.cb):
            return None
        return int(result.WorkingSetSize)
    finally:
        kernel.CloseHandle(handle)


def schema_valid(value, node, schema):
    """Exact evaluator for only the keywords used in the pinned R6.18 schema."""
    supported = {'$schema', '$id', 'title', '$defs', '$ref', 'type', 'const', 'enum', 'oneOf',
                 'additionalProperties', 'required', 'properties', 'pattern', 'minItems', 'maxItems',
                 'items', 'minimum', 'maximum', 'minProperties', 'maxProperties', 'propertyNames', 'uniqueItems'}
    assert set(node) <= supported, 'unimplemented schema keyword'
    if '$ref' in node:
        ref = node['$ref'].split('/')[-1]
        return schema_valid(value, schema['$defs'][ref], schema)
    if 'oneOf' in node and sum(schema_valid(value, n, schema) for n in node['oneOf']) != 1:
        return False
    if 'const' in node and (type(value) is not type(node['const']) or value != node['const']):
        return False
    if 'enum' in node and not any(type(value) is type(v) and value == v for v in node['enum']):
        return False
    types = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool, 'null': type(None)}
    if 'type' in node and type(value) is not types[node['type']]:
        return False
    if type(value) is str and 'pattern' in node and re.search(node['pattern'], value) is None:
        return False
    if type(value) is int and not node.get('minimum', value) <= value <= node.get('maximum', value):
        return False
    if type(value) is list:
        if not node.get('minItems', 0) <= len(value) <= node.get('maxItems', len(value)):
            return False
        if node.get('uniqueItems') and len({canonical(v) for v in value}) != len(value):
            return False
        if 'items' in node and not all(schema_valid(v, node['items'], schema) for v in value):
            return False
    if type(value) is dict:
        if not node.get('minProperties', 0) <= len(value) <= node.get('maxProperties', len(value)):
            return False
        if not set(node.get('required', [])) <= set(value):
            return False
        props = node.get('properties', {})
        extra = set(value) - set(props)
        additional = node.get('additionalProperties', True)
        if additional is False and extra:
            return False
        if 'propertyNames' in node and not all(schema_valid(k, node['propertyNames'], schema) for k in value):
            return False
        if not all(schema_valid(value[k], props[k], schema) for k in set(value) & set(props)):
            return False
        if type(additional) is dict and not all(schema_valid(value[k], additional, schema) for k in extra):
            return False
    return True


def score(text, row):
    c = load_composition()
    result = {'output_valid': False, 'schema_valid': False, 'type_valid': 'NOT_REACHED',
              'semantic_valid': False, 'functional_acceptance': False, 'functional_cases': [],
              'exact_target_match': text == row['completion'][0]['content'], 'normalized_target_match': False,
              'target_character_similarity': difflib.SequenceMatcher(None, text, row['completion'][0]['content'], autojunk=False).ratio(),
              'repair_count': 0, 'seal_tool_calls': 0}
    try:
        package = c.load(text)
        result['output_valid'] = type(package) is dict
        schema = read(ROOT / 'experiments/typed_composition_r6_18/typed-composition-1.schema.json')
        result['schema_valid'] = schema_valid(package, schema, schema)
        result['normalized_target_match'] = package == json.loads(row['completion'][0]['content'])
        if not result['output_valid']:
            return result
        try:
            c.validate(package)
            result['semantic_valid'] = True
            result['type_valid'] = True
        except c.Diagnostic as exc:
            result['native_diagnostic'] = exc.data
            if exc.data['code'] == 'TYPE':
                result['type_valid'] = False
            elif (exc.data['code'] == 'IDENTITY' and package.get('definitions') == []
                  and exc.data['detail'] == 'semantic content tampered'):
                result['type_valid'] = True  # All program type checks precede its final seal check.
            return result
        expanded = c.expand(package)
        eid = row['episode_id'].split('/')[-1]
        cases = read(ROOT / f'benchmark/results/phase6/r6_48/episodes/{eid}/ACCEPTANCE.json')['cases']
        root = 'program/' + package['program']['identity']
        for index, case in enumerate(cases):
            actual = copy.deepcopy(c.vm.execute(expanded['plan'], bytes.fromhex(case['input_hex']), case.get('limits')))
            if 'output' in actual:
                actual['output_hex'] = actual.pop('output').hex()
            expected = copy.deepcopy(case['expected'])
            if 'error' in expected:
                role = expected['error'].pop('role')
                expected['error']['node'] = root if role == 'program' else root + '/' + role
            differences = {k: {'expected': v, 'actual': actual.get(k)} for k, v in expected.items()
                           if k not in actual or type(actual[k]) is not type(v) or actual[k] != v}
            result['functional_cases'].append({'index': index, 'input_hex': case['input_hex'],
                                              'actual': actual, 'differences': differences})
        result['functional_acceptance'] = all(not o['differences'] for o in result['functional_cases'])
    except (c.Diagnostic, ValueError, KeyError, TypeError) as exc:
        result['native_diagnostic'] = getattr(exc, 'data', {'code': type(exc).__name__, 'detail': str(exc)})
    return result


def file_manifest(folder):
    return {p.relative_to(folder).as_posix(): {'sha256': sha(p), 'bytes': p.stat().st_size}
            for p in sorted(folder.rglob('*')) if p.is_file()}


def frozen_check():
    freeze = read(OUT / 'PREFLIGHT.json')
    assert freeze['status'] == 'PASS'
    for name, digest in freeze['frozen_payloads'].items():
        assert sha(ROOT / name) == digest, name
    assert identity(read(OUT / 'TRAINING-CONFIGURATION.json')['configuration']) == freeze['training_configuration_identity']
    return freeze
