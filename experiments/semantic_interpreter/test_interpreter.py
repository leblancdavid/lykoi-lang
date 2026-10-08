"""R6.10 synthetic conformance expectations from frozen R6.6 witnesses."""
import copy
import json
from pathlib import Path
import sys
import unittest

from interpreter import Cell, Machine, Rejection, DEFAULT_LIMITS, execute, validate
import build_plans as b

HERE = Path(__file__).resolve().parent
PLANS = {f: json.loads((HERE / f'{f}.plan.json').read_text(encoding='utf-8')) for f in ('CFG66','DSV66','BXC66')}
ONE = bytes.fromhex('52 36 36 43 01 01 01 61 00 02 FF 00 00 02 00 10')
ZERO = bytes.fromhex('52 36 36 43 01 00 00 08')
b.counter = 1000  # Mutated test plans use fresh IDs beyond frozen plan IDs.


class Formats(unittest.TestCase):
    def test_cfg_witness(self):
        r = execute(PLANS['CFG66'], b'title="a\\n\\"b"\ncount=007\nenabled=true\nnote=none\n')
        self.assertEqual(r['status'],'success',r)
        self.assertEqual(r['value'],[
            {'name':'title','value':{'kind':'text','present':True,'text':'a\n"b'}},
            {'name':'count','value':{'kind':'integer','present':True,'integer':7}},
            {'name':'enabled','value':{'kind':'boolean','present':True,'boolean':True}},
            {'name':'note','value':{'kind':'absent','present':False}}])
        self.assertEqual(r['output'],b'title="a\\n\\"b"\ncount=7\nenabled=true\nnote=none\n')

    def test_optional_empty_and_false(self):
        r = execute(PLANS['CFG66'],b'a=none\nb=""\nc=false\n')
        self.assertEqual(r['status'],'success',r)
        self.assertFalse(r['value'][0]['value']['present'])
        self.assertEqual(r['value'][1]['value']['text'],'')
        self.assertIs(r['value'][2]['value']['boolean'],False)

    def test_cfg_span(self):
        r = execute(PLANS['CFG66'],b'x  =  "a"  \n')
        self.assertEqual(r['status'],'success',r)
        self.assertEqual(r['provenance']['items'][0]['span'],[0,9])
        self.assertEqual(r['provenance']['items'][0]['fields']['value']['fields']['text']['origins'],[7])

    def test_dsv_witness(self):
        r = execute(PLANS['DSV66'],b'k1,"a,b",007\nk2,"say ""hi""",0\n')
        self.assertEqual(r['status'],'success',r)
        self.assertEqual(r['value'],[{'key':'k1','label':'a,b','quantity':7},{'key':'k2','label':'say "hi"','quantity':0}])
        self.assertEqual(r['output'],b'"k1","a,b",7\n"k2","say ""hi""",0\n')

    def test_dsv_provenance(self):
        r = execute(PLANS['DSV66'],b'"a","say ""hi""","007"\n')
        self.assertEqual(r['status'],'success',r)
        label = r['provenance']['items'][0]['fields']['label']
        self.assertEqual(label['origins'],[5,6,7,8,9,11,12,13])
        self.assertEqual(r['value'][0]['quantity'],7)

    def test_bxc_witness(self):
        r = execute(PLANS['BXC66'],ONE)
        self.assertEqual(r['status'],'success',r)
        self.assertEqual(r['value'],[{'name':'a','content':b'\xff\0','declared_length':2}])
        self.assertEqual(r['output'],ONE)

    def test_bxc_nested_opaque(self):
        data = b'R66C\1\1\1a'+bytes([0,len(ZERO)])+ZERO+bytes([0,len(ZERO)])+b'\0\26'
        r = execute(PLANS['BXC66'],data)
        self.assertEqual(r['status'],'success',r)
        self.assertEqual(r['value'][0]['content'],ZERO)

    def test_same_length_tamper_accepted(self):
        data = ONE[:10]+b'\xfe'+ONE[11:]
        self.assertEqual(execute(PLANS['BXC66'],data)['status'],'success')

    def test_dsv_nested_looking_literal(self):
        self.assertEqual(execute(PLANS['DSV66'],b'a,"[{}]",1\n')['value'][0]['label'],'[{}]')

    def test_roundtrip_and_determinism(self):
        samples = [('CFG66',b'x = 007 \ny="\\n"\n'),('DSV66',b'a,b,"007"\n'),('BXC66',ONE)]
        for fmt,data in samples:
            r = execute(PLANS[fmt],data)
            self.assertEqual(r['status'],'success',r)
            for _ in range(5): self.assertEqual(execute(PLANS[fmt],data),r)
            canonical = execute(PLANS[fmt],r['output'])
            self.assertEqual(canonical['value'],r['value'])
            self.assertEqual(canonical['output'],r['output'])

    def test_all_truncations(self):
        for fmt,data in [('CFG66',b'x="abc"\n'),('DSV66',b'a,b,1\n'),('BXC66',ONE)]:
            for k in range(1,len(data)):
                r = execute(PLANS[fmt],data[:k])
                self.assertEqual(r['status'],'reject',(fmt,k,r))
                self.assertEqual(r['error']['offset'],k,(fmt,k,r))

    def test_private_failure(self):
        r = execute(PLANS['CFG66'],b'a=1\na=2\n')
        self.assertEqual(set(r),{'status','error','work'})

    def test_low_work_every_boundary(self):
        for fmt,data in [('CFG66',b'x=1\n'),('DSV66',b'a,b,1\n'),('BXC66',ONE)]:
            full = execute(PLANS[fmt],data)
            for work in range(full['work']):
                r = execute(PLANS[fmt],data,{'work':work})
                self.assertEqual(r['error']['code'],'WORK_LIMIT',(fmt,work,r))
                self.assertEqual(r['work'],work)
                self.assertEqual(execute(PLANS[fmt],data,{'work':work}),r)
            self.assertEqual(execute(PLANS[fmt],data,{'work':full['work']}),full)

    def test_ordered_conflicting_checks(self):
        for fmt,data in [('CFG66',b''),('DSV66',b''),('BXC66',ZERO)]:
            p = copy.deepcopy(PLANS[fmt])
            p['decode']['steps'].extend([b.step(b.check(b.const(False),'FIRST',b.ref('rows'))),b.step(b.check(b.const(False),'SECOND',b.ref('rows')))])
            self.assertEqual(execute(p,data)['error']['code'],'FIRST')

    def test_fixed_depth_generic_plan(self):
        inner = b.seq([b.step(b.lit('[')),b.step(b.lit('a'),'leaf'),b.step(b.lit(']'))],b.record(leaf=b.ref('leaf')))
        outer = b.seq([b.step(b.lit('{')),b.step(inner,'inner'),b.step(b.lit('}')),b.step(b.end())],b.record(inner=b.ref('inner')))
        p = dict(version='semantic-plan-1',text=True,rules={},decode=outer,encode=b.emit('ascii',b.const('{[a]}')))
        self.assertEqual(execute(p,b'{[a]}')['value'],{'inner':{'leaf':b'a'}})
        self.assertEqual(execute(p,b'{[a]}',{'depth':2})['error']['code'],'DEPTH_LIMIT')

    def test_dsv_select_increment_witness(self):
        p=copy.deepcopy(PLANS['DSV66'])
        p['decode']['steps'].append(b.step(b.node('select',source=b.ref('checked'),test=b.expr('le',b.const(1),b.ref('item.quantity'))),'selected'))
        transform=b.seq([b.step(b.check(b.expr('le',b.ref('item.quantity'),b.const(999)),'PRECONDITION',b.ref('item.quantity')))],b.record(key=b.ref('item.key'),label=b.ref('item.label'),quantity=b.expr('add',b.ref('item.quantity'),b.const(1))))
        p['decode']['steps'].append(b.step(b.node('map',source=b.ref('selected'),body=transform),'transformed'))
        p['decode']['result']=b.ref('transformed')
        r=execute(p,b'k1,"a,b",007\nk2,"say ""hi""",0\n')
        self.assertEqual(r['status'],'success',r)
        self.assertEqual(r['output'],b'"k1","a,b",8\n')

    def test_bxc_select_empty_witness(self):
        p=copy.deepcopy(PLANS['BXC66'])
        p['decode']['steps'].append(b.step(b.node('select',source=b.ref('rows'),test=b.const(False)),'selected'))
        p['decode']['result']=b.ref('selected')
        self.assertEqual(execute(p,ONE)['output'],ZERO)


CASES = [
 ('cfg_empty','CFG66',b'',None,None),('dsv_empty','DSV66',b'',None,None),('bxc_empty','BXC66',b'','TRUNCATED',0),('bxc_zero','BXC66',ZERO,None,None),
 ('cfg_value','CFG66',b'x=\n','VALUE',2),('cfg_escape','CFG66',b'x="\\q"\n','ESCAPE',3),('cfg_truncated','CFG66',b'x=1','TRUNCATED',3),
 ('cfg_duplicate','CFG66',b'x=1\nx=2\n','DUPLICATE',4),('cfg_nested','CFG66',b'x={}\n','VALUE',2),('cfg_overflow','CFG66',b'x=32768\n','OVERFLOW',6),
 ('cfg_bad_encoding_precedence','CFG66',b'=\xff','ENCODING',1),('cfg_tab','CFG66',b'x\t=1\n','NAME',1),('cfg_cr','CFG66',b'x=1\r\n','DECIMAL',3),
 ('cfg_keyword_boundary','CFG66',b'x=truex\n','VALUE',6),('cfg_ninth','CFG66',b''.join(f'a{i}=1\n'.encode() for i in range(9)),'OCCURRENCE_LIMIT',40),
 ('cfg_overflow_before_bad_suffix','CFG66',b'x=32768z\n','OVERFLOW',6),
 ('cfg_name_bound','CFG66',b'a'*33+b'=1\n','BOUND',32),('cfg_text_bound','CFG66',b'x="'+b'a'*257+b'"\n','BOUND',259),
 ('dsv_truncated','DSV66',b'a,b,1','TRUNCATED',5),('dsv_empty_quantity','DSV66',b'a,b,\n','DECIMAL',4),('dsv_bad_close','DSV66',b'a,"b"x,1\n','SYNTAX',5),
 ('dsv_bad_encoding','DSV66',b'a,"\xff",1\n','ENCODING',3),('dsv_duplicate','DSV66',b'a,b,1\na,c,2\n','DUPLICATE',6),
 ('dsv_syntax_before_semantic','DSV66',b',b,1\na,"b"x,1\n','SYNTAX',10),('dsv_conversion_before_key','DSV66',b',b,32768\n','OVERFLOW',7),
 ('dsv_provenance_decimal','DSV66',b'a,b,"32""7"\n','DECIMAL',7),('dsv_quantity_limit','DSV66',b'a,b,1001\n','QUANTITY',4),
 ('dsv_duplicate_before_later_empty','DSV66',b'a,b,1\na,b,1\n,b,1\n','DUPLICATE',6),('dsv_duplicate_before_quantity','DSV66',b'a,b,1\na,b,1001\n','DUPLICATE',6),
 ('bxc_total','BXC66',ONE[:-1]+b'\x11','TOTAL_LENGTH',14),('bxc_echo','BXC66',ONE[:13]+b'\x03'+ONE[14:],'LENGTH_ECHO',12),
 ('bxc_truncated','BXC66',ONE[:-1],'TRUNCATED',15),('bxc_version','BXC66',ONE[:4]+b'\x02'+ONE[5:],'VERSION',4),
 ('bxc_count','BXC66',b'R66C\1\x09','BOUND',5),('bxc_zero_name','BXC66',b'R66C\1\1\0','BOUND',6),
 ('bxc_bad_name','BXC66',ONE[:7]+b'\xff'+ONE[8:],'NAME',7),('bxc_length_before_truncation','BXC66',ONE[:8]+b'\x04\x01','BOUND',8),
 ('bxc_name_before_truncation','BXC66',b'R66C\1\1\2/','NAME',7),
 ('bxc_trailing','BXC66',ONE+b'x','TRAILING',16),
 ('bxc_duplicate','BXC66',b'R66C\1\2'+b'\1a\0\0\0\0'*2+b'\0\24','DUPLICATE',13),
]


def case_test(fmt, data, code, offset):
    def test(self):
        r = execute(PLANS[fmt],data)
        if code is None:
            self.assertEqual(r['status'],'success',r)
        else:
            self.assertEqual(r['status'],'reject',r)
            self.assertEqual((r['error']['code'],r['error']['offset']),(code,offset),r)
            self.assertEqual(execute(PLANS[fmt],data),r)
    return test


for name,fmt,data,code,offset in CASES:
    setattr(Formats,'test_'+name,case_test(fmt,data,code,offset))


class PlanValidation(unittest.TestCase):
    def test_plan_node_bounds(self):
        self.assertEqual([validate(PLANS[n]) for n in ('CFG66','DSV66','BXC66')],[53,39,31])

    def refuse(self, p): self.assertEqual(execute(p,b'')['status'],'plan_reject')

    def test_unknown_operation(self):
        p = copy.deepcopy(PLANS['CFG66']); p['decode']['op']='eval'; self.refuse(p)
    def test_unknown_codec(self):
        p = copy.deepcopy(PLANS['BXC66']); p['decode']['steps'][1]['node']['codec']='zip'; self.refuse(p)
    def test_undeclared_dependency(self):
        p = copy.deepcopy(PLANS['CFG66']); p['decode']['result']=b.ref('future'); self.refuse(p)
    def test_shadowing(self):
        p = copy.deepcopy(PLANS['CFG66']); p['decode']['steps'][1]['bind']='rows'; self.refuse(p)
    def test_empty_repeat(self):
        p = copy.deepcopy(PLANS['CFG66']); p['decode']['steps'][0]['node']['body']=b.lit(''); self.refuse(p)
    def test_cycle(self):
        p = copy.deepcopy(PLANS['CFG66']); p['rules']['string']=b.call('string'); self.refuse(p)
    def test_ambiguous_prefix(self):
        p = copy.deepcopy(PLANS['CFG66']); p['decode']=b.choice([([97],b.lit('a')),([97],b.lit('ab'))],'VALUE'); self.refuse(p)
    def test_prefix_overlap(self):
        p = copy.deepcopy(PLANS['CFG66']); p['decode']=b.node('choice',branches=[{'prefixes':[[97],[97,98]],'node':b.lit('a')}],code='VALUE'); self.refuse(p)
    def test_filesystem_callback(self):
        p = copy.deepcopy(PLANS['CFG66']); p['decode']['destination']='outside'; self.refuse(p)
    def test_script_expression(self):
        p = copy.deepcopy(PLANS['CFG66']); p['decode']['result']={'python':'__import__("os")'}; self.refuse(p)
    def test_malformed_and_limits(self):
        for p in (None,{}, {'version':2},PLANS['CFG66'] | {'provider':'x'}): self.refuse(p)
        for limits in ({'work':-1},{'depth':True},{'network':1}):
            self.assertEqual(execute(PLANS['CFG66'],b'',limits)['status'],'plan_reject')
    def test_input_limit_before_encoding(self):
        r=execute(PLANS['CFG66'],b'\xff'*4097)
        self.assertEqual((r['error']['code'],r['error']['offset']),('INPUT_LIMIT',4096))
    def test_output_limit_private(self):
        r=execute(PLANS['BXC66'],ONE,{'output':15})
        self.assertEqual(r['error']['code'],'OUTPUT_LIMIT'); self.assertNotIn('output',r)
    def test_oversized_plan(self):
        p=copy.deepcopy(PLANS['CFG66'])
        p['decode']['steps'].extend(b.step(b.lit('')) for _ in range(65))
        self.refuse(p)
    def test_missing_result_dependency(self):
        p=copy.deepcopy(PLANS['DSV66']); p['decode']['result']=b.ref('undeclared.quantity'); self.refuse(p)
    def test_work_precedes_depth(self):
        r=execute(PLANS['BXC66'],ZERO,{'work':0,'depth':0})
        self.assertEqual(r['error']['code'],'WORK_LIMIT')
    def test_occurrence_limit_declared(self):
        for fmt,data in [('CFG66',b'a=1\nb=2\n'),('DSV66',b'a,b,1\nc,d,2\n')]:
            r=execute(PLANS[fmt],data,{'occurrences':1})
            self.assertEqual(r['error']['code'],'OCCURRENCE_LIMIT')


class AtomicAndReuse(unittest.TestCase):
    def test_all_uint16_values(self):
        for v in range(65536):
            m=Machine(b'',DEFAULT_LIMITS)
            encoded=m.encode('uint16be',Cell(v,0,0),{})
            self.assertEqual(m.decode('uint16be',Cell(encoded,0,2)).value,v)
    def test_ascii_all_values(self):
        m=Machine(b'',DEFAULT_LIMITS)
        a=bytes(range(128)); c=m.decode('ascii',Cell(a,0,128,tuple(range(128))))
        self.assertEqual(m.encode('ascii',c,{}),a)
    def test_decimal_boundaries(self):
        for v in (0,1,7,999,1000,32767):
            m=Machine(b'',DEFAULT_LIMITS)
            a=m.encode('decimal15',Cell(v,0,0),{})
            self.assertEqual(m.decode('decimal15',Cell(a,0,len(a))).value,v)
    def test_wrong_atomic_types_ranges(self):
        for c,v in [('uint8',256),('uint8',True),('uint16be',-1),('decimal15',32768),('ascii','é'),('bytes','x')]:
            with self.assertRaises(Rejection): Machine(b'',DEFAULT_LIMITS).encode(c,Cell(v,0,0),{})
    def test_negative_take(self):
        p=dict(version='semantic-plan-1',text=False,rules={},decode=b.node('take',length=b.const(-1),max=32,code='BOUND'),encode=b.emit('bytes',b.ref('root')))
        self.assertEqual(execute(p,b'')['error']['code'],'BOUND')
    def test_kernel_predicate_correspondence(self):
        sys.path.insert(0,str(HERE.parents[1]/'src'))
        from air_compiler.predicate_runtime import predicate_eval
        for op in ('eq','le'):
            for a,z in [(0,0),(1,2),(32767,1),('a','b')]:
                typ={'type':'integer' if type(a) is int else 'string','domain':[]}
                tree=dict(kind='compare',operator=op,left=dict(kind='literal',value=a,type=typ),right=dict(kind='literal',value=z,type=typ),policy=dict(normalization='none',case='exact'))
                m=Machine(b'',DEFAULT_LIMITS)
                self.assertEqual(m.expr(b.expr(op,b.const(a),b.const(z)),{}).value,predicate_eval(tree))
    def test_k24_signed_add_and_overflow(self):
        m=Machine(b'',DEFAULT_LIMITS)
        for a,z in [(1,1),(-1,1),(2**63-2,1),(-2**63,0)]:
            self.assertEqual(m.expr(b.expr('add',b.const(a),b.const(z)),{}).value,a+z)
        with self.assertRaises(Rejection): m.expr(b.expr('add',b.const(2**63-1),b.const(1)),{})


if __name__=='__main__': unittest.main(verbosity=2)
