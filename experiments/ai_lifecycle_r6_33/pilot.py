"""R6.33 orchestration/scoring only; delegates execution to unchanged R6.18/VM."""
import copy
import hashlib
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_33'
TEMP = Path('C:/Users/lblan/AppData/Local/Temp/opencode/r6_33_author')
OPENCODE = str(Path(os.environ['APPDATA']) / 'npm/node_modules/opencode-ai/bin/opencode.exe')
sys.path.insert(0, str(ROOT / 'experiments/lifecycle_r6_32'))
from lifecycle import Registry, Journal, c, digest


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path = Path(path)
    assert path.parent.exists(), path.parent
    with path.open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(value, indent=2, sort_keys=True) + '\n')


def rawsave(path, value):
    with Path(path).open('xb') as f:
        f.write(value)


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def protected():
    prev = ROOT / 'benchmark/results/phase6/r6_32'
    pins = load(prev / 'BASELINE.json')['protected_files']
    receipt = load(prev / 'VERIFICATION.json')
    assert receipt['passed'] and receipt['kernel'] == 26
    assert receipt['manifest_sha256'] == sha(prev / 'PUBLICATION-IDENTITIES.json')
    for name, meta in load(prev / 'PUBLICATION-IDENTITIES.json')['files'].items():
        assert 'p6_a05' not in name.lower().replace('-', '_')
        assert sha(ROOT / name) == meta['sha256'], name
        assert (ROOT / name).stat().st_size == meta['bytes'], name
        pins[name] = meta['sha256']
    for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
        pins[(prev / name).relative_to(ROOT).as_posix()] = sha(prev / name)
    mismatches = [p for p, h in pins.items() if sha(ROOT / p) != h]
    assert not mismatches, mismatches
    return pins


CONFIG = {
    '$schema': 'https://opencode.ai/config.json', 'share': 'disabled',
    'autoupdate': False, 'snapshot': False, 'permission': 'deny',
    'agent': {'r633-author': {
        'description': 'Bounded symbolic JSON participant', 'mode': 'primary',
        'model': 'openai/gpt-6.1-sol', 'variant': 'high', 'permission': 'deny',
        'prompt': 'Author symbolic JSON only. No tools. Output exactly one JSON object, no fences. '
                  'Use only the supplied frozen syntax and requirements. Never invent operations.'}},
    'default_agent': 'r633-author'
}


def prepare():
    assert ROOT.exists() and OUT.parent.exists() and TEMP.parent.exists()
    OUT.mkdir(exist_ok=False)
    TEMP.mkdir(exist_ok=False)
    pins = protected()
    save(OUT / 'BASELINE.json', dict(round='R6.33', kernel=26, protected_files=pins,
        protected_count=len(pins), R6_32_publication_verified=True,
        initial_git_status='clean before R6.33 additions',
        head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()))
    metadata_run = subprocess.run([OPENCODE, 'models', 'openai', '--verbose'],
        capture_output=True, timeout=120)
    text = metadata_run.stdout.decode('utf-8').replace('\r\n', '\n')
    marker = 'openai/gpt-6.1-sol\n'
    meta, _ = json.JSONDecoder().raw_decode(text.split(marker, 1)[1].lstrip())
    save(OUT / 'MODEL.json', dict(provider='openai', model='gpt-6.1-sol',
        opencode_version='1.18.32', variant='high', requested_reasoning=meta['variants']['high'],
        advertised_metadata=meta, advertised_context_limits=meta['limit'],
        author_tool_definitions=[], tool_boundary='all agent/global permissions denied',
        effective_provider_tool_schema=None, effective_provider_reasoning_attestation=None,
        hidden_provider_context_attestation=None, billing=None,
        config=CONFIG, timeout_seconds=600, proposals_per_stage=3,
        selection='fixed before any symbolic model response'))
    save(TEMP / 'opencode.json', CONFIG)
    base = '''Create a reusable BoundedScore with ordered params x:Int64,y:Int64,limit:Int64,bias:Int64 -> Int64.
Consumes no bytes. Check x>=0 first (code X_NEGATIVE, site ref x), then y>=0
(Y_NEGATIVE, site ref y), compute checked x+y, check sum<=limit (SUM_LIMIT, site ref x),
then return checked sum+bias. No additional input checks. Use only existing operations.
Return {"action":"admit","predecessor":null,"definitions":[DEFINITION_WITHOUT_IDENTITY]}.
'''
    syntax = '''Exact definition fields: name,revision (always1),params (array of {name,type}),
dependencies (symbol->exact hash),steps (array of {id,type,deps,node}),order (exact step id permutation),
result (expression),result_type. OMIT identity: broker calls existing seal unchanged.
Types Int64,Bool,Unit. Expressions {"ref":"identifier"},{"const":integer/bool/null},
{"add":[expr,expr]},{"le":[expr,expr]},{"eq":[expr,expr]}.
Nodes {"op":"value","expr":expr}, {"op":"check","test":bool_expr,"site":expr,"code":"CODE"},
{"op":"atom","codec":"uint8"}, {"op":"end"},
{"op":"compose","symbol":"Family","identity":"actual SHA256","args":{"param":ref_or_const}}.
Each step deps lists exactly all refs in its node, including check site.
Declared type equals inferred node result. check/end return Unit. No params or local shadowing.
Declarations are a DAG, order respects deps; all steps execute in order until first rejection.
Symbol dependencies exactly match compose families; actual immutable pins only. No cycles.
Calls args refs/literals only. Max32 steps/definition,8 definitions/closure,64 expanded nodes,nesting4.
Root program must have params[] and result_type Int64. VM encodes final root as UInt16BE.
All definitions pass unchanged R6.32 admission/R6.18 expansion/VM validation.
Do not use tools or output prose. One exact JSON object only.
'''
    rawsave(OUT / 'BASE-PROMPT.txt', (syntax + '\n' + base).encode())
    rawsave(OUT / 'SYNTAX.txt', syntax.encode())
    rawsave(OUT / 'MODIFICATION.txt', b'Change BoundedScore to add surcharge2 AFTER checked sum+bias. '
        b'Preserve exact name/ordered signature/check order/error sites. Admit an immutable successor. '
        b'Update only CallerA by dependency/call pins; retain CallerB on predecessor. Explicit migration required.\n')
    frozen = [HERE / 'PROTOCOL.md', HERE / 'pilot.py', OUT / 'MODEL.json',
              OUT / 'BASE-PROMPT.txt', OUT / 'SYNTAX.txt', OUT / 'MODIFICATION.txt']
    save(OUT / 'FREEZE.json', dict(utc=datetime.now(timezone.utc).isoformat(),
        model_calls_at_freeze=0, inputs={p.relative_to(ROOT).as_posix(): sha(p) for p in frozen},
        acceptance='pilot.py evaluate and PROTOCOL.md; separate requirement-derived dependency map',
        author_exposure='only BASE-PROMPT initially; modification after original acceptance'))
    print('R6.33 frozen:', len(pins), 'protected identities')


def normalized(value):
    if isinstance(value, bytes):
        return {'bytes_hex': value.hex()}
    if isinstance(value, dict):
        return {k: normalized(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalized(v) for v in value]
    return value


def execute(plan, data, limits=None):
    trace = []
    original = c.vm.Machine.run
    def observer(machine, node, env, depth=1):
        trace.append(dict(id=node['id'], op=node['op'], cursor=machine.i, work=machine.work))
        return original(machine, node, env, depth)
    c.vm.Machine.run = observer
    try:
        result = c.vm.execute(plan, data, limits)
    finally:
        c.vm.Machine.run = original
    assert c.vm.execute(plan, data, limits) == result, 'observer changed envelope'
    return dict(envelope=normalized(result), trace=trace)


def closed_package(registry, target):
    # Caller definitions are already closed; reuse exact AI-authored body as root.
    closure = registry.retrieve(pin=target['identity'])
    return dict(version=c.VERSION, foundation=c.FOUNDATION,
                definitions=[d for d in closure if d['identity'] != target['identity']], program=target)


def direct_package(registry, target, values):
    # Frozen evaluator-only invocation harness, never shown as an authored solution.
    root = c.seal(dict(name='SignedProbe', revision=1, params=[],
        dependencies={target['name']: target['identity']},
        steps=[dict(id='invoke', type='Int64', deps=[], node=dict(op='compose',
            symbol=target['name'], identity=target['identity'],
            args={k: {'const': v} for k, v in zip(('x','y','limit','bias'), values)}))],
        order=['invoke'], result={'ref':'invoke'}, result_type='Int64'))
    return dict(version=c.VERSION, foundation=c.FOUNDATION,
                definitions=registry.retrieve(pin=target['identity']), program=root)


def expected_direct(values, delta):
    x, y, limit, bias = values
    if x < 0: return 'X_NEGATIVE'
    if y < 0: return 'Y_NEGATIVE'
    if x+y >= 2**63: return 'OVERFLOW'
    if x+y > limit: return 'SUM_LIMIT'
    total = x+y+bias
    if not -2**63 <= total < 2**63: return 'OVERFLOW'
    total += delta
    if not -2**63 <= total < 2**63: return 'OVERFLOW'
    return total if 0 <= total <= 65535 else 'ENCODE_RANGE'


def evaluate(registry, artifacts, modified=False, cutoffs=False):
    start = time.perf_counter()
    rows, expansions = [], {}
    def observe(label, expanded, data, expected, limits=None):
        obs = execute(expanded['plan'], data, limits)
        r = obs['envelope']
        if type(expected) is int:
            passed = (r['status'] == 'success' and type(r['value']) is int and
                r['value'] == expected and r['output'] == {'bytes_hex':expected.to_bytes(2,'big').hex()})
        else:
            passed = r['status'] in ('reject','plan_reject') and r['error']['code'] == expected
        rows.append(dict(case=label, input_hex=data.hex() if isinstance(data,bytes) else None,
            expected=expected, limits=limits, passed=passed, observation=obs))
        return obs
    for label, key, delta in [('A_original','a',0),('B_retained','b',0)] + (
            [('A_modified','a_new',2)] if modified else []):
        package = closed_package(registry, artifacts[key])
        t = time.perf_counter()
        expanded = c.expand(package)
        validation_time = time.perf_counter()-t
        assert c.expand(package) == expanded
        expansions[label] = dict(package=package, expanded=expanded, validation_seconds=validation_time)
        is_a = key in ('a','a_new')
        cases = itertools.product((0,1,11,127,189,200,254,255), repeat=2) if is_a else ((x,) for x in range(256))
        for values in cases:
            x, y = (values if is_a else (values[0],11))
            expected = x+y+(7 if is_a else 3)+delta if x+y <= (300 if is_a else 200) else 'SUM_LIMIT'
            observe(label+':'+','.join(map(str,values)), expanded, bytes(values), expected)
        invalid = [(b'', 'TRUNCATED'), (b'\x00\x00\x00' if is_a else b'\x00\x00','TRAILING'),
                   (b'\xff\xff\x00' if is_a else b'\xff\x00','SUM_LIMIT')]
        if is_a: invalid.append((b'\x00','TRUNCATED'))
        for i, (data, code) in enumerate(invalid):
            observe(label+':invalid:'+str(i), expanded, data, code)
        observe(label+':input-type', expanded, None, 'INPUT_TYPE')
        if cutoffs:
            for data in ([b'\x00\x00',b'\xff\xff'] if is_a else [b'\x00',b'\xff']):
                full = execute(expanded['plan'], data)
                for limit in range(full['envelope']['work']):
                    observe(label+':cutoff:'+data.hex()+':'+str(limit),expanded,data,'WORK_LIMIT',{'work':limit})
                assert execute(expanded['plan'],data,{'work':full['envelope']['work']}) == full
    probes = [(-1,-1,300,7),(0,-1,300,7),(0,0,-1,7),(2**63-1,1,2**63-1,0),
              (1,0,300,2**63-1),(300,0,300,7),(0,0,300,-1),(0,0,300,65536),
              (0,0,300,2**63-2)]
    for label, key, delta in [('predecessor','old',0)] + ([('successor','new',2)] if modified else []):
        for i, values in enumerate(probes):
            package = direct_package(registry,artifacts[key],values)
            expanded = c.expand(package)
            observe(label+':signed:'+str(i), expanded, b'', expected_direct(values,delta))
    # Ordering is requirement-derived: A reads x/y, B reads x; nested checks before end.
    ordering = []
    for label, record in expansions.items():
        rows_for = [r for r in rows if r['case'] == label+':'+('0,0' if label.startswith('A') else '0')]
        trace = rows_for[0]['observation']['trace']
        ops = [e['op'] for e in trace]
        n = 2 if label.startswith('A') else 1
        checks = [i for i, op in enumerate(ops) if op == 'check']
        end = ops.index('end')
        passed = ops.count('atom') == n and len(checks) == 3 and max(checks) < end
        ordering.append(dict(caller=label, operations=ops, passed=passed))
    return dict(rows=rows, expansions=expansions, ordering=ordering,
        passed=sum(r['passed'] for r in rows), total=len(rows),
        all_passed=all(r['passed'] for r in rows) and all(r['passed'] for r in ordering),
        wall_seconds=time.perf_counter()-start)


class Author:
    def __init__(self, journal):
        self.session = None
        self.calls = []
        self.journal = journal

    def ask(self, stage, prompt):
        number = len(self.calls)+1
        directory = OUT / 'calls' / f'{number:02}'
        directory.mkdir(parents=True, exist_ok=False)
        rawsave(directory / 'prompt.txt', prompt.encode())
        command = [OPENCODE,'run','--pure','--model','openai/gpt-6.1-sol',
            '--variant','high','--agent','r633-author','--format','json',
            '--title','R6.33 bounded lifecycle author', prompt]
        if self.session:
            command[2:2] = ['--session',self.session]
        env = os.environ.copy()
        env.update(OPENCODE_DISABLE_PROJECT_CONFIG='1', OPENCODE_CONFIG_CONTENT=json.dumps(CONFIG),
            OPENCODE_DISABLE_EXTERNAL_SKILLS='1', OPENCODE_DISABLE_CLAUDE_CODE_SKILLS='1',
            OPENCODE_PURE='1', OPENCODE_DISABLE_DEFAULT_PLUGINS='1')
        self.journal.record('model_start',dict(stage=stage,call=number,prompt_sha256=sha(directory/'prompt.txt')))
        start = time.perf_counter()
        child = subprocess.run(command,cwd=TEMP,env=env,capture_output=True,
            timeout=600)
        seconds = time.perf_counter()-start
        rawsave(directory/'stdout.jsonl',child.stdout)
        rawsave(directory/'stderr.txt',child.stderr)
        events = [json.loads(line) for line in child.stdout.decode('utf-8').splitlines() if line.startswith('{')]
        for e in events:
            if e.get('sessionID'): self.session=e['sessionID']
        finishes = [e['part'] for e in events if e.get('type')=='step_finish']
        texts = [e['part']['text'] for e in events if e.get('type')=='text']
        record = dict(call=number,stage=stage,session=self.session,wall_seconds=seconds,
            returncode=child.returncode,step_finishes=finishes,
            participant_tool_calls=sum(e.get('type')=='tool_use' for e in events))
        self.calls.append(record)
        save(directory/'MEASUREMENT.json',record)
        self.journal.record('model_complete',record)
        if child.returncode or not texts:
            raise RuntimeError('MODEL_TRANSPORT_OR_EMPTY_RESPONSE: '+str(record))
        text = '\n'.join(texts).strip()
        # Pure serialization extraction, no semantic correction.
        if text.startswith('```'):
            text = '\n'.join(text.splitlines()[1:-1])
        return c.load(text)

    def close(self):
        if self.session:
            result = subprocess.run([OPENCODE,'export',self.session],capture_output=True,
                timeout=120,cwd=TEMP)
            rawsave(OUT/'SESSION-EXPORT.json',result.stdout)
            rawsave(OUT/'SESSION-EXPORT.stderr.txt',result.stderr)
        save(OUT/'AUTHORING-CLOSED.json',dict(session=self.session,calls=self.calls,
            utc=datetime.now(timezone.utc).isoformat(),child_processes_terminated=True,
            no_further_inference_authorized=True))


def run():
    for p,h in load(OUT/'FREEZE.json')['inputs'].items(): assert sha(ROOT/p)==h,p
    journal = Journal(OUT/'telemetry')
    registry = Registry(OUT/'registry',journal)
    author = Author(journal)
    artifacts, rejected = {}, []
    start = time.perf_counter()
    def stage(name,prompt,keys,predecessor=None):
        for turn in range(3):
            proposal = author.ask(name,prompt)
            save(OUT/'calls'/f'{len(author.calls):02}'/'PROPOSAL.json',proposal)
            try:
                c.shape(proposal,{'action','definitions','predecessor'},'$/action')
                assert proposal['action']=='admit' and proposal['predecessor']==predecessor
                assert len(proposal['definitions'])==len(keys)
                for d in proposal['definitions']: assert 'identity' not in d
                definitions = [c.seal(d) for d in proposal['definitions']]
                receipt = registry.admit(definitions,registry.read()['token'],predecessor)
                for key,d in zip(keys,definitions):
                    artifacts[key]=d
                    save(OUT/(key+'.json'),d)
                save(OUT/(name+'-ADMISSION.json'),receipt)
                retrieved = {key:registry.retrieve(pin=artifacts[key]['identity']) for key in keys}
                save(OUT/(name+'-RETRIEVAL.json'),retrieved)
                return retrieved
            except (c.Diagnostic,AssertionError) as exc:
                diagnostic = getattr(exc,'data',dict(code='ACTION_CONTRACT',detail=str(exc)))
                rejected.append(dict(stage=name,turn=turn,proposal=proposal,diagnostic=diagnostic))
                journal.record('proposal_rejected',rejected[-1])
                prompt='Your proposal rejected. Native diagnostic: '+json.dumps(diagnostic)+'. Return corrected exact requested action JSON.'
        raise RuntimeError('AI_AUTHORING_GAP: '+name)
    try:
        retrieved=stage('discovery',(OUT/'BASE-PROMPT.txt').read_text(),['old'])
        prompt='Predecessor admitted; exact retrieval: '+json.dumps(retrieved)+'''\nIndependently construct CallerA and CallerB closed Int64 definitions.
CallerA read x then y UInt8, compose BoundedScore exact pin with x/y refs,limit300,bias7,
then end; return score. CallerB read x UInt8, compose same exact pin with x ref,y11,limit200,bias3,
then end; return score. Reuse by compose only, no copied shared checks/computation.
Return {"action":"admit","predecessor":null,"definitions":[CallerA_without_identity,CallerB_without_identity]}.
'''
        stage('reuse',prompt,['a','b'])
        original=evaluate(registry,artifacts)
        save(OUT/'ORIGINAL-ACCEPTANCE.json',original)
        assert original['all_passed'],'Original functional acceptance failed; no manual repair'
        old=artifacts['old']['identity']
        assert registry.dependents(old)['direct']==sorted([artifacts[k]['identity'] for k in ('a','b')])
        prompt=(OUT/'MODIFICATION.txt').read_text()+'\nPredecessor: '+json.dumps(artifacts['old'])+\
            '\nReturn admit action for one successor definition WITHOUT identity, predecessor="'+old+'".'
        stage('successor',prompt,['new'],old)
        prompt='Successor retrieved: '+json.dumps(registry.retrieve(pin=artifacts['new']['identity']))+\
            '\nOld CallerA: '+json.dumps(artifacts['a'])+\
            '\nAdmit CallerA successor changing ONLY dependency/call pins. Preserve all other fields. '+\
            'Return action admit, predecessor="'+artifacts['a']['identity']+'",definitions:[new CallerA without identity].'
        stage('caller-update',prompt,['a_new'],artifacts['a']['identity'])
        migration_prompt='Exact retrieved artifacts: '+json.dumps(artifacts)+'''
Return {"action":"migrate","predecessor":old_BoundedScore_pin,"successor":new_BoundedScore_pin,
"decisions":{old_CallerA_pin:new_CallerA_pin,old_CallerB_pin:null}} with actual hashes.
Explicitly retain CallerB. No other keys. Host validates dependency graph then executes both versions.
'''
        for turn in range(3):
            proposal=author.ask('migration',migration_prompt)
            save(OUT/'calls'/f'{len(author.calls):02}'/'PROPOSAL.json',proposal)
            try:
                c.shape(proposal,{'action','predecessor','successor','decisions'},'$/migration')
                assert proposal['action']=='migrate' and proposal['predecessor']==old
                assert proposal['successor']==artifacts['new']['identity']
                assert proposal['decisions']=={artifacts['a']['identity']:artifacts['a_new']['identity'],artifacts['b']['identity']:None}
                registry.migrate(proposal['predecessor'],proposal['successor'],proposal['decisions'],registry.read()['token'])
                save(OUT/'MIGRATION.json',proposal)
                break
            except (c.Diagnostic,AssertionError) as exc:
                rejected.append(dict(stage='migration',turn=turn,proposal=proposal,
                    diagnostic=getattr(exc,'data',{'code':'ACTION_CONTRACT'})))
                journal.record('proposal_rejected',rejected[-1])
                migration_prompt='Rejected: '+json.dumps(rejected[-1]['diagnostic'])+'. Correct the requested migration JSON.'
        else: raise RuntimeError('AI_AUTHORING_GAP: migration')
        final=evaluate(registry,artifacts,True,True)
        save(OUT/'FUNCTIONAL.json',final)
        assert final['all_passed'],'Final acceptance failed'
        state=registry.read()['state']
        expectation=dict(selected_roots={'CallerA':artifacts['a_new']['identity'],'CallerB':artifacts['b']['identity']},
            dependencies={k:d['dependencies'] for k,d in artifacts.items()},
            expected_successors={artifacts['new']['identity']:old,artifacts['a_new']['identity']:artifacts['a']['identity']},
            expected_decisions={artifacts['a']['identity']:artifacts['a_new']['identity'],artifacts['b']['identity']:None})
        assert state['successors']==expectation['expected_successors']
        assert state['migrations'][0]['decisions']==expectation['expected_decisions']
        for key,target in [('a','old'),('b','old'),('a_new','new')]:
            assert artifacts[key]['dependencies']=={'BoundedScore':artifacts[target]['identity']}
        save(OUT/'DEPENDENCY-IMPACT.json',dict(expectation=expectation,passed=True,
            old_direct_users=registry.dependents(old),new_direct_users=registry.dependents(artifacts['new']['identity']),
            final_registry=registry.read(), independently_reviewed=False))
        status='LIFECYCLE_COMPLETED_AWAITING_REPLAY'
        error=None
    except Exception as exc:
        status='R6_33_AI_AUTHORING_GAP' if artifacts else 'R6_33_PROTOCOL_HALT'
        error=dict(exception=type(exc).__name__,detail=str(exc))
        journal.record('halt',error)
    finally:
        author.close()
        save(OUT/'AUTHORING-RESULT.json',dict(status=status,error=error,
            artifact_keys=list(artifacts),rejected_proposals=rejected,model_invocations=len(author.calls),
            wall_seconds=time.perf_counter()-start, participant_tool_calls=sum(x['participant_tool_calls'] for x in author.calls),
            semantic_repairs_by_coordinator=0))
    print(status)


def replay():
    assert load(OUT/'AUTHORING-CLOSED.json')['child_processes_terminated']
    result=load(OUT/'AUTHORING-RESULT.json')
    assert result['status']=='LIFECYCLE_COMPLETED_AWAITING_REPLAY',result
    protected()
    registry=Registry(OUT/'registry')
    artifacts={k:load(OUT/(k+'.json')) for k in ('old','new','a','b','a_new')}
    for d in artifacts.values():
        assert d['identity']==c.identity(d)
        assert registry.read()['state']['definitions'][d['identity']]==d
    prior=load(OUT/'FUNCTIONAL.json')
    runs=[]
    for i in range(3):
        current=evaluate(registry,artifacts,True,True)
        # Timing excluded from equivalence; every full envelope/trace must match.
        assert current['rows']==prior['rows'] and current['ordering']==prior['ordering']
        assert all(current['expansions'][k]['expanded']==prior['expansions'][k]['expanded'] for k in prior['expansions'])
        assert current['all_passed']
        runs.append(dict(run=i+1,passed=current['passed'],total=current['total'],
            observations_sha256=digest(current['rows']),wall_seconds=current['wall_seconds']))
    save(OUT/'REPLAY.json',dict(classification='R6_33_AI_LIFECYCLE_SUPPORTED',model_calls=0,
        fresh_process=True,artifacts={k:dict(content_identity=d['identity'],raw_sha256=sha(OUT/(k+'.json'))) for k,d in artifacts.items()},
        runs=runs,full_envelopes_traces_expansions_equal=True,dependency_bindings_equal=True))
    print('Replay supported:',runs)


def diagnostic():
    sys.path.insert(0,str(ROOT/'src'))
    from air_compiler.parser import parse
    from air_compiler.semantics import impact
    model=parse((ROOT/'air/task_manager.json').read_text())
    rows=[]
    for seed in ('symbol:BoundedScore','definition:BoundedScore'):
        try: rows.append(dict(seed=seed,output=impact(model,seed)))
        except Exception as exc: rows.append(dict(seed=seed,exception=type(exc).__name__,detail=str(exc)))
    save(OUT/'PRODUCTION-IMPACT-DIAGNOSTIC.json',dict(rows=rows,
        oracle=False,note='Symbolic definitions outside production model domain; recorded native output only'))


def publish():
    pins=load(OUT/'BASELINE.json')['protected_files']
    assert all(sha(ROOT/p)==h for p,h in pins.items())
    for p,h in load(OUT/'FREEZE.json')['inputs'].items(): assert sha(ROOT/p)==h,p
    check=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
    assert check.returncode==0,check.stdout+check.stderr
    paths=[p for base in (HERE,OUT) for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths += [ROOT/'benchmark/results/phase6/R6_33-REPORT.md']
    paths += [ROOT/('docs/'+n+'-r6.33.md') for n in ('project-overview','research-log','decisions')]
    excluded={'PUBLICATION-IDENTITIES.json','VERIFICATION.json'}
    paths=[p for p in paths if p.name not in excluded]
    for p in paths:
        if p.suffix=='.json': load(p)
    classification=load(OUT/'REPLAY.json')['classification'] if (OUT/'REPLAY.json').exists() else load(OUT/'AUTHORING-RESULT.json')['status']
    save(OUT/'PUBLICATION-IDENTITIES.json',dict(round='R6.33',classification=classification,
        files={p.relative_to(ROOT).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in paths}))
    save(OUT/'VERIFICATION.json',dict(round='R6.33',classification=classification,passed=True,
        manifest_sha256=sha(OUT/'PUBLICATION-IDENTITIES.json'),protected_verified=len(pins),
        publication_files=len(paths),source_freeze_verified=True,git_diff_check=True,kernel=26,
        P6_A04_acceptance=False,P6_A05_access=False,stopped_after_publication=True))
    print('Publication verified:',classification,len(pins),'protected;',len(paths),'published')


if __name__=='__main__':
    {'prepare':prepare,'run':run,'replay':replay,'diagnostic':diagnostic,'publish':publish}[sys.argv[1]]()
