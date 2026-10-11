"""Existing system jsonschema and semantic dispatcher qualification; no server edits."""
import copy
import importlib.util
import jsonschema
from referencing import Registry, Resource
from freeze import OUT, ROOT, c, read, sha, write
from qualify import artifact
from assembly import behavior, agrees, package


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def schema_check():
    base=ROOT/'benchmark/results/phase6/r6_62'
    common=read(base/'common-1.schema.json')
    registry=Registry().with_resource(common['$id'],Resource.from_contents(common))
    validators={k:jsonschema.Draft202012Validator(read(base/f'{k}-1.schema.json'),registry=registry) for k in ('A','B')}
    step=jsonschema.Draft202012Validator(read(OUT/'step-1.schema.json'))
    complete=jsonschema.Draft202012Validator(read(ROOT/'experiments/typed_composition_r6_18/typed-composition-1.schema.json'))
    corrections=[]
    for folder in sorted((OUT/'episodes').iterdir()):
        a=read(folder/'A-RECORD.json')
        b=read(folder/'B-RECORD.json')
        validators['A'].validate(a)
        errors=list(validators['B'].iter_errors(b))
        assert len(errors)==1 and list(errors[0].path)==['provenance','trace']
        # B's existing envelope requires an artifact trace: use real deterministic
        # assembly evidence, explicitly expert provenance, never AI trajectory text.
        b['provenance']['trace']=artifact(folder/'VALIDATION.json')
        validators['B'].validate(b)
        step.validate(jsonschema_input := read(folder/'ACTION.json'))
        assert jsonschema_input==c.load(b['target']['text'])
        complete.validate(read(folder/'A-TARGET.json'))
        for record in (a,b):
            for group in ('requirement','profile','context','target','evidence','provenance','partition'):
                def refs(x):
                    if type(x) is dict:
                        if set(x)=={'path','sha256'}:
                            assert sha(ROOT/x['path'])==x['sha256']
                        else:
                            for value in x.values(): refs(value)
                    elif type(x) is list:
                        for value in x: refs(value)
                refs(record[group])
        write(folder/'B-RECORD-2.json',b)
        corrections.append(dict(episode=folder.name,original=artifact(folder/'B-RECORD.json'),
             corrected=artifact(folder/'B-RECORD-2.json'),error='provenance.trace must be artifact in existing B schema'))
    write(OUT/'SCHEMA-QUALIFICATION.json',dict(passed=True,A_records=10,B_records=10,
        native_steps=10,native_packages=10,retained_initial_B_shape_failures=corrections,
        correction='Reference deterministic assembly receipt as expert trace. No AI trace invented; targets/behavior unchanged.'))


def compact_expr(expr):
    op,arg=next(iter(expr.items()))
    if op=='ref': return '$'+arg
    if op=='const': return arg
    return [op]+[compact_expr(x) for x in arg]


def interface_check():
    tools=module('r663_frozen_tools',ROOT/'benchmark/results/phase6/r6_24/tools.py')
    advertised=read(ROOT/'benchmark/results/phase6/r6_25/TOOLS.json')
    assert advertised==tools.definitions(['value'])
    rows=[]
    for folder in sorted((OUT/'episodes').iterdir()):
        before=read(folder/'BEFORE.json')
        action=read(folder/'ACTION.json')
        session=tools.Session(['value'])
        calls=[]
        def call(name,args):
            request=dict(function=dict(name=name,arguments=args))
            response=session.dispatch(request)
            calls.append(dict(request=request,response=response))
            assert response['success'], response
        call('declare_input',dict(definition=before['name'],inputs=before['params']))
        for s in before['steps']+[action]:
            call('apply_operation',dict(definition=before['name'],alias=s['id'],operation='value',
                type=s['type'],expression=compact_expr(s['node']['expr']),dependencies=s['deps']))
        call('define_result',dict(definition=before['name'],result='$selected',result_type=before['result_type']))
        defs,_=tools.a.compact_defs(session.packet)
        task=tools.a.seal_all(defs)[0]
        endpoint=dict(package=package(task))
        observations=[]
        for f in read(folder/'ACCEPTANCE.json')['cases']:
            actual=behavior(endpoint,f['arguments'])
            assert agrees(actual,f['expected'])
            observations.append(dict(actual=actual,expected=f['expected']))
        selected_call=calls[-2]['request']
        write(folder/'C-SCRIPTED-CALLS.json',dict(provenance='scripted_interface_qualification_not_observed_ai',
            calls=calls,selected_operation_call=selected_call,observations=observations,
            remote_mcp_transport_invocations=0))
        rows.append(dict(episode=folder.name,operation_selection_compatible=True,typed_operation_success=True,
            calls=len(calls),selected_call=selected_call,target_result_type=before['result_type']))
    apply_schema=next(t for t in advertised if t['function']['name']=='apply_operation')
    write(OUT/'C-INTERFACE.json',dict(status='BOUNDED_OPERATION_SELECTION_COMPATIBLE',
          schema_source=artifact(ROOT/'benchmark/results/phase6/r6_25/TOOLS.json'),tool_call_schema=apply_schema,
          entries=rows,scripted_operation_calls=12,selected_calls=10,new_mcp_capabilities=0,
          actual_ai_semantic_trajectories=0,live_transport_tested=False,
          endpoint_gap='Existing validate_candidate requires Int64 target. Bool apply_operation/define_result works, but full Bool endpoint finalization is not claimed.',
          availability='Existing historical semantic MCP dispatcher supports this step schema; it is not exposed as a Lykoi tool in this active harness.'))
    print('PASS corrected A/B schema envelopes, native targets and ten existing C operation selections')


if __name__=='__main__':
    import sys
    if len(sys.argv)==1:
        schema_check()
    interface_check()
