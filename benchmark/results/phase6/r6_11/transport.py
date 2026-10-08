"""Unscored hex/JSON transport and result projection; no task behavior."""
import importlib.util
import json
from pathlib import Path
import sys


def main():
    track, artifact = sys.argv[1:]
    data = bytes.fromhex(json.loads(sys.stdin.read())['hex'])
    if track == 'conventional':
        spec = importlib.util.spec_from_file_location('candidate', artifact)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.solve(data)
    else:
        root = Path(__file__).resolve().parents[4]
        sys.path.insert(0, str(root / 'experiments/semantic_interpreter'))
        from interpreter import execute
        result = execute(json.loads(Path(artifact).read_text(encoding='utf-8')),
                         data, limits={'input': 64}, assemble=False)
        if result['status'] == 'success':
            result = {'status': 'success', 'value': result['value']}
        elif result['status'] == 'reject':
            result = {'status': 'reject', 'code': result['error']['code'],
                      'offset': result['error']['offset']}
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
