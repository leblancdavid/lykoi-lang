"""Recover real OpenCode construction exchanges; never synthesize tool decisions."""
import json
import re
import subprocess
from prepare import ROOT, OUT, read, write, ref, now

SESSION = 'ses_ed930fe94ffeDszosM0sppE8ob'


def main():
    p = subprocess.run(['pwsh', '-NoProfile', '-Command',
        'opencode export ' + SESSION + ' --pure'], cwd=ROOT,
        capture_output=True, text=True, encoding='utf-8', timeout=90)
    assert p.returncode == 0, 'session export failed; do not fabricate missing transcript'
    exported = json.loads(p.stdout)
    rows, metadata = [], []
    relevant = ['AI-INTENT.json', 'training_data_r6_49/build.py', 'training_data_r6_49/replay.py']
    for message in exported.get('messages', []):
        info = message.get('info', {})
        if info.get('role') != 'assistant':
            continue
        selected = []
        for part in message.get('parts', []):
            if part.get('type') != 'tool':
                continue
            state = part.get('state', {})
            arguments = state.get('input', {})
            text = json.dumps(arguments).replace('\\', '/')
            if not any(marker in text for marker in relevant):
                continue
            selected.append({'part_id': part.get('id'), 'call_id': part.get('callID'),
                'tool': part.get('tool'), 'arguments': arguments, 'status': state.get('status'),
                'response': state.get('output'), 'error': state.get('error'), 'time': state.get('time')})
        if selected:
            meta = {k: info[k] for k in ('id', 'modelID', 'providerID', 'tokens', 'cost', 'time', 'finish') if k in info}
            metadata.append(meta)
            rows.append({'message_metadata': meta, 'actual_tool_calls': selected})
    assert rows
    serialized = json.dumps(rows)
    assert not re.search(r'(?:sk-[A-Za-z0-9_-]{32,}|ghp_[A-Za-z0-9]{32,}|hf_[A-Za-z0-9]{32,})', serialized)
    tools = [t for row in rows for t in row['actual_tool_calls']]
    assert any('AI-INTENT.json' in json.dumps(t['arguments']) for t in tools)
    assert any('INVALID_TYPED_SCALAR_RELATION' in str(t['response']) for t in tools)
    assert any('validated, lowered and frozen' in str(t['response']) for t in tools)
    write(OUT / 'AI-CONSTRUCTION-TRANSCRIPT.json', {'kind': 'ACTUAL_OPENCODE_SYMBOLIC_EDIT_TRAJECTORY',
        'session_id': SESSION, 'captured_utc': now(), 'entries': rows,
        'hidden_reasoning_included': False, 'unrelated_messages_included': False,
        'semantic_mcp_calls': 0, 'episodes_constructed': ['S01', 'S02'],
        'original_validation_failure': ref(OUT / 'BUILD-FAILURE.json'),
        'final_artifacts': {e: {n: ref(OUT / 'episodes' / e / n) for n in
            ('AI-INTENT.json', 'SYMBOLIC-IR.json', 'APPLICATION.py', 'VALIDATION.json')} for e in ('S01', 'S02')},
        'limitation': 'editing tools, not semantic MCP; both episodes share one real creation and correction exchange'})
    write(OUT / 'TOOL-EXPOSURE.json', {'scope': 'construction-relevant actual harness tools',
        'semantic_lykoi_tools_exposed': [], 'provider_full_prompt_schema_capture': None,
        'schema_provenance': 'literal relevant schemas from current developer tool definitions, not inferred from calls',
        'tools': [
            {'name': 'functions.apply_patch', 'description': 'Edit files using stripped-down file-oriented diff',
             'parameters': {'type': 'object', 'required': ['patchText'],
                'properties': {'patchText': {'type': 'string'}}}},
            {'name': 'functions.bash', 'description': 'Execute a PowerShell 7+ command with optional timeout and workdir',
             'parameters': {'type': 'object', 'required': ['command'], 'properties': {
                 'command': {'type': 'string'}, 'timeout': {'type': 'integer'}, 'workdir': {'type': 'string'}}}}],
        'input_symbolic_schema': ref(ROOT / 'experiments/value_added_r6_16/intent-2.schema.json'),
        'downstream_contract': 'R6.16 generate.generate(intent, C) using unchanged production validators',
        'inventory_limitation': 'full provider-side tool payload and hidden context not attested; relevant schemas only'})
    tokens = [m['tokens'] for m in metadata if 'tokens' in m]
    write(OUT / 'CONSTRUCTION-COST.json', {'utc': now(), 'source': 'actual exported assistant metadata for relevant tool messages',
        'message_count': len(metadata), 'tool_call_count': len(tools),
        'usage': {k: sum(t.get(k, 0) for t in tokens) for k in ('input', 'output', 'reasoning')},
        'cache_read_tokens': sum(t.get('cache', {}).get('read', 0) for t in tokens),
        'cache_write_tokens': sum(t.get('cache', {}).get('write', 0) for t in tokens),
        'tokens_available_for_all_selected_messages': len(tokens) == len(metadata),
        'reported_cost_field_sum': sum(m.get('cost', 0) for m in metadata),
        'actual_api_billing_usd': None, 'commissioning_review_cost': None,
        'scope_limit': 'selected construction/verification messages only, excludes full coordinator effort; zero cost metadata is not free billing',
        'training_cost': 0, 'new_model_downloads': 0, 'package_installs': 0})
    print(json.dumps({'actual_tool_calls': len(tools), 'messages': len(metadata), 'semantic_mcp_calls': 0,
        'model_ids': sorted({m.get('modelID', 'unavailable') for m in metadata})}))


if __name__ == '__main__':
    main()
