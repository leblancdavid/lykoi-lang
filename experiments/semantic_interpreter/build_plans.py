"""Author explicit operation graphs; resulting JSON is the executable source.

This module is a plan authoring convenience, never imported by the VM.
"""
import json
from pathlib import Path
from interpreter import validate, FIELDS, REQUIRED, EXPRS

HERE = Path(__file__).resolve().parent
counter = 0


def node(op, **kw):
    global counter
    counter += 1
    return dict(id=f'n{counter:03}', op=op, **kw)


def ref(s): return {'ref': s}
def const(v): return {'const': v}
def expr(op, *a): return {op: a[0] if len(a) == 1 else list(a)}
def dec(c, x): return {'decode': [c, x]}
def record(**kw): return {'record': kw}
def step(n, bind=None): return dict(node=n, **({'bind': bind} if bind else {}))
def seq(steps, result): return node('seq', steps=steps, result=result)
def lit(s, value=None, code=None):
    return node('literal', bytes=list(s.encode('ascii')), **({'value': const(value)} if value is not None else {}), **({'code': code} if code else {}))
def emit(c, x, escapes=None): return node('emit', codec=c, expr=x, **({'escapes': escapes} if escapes else {}))
def out(s): return emit('ascii', const(s))
def scan(first, rest=None, stop=(), minimum=0, maximum=256, eof=False, code='SYNTAX'):
    return node('scan', first=sorted(first), rest=sorted(first if rest is None else rest), stop=sorted(stop), min=minimum, max=maximum, eof=eof, code=code)
def check(test, code, site): return node('check', test=test, code=code, site=site)
def repeat(body, stop=(), eof=True, maximum=8, count=None):
    return node('repeat', body=body, stop=[list(p) for p in stop], eof=eof, max=maximum, occurrence_limit=maximum<=8, **({'count': count} if count is not None else {}))
def choice(branches, code): return node('choice', branches=[dict(prefixes=[[b] for b in bs], node=n) for bs, n in branches], code=code)
def spaces(): return scan([32], stop=set(range(256)) - {32}, maximum=4096, eof=True)
def call(name): return node('call', rule=name)
def end(): return node('end')
def unique(source, field): return node('unique', source=source, field=field, code='DUPLICATE')


def cfg():
    plain = set(range(32, 127)) - {34, 92}
    escape = choice([([34], lit('"', '"')), ([92], lit('\\', '\\')), ([110], lit('n', '\n'))], 'ESCAPE')
    # The initiating backslash, not its successor, is the error site.
    escaped = seq([step(lit('\\')), step(escape, 'char')], ref('char'))
    escaped['rebase_errors'] = ['ESCAPE']
    chunks = repeat(choice([([92], escaped), (plain, scan(plain, stop=[34,92], minimum=1))], 'STRING'), stop=[b'"'], eof=False, maximum=256)
    string = seq([step(lit('"')), step(chunks, 'chunks'), step(lit('"'))], expr('join', ref('chunks')))
    integer = node('value', expr=ref('digits'))
    digits = scan(range(48,58), stop=[32,10], minimum=1, maximum=4096, code='DECIMAL')
    digits['codec'] = 'decimal15'
    number = seq([step(digits, 'digits'), step(integer, 'number')], record(kind=const('integer'), present=const(True), integer=ref('number')))
    text = seq([step(call('string'), 'text')], record(kind=const('text'), present=const(True), text=ref('text')))
    keyword_nodes = []
    for word, kind, present, field, value in [('true','boolean',True,'boolean',True), ('false','boolean',True,'boolean',False), ('none','absent',False,None,None)]:
        # Empty scan enforces a keyword boundary without consuming it.
        boundary = scan([], stop=[32,10], maximum=0, code='VALUE')
        r = dict(kind=const(kind), present=const(present))
        if field: r[field] = const(value)
        keyword_nodes.append(([ord(word[0])], seq([step(lit(word)), step(boundary)], {'record': r})))
    value = choice([([34], text), (range(48,58), number)] + keyword_nodes, 'VALUE')
    assignment = seq([step(scan(range(97,123), set(range(97,123)) | set(range(48,58)) | {95}, [32,61], 1,32, code='NAME'), 'name'), step(spaces()), step(lit('=')), step(spaces()), step(value,'value'), step(spaces()), step(lit('\n'))], record(name=dec('ascii',ref('name')), value=ref('value')))
    assignment['span_end'] = ref('value')
    decode = seq([step(repeat(assignment), 'rows'), step(end()), step(unique(ref('rows'),'name'))], ref('rows'))
    tags = {
        'text': seq([step(out('"')), step(emit('ascii',ref('item.value.text'), {'"':'\\"','\\':'\\\\','\n':'\\n'})), step(out('"'))], const(None)),
        'integer': emit('decimal15',ref('item.value.integer')),
        'boolean': node('dispatch',expr=ref('item.value.boolean'),branches={'True':out('true'),'False':out('false')}),
        'absent': out('none')}
    layout = seq([step(emit('ascii',ref('item.name'))),step(out('=')),step(node('dispatch',expr=ref('item.value.kind'),branches=tags)),step(out('\n'))],const(None))
    encode = node('each',source=ref('root'),body=layout)
    return dict(version='semantic-plan-1',text=True,rules={'string':string},decode=decode,encode=encode)


def dsv():
    qplain = set(range(32,127)) - {34}
    escaped = lit('""','"')
    quoted = seq([step(lit('"')),step(repeat(choice([([34],escaped),(qplain,scan(qplain,stop=[34],minimum=1))],'FIELD'),stop=[b'",',b'"\n'],eof=False,maximum=256),'chunks'),step(lit('"'))],expr('join',ref('chunks')))
    unplain = set(range(32,127)) - {34,44}
    unquoted = seq([step(scan(unplain,stop=[44,10],minimum=0),'raw')],dec('ascii',ref('raw')))
    field = choice([([34],quoted),(unplain | {44,10},unquoted)],'FIELD')
    row = seq([step(call('field'),'key'),step(lit(',')),step(call('field'),'label'),step(lit(',')),step(call('field'),'quantity'),step(lit('\n'))],record(key=ref('key'),label=ref('label'),quantity=ref('quantity')))
    converted = seq([step(node('value',expr=dec('decimal15',ref('item.quantity'))),'quantity')],record(key=ref('item.key'),label=ref('item.label'),quantity=ref('quantity')))
    checks = seq([step(check(expr('nonempty',ref('item.key')),'KEY',ref('item.key'))),step(unique(ref('prefix'),'key')),step(check(expr('le',expr('length',ref('item.key')),const(32)),'BOUND',ref('item.key'))),step(check(expr('le',expr('length',ref('item.label')),const(256)),'BOUND',ref('item.label'))),step(check(expr('le',ref('item.quantity'),const(1000)),'QUANTITY',ref('item.quantity')))],ref('item'))
    decode = seq([step(repeat(row),'rawrows'),step(end()),step(node('map',source=ref('rawrows'),body=converted),'rows'),step(node('map',source=ref('rows'),body=checks),'checked')],ref('checked'))
    layout = seq([step(out('"')),step(emit('ascii',ref('item.key'),{'"':'""'})),step(out('","')),step(emit('ascii',ref('item.label'),{'"':'""'})),step(out('",')),step(emit('decimal15',ref('item.quantity'))),step(out('\n'))],const(None))
    return dict(version='semantic-plan-1',text=True,rules={'field':field},decode=decode,encode=node('each',source=ref('root'),body=layout))


def bxc():
    namebytes = set(range(97,123)) | set(range(48,58)) | {95}
    # Dynamic raw access includes an explicit per-byte membership precondition.
    entry = seq([step(node('atom',codec='uint8'),'nl'),step(check(expr('le',const(1),ref('nl')),'BOUND',ref('nl'))),step(check(expr('le',ref('nl'),const(32)),'BOUND',ref('nl'))),step(node('take',length=ref('nl'),max=32,code='NAME'),'name'),step(node('atom',codec='uint16be'),'cl'),step(node('take',length=ref('cl'),max=1024,code='BOUND'),'content'),step(node('atom',codec='uint16be'),'echo'),step(check(expr('eq',ref('cl'),ref('echo')),'LENGTH_ECHO',ref('echo')))],record(name=dec('ascii',ref('name')),content=ref('content'),declared_length=ref('cl')))
    # Finite membership on supplied name bytes is declared explicitly.
    entry['steps'][3]['node']['allowed'] = sorted(namebytes)
    decode = seq([step(lit('R66C',code='HEADER')),step(node('atom',codec='uint8'),'version'),step(check(expr('eq',ref('version'),const(1)),'VERSION',ref('version'))),step(node('atom',codec='uint8'),'count'),step(repeat(entry,count=ref('count')),'rows'),step(node('atom',codec='uint16be'),'total'),step(end()),step(check(expr('eq',ref('total'),{'input_length':None}),'TOTAL_LENGTH',ref('total'))),step(unique(ref('rows'),'name'))],ref('rows'))
    layout = seq([step(emit('uint8',expr('length',ref('item.name')))),step(emit('ascii',ref('item.name'))),step(emit('uint16be',expr('length',ref('item.content')))),step(emit('bytes',ref('item.content'))),step(emit('uint16be',expr('length',ref('item.content'))))],const(None))
    encode = seq([step(out('R66C')),step(emit('uint8',const(1))),step(emit('uint8',expr('length',ref('root')))),step(node('each',source=ref('root'),body=layout)),step(emit('uint16be',expr('add',{'output_length':None},const(2))))],const(None))
    return dict(version='semantic-plan-1',text=False,rules={},decode=decode,encode=encode)


if __name__ == '__main__':
    for name, make in [('CFG66',cfg),('DSV66',dsv),('BXC66',bxc)]:
        counter = 0
        p = make()
        print(name, validate(p), 'structural nodes')
        (HERE / f'{name}.plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    # JSON Schema closes operation and expression vocabulary. Cross-reference,
    # progress and dominance obligations are enforced by validate().
    definitions = {}
    for op, fields in FIELDS.items():
        props = {'id':{'type':'string','minLength':1},'op':{'const':op}}
        props.update({f:{} for f in fields})
        definitions[op] = {'type':'object','required':['id','op']+sorted(REQUIRED[op]),'additionalProperties':False,'properties':props}
        for field in ('expr','result','source','site','test','length','count','span_end','value'):
            if field in props: props[field] = {'$ref':'#/$defs/expression'}
        for field in ('body',):
            if field in props: props[field] = {'$ref':'#/$defs/node'}
        for field in ('max','min'):
            if field in props: props[field] = {'type':'integer','minimum':0,'maximum':4096}
        for field in ('first','rest','allowed','bytes'):
            if field in props: props[field] = {'type':'array','maxItems':4096 if field=='bytes' else 256,'items':{'type':'integer','minimum':0,'maximum':255}}
        if 'eof' in props: props['eof']={'type':'boolean'}
        if 'occurrence_limit' in props: props['occurrence_limit']={'type':'boolean'}
        if 'codec' in props: props['codec']={'enum': ['uint8','uint16be'] if op=='atom' else ['decimal15'] if op=='scan' else ['ascii','bytes','decimal15','uint8','uint16be']}
        if 'code' in props: props['code']={'type':'string','minLength':1}
        if 'rule' in props: props['rule']={'type':'string','minLength':1}
        if 'field' in props: props['field']={'type':'string','minLength':1}
        if 'steps' in props: props['steps']={'type':'array','maxItems':64,'items':{'type':'object','required':['node'],'additionalProperties':False,'properties':{'node':{'$ref':'#/$defs/node'},'bind':{'type':'string','pattern':'^[A-Za-z_][A-Za-z0-9_]*$'}}}}
        prefix={'type':'array','minItems':1,'maxItems':8,'items':{'type':'integer','minimum':0,'maximum':255}}
        if 'stop' in props: props['stop'] = {'type':'array','items':prefix if op=='repeat' else {'type':'integer','minimum':0,'maximum':255}}
        if op=='choice': props['branches']={'type':'array','minItems':1,'maxItems':256,'items':{'type':'object','required':['prefixes','node'],'additionalProperties':False,'properties':{'prefixes':{'type':'array','items':prefix},'node':{'$ref':'#/$defs/node'}}}}
        if op=='dispatch': props['branches']={'type':'object','minProperties':1,'additionalProperties':{'$ref':'#/$defs/node'}}
        if 'escapes' in props: props['escapes']={'type':'object','additionalProperties':{'type':'string'}}
        if 'rebase_errors' in props: props['rebase_errors']={'type':'array','items':{'type':'string'}}
    schema = {'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:lykoi:experiment:semantic-plan:1','title':'R6.10 semantic plan 1','type':'object','additionalProperties':False,'required':['version','text','rules','decode','encode'],'properties':{'version':{'const':'semantic-plan-1'},'text':{'type':'boolean'},'rules':{'type':'object','additionalProperties':{'$ref':'#/$defs/node'}},'decode':{'$ref':'#/$defs/node'},'encode':{'$ref':'#/$defs/node'}},'$defs':definitions}
    schema['$defs']['node'] = {'oneOf':[{'$ref':f'#/$defs/{op}'} for op in FIELDS]}
    forms=[]
    for op,arity in EXPRS.items():
        if op=='ref': arg={'type':'string','maxLength':256}
        elif op=='const': arg={'type':['null','string','integer','boolean']}
        elif op=='record': arg={'type':'object','additionalProperties':{'$ref':'#/$defs/expression'}}
        elif op=='decode': arg={'type':'array','prefixItems':[{'enum':['ascii','bytes','decimal15','uint8','uint16be']},{'$ref':'#/$defs/expression'}],'minItems':2,'maxItems':2}
        elif arity==0: arg={'type':'null'}
        elif arity==1: arg={'$ref':'#/$defs/expression'}
        else: arg={'type':'array','minItems':arity,'maxItems':arity,'items':{'$ref':'#/$defs/expression'}}
        forms.append({'type':'object','required':[op],'additionalProperties':False,'properties':{op:arg}})
    schema['$defs']['expression']={'oneOf':forms}
    (HERE / 'semantic-plan-1.schema.json').write_text(json.dumps(schema,indent=2)+'\n',encoding='utf-8')
