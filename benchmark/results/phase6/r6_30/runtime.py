"""Conventional standard-library host envelope and development helpers for A/B."""
MIN, MAX = -(2**63), 2**63-1

class Rejection(Exception):
    def __init__(self, code, stage, step=None):
        self.code,self.stage,self.step=code,stage,step

def add(a,b,step):
    v=a+b
    if not MIN<=v<=MAX:
        raise Rejection('OVERFLOW','structure',step)
    return v

def check(predicate,code,step):
    if not predicate:
        raise Rejection(code,'validation',step)

def host(args,signature):
    if type(args) is not dict or set(args)!=set(signature):
        raise Rejection('SHAPE',None)
    if any(type(v) not in (int,bool,str,type(None)) for v in args.values()):
        raise Rejection('SHAPE',None)
    for name,kind in signature.items():
        v=args[name]
        if (kind=='Int64' and (type(v) is not int or not MIN<=v<=MAX)) or (kind=='Bool' and type(v) is not bool):
            raise Rejection('TYPE',None)
    return args

def execute(fn,args,signature):
    try:
        v=fn(host(args,signature))
        if type(v) is not int or not 0<=v<=65535:
            raise Rejection('ENCODE_RANGE','encode')
        return dict(status='success',value=v,output_hex=v.to_bytes(2,'big').hex(),consumed=0)
    except Rejection as e:
        return dict(status='wrapper_reject' if e.stage is None else 'reject',code=e.code,stage=e.stage,step=e.step)

def generate(intent):
    """Lean Python expression/ordered-statement generator; no Lykoi validation."""
    lines=['def compute(v):']
    for name in intent['inputs']:
        if not name.isidentifier():
            raise ValueError('invalid Python identifier')
        lines.append('    '+name+' = v['+repr(name)+']')
    for stmt in intent['statements']:
        if stmt['kind']=='assign':
            if not stmt['name'].isidentifier():
                raise ValueError('invalid Python identifier')
            lines.append('    '+stmt['name']+' = '+stmt['expression'])
        elif stmt['kind']=='check':
            lines.append('    check('+stmt['expression']+', '+repr(stmt['code'])+', '+repr(stmt['step'])+')')
        else:
            raise ValueError('unknown statement kind')
    lines.append('    return '+intent['result'])
    return '\n'.join(lines)+'\n'
