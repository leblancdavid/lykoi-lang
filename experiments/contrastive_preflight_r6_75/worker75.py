"""Same prospective entry point for dry qualification and later authorized execution."""
import os
import sys
import context75 as x


def effective_source():
    source = (x.OLD/'EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    source = source.replace('from runtime import ', 'from runtime75 import ')
    source = source.replace("__import__('runtime')", "__import__('runtime75')")
    source = source.replace("'round': 'R6.74'", "'round': 'R6.75'")
    source = source.replace('def train():\n', "def train():\n    if os.environ.get('LYKOI_R6_75_DRY_RUN') == '1':\n        return __import__('runtime75').launch_check('train')\n", 1)
    return source


def main():
    dry = '--dry-run' in sys.argv
    if dry:
        x.guard()
        assert os.environ.get('LYKOI_R6_75_DRY_RUN') == '1'
    else:
        assert os.environ.get('LYKOI_R6_75_EXECUTION_AUTHORIZED') == '1', 'Separate owner authorization required'
        assert os.environ.get('LYKOI_R6_75_DRY_RUN') != '1'
    x.frozen_check()
    source = (x.OUT/'EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    assert source == effective_source()
    namespace = {}
    exec(compile(source, 'r675-worker', 'exec'), namespace)
    import runtime75
    assert runtime75.diagnostic_source() == (x.OUT/'EFFECTIVE-DIAGNOSTIC.py.txt').read_text(encoding='utf-8')
    mode = sys.argv[1]
    result = namespace['train']() if mode == 'train' else runtime75.diagnostic(mode)
    if dry:
        import json
        print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
