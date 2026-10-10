"""Preserve the actual owner request, without exporting unrelated session data."""
import json
import re
import subprocess
from prepare import ROOT, OUT, read, write, now
from transcript import SESSION


def main():
    p = subprocess.run(['pwsh', '-NoProfile', '-Command',
        'opencode export ' + SESSION + ' --pure'], cwd=ROOT, capture_output=True, text=True,
        encoding='utf-8', timeout=90)
    assert p.returncode == 0
    exported = json.loads(p.stdout)
    parts = {part.get('id'): part for m in exported.get('messages', []) for part in m.get('parts', [])}
    for row in read(OUT / 'AI-CONSTRUCTION-TRANSCRIPT.json')['entries']:
        for call in row['actual_tool_calls']:
            state = parts[call['part_id']]['state']
            assert call['arguments'] == state.get('input', {})
            assert call['response'] == state.get('output')
    found = []
    for message in exported.get('messages', []):
        info = message.get('info', {})
        if info.get('role') != 'user':
            continue
        for part in message.get('parts', []):
            text = part.get('text', '') if part.get('type') == 'text' else ''
            if 'R6.49' in text and 'Training Data Admission Policy' in text:
                found.append({'message_id': info['id'], 'part_id': part.get('id'), 'text': text})
    assert len(found) == 1, 'exact original owner authorization message required'
    assert 'Do not train or fine-tune a model.' in found[0]['text']
    assert not re.search(r'(?:sk-[A-Za-z0-9_-]{32,}|ghp_[A-Za-z0-9]{32,}|hf_[A-Za-z0-9]{32,})', found[0]['text'])
    write(OUT / 'OWNER-AUTHORIZATION.json', {'session_id': SESSION, 'captured_utc': now(),
        'original_owner_message': found[0],
        'scope_interpretation': 'bounded synthetic-data pilot and training-candidate review; no actual training, deployment or general redistribution authorization',
        'prior_construction_transcript_matches_utf8_reexport': True,
        'provenance': 'actual active-session user text recovered by OpenCode export, not recreated from memory'})
    print('Exact original owner authorization retained')


if __name__ == '__main__':
    main()
