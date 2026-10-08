"""Small constructions on unchanged APIs, separate from scored R6.12 candidates."""
import copy
import sys

from audit import HERE, ROOT, load, now, save, sha, verify

sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'experiments/semantic_interpreter'))
from air_compiler import predicates, computation
from air_compiler.predicate_runtime import predicate_eval
from interpreter import execute, validate


def node(identity, op, **fields):
    return dict(id=identity, op=op, **fields)


def xor_lookup(size):
    # Explicit finite relation as prefixes grouped by result. This is plan data,
    # never a host callback. Neither VM nor production source is changed.
    choice = node('lookup', 'choice', code='DOMAIN', branches=[
        dict(prefixes=[[a,b] for a in range(size) for b in range(size) if a ^ b == result],
             node=node(f'value{result}', 'value', expr={'const':result}))
        for result in range(size)])
    return dict(version='semantic-plan-1',text=False,rules={},
        decode=node('decode','seq',steps=[dict(node=choice,bind='answer'),
            dict(node=node('consume','take',length={'const':2},max=2,code='BOUND')),
            dict(node=node('end','end'))],result={'ref':'answer'}),
        encode=node('emit','emit',codec='uint8',expr={'ref':'root'}))


def serial(value):
    if isinstance(value, bytes):
        return {'bytes_hex':value.hex()}
    if isinstance(value, dict):
        return {k:serial(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)):
        return [serial(v) for v in value]
    return value


def main():
    verify()
    started = now()
    string = dict(type='string',domain=[])
    eq = dict(kind='compare',result_type='boolean',operator='eq',
        left=dict(kind='parameter',type=string,name='old'),
        right=dict(kind='parameter',type=string,name='original_slice'),
        policy=dict(case='sensitive',normalization='none'),nulls='false')
    absent = dict(kind='not',result_type='boolean',child=eq)
    record_type = dict(type='record',fields={'sku':string,'qty':dict(type='integer',domain=[])})
    collection = dict(type='collection',element=record_type,ordering='insertion',duplicates='allow',equality='exact')
    direct_xor = dict(version='semantic-plan-1',text=False,rules={},
        decode=node('direct','value',expr={'xor':[{'const':1},{'const':2}]}),
        encode=node('emit','emit',codec='uint8',expr={'ref':'root'}))
    prefix_plan = dict(version='semantic-plan-1',text=False,rules={},
        decode=node('decode','seq',steps=[dict(bind='items',node=node('read','repeat',
            count={'const':3},max=3,stop=[],eof=False,occurrence_limit=True,
            body=node('byte','atom',codec='uint8'))),
            dict(bind='mapped',node=node('mapping','map',source={'ref':'items'},
                body=node('body','value',expr={'record':{'source':{'ref':'item'},
                    'increment':{'add':[{'ref':'item'},{'const':1}]},'prefix':{'ref':'prefix'}}}))),
            dict(node=node('end','end'))],result={'ref':'mapped'}),
        encode=node('emit','emit',codec='ascii',expr={'const':''}))
    direct_slice = copy.deepcopy(direct_xor)
    direct_slice['decode']['expr'] = {'slice':[{'const':'abc'},{'const':0},{'const':1}]}
    specifications = dict(version='r6.13-capability-probes-1',utc=started,
        scope='Partial interfaces only; no full-task acceptance credit',
        production_record_collection=collection,production_absent=absent,
        vm_nibble_xor=xor_lookup(16),vm_full_byte_lookup=xor_lookup(256),
        vm_direct_xor=direct_xor,vm_direct_slice=direct_slice,vm_prefix=prefix_plan)
    save(HERE/'PROBE-INPUTS.json',specifications)
    save(HERE/'PROBE-FREEZE.json',dict(utc=now(),files={name:sha(HERE/name) for name in ['probes.py','PROBE-INPUTS.json']},
        protected_baseline_sha256=sha(HERE/'BASELINE.json')))
    observations = []
    try:
        value = predicates.scalar_type(collection)
        observations.append(dict(id='B-record-collection',status='accepted',actual=value))
    except Exception as exc:
        observations.append(dict(id='B-record-collection',status='rejected',exception_type=type(exc).__name__,detail=str(exc)))
    predicates.validate(absent,parameters={'old':string,'original_slice':string})
    for old, original, expected in [('aa','bb',True),('aa','aa',False),('','',False)]:
        actual = predicate_eval(absent,inputs={'old':old,'original_slice':original})
        observations.append(dict(id='B-absent',input=dict(old=old,original_slice=original),actual=actual,
            expected=expected,passed=actual is expected,scope='Boolean subset on already supplied strings; byte slicing not supplied'))
    for op in ('xor','slice','permutations'):
        graph = dict(nodes=[dict(binding='result',operator=op,type=computation.INTEGER,
            operands=[],depends_on=[],error='BAD')],policy=computation.POLICY)
        try:
            actual = computation.validate(graph,{'row':{}},'row',{})
            observations.append(dict(id='B-direct-'+op,construction=graph,status='accepted',actual=actual))
        except Exception as exc:
            observations.append(dict(id='B-direct-'+op,construction=graph,status='rejected',exception_type=type(exc).__name__,detail=str(exc)))
    for name in ('vm_direct_xor','vm_direct_slice','vm_full_byte_lookup','vm_prefix'):
        plan = specifications[name]
        try:
            count = validate(plan)
            result = execute(plan,b'\x01\x02\x03' if name=='vm_prefix' else b'\0\1')
            observations.append(dict(id=name,structural_nodes=count,result=serial(result)))
        except Exception as exc:
            observations.append(dict(id=name,status='plan_reject',exception_type=type(exc).__name__,detail=str(exc)))
    plan = specifications['vm_nibble_xor']
    count = validate(plan)
    for a in range(16):
        for b in range(16):
            result = execute(plan,bytes([a,b]))
            expected = a ^ b
            observations.append(dict(id='C-nibble-XOR',input_hex=bytes([a,b]).hex(),expected=expected,
                passed=result.get('value')==expected and result.get('output')==bytes([expected]),
                structural_nodes=count,result=serial(result)))
    # Non-domain input demonstrates this construction is not a full byte codec.
    observations.append(dict(id='C-nibble-outside-domain',result=serial(execute(plan,b'\x10\x00'))))
    verify()
    save(HERE/'PROBE-RESULTS.json',dict(start_utc=started,completion_utc=now(),
         scope='New bounded semantic probes, NOT frozen-candidate full-task acceptance or authoring trials',
         observations=observations,inputs_sha256=sha(HERE/'PROBE-INPUTS.json')))
    print('Preserved bounded attempts: production record/direct-op rejection, absent predicate; VM finite XOR, direct ops, naive lookup and map prefix')


if __name__ == '__main__':
    main()
