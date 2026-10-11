"""Fresh coordinator-authored diagnostic; literal fixtures are not model-derived."""
def specifications(f):
    state, fixture = f.data.state, f.data.fixture
    r = lambda n: {'ref': n}
    k = lambda v: {'const': v}
    def action(op, args, typ):
        return dict(id='selected', type=typ, deps=sorted({a['ref'] for a in args if 'ref' in a}),
                    node=dict(op='value', expr={op: args}))
    prefix = [dict(id='adjusted', type='Int64', deps=['raw'], node=dict(op='value', expr={'add':[r('raw'),k(-3)]})),
              dict(id='echo', type='Int64', deps=['raw'], node=dict(op='value', expr=r('raw')))]
    # Each tuple: id, immutable scope, requirement, expected action, explicit fixtures.
    return [
      ('S01', state('BindingLiteralPair',[('backup','Int64'),('ok','Bool')],[-9,14,False],'Int64'),
       'Combine fixed negative nine with fixed fourteen, in that order, to obtain their total. Neither stored field contributes.',
       action('add',[k(-9),k(14)],'Int64'),[fixture(dict(backup=14,ok=True),5),fixture(dict(backup=-9,ok=False),5)]),
      ('S02', state('BindingSpare',[('ready','Bool'),('credit','Int64'),('spares','Int64')],[8,True],'Int64'),
       'The total consists of eight fixed units followed by stored credit. spares is an unrelated stock; ready is not a number.',
       action('add',[k(8),r('credit')],'Int64'),[fixture(dict(ready=True,credit=-10,spares=8),-2),fixture(dict(ready=False,credit=4,spares=-10),12)]),
      ('S03', state('BindingRepeated',[('shadow','Int64'),('raw','Int64')],[-3],'Int64',prefix),
       'Total two copies of the previously adjusted quantity. Use adjusted for both slots, not echo, raw or shadow. Declare each direct dependency only once.',
       action('add',[r('adjusted'),r('adjusted')],'Int64'),[fixture(dict(shadow=100,raw=5),4),fixture(dict(shadow=-20,raw=-2),-10)]),
      ('S04', state('BindingSpareReworded',[('spares','Int64'),('credit','Int64'),('ready','Bool')],[True,8],'Int64'),
       'Compute the sum with literal eight as its first operand and credit as its second. Disregard ready and spares.',
       action('add',[k(8),r('credit')],'Int64'),[fixture(dict(ready=True,credit=-10,spares=8),-2),fixture(dict(ready=False,credit=4,spares=-10),12)]),
      ('S05', state('BindingReversed',[('ceiling','Int64'),('observed','Int64'),('enabled','Bool')],[],'Bool'),
       'Is the ceiling not greater than the observed quantity? Return that inclusive comparison with ceiling first and observed second; enabled is irrelevant.',
       action('le',[r('ceiling'),r('observed')],'Bool'),[fixture(dict(ceiling=7,observed=2,enabled=True),False),fixture(dict(ceiling=2,observed=7,enabled=False),True),fixture(dict(ceiling=2,observed=2,enabled=True),True)]),
      ('S06', state('BindingLowerLiteral',[('decoy','Int64'),('reading','Int64')],[-6,0],'Bool'),
       'The reading must be at least negative six. Encode the test as negative six on the left and reading on the right; do not test decoy.',
       action('le',[k(-6),r('reading')],'Bool'),[fixture(dict(decoy=0,reading=-7),False),fixture(dict(decoy=-7,reading=-6),True),fixture(dict(decoy=90,reading=3),True)]),
      ('S07', state('BindingPriorBound',[('raw','Int64'),('shadow','Int64')],[-3],'Bool',prefix),
       'Check that echo is at most adjusted, in that order. Only the two prior-result identities are direct operands; the source raw is indirect.',
       action('le',[r('echo'),r('adjusted')],'Bool'),[fixture(dict(raw=5,shadow=1),False),fixture(dict(raw=-2,shadow=100),False)]),
      ('S08', state('BindingReversedReworded',[('enabled','Bool'),('observed','Int64'),('ceiling','Int64')],[],'Bool'),
       'Determine whether observed is at least ceiling. Express this using ceiling as the first operand and observed as the second, including equality.',
       action('le',[r('ceiling'),r('observed')],'Bool'),[fixture(dict(ceiling=7,observed=2,enabled=True),False),fixture(dict(ceiling=2,observed=7,enabled=False),True),fixture(dict(ceiling=2,observed=2,enabled=True),True)]),
      ('S09', state('BindingFalseEquality',[('count','Int64'),('active','Bool'),('override','Bool')],[0,False],'Bool'),
       'Check whether active equals the Boolean literal false. active is first. Do not use integer zero, count or override.',
       action('eq',[r('active'),k(False)],'Bool'),[fixture(dict(count=0,active=True,override=False),False),fixture(dict(count=1,active=False,override=True),True)]),
      ('S10', state('BindingTypedEquality',[('flag','Bool'),('code','Int64'),('alias','Int64')],[False,0],'Bool'),
       'Does integer zero exactly match code? Use the literal integer first, not Boolean false; neither alias nor flag participates.',
       action('eq',[k(0),r('code')],'Bool'),[fixture(dict(flag=False,code=0,alias=8),True),fixture(dict(flag=True,code=8,alias=0),False)]),
      ('S11', state('BindingSelfEquality',[('origin','Bool'),('noise','Bool'),('n','Int64')],[],'Bool',
          [dict(id='snapshot',type='Bool',deps=['origin'],node=dict(op='value',expr=r('origin')))]),
       'Determine equality of snapshot with snapshot, naming that prior result in both operand positions. Only its distinct direct identity belongs in dependencies.',
       action('eq',[r('snapshot'),r('snapshot')],'Bool'),[fixture(dict(origin=False,noise=True,n=4),True),fixture(dict(origin=True,noise=False,n=-4),True)]),
      ('S12', state('BindingAgreement',[('noise','Bool'),('right','Bool'),('left','Bool'),('count','Int64')],[],'Bool'),
       'Do the left and right Boolean decisions agree exactly? Keep left then right. noise and count are unrelated.',
       action('eq',[r('left'),r('right')],'Bool'),[fixture(dict(noise=True,left=False,right=False,count=0),True),fixture(dict(noise=False,left=False,right=True,count=1),False),fixture(dict(noise=True,left=True,right=False,count=1),False)])
    ]
