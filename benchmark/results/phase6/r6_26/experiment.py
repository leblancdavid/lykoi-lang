"""Prepare sealed tasks and run OpenCode using existing authentication only."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from common import HERE, ROOT, now, save, read, sha, tools, runner

TEMP = Path(r'C:\Users\lblan\AppData\Local\Temp\opencode')
MODEL = 'openai/gpt-6.1-sol'

def cmd(args, **kwargs):
    # Windows opencode is a command shim; resolve explicitly.
    if args[0] == 'opencode':
        args[0] = shutil.which('opencode')
    return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', **kwargs)

def prepare():
    assert not (HERE / 'BASELINE.json').exists()
    old = HERE.parent / 'r6_25'
    b = json.loads((old / 'BASELINE.json').read_text())
    pub = json.loads((old / 'PUBLICATION-IDENTITIES.json').read_text())
    receipt = json.loads((old / 'VERIFICATION.json').read_text())
    assert receipt['passed'] and receipt['publication_manifest_sha256'] == sha(old / 'PUBLICATION-IDENTITIES.json')
    pins = dict(b['protected_files'])
    pins.update({p: x['sha256'] for p, x in pub['files'].items()})
    for n in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
        p = old / n
        pins[p.relative_to(ROOT).as_posix()] = sha(p)
    assert all(sha(ROOT / p) == h for p, h in pins.items())
    assert len(b['kernel_ledger']['baseline_kernel']) + len(b['kernel_ledger']['preserved_additions']) == 26
    save('BASELINE.json', dict(timestamp=now(), protected_files=pins, protected_count=len(pins), kernel=26,
        kernel_ledger=b['kernel_ledger'], implementations=b['implementations'], historical_publication_verified=True,
        semantic_schemas_sha256=sha(old / 'TOOLS.json'), git_head=cmd(['git', 'rev-parse', 'HEAD']).stdout.strip()))
    inventory = cmd(['opencode', 'models'])
    verbose = cmd(['opencode', 'models', 'openai', '--verbose'])
    # Extract catalog entries; do not read or export auth/config secrets.
    text = verbose.stdout
    key = MODEL + '\n'
    pos = text.index(key) + len(key)
    model, _ = json.JSONDecoder().raw_decode(text[pos:].lstrip())
    save('INVENTORY.json', dict(timestamp=now(), version=cmd(['opencode', '--version']).stdout.strip(),
        models=inventory.stdout.splitlines(), selected=model, selection='Prospective capable programming/reasoning/tool-use model, same explicit identity as coordinator; catalog is not authenticated availability proof.',
        optional_C='Not selected', credential_values_collected=False))
    config = dict(model=MODEL, provider='openai', reasoning_variant='high', reasoning_attestation='requested, not independently attested',
        native_tools=True, max_steps=16, tool_budget=24, correction_turns=3, wall_seconds=180,
        output_cap_requested=4096, cumulative_input_cap=60000, cumulative_output_cap=16384,
        catalog_limits=model['limit'], billing=None, telemetry='OpenCode JSON completion events and measured wall time; upstream HTTP not available')
    save('MODEL-CONFIG.json', config)
    success, reject, invalid = runner.success, runner.reject, runner.invalid
    tasks = [
        dict(id='N1', target='Reserve', requirement='Reserve(stock:Int64,credit:Int64): first store add(stock,credit), then store add of that prior subtotal and -7. Return the second stored value. Exactly two ordered value steps and one definition. The second step must depend on the first.',
            signatures={'Reserve': [['stock','Int64'],['credit','Int64']]}, operations={'Reserve':['value','value']}, edges=[],
            cases=[success({'stock':20,'credit':4},17),success({'stock':3,'credit':4},0),success({'stock':65535,'credit':7},65535),reject({'stock':0,'credit':0},'ENCODE_RANGE','encode',None),reject({'stock':65535,'credit':8},'ENCODE_RANGE','encode',None),reject({'stock':2**63-1,'credit':1},'OVERFLOW','structure'),invalid({'stock':True,'credit':7})]),
        dict(id='N2', target='Threshold', requirement='Threshold(base:Int64,extra:Int64,ceiling:Int64): store add(base,extra) as Int64; store le of that stored subtotal and ceiling as Bool; check the stored Bool with code CEILING and site literal71; return the stored subtotal. Exactly value,value,check in this order and one definition.',
            signatures={'Threshold':[['base','Int64'],['extra','Int64'],['ceiling','Int64']]},operations={'Threshold':['value','value','check']},edges=[],
            cases=[success({'base':5,'extra':8,'ceiling':13},13),reject({'base':5,'extra':8,'ceiling':12},'CEILING'),success({'base':0,'extra':0,'ceiling':0},0),reject({'base':-2,'extra':0,'ceiling':0},'ENCODE_RANGE','encode',None),reject({'base':2**63-1,'extra':1,'ceiling':0},'OVERFLOW','structure'),invalid({'base':0,'extra':0,'ceiling':False})]),
        dict(id='N3', target='Gate', requirement='Gate(allowed:Bool,x:Int64,y:Int64): check allowed with code CLOSED and site literal73; then store Bool le(x,y); check that stored Bool with code ORDER and site literal79; then store add(x,11) and return it. Exactly check,value,check,value in this order and one definition. Earlier failure must absorb later checks/arithmetic.',
            signatures={'Gate':[['allowed','Bool'],['x','Int64'],['y','Int64']]},operations={'Gate':['check','value','check','value']},edges=[],
            cases=[success({'allowed':True,'x':2,'y':3},13),reject({'allowed':False,'x':9,'y':0},'CLOSED'),reject({'allowed':True,'x':9,'y':0},'ORDER'),reject({'allowed':False,'x':2**63-1,'y':2**63-1},'CLOSED'),reject({'allowed':True,'x':2**63-1,'y':2**63-1},'OVERFLOW','structure'),invalid({'allowed':1,'x':0,'y':0})]),
        dict(id='N4', target='Bundle', requirement='Reusable Lift(v:Int64): store add(v,5), return the stored value. Bundle(left:Int64,right:Int64,ceiling:Int64) must compose the SAME Lift first with left, then with right; store add of the two call results; check le of that stored total and ceiling with code BUNDLE and site literal83; return the stored total. Exactly two definitions, Lift[value], Bundle[compose,compose,value,check], no inlining.',
            signatures={'Lift':[['v','Int64']],'Bundle':[['left','Int64'],['right','Int64'],['ceiling','Int64']]},operations={'Lift':['value'],'Bundle':['compose','compose','value','check']},edges=[['Bundle','Lift'],['Bundle','Lift']],
            cases=[success({'left':1,'right':2,'ceiling':13},13),success({'left':-5,'right':-5,'ceiling':0},0),success({'left':32760,'right':32765,'ceiling':65535},65535),reject({'left':1,'right':2,'ceiling':12},'BUNDLE'),reject({'left':2**63-1,'right':0,'ceiling':0},'OVERFLOW','structure'),invalid({'left':0,'right':None,'ceiling':20})])]
    save('TASKS.json', dict(source='coordinator-authored synthetic, fresh variants not historical tasks', tasks=tasks, cases=sum(len(t['cases']) for t in tasks)))
    save('CALIBRATION.json', json.loads((old / 'REQUIREMENT.json').read_text()))
    shared = (HERE.parent / 'r6_23/CONTRACT.txt').read_text().split('\nTRACK_A\n')[0].replace('Do not emit examples, schemas, Markdown or commentary. Return one JSON packet.', '')
    prompt = shared + '\nUse only native lykoi construction tools; declare typed inputs, append ordered operations, finalize each result, then validate_candidate. Expressions use scalar literals, $input_or_prior_alias, or [add|le|eq,operand,operand], one binary layer. Exact dependencies include every referenced input/local alias once. Limits3 definitions/4 inputs/8 operations per definition. Errors leave state unchanged. Stop on completed validation. No supplied library or solution. Maximum16 model turns/24 tool calls/3 correction turns. Do not access files, other tools or other sessions.'
    save('PROMPTS.json', dict(system=prompt, neutral='Call lykoi_declare_input with definition Neutral and inputs []. Then call lykoi_apply_operation with definition Neutral, alias n, operation value, type Int64, expression 4, dependencies []. These tools are inert; this tests schema visibility and ordered invocation only. Stop after both succeed.',
        calibration=read('CALIBRATION.json')['requirement'], fresh={t['id']:t['requirement'] for t in tasks}))
    save('TOOLS.json', tools.definitions(['value','check','compose']))
    save('CALIBRATION-TOOLS.json', tools.definitions(['value']))
    save('PREPARATION-FREEZE.json', dict(timestamp=now(), model_exposure=False, files={p.name:sha(p) for p in HERE.iterdir() if p.is_file() and p.name != 'PREPARATION-FREEZE.json'}))
    print('Verified',len(pins),'protected identities; frozen4 tasks/',sum(len(t['cases']) for t in tasks),'observations; selected',MODEL)

def configuration(label, mode):
    prompt = 'Perform only the requested inert tool calls.' if mode == 'neutral' else read('PROMPTS.json')['system']
    return {'$schema':'https://opencode.ai/config.json', 'model':MODEL, 'small_model':MODEL,
        'share':'disabled','autoupdate':False,'snapshot':False,'instructions':[], 'plugin':[], 'lsp':False,'formatter':False,
        'compaction':{'auto':False}, 'enabled_providers':['openai'],
        'permission':{'*':'deny','lykoi_*':'allow'}, 'tools':{'*':False,'lykoi_*':True},
        'agent':{'r626':{'mode':'primary','model':MODEL,'variant':'high','prompt':prompt,'steps':16,'options':{'maxOutputTokens':4096},'permission':{'*':'deny','lykoi_*':'allow'}}},
        'mcp':{'lykoi':{'type':'local','command':[sys.executable,str(HERE / 'bridge.py'),label,mode],'enabled':True}}}

def invoke(label, mode, message):
    assert TEMP.is_dir()
    directory = HERE / label
    assert not directory.exists(), 'no retry'
    directory.mkdir()
    cfg = configuration(label, mode)
    save(label + '/OPENCODE-CONFIG.json', cfg)
    env = os.environ.copy()
    env.update(OPENCODE_CONFIG_CONTENT=json.dumps(cfg), OPENCODE_DISABLE_PROJECT_CONFIG='1', OPENCODE_DISABLE_EXTERNAL_SKILLS='1', OPENCODE_DISABLE_CLAUDE_CODE_SKILLS='1', OPENCODE_PURE='1')
    args = ['opencode','run','--pure','--model',MODEL,'--variant','high','--agent','r626','--format','json','--title','R6.26 '+label,message]
    save(label + '/REQUEST.json', dict(timestamp=now(), command=args, cwd=str(TEMP), configuration=cfg, fresh_session=True))
    begin = time.perf_counter()
    proc = subprocess.Popen([shutil.which('opencode')] + args[1:], cwd=TEMP, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = proc.communicate(timeout=180)
        termination = 'PROCESS_COMPLETED'
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'], capture_output=True)
        out, err = proc.communicate()
        termination = 'WALL_BUDGET'
    (directory / 'EVENTS.jsonl').write_bytes(out)
    (directory / 'STDERR.txt').write_bytes(err)
    save(label + '/STATUS.json',dict(timestamp=now(), returncode=proc.returncode, termination=termination, wall_seconds=time.perf_counter()-begin))
    print(label,termination,'exit',proc.returncode,'seconds',round(time.perf_counter()-begin,3))

def neutral():
    assert all(sha(HERE / p)==h for p,h in read('PREPARATION-FREEZE.json')['files'].items())
    invoke('NEUTRAL','neutral',read('PROMPTS.json')['neutral'])
    rows = read('NEUTRAL/INTERACTION.json')['rows'] if (HERE / 'NEUTRAL/INTERACTION.json').exists() else []
    passed = len(rows)==2 and all(r.get('dispatch',{}).get('success') for r in rows)
    save('PROVIDER-QUALIFICATION.json',dict(timestamp=now(),passed=passed,neutral_only=True, construction_exposure=False,
        calls=len(rows), boundary='OpenCode SDK/MCP envelope, not raw provider HTTP', semantic_schemas_changed=False,
        failure=None if passed else 'See NEUTRAL/EVENTS.jsonl, STDERR.txt and MCP.jsonl for exact startup/schema/provider diagnostic'))
    print('Neutral compatibility:',passed)

if __name__ == '__main__':
    {'prepare':prepare,'neutral':neutral}[sys.argv[1]]()
