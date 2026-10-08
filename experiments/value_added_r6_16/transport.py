"""One operation per fresh process. No application relation computed here."""
import importlib.util
import json
import sys


def main():
    spec = importlib.util.spec_from_file_location('submission', sys.argv[1])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    request = json.loads(sys.stdin.read())
    providers = {name: (lambda value=value: value) for name, value in request['providers'].items()}
    result = module.handle(request['op'], request['args'], providers)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
