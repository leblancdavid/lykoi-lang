"""Fresh data-only plan authoring. Prints a patch; never used by the VM.

Run without arguments to print the immutable initial artifact patch.
No task input, interpreter import, callback, or task runtime exists here.
"""
import json


def make(task):
    serial = 0
    def node(op, **fields):
        nonlocal serial
        serial += 1
        return dict(id=f'{task}_{serial}', op=op, **fields)
    def ref(name): return {'ref': name}
    def const(value): return {'const': value}
    def le(a, b): return {'le': [a, b]}
    def step(n, bind=None):
        return {'node': n, **({'bind': bind} if bind else {})}
    def seq(steps, result): return node('seq', steps=steps, result=result)
    def val(x): return node('value', expr=x)
    def atom(): return node('atom', codec='uint8')
    def check(test, site, code): return node('check', test=test, site=site, code=code)
    def emit(x): return node('emit', codec='uint8', expr=x)
    def dispatch(test, yes, no):
        return node('dispatch', expr=test, branches={'True': yes, 'False': no})
    null = const(None)
    if task == 'T1':
        mode = node('choice', code='MODE', branches=[
            {'prefixes': [[0]], 'node': node('literal', bytes=[0], value=const(0))},
            {'prefixes': [[1]], 'node': node('literal', bytes=[1], value=const(10))}])
        raw = {'add': [{'add': [ref('x'), ref('y')]}, ref('boost')]}
        record = lambda amount, clipped: {'record': {'amount': amount, 'clipped': const(clipped)}}
        decode = seq([
            step(mode, 'boost'), step(atom(), 'x'), step(atom(), 'y'),
            step(node('end')), step(val(raw), 'raw'),
            step(dispatch(le(ref('raw'), const(200)),
                          val(record(ref('raw'), False)),
                          val(record(const(200), True))), 'answer')], ref('answer'))
        encode = seq([
            step(emit(ref('root.amount'))),
            step(dispatch(ref('root.clipped'), emit(const(1)), emit(const(0))))], null)
    else:
        # Count is emitted privately before parsing; only even <=16 lengths succeed.
        count = emit(const(8))
        for n in reversed(range(8)):
            count = dispatch(le({'input_length': None}, const(2*n)), emit(const(n)), count)
        peek = node('choice', code='INTERNAL_LOOKAHEAD', branches=[
            *[{'prefixes': [[n]], 'node': val(const(n))} for n in range(16)],
            {'prefixes': [[n] for n in range(16, 256)], 'node': val(const(16))}])
        # This branch always rejects, but first respects the next record's checks.
        overlap = seq([
            step(atom(), 'next_start'), step(atom(), 'next_end'),
            step(check(le(ref('next_end'), const(15)), ref('next_end'), 'RANGE')),
            step(check(le(ref('next_start'), ref('next_end')), ref('next_start'), 'ORDER')),
            step(check(const(False), ref('next_start'), 'OVERLAP'))], null)
        inspect_next = seq([
            step(peek, 'peek'),
            step(dispatch(le(ref('end'), ref('peek')), val(null), overlap))], null)
        # output_length = cursor+1 after count and successfully parsed records.
        # Skip lookahead at EOF and at the ninth-record boundary.
        following = dispatch(le(const(17), {'output_length': None}), val(null),
            dispatch(le({'input_length': None}, {'add': [{'output_length': None}, const(-1)]}),
                     val(null), inspect_next))
        row = seq([
            step(atom(), 'start'),
            step(check(le(ref('start'), const(15)), ref('start'), 'RANGE')),
            step(atom(), 'end'),
            step(check(le(ref('end'), const(15)), ref('end'), 'RANGE')),
            step(check(le(ref('start'), ref('end')), ref('start'), 'ORDER')),
            step(emit(ref('start'))), step(emit(ref('end'))), step(following)],
            {'record': {'start': ref('start'), 'end': ref('end')}})
        rows = node('repeat', body=row, stop=[], eof=True, max=8, occurrence_limit=True)
        decode = seq([step(count), step(rows, 'rows')], ref('rows'))
        encode = val(null)
    return dict(version='semantic-plan-1', text=False, rules={}, decode=decode, encode=encode)


if __name__ == '__main__':
    print('*** Begin Patch')
    for task in ('T1', 'T3'):
        content = json.dumps(make(task), separators=(',', ':'))
        for phase in ('base', 'first'):
            print(f'*** Add File: D:/Dev/axiom/benchmark/results/phase6/r6_15/C/{phase}/{task}.plan.json')
            print('+' + content)
    print('*** End Patch')
