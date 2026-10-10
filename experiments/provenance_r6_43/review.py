"""Separate static expectation review; imports no producer, VM or execution oracle."""
import ast
from common import ROOT, OLD, OUT, read, sha


def review():
    source = ROOT / 'experiments/semantic_interpreter/interpreter.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    machine = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Machine')
    decode = next(n for n in machine.body if isinstance(n, ast.FunctionDef) and n.name == 'decode')
    # UInt return explicitly omits fourth constructor argument (origins).
    final = decode.body[-1]
    assert isinstance(final, ast.Return) and isinstance(final.value, ast.Call)
    assert ast.unparse(final.value) == 'Cell(v, x.start, x.end)'
    cell = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Cell')
    origin = next(n for n in cell.body if isinstance(n, ast.AnnAssign) and n.target.id == 'origins')
    assert isinstance(origin.value, ast.Tuple) and not origin.value.elts
    run = next(n for n in machine.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
    calls = [n for n in ast.walk(run) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == 'Cell']
    assert any(ast.unparse(n) == 'Cell(self.data[start:self.i], start, self.i, tuple(range(start, self.i)))'
               for n in calls)
    assert any(len(n.args) == 4 and ast.unparse(n.args[1]) == 'start'
               and "span_end if op == 'seq' else self.i" == ast.unparse(n.args[2]) for n in calls)
    package = read(OLD / 'COMPACT.json')
    guarded, nested = package['definitions']
    root = 'program/' + package['program']['identity']
    mapping = {root: {'definition': package['program']['identity'], 'local': 'region'}}
    chains = {root: []}
    for local in ('x', 'y', 'end', 'post_low', 'post_high', 'total', 'encode'):
        mapping[root + '/' + local] = {'definition': package['program']['identity'], 'local': local}
        chains[root + '/' + local] = []
    for side in ('left', 'right'):
        n = root + '/' + side + '/' + nested['identity']
        g = n + '/inner/' + guarded['identity']
        chain = [{'call_local': side, 'definition': nested['identity']}]
        for path, pin, local, trail in ((n, nested['identity'], 'region', chain),
             (g, guarded['identity'], 'region', chain + [{'call_local': 'inner', 'definition': guarded['identity']}]),
             (g + '/guard', guarded['identity'], 'guard', chain + [{'call_local': 'inner', 'definition': guarded['identity']}]),
             (g + '/sum', guarded['identity'], 'sum', chain + [{'call_local': 'inner', 'definition': guarded['identity']}])):
            mapping[path] = {'definition': pin, 'local': local}
            chains[path] = trail
    assert mapping == read(OLD / 'EXPECTED-MAP.json')
    assert chains == read(OLD / 'CORRESPONDENCE.json')['expansion_paths']
    expectations = read(OUT / 'EXPECTATIONS.json')
    anchors = {'0201': ('success', None, 51, 43), '0404': ('INNER', 0, 15, 13),
               '0004': ('INNER', 1, 27, 21), '0000': ('POST_LOW', 2, 37, 29),
               '0302': ('POST_HIGH', 2, 43, 35), '020100': ('TRAILING', 2, 8, 8)}
    for row in expectations['rows']:
        data = bytes.fromhex(row['input_hex'])
        assert row['forms']['compact'] == row['forms']['exact']
        for form, wanted in row['forms'].items():
            assert all(c['origins'] == [] for c in wanted['cells'])
            for index, numeric in enumerate(wanted['decodes']):
                assert numeric['span'] == [index, index + 1]
                assert numeric['raw_origins'] == [index] and numeric['numeric_origins'] == []
                assert numeric['value'] == data[index]
            for c in wanted['cells']:
                if c['node'] in chains and c['node'] != root and mapping[c['node']]['local'] == 'region':
                    assert c['span'] == [2, 2]
                if c['node'] in (root, 'flat/Entry'):
                    assert c['span'] == [0, 2]
            if row['input_hex'] in anchors:
                code, offset, compact_work, flat_work = anchors[row['input_hex']]
                assert wanted.get('code', wanted['status']) == code
                assert wanted['work'] == (flat_work if form == 'flat' else compact_work)
                if code != 'success':
                    flat_offset = 0 if code == 'POST_LOW' else 1 if code == 'POST_HIGH' else offset
                    assert wanted['offset'] == (flat_offset if form == 'flat' else offset)
    # Static exact form retains four zero-byte nested seqs; flat retains only root.
    node_counts = {}
    for form in ('EXACT', 'FLAT'):
        plan = read(OLD / (form + '.json'))
        nodes = []

        def walk(n):
            nodes.append(n)
            for step in n.get('steps', []):
                walk(step['node'])

        walk(plan['decode'])
        nodes.append(plan['encode'])
        assert len(nodes) == (16 if form == 'EXACT' else 12)
        assert sum(n['op'] == 'seq' for n in nodes) == (5 if form == 'EXACT' else 1)
        node_counts[form] = len(nodes)
    authorities = [source, ROOT / 'experiments/semantic_interpreter/CONTRACT-1.md',
                   ROOT / 'experiments/typed_composition_r6_18/SEMANTICS-1.md']
    return {'passed': True, 'method': 'separate AST/static coordinate audit and six manually derived anchors',
            'candidate_executions': 0, 'historical_output_reads': 0, 'reviewed_inputs': 39,
            'map_entries': len(mapping), 'node_counts': node_counts,
            'coordinate_distinctions_reviewed': ['raw_byte', 'decoded_numeric', 'sequence_return', 'symbolic', 'flat'],
            'authorities': {p.relative_to(ROOT).as_posix(): sha(p) for p in authorities},
            'limitations': ['same coordinator and shared prior knowledge', 'no independent human reviewer',
                           'no cognitive or blind independence', 'static review is not universal semantic proof']}
