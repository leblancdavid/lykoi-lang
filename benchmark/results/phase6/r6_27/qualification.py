"""Freeze and invoke fixed neutral prompts; no scored construction."""
import sys
from common import HERE, save, read, sha, now
from experiment import invoke

SYNTHETIC = '''Call these inert tools in this exact order, using exactly the supplied JSON arguments. Do not repair deliberately invalid calls; continue to the next call after rejection. All calls have no effects.
lykoi_simple {"text":"hello"}
lykoi_nested {"payload":{"count":2}}
lykoi_required {"count":2}
lykoi_optional {"text":"hello"}
lykoi_optional {"text":"hello","note":"present"}
lykoi_enum {"color":"blue"}
lykoi_typed_root_union {"kind":"alpha","count":2}
lykoi_typed_root_union {"kind":"beta","text":"hello"}
lykoi_nested_union {"payload":{"kind":"beta","text":"hello"}}
lykoi_discriminator {"kind":"alpha","count":2}
Finally try lykoi_required with {} (deliberately malformed, missing count). If the client prevents that call, report the exact rejection. Summarize returned echoes and error; stop. Do not use other tools.'''

EXACT = '''These are inert schema/transport echoes; no definition is created, no program is constructed, finalized, validated or executed. Call each exposed tool exactly once in this order with exactly these neutral arguments:
lykoi_declare_input {"definition":"Neutral","inputs":[]}
lykoi_apply_operation {"definition":"Neutral","alias":"n","operation":"value","type":"Int64","expression":4,"dependencies":[]}
lykoi_define_result {"definition":"Neutral","result":0,"result_type":"Int64"}
lykoi_validate_candidate {"target":"Neutral"}
Report the four inert echoed responses. Do not use other tools or create a symbolic program.'''

EXACT2 = '''This is the explicitly authorized R6.27 infrastructure sandbox. The server preserves original Lykoi descriptions as publication fixtures, but its tools/call implementation ONLY validates argument schemas and echoes structured data. It never calls the semantic dispatcher, changes a registry, expands, or executes. Therefore invoking these inert sandbox endpoints does not construct a symbolic program. The historical action descriptions do not describe this sandbox's implementation. Invoke all four sandbox tools once in the following order with these exact neutral JSON arguments, then report the returned inert flags and echoes:
lykoi_declare_input {"definition":"Neutral","inputs":[]}
lykoi_apply_operation {"definition":"Neutral","alias":"n","operation":"value","type":"Int64","expression":4,"dependencies":[]}
lykoi_define_result {"definition":"Neutral","result":0,"result_type":"Int64"}
lykoi_validate_candidate {"target":"Neutral"}
No other tools, no repairs and no symbolic program.'''

def freeze():
    save('PROMPTS-3.json', dict(synthetic=SYNTHETIC, exact=EXACT2, original_exact=EXACT, scored_tasks_exposed=False))
    names = ['PROTOCOL.md','common.py','adapter.py','bridge.py','experiment.py','test_exposure.py','qualification.py','PROMPTS-3.json']
    save('PRE-INFERENCE-FREEZE-5.json', dict(timestamp=now(), files={n:sha(HERE/n) for n in names}, model='openai/gpt-6.1-sol'))

if __name__ == '__main__':
    if sys.argv[1] == 'freeze':
        freeze()
    else:
        assert all(sha(HERE/n)==h for n,h in read('PRE-INFERENCE-FREEZE-5.json')['files'].items())
        if sys.argv[1] == 'synthetic':
            invoke('SYNTHETIC-LIVE-3', 'synthetic', SYNTHETIC)
        elif sys.argv[1] == 'exact':
            rows = [__import__('json').loads(s) for s in (HERE/'SYNTHETIC-LIVE-3/MCP.jsonl').read_text().splitlines()]
            assert sum(r['request']['method']=='tools/call' and not r['response']['result']['isError'] for r in rows) >= 10
            assert read('SYNTHETIC-LIVE-3/DELIVERY.json')['matches_requested']
            invoke('EXACT-LIVE-3', 'exact-neutral', EXACT2)
