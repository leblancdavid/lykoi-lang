"""Preconstruction source/acceptance freeze; no candidate or expected-value evaluator."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'benchmark/results/phase6/r6_63'
sys.path.insert(0, str(ROOT / 'experiments/typed_composition_r6_18'))
import composition as c


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def pin(value):
    return hashlib.sha256(c.canonical(value)).hexdigest()


def write(path, value):
    assert not path.exists(), path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def baseline():
    path = ROOT / 'experiments/curriculum_design_r6_62/audit.py'
    spec = importlib.util.spec_from_file_location('r663_identity_only', path)
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    inherited = prior.baseline()  # identity checks only, never prior scorer/publication
    assert inherited == read(prior.OUT / 'BASELINE.json')
    manifest = read(prior.OUT / 'PUBLICATION-IDENTITIES.json')
    for name, entry in manifest['files'].items():
        assert sha(ROOT / name) == entry['sha256'], name
    assert read(prior.OUT / 'VERIFICATION.json')['passed']
    paths = ['docs/training-data-admission-r6.49.md',
             'experiments/typed_composition_r6_18/composition.py',
             'experiments/semantic_interpreter/interpreter.py',
             'benchmark/results/phase6/r6_23/adapter.py',
             'benchmark/results/phase6/r6_24/tools.py',
             'benchmark/results/phase6/r6_25/TOOLS.json']
    paths += [f'benchmark/results/phase6/r6_62/{n}' for n in
              ('A-1.schema.json', 'B-1.schema.json', 'C-1.schema.json', 'common-1.schema.json')]
    return dict(status='PASS', inherited=inherited,
                r6_62_publication_sha256=sha(prior.OUT / 'PUBLICATION-IDENTITIES.json'),
                r6_62_payload_files=len(manifest['files']),
                explicit_identities={p: sha(ROOT / p) for p in paths}, kernel_constructs=26,
                kernel_basis='unchanged inherited accounting and production implementation',
                historical_rescoring=0)


def state(name, params, literals, result_type, prefix=None):
    body = dict(version='r6.63-state-1', foundation=c.FOUNDATION, name=name,
                params=[dict(name=n, type=t) for n, t in params],
                steps=prefix or [], order=[s['id'] for s in (prefix or [])],
                literals=literals, output_id='selected', result_type=result_type)
    return dict(body, identity=pin(body))


def fixture(args, value=None, error=None):
    expected = dict(status='reject', code=error) if error else dict(
        status='success', type='Bool' if type(value) is bool else 'Int64', value=value)
    return dict(arguments=args, expected=expected)


def freeze():
    write(OUT / 'BASELINE.json', baseline())
    hi, lo = 9223372036854775807, -9223372036854775808
    # Every expected output below is an explicit source fixture, not candidate-derived.
    rows = [
      ('D01', 'PAIR_SUM', 'Combine the stored arrival count and stored reserve count. Ignore the decoy flag.',
       state('PairSum', [('arrivals','Int64'),('reserve','Int64'),('decoy','Bool')], [], 'Int64'),
       [fixture(dict(arrivals=2,reserve=3,decoy=True),5), fixture(dict(arrivals=hi,reserve=0,decoy=False),hi),
        fixture(dict(arrivals=hi,reserve=1,decoy=False),error='OVERFLOW'), fixture(dict(arrivals=lo,reserve=-1,decoy=True),error='OVERFLOW'),
        fixture(dict(arrivals=lo,reserve=1,decoy=False),-9223372036854775807), fixture(dict(arrivals=True,reserve=1,decoy=False),error='ARGUMENT_TYPE')]),
      ('D02','LITERAL_INCREMENT','Add one fixed spare unit to the stored count; the spare is the left operand. Ignore the stored bonus.',
       state('SpareFirst',[('count','Int64'),('bonus','Int64')],[1,7],'Int64'),
       [fixture(dict(count=0,bonus=7),1),fixture(dict(count=hi,bonus=0),error='OVERFLOW'),
        fixture(dict(count=lo,bonus=9),-9223372036854775807),fixture(dict(count=-1,bonus=1),0)]),
      ('D03','REPEATED_REFERENCE','Count the same stored batch twice. Do not use the independent distractor batch.',
       state('DoubleBatch',[('batch','Int64'),('other','Int64')],[],'Int64'),
       [fixture(dict(batch=0,other=99),0),fixture(dict(batch=-3,other=3),-6),fixture(dict(batch=4611686018427387903,other=0),9223372036854775806),
        fixture(dict(batch=4611686018427387904,other=0),error='OVERFLOW'),fixture(dict(batch=-4611686018427387904,other=1),lo)]),
      ('D04','SUBTOTAL_REUSE','Add the stored adjustment to the already constructed subtotal. Use subtotal, not the original base or the unused mirror.',
       state('SubtotalReuse',[('base','Int64'),('delta','Int64'),('adjustment','Int64')],[],'Int64',[
           dict(id='subtotal',type='Int64',deps=['base','delta'],node=dict(op='value',expr={'add':[{'ref':'base'},{'ref':'delta'}]})),
           dict(id='mirror',type='Int64',deps=['base'],node=dict(op='value',expr={'ref':'base'}))]),
       [fixture(dict(base=2,delta=3,adjustment=4),9),fixture(dict(base=-2,delta=1,adjustment=1),0),
        fixture(dict(base=hi,delta=0,adjustment=1),error='OVERFLOW'),fixture(dict(base=hi,delta=1,adjustment=-1),error='OVERFLOW')]),
      ('D05','UPPER_BOUND','Report whether the stored load is no greater than five. The unrelated cap is a distractor.',
       state('UpperBound',[('load','Int64'),('cap','Int64')],[5,0],'Bool'),
       [fixture(dict(load=4,cap=0),True),fixture(dict(load=5,cap=0),True),fixture(dict(load=6,cap=99),False),
        fixture(dict(load=lo,cap=0),True),fixture(dict(load=hi,cap=0),False)]),
      ('D06','LOWER_BOUND','Report whether five is no greater than the stored stock. Ignore the spare stock.',
       state('LowerBound',[('stock','Int64'),('spare','Int64')],[5,0],'Bool'),
       [fixture(dict(stock=4,spare=99),False),fixture(dict(stock=5,spare=0),True),fixture(dict(stock=6,spare=0),True),
        fixture(dict(stock=lo,spare=0),False),fixture(dict(stock=hi,spare=0),True)]),
      ('D07','ORDERED_REFERENCE_LIMIT','Report whether requested units fit within available units. Preserve requested then available operand order.',
       state('Fits',[('requested','Int64'),('available','Int64'),('noise','Bool')],[],'Bool'),
       [fixture(dict(requested=1,available=2,noise=True),True),fixture(dict(requested=2,available=1,noise=False),False),
        fixture(dict(requested=hi,available=hi,noise=False),True),fixture(dict(requested=lo,available=hi,noise=True),True),
        fixture(dict(requested=hi,available=lo,noise=True),False)]),
      ('D08','INTEGER_AGREEMENT','Report whether the recorded reading exactly matches the reference reading; ordering alone is insufficient.',
       state('ReadingMatch',[('recorded','Int64'),('reference','Int64'),('unused','Int64')],[],'Bool'),
       [fixture(dict(recorded=2,reference=2,unused=0),True),fixture(dict(recorded=1,reference=2,unused=1),False),
        fixture(dict(recorded=2,reference=1,unused=2),False),fixture(dict(recorded=lo,reference=lo,unused=0),True),
        fixture(dict(recorded=hi,reference=lo,unused=0),False)]),
      ('D09','BOOLEAN_AGREEMENT','Report whether the two Boolean acknowledgments agree. Never convert them to integers.',
       state('Acknowledgments',[('first','Bool'),('second','Bool'),('decoy','Int64')],[],'Bool'),
       [fixture(dict(first=False,second=False,decoy=1),True),fixture(dict(first=False,second=True,decoy=0),False),
        fixture(dict(first=True,second=False,decoy=0),False),fixture(dict(first=True,second=True,decoy=0),True),
        fixture(dict(first=1,second=True,decoy=0),error='ARGUMENT_TYPE')]),
      ('D10','BOOLEAN_LITERAL_MATCH','Report whether the stored enabled flag equals literal true, ignoring the override flag.',
       state('EnabledMatch',[('enabled','Bool'),('override','Bool')],[True,False],'Bool'),
       [fixture(dict(enabled=False,override=True),False),fixture(dict(enabled=True,override=False),True),
        fixture(dict(enabled=0,override=True),error='ARGUMENT_TYPE'),fixture(dict(enabled=True),error='ARGUMENT_SHAPE')])
    ]
    for eid, family, text, before, cases in rows:
        folder = OUT / 'episodes' / eid
        source = dict(episode=eid,family=family,component='R663_FIXED_TYPED_STEP',requirement=text,
                      provenance='coordinator_authored_synthetic_expert_fixture',
                      expected_result_type=before['result_type'], acceptance_scope='finite declared fixtures',
                      rights='owner-authorized research data qualification; actual training requires new authorization')
        write(folder / 'SOURCE.json', source)
        write(folder / 'BEFORE.json', before)
        write(folder / 'FRC.json', dict(source_sha256=sha(folder/'SOURCE.json'),before_sha256=sha(folder/'BEFORE.json'),
              obligations=['source relation','ordered exact operands','typed result','exact direct deps','unchanged prefix','frozen boundary behavior']))
        write(folder / 'ACCEPTANCE.json', dict(cases=cases, expected_origin='literal source fixtures frozen before expert action'))
    write(OUT / 'PARTITIONS.json', dict(training_development=[r[0] for r in rows], tier_e=0,
        reserved_family='UNIT_EQUALITY_OVER_SHARED_DIAMOND_DEPENDENCIES',
        reserved_requirement='Future task compares two prior Unit-valued bindings reached through a shared diamond dependency graph.',
        completed_evaluation_solutions=0, withholding='DESCRIPTION_ONLY_NO_ENFORCEABLE_CUSTODY',
        limitation='Same repository and coordinator; future producer access is not enforceably excluded. No independent evaluation qualification.'))
    files = [p for p in OUT.rglob('*') if p.is_file()]
    files += [Path(__file__)]
    write(OUT / 'SOURCE-FREEZE.json', dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(files)},
          expert_actions_exist=False, candidate_execution=0))
    print('PASS baseline and ten preconstruction source/before/acceptance freezes')


if __name__ == '__main__':
    freeze()
