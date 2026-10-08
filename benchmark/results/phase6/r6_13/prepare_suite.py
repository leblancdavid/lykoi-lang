"""Contract-derived fixtures. Never imports, inspects or invokes a candidate."""
from audit import HERE, ROOT, load, now, save, sha, verify

VERSION = 'r6.13-adversarial-1'
cases = []


def add(task, stage, label, request, expected, rationale):
    cases.append(dict(id=f'{task}-{stage}-{label}', task=task, stage=stage,
                      input=request, expected=expected, rationale=rationale))


def error(code, at=None, other=None):
    value = {'error': code}
    if at is not None:
        value['at'] = at
    if other is not None:
        value['other'] = other
    return value


def stock(rows, holds=()):
    return {'stock': [dict(sku=s, free=f, held=h, shipped=p) for s, f, h, p in rows],
            'holds': [dict(id=i, sku=s, n=n) for i, s, n in holds]}


def reserve(i, s, n):
    return dict(kind='reserve', id=i, sku=s, n=n)


def job(i, d=1, w=0, deadline=63, deps=()):
    return dict(id=i, duration=d, weight=w, deadline=deadline, deps=list(deps))


def frame(records):
    # Fixture serialization only: XOR tag, length, payload; no normalization.
    data = [1, len(records)]
    for tag, payload in records:
        check = tag ^ len(payload)
        for byte in payload:
            check ^= byte
        data += [tag, len(payload), *payload, check]
    return bytes(data).hex()


def binary_expected(records):
    return dict(hex=frame(records), records=len(records), payloadBytes=sum(len(p) for _, p in records))


def patch(at, old='', new='', when='always'):
    return dict(at=at, old=old, new=new, when=when)


def patched(hex_value, applied=(), skipped=()):
    return dict(hex=hex_value, applied=list(applied), skipped=list(skipped))


def round_value(ids, votes, exhausted=0, eliminated=None):
    return dict(totals=[dict(id=i, votes=v) for i, v in zip(ids, votes)],
                exhausted=exhausted, eliminated=eliminated)


def prepare():
    verify()
    # T1: shape/phase coverage and maximally interleaved coupled state.
    for label, request in [
        ('nested', {'stock': [None], 'ops': []}),
        ('float', {'stock': [dict(sku='A', qty=1.0)], 'ops': []}),
        ('empty', {'stock': [], 'ops': []}),
        ('extra', {'stock': [dict(sku='A', qty=1)], 'ops': [], 'extra': 0})]:
        add('T1', 'base', label, request, error('shape', -1), 'Whole-request strict shape/type phase rejects this valid-JSON malformed input.')
    skus = list('HGFEDCBA')
    ops = [reserve(chr(104-i), s, 100) for i, s in enumerate(skus)]
    ops += [dict(kind='ship' if i % 2 == 0 else 'release', id=chr(104-i)) for i in range(8)]
    add('T1', 'base', 'max-state', dict(stock=[dict(sku=s, qty=100) for s in skus], ops=ops),
        stock([(s, 100 if s in 'ACEG' else 0, 0, 0 if s in 'ACEG' else 100) for s in 'ABCDEFGH']),
        'Eight SKUs/16 operations/qty100; interleaved histories ship H,F,D,B and release G,E,C,A; stock output sorted.')
    add('T1', 'base', 'ids-order', dict(stock=[dict(sku='ZZZZ', qty=100), dict(sku='A', qty=0)],
        ops=[reserve('zzzz', 'ZZZZ', 99), reserve('a', 'ZZZZ', 1)]),
        stock([('A', 0, 0, 0), ('ZZZZ', 0, 100, 0)], [('a', 'ZZZZ', 1), ('zzzz', 'ZZZZ', 99)]),
        'One/four-character identifier boundaries; holds sorted independently of insertion.')
    add('T1', 'base', 'used-before-sku', dict(stock=[dict(sku='A', qty=1)], ops=[reserve('x', 'A', 1),
        dict(kind='ship', id='x'), reserve('x', 'Z', 100)]), error('duplicate_id', 2), 'Used-ID persists after ship; duplicate precedes unknown SKU and insufficient.')
    add('T1', 'base', 'duplicates-before-ops', dict(stock=[dict(sku='A', qty=0)]*2,
        ops=[dict(kind='release', id='x')]), error('duplicate_sku', -1), 'Duplicate stock phase precedes operation lookup.')
    add('T1', 'base', 'late-shape', dict(stock=[dict(sku='A', qty=0)]*2,
        ops=[dict(kind='release', id='x'), reserve('z', 'A', 101)]), error('shape', -1), 'Late range violation outranks duplicate stock and early unknown hold.')
    add('T1', 'base', 'ops17', dict(stock=[dict(sku='A', qty=0)], ops=[dict(kind='release', id='x')]*17),
        error('shape', -1), 'Operation upper bound overrides runtime errors.')
    # Modification-only histories; never offered to base snapshots.
    base_stock = [dict(sku='A', qty=100)]
    resize = lambda n: dict(kind='resize', id='x', n=n)
    add('T1', 'modification', 'repeat-resize', dict(stock=base_stock, ops=[reserve('x', 'A', 100), resize(1),
        reserve('y', 'A', 99), dict(kind='release', id='y'), resize(100), resize(100), resize(1), dict(kind='ship', id='x')]),
        stock([('A', 99, 0, 1)]), 'Shrink/grow/equality interleave with another hold, then ship; conservation 99+1=100.')
    add('T1', 'modification', 'coupled-insufficient', dict(stock=base_stock, ops=[reserve('x','A',1),
        reserve('y','A',99), resize(2)]), error('insufficient', 2), 'Increase tests shared free=0, not original quantity.')
    add('T1', 'modification', 'removed-hold', dict(stock=base_stock, ops=[reserve('x','A',1),
        dict(kind='release', id='x'), resize(100)]), error('unknown_hold', 2), 'Used historical ID is not an active resize target.')
    add('T1', 'modification', 'shape-first', dict(stock=base_stock, ops=[resize(1), resize(True)]),
        error('shape', -1), 'Late Boolean n outranks early unknown hold.')
    add('T1', 'modification', 'resize-extra', dict(stock=base_stock, ops=[dict(kind='resize',id='x',n=1,sku='A')]),
        error('shape', -1), 'Extended union branch still rejects extra keys.')
    add('T1', 'modification', 'max16', dict(stock=base_stock, ops=[reserve('x','A',1)]+[resize(100),resize(1)]*7+[resize(100)]),
        stock([('A',0,100,0)], [('x','A',100)]), 'Sixteen operations with repeated resize at both quantity boundaries.')
    # T2: closed-form optima, not candidate-derived search results.
    for label, jobs in [('nonobject',[None]), ('bool',[job('A', True)]),
                        ('float',[job('A', w=1.0)]), ('eight',[job(i) for i in 'ABCDEFGH'])]:
        add('T2','base',label,dict(jobs=jobs),error('shape'),'Strict nested/numeric/cardinality validation precedes scheduling.')
    add('T2','base','seven-optimum',dict(jobs=[job(i,1,w) for i,w in zip('ABCDEFG',range(1,8))]),
        dict(order=list('GFEDCBA'), completion=list(range(1,8)), cost=84),
        'Seven independent jobs allow 5040 orders; equal durations require descending weights by adjacent-swap argument; cost 7+12+15+16+15+12+7=84.')
    add('T2','base','seven-tie',dict(jobs=[job(i,9,0) for i in 'GFEDCBA']),
        dict(order=list('ABCDEFG'), completion=[9*i for i in range(1,8)], cost=0),
        '5040 equal-cost orders, lexical winner independent of input order, final inclusive deadline63.')
    add('T2','base','cycle',dict(jobs=[job('A',deps=['B']),job('B',deps=['C']),job('C',deps=['A'])]),
        error('cycle'),'Pure three-job cycle, no missing dependencies.')
    add('T2','base','phase-combination',dict(jobs=[job('A',deps=['B','Z']),job('B',deps=['A'])]),
        error('unknown_dep'),'Unknown dependency phase beats existing two-node cycle.')
    add('T2','base','dependency-tie-deadline',dict(jobs=[job('C',1,0,3,['A','B']),job('B',1,0,2),job('A',1,0,1)]),
        dict(order=list('ABC'), completion=[1,2,3],cost=0),'Inclusive deadlines force AB before dependent C; all costs tie.')
    add('T2','base','shape-before-duplicate',dict(jobs=[job('A',deps=['Z']),job('A',deadline=64)]),
        error('shape'),'Late deadline64 outranks duplicate ID and unknown dependency.')
    # T3 boundary serialization uses explicitly specified normalized payloads.
    records = [(i%3,[255,0,255,1,1,128,0,2]) for i in range(8)]
    normalized = [(t, p if t==0 else list(reversed(p)) if t==1 else [0,0,1,1,2,128,255,255]) for t,p in records]
    add('T3','base','max-message',dict(hex=frame(records).upper(), action='normalize'),binary_expected(normalized),
        'Eight records,64 payload bytes,180 hex chars; reversal, unsigned duplicate-preserving sort, uppercase decode and checksum re-encoding.')
    for label, hx, expected in [('missing-tag','0101','truncated'),('missing-length','010100','truncated'),
                                ('tag-before-length','010103','truncated'),('tag-with-length','01010309','tag'),
                                ('length-before-truncated','01010009','length'),
                                ('checksum-before-trailing','010100010100ff','trailing')]:
        # Last message has checksum 0 (0 xor 1 xor 1), then trailing ff.
        add('T3','base',label,dict(hex=hx,action='normalize'),error(expected),
            'Record-phase precedence from contract 2; missing tag/length checked before tag range, then length, payload/checksum, trailing.')
    add('T3','base','bad-checksum-later-tag',dict(hex='0102000101ff0300',action='prune'),error('checksum'),
        'First record bad checksum beats later invalid tag; validation precedes prune.')
    add('T3','base','overlong-before-version',dict(hex='02'+'00'*90,action='normalize'),error('shape'),
        '182 hex characters fail shape even with wrong binary version.')
    add('T3','base','wrong-action-shape',dict(hex='02ff',action=[]),error('shape'),'Valid JSON wrong action type beats binary version/count.')
    for label, source, expected_records, rationale in [
        ('exact8',[(2,[4,3,2,1]),(2,[8,7,6,5])],[(2,[1,2,3,4,5,6,7,8])],'Exact length8 merge accepted.'),
        ('split-then-merge',[(0,[1]*7),(0,[2]*2),(0,[3]*6)],[(0,[1]*7),(0,[2]*2+[3]*6)],'7+2 splits, newly last length2 then merges6; never reconsider earlier output.'),
        ('not-resort',[(2,[9,8]),(2,[2,1])],[(2,[8,9,1,2])],'Normalize each original, concatenate without global resort.'),
        ('empty-cap',[(1,list(range(8))),(1,[]),(1,[9])],[(1,list(reversed(range(8)))),(1,[9])],'Empty merges into full8; next byte creates new record.'),
        ('eight-empties',[(0,[])]*8,[(0,[])],'Eight same-tag empty records coalesce to one, not prune.'),
        ('alternating',[(i%2,[]) for i in range(8)],[(i%2,[]) for i in range(8)],'Alternating empty tags remain eight records.')]:
        add('T3','modification',label,dict(hex=frame(source),action='coalesce'),binary_expected(expected_records),rationale)
    # T4 max output and first-pair (not positional) precedence.
    add('T4','base','max160',dict(hex='00'*32,patches=[patch(i,new='ff'*8) for i in range(16)]),
        patched(('ff'*8+'00')*16+'00'*16,range(16)), 'Sixteen distinct insertions add128 bytes to32;160-byte result, all original zeros retained.')
    add('T4','base','pair-precedence',dict(hex='00000000',patches=[patch(2,'0000'),patch(0,'0000'),patch(1,'0000'),patch(2,'00')]),
        error('conflict',0,2),'Several conflicts: (0,2) wins before (0,3) and (1,2), irrespective of position order.')
    add('T4','base','unsorted-inserts',dict(hex='0102',patches=[patch(2,new='ee'),patch(0,new='ff'),patch(1,new='aa')]),
        patched('ff01aa02ee',[0,1,2]),'Assembly sorted by position; applied indices retain original order.')
    add('T4','base','skipped-overlap',dict(hex='0102',patches=[patch(0,'ffff','aa','match'),patch(0,'0102','bb')]),
        patched('bb',[1],[0]),'Skipped mismatching patch overlaps applied span but cannot conflict.')
    add('T4','base','bounds-before-mismatch',dict(hex='0102',patches=[patch(0,'ff'),patch(2,'01'),patch(3)]),
        error('bounds',1),'First bounds at1 outranks earlier mismatch and later bounds.')
    add('T4','base','mismatch-before-conflict',dict(hex='0102',patches=[patch(0,'01'),patch(0,'0102'),patch(1,'ff')]),
        error('mismatch',2),'All always comparisons before pair conflicts.')
    for label, request in [('bool',dict(hex='',patches=[patch(True)])),
                           ('nested',dict(hex='',patches=[None])),
                           ('over32',dict(hex='00'*33,patches=[])),
                           ('patch17',dict(hex='',patches=[patch(0)]*17))]:
        add('T4','base',label,request,error('shape',-1),'Strict shape/type/cardinality boundaries precede patch effects.')
    add('T4','modification','all-empty-absent',dict(hex='00'*32,patches=[patch(i,new='ff'*8,when='absent') for i in range(16)]),
        patched('00'*32,[],range(16)),'Sixteen empty-old absent patches skip, no insertions or conflicts.')
    add('T4','modification','original-slices',dict(hex='010203',patches=[patch(2,'ff','aa','absent'),patch(0,'00','','absent'),patch(1,'02','bb','absent')]),
        patched('02aa',[0,1],[2]),'Original coordinates for differing deletions/replacements; equal middle absent skips.')
    add('T4','modification','absent-pair',dict(hex='0000',patches=[patch(0,'ff','aa','absent'),patch(1,'ff','bb','absent'),patch(0,'ffff','cc','absent')]),
        error('conflict',0,2),'Applied absence predicates produce first overlapping pair (0,2).')
    add('T4','modification','bounds-skipped',dict(hex='00',patches=[patch(1,'ff','aa','absent')]),
        error('bounds',0),'Bounds checked even if predicate would otherwise be consulted.')
    add('T4','modification','always-precedence',dict(hex='0000',patches=[patch(0,'ff','aa','absent'),patch(0,'ffff','bb','absent'),patch(1,'ff')]),
        error('mismatch',2),'Always mismatch precedes conflict among two applied absent spans.')
    add('T4','modification','wrong-enum',dict(hex='',patches=[patch(0,when={})]),
        error('shape',-1),'Malformed union enum type remains shape error.')
    # T5 explicit round histories with closed-form tallies.
    ballots = [dict(ranks=[i],weight=9) for i in 'FEDCBA' for _ in range(2)]
    rounds = [round_value('ABCDEF'[:6-k],[18]*(6-k),18*k,'FEDCB'[k] if k<5 else None) for k in range(6)]
    add('T5','base','six-round-max',dict(candidates=list('FEDCBA'),ballots=ballots),dict(winner='A',rounds=rounds),
        'Six candidates,12 ballots,max weight9; equal18 totals eliminate F,E,D,C,B; exhaustion18 per round; final A18 wins over nonexhausted18.')
    add('T5','base','transfer-not-exhaust',dict(candidates=list('CBA'),ballots=[dict(ranks=list('BA'),weight=2),
        dict(ranks=list('CA'),weight=2),dict(ranks=['A'],weight=2)]),
        dict(winner='A',rounds=[round_value('ABC',[2,2,2],eliminated='C'),round_value('AB',[4,2])]),
        'Tied first round eliminates C, its weight transfers to A, no exhaustion.')
    add('T5','base','half-exhausted',dict(candidates=['B','A'],ballots=[dict(ranks=['A'],weight=9),
        dict(ranks=['B'],weight=9),dict(ranks=[],weight=9)]),dict(winner='A',rounds=[
        round_value('AB',[9,9],9,'B'),round_value('A',[9],18)]),
        'Exactly half18 is not majority; empty ballot excluded; second round counts newly exhausted B weight.')
    add('T5','base','all-exhaust-max',dict(candidates=list('FEDCBA'),ballots=[dict(ranks=[],weight=9)]*12),
        dict(winner=None,rounds=[round_value('ABCDEF',[0]*6,108)]),'All108 exhausted ends immediately with sorted zero totals.')
    for label, request in [('nested',dict(candidates=['A'],ballots=[None])),
                           ('ranks-type',dict(candidates=['A'],ballots=[dict(ranks='A',weight=1)])),
                           ('weight-float',dict(candidates=['A'],ballots=[dict(ranks=['A'],weight=1.0)])),
                           ('thirteen',dict(candidates=['A'],ballots=[dict(ranks=['A'],weight=1)]*13))]:
        add('T5','base',label,request,error('shape'),'Nested shape/types/ballot upper boundary validated before rounds.')
    add('T5','base','shape-before-duplicate',dict(candidates=['A','A'],ballots=[dict(ranks=['Z','Z'],weight=1)]),
        error('shape'),'Repeated rank shape violation precedes duplicate candidate and unknown rank.')
    add('T5','base','duplicate-before-unknown',dict(candidates=['B','B'],ballots=[dict(ranks=['Z'],weight=9)]),
        error('duplicate_candidate'),'Domain duplicate candidate phase precedes unknown rank.')
    ids = [c['id'] for c in cases]
    assert len(ids) == len(set(ids)) == 68
    assert all(len(__import__('json').dumps(c['input']).encode('utf-8')) <= 16384 for c in cases)
    save(HERE / 'ADVERSARIAL-1.json', dict(version=VERSION, utc=now(), source='R6.12 contracts and VERIFICATION-REVIEW omissions', cases=cases))
    paths = ['PROTOCOL.md','scorer.py','test_scorer.py','prepare_suite.py','ADVERSARIAL-1.json','audit.py']
    save(HERE / 'FREEZE.json', dict(utc=now(), acceptance_version=VERSION,
         files={p:sha(HERE / p) for p in paths}, candidate_identities=load(HERE / 'BASELINE.json')['candidate_identities'],
         selection_before_candidate_execution=True, unique_suite_entries=68,
         base_entries=50, modification_entries=18, repeated_base_on_modifications=30))
    print('Frozen 68 new suite entries: 50 base + 18 modification; 30 base repeats on modifications')


if __name__ == '__main__':
    prepare()
