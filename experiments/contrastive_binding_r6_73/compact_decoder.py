"""Scope-bounded prefix language. No requirement or semantic-answer inputs."""
from itertools import combinations, product
from reconstruct import serialize


def language(scope):
    names = sorted([p['name'] for p in scope['params']] + [s['id'] for s in scope['steps']])
    assert len(names) == len(set(names))
    operands = [{'ref': n} for n in names]
    for value in scope['literals']:
        typ = 'Bool' if type(value) is bool else ('Int64' if type(value) is int else 'Unit')
        operands.append({'literal': dict(type=typ, value=value)})
    operands = list({serialize(a): a for a in operands}.values())
    dependencies = [list(ds) for length in range(3) for ds in combinations(names, length)]
    return tuple(serialize(dict(op=op, left=a, right=b, deps=ds))
                 for op, a, b, ds in product(('add', 'le', 'eq'), operands, operands, dependencies))


class CompletionLanguage:
    def __init__(self, scope):
        self.texts = language(scope)
        self.terminals = set(self.texts)
        self.prefixes = {text[:i] for text in self.texts for i in range(len(text) + 1)}

    def accepts(self, text):
        return text in self.prefixes, text in self.terminals

    def allowed(self, tokenizer, ids, token_ids):
        prefix = tokenizer.decode(ids, skip_special_tokens=False)
        assert prefix in self.prefixes, 'COMPACT_PREFIX_REJECTED'
        if prefix in self.terminals:
            return [tokenizer.eos_token_id]
        # Decode the full appended sequence, not concatenated singleton pieces.
        return [i for i in token_ids if i not in tokenizer.all_special_ids
                and self.accepts(tokenizer.decode(ids + [i], skip_special_tokens=False))[0]]
