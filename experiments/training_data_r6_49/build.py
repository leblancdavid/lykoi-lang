"""Deterministic lowering of actual AI-selected intent files; not AI decisions."""
import sys
import traceback
from prepare import ROOT, OUT, read, write, ref, now, sha

sys.path.insert(0, str(ROOT / 'experiments/value_added_r6_16'))
from generate import generate


def main():
    for p, h in read(OUT / 'SOURCE-FREEZE.json')['files'].items():
        assert sha(ROOT / p) == h, p
    files = {}
    for eid in ('S01', 'S02'):
        folder = OUT / 'episodes' / eid
        intent = read(folder / 'AI-INTENT.json')
        start = now()
        try:
            source, ir = generate(intent, 'C')
        except Exception as exc:
            write(OUT / 'BUILD-FAILURE.json', {'utc': now(), 'episode_id': eid,
                'inputs': {e: read(OUT / 'episodes' / e / 'AI-INTENT.json') for e in ('S01', 'S02')},
                'error_type': type(exc).__name__, 'error': str(exc), 'traceback': traceback.format_exc(),
                'attempt': 'second identical build call, preserving first-call defect before correction',
                'first_call': 'original real failure retained in exported OpenCode tool transcript'})
            raise
        with (folder / 'APPLICATION.py').open('x', encoding='utf-8', newline='\n') as f:
            f.write(source)
        write(folder / 'SYMBOLIC-IR.json', ir)
        write(folder / 'VALIDATION.json', {'status': 'VALID', 'utc': now(),
            'intent': ref(folder / 'AI-INTENT.json'), 'symbolic': ref(folder / 'SYMBOLIC-IR.json'),
            'application': ref(folder / 'APPLICATION.py'),
            'validator': 'unchanged generate.check + lower + generate_mutable validators',
            'corrections': 1, 'new_execution_semantics': False})
        write(folder / 'SCRIPTED-LOWERING.json', {'kind': 'DETERMINISTIC_NOT_AI_TOOL_TRAJECTORY',
            'started': start, 'finished': now(), 'function': 'R6.16 generate.generate',
            'arguments': {'intent': intent, 'track': 'C'},
            'response': {'source': ref(folder / 'APPLICATION.py'), 'ir': ref(folder / 'SYMBOLIC-IR.json')},
            'ai_selected_input': 'actual current-session apply_patch; see AI-CONSTRUCTION transcript'})
        for name in ('AI-INTENT.json', 'APPLICATION.py', 'SYMBOLIC-IR.json', 'VALIDATION.json', 'SCRIPTED-LOWERING.json'):
            p = folder / name
            files[p.relative_to(ROOT).as_posix()] = sha(p)
    write(OUT / 'CANDIDATE-FREEZE.json', {'utc': now(), 'files': files,
        'source_freeze_sha256': sha(OUT / 'SOURCE-FREEZE.json')})
    print('Two AI-selected production-backed intents validated, lowered and frozen')


if __name__ == '__main__':
    main()
