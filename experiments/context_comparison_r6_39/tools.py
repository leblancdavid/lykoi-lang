"""Common facade, including equivalent read-only context retrieval for all conditions."""
from common import ROOT, OUT, module, load, c

facade = module('r639_facade', ROOT / 'experiments/state_context_r6_38/tools.py')
TOOLS = facade.TOOLS + [facade.legacy.schema('lykoi_context',
    'Read frozen full original construction history, deterministic ordinary summary, or symbolic snapshot. '
    'Same read-only access for every condition; no acceptance expectations.',
    {'kind': {'type': 'string', 'enum': ['history', 'summary', 'snapshot']}}, ['kind'])]
facade.TOOLS = TOOLS
original_dispatch = facade.legacy.dispatch

def dispatch(name, args):
    if name == 'lykoi_context':
        c.shape(args, {'kind'}, '$/arguments')
        names = {'history': 'HISTORY.json', 'summary': 'SUMMARY.json', 'snapshot': 'SNAPSHOT.json'}
        if args['kind'] not in names: c.fail('ARGUMENT_SCHEMA', '$', 'unknown context kind')
        path = facade.STORE / names[args['kind']]
        if not path.exists(): c.fail('NOT_AVAILABLE', '$', 'base construction has no continuation context')
        return load(path)
    return original_dispatch(name, args)

facade.legacy.dispatch = dispatch
if __name__ == '__main__': facade.main()
