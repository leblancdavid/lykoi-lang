"""Version 2: canonical compact wire order; semantic renderer unchanged from v1."""
import json
from reconstruct_v1 import Rejection, c, assembly, scorer, parse, reconstruct


def serialize(obj):
    if type(obj) is dict and set(obj) == {'op', 'left', 'right', 'deps'}:
        ordered = {key: obj[key] for key in ('op', 'left', 'right', 'deps')}
        for key in ('left', 'right'):
            arg = ordered[key]
            if type(arg) is dict and set(arg) == {'literal'}:
                literal = arg['literal']
                if type(literal) is dict and set(literal) == {'type', 'value'}:
                    ordered[key] = {'literal': {name: literal[name] for name in ('type', 'value')}}
        # Content identity, including types, must survive envelope ordering.
        assert c.canonical(ordered) == c.canonical(obj)
        obj = ordered
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True, allow_nan=False)
