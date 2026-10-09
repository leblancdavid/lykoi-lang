"""Deterministic, exact-state context, with fail-closed authoritative comparison."""
from common import c, digest, package


def generate(registry, requirement, objective, bindings, constraints):
    if not requirement or not objective or not constraints or set(bindings) != {'CallerA', 'CallerB'}:
        c.fail('INCOMPLETE_STATE', '$/snapshot', 'required facts and both caller bindings required')
    current = registry.read()
    if current['pending']:
        c.fail('INCOMPLETE_STATE', '$/snapshot', 'pending registry write')
    definitions = {}
    validations = {}
    for name, pin in sorted(bindings.items()):
        closure = registry.retrieve(pin=pin, expected=current['token'])
        if next(d for d in closure if d['identity'] == pin)['name'] != name:
            c.fail('IDENTITY', '$/snapshot', 'caller name mismatch')
        definitions.update({d['identity']: d for d in closure})
        expanded = c.expand(package(registry, pin))
        validations[pin] = {k: expanded[k] for k in ('program_identity', 'plan_identity', 'nodes')}
    state = current['state']
    # Lifecycle metadata is retained verbatim, not inferred from definition names.
    body = dict(version='r638-snapshot-1', requirement=requirement, objective=objective,
        constraints=constraints, registry_token=current['token'], generation=current['generation'],
        definitions=definitions, signatures={p: [d['params'], d['result_type']] for p, d in sorted(definitions.items())},
        dependencies={p: d['dependencies'] for p, d in sorted(definitions.items())},
        caller_bindings=bindings, successors=state['successors'], migrations=state['migrations'],
        validation=validations, retrieval_references={p: {'identity': p, 'kind': 'definition'} for p in sorted(state['definitions'])})
    return dict(body, identity=digest(body))


def verify(snapshot, registry, requirement, objective, bindings, constraints):
    body = {k: v for k, v in snapshot.items() if k != 'identity'}
    if snapshot.get('identity') != digest(body):
        c.fail('IDENTITY', '$/snapshot', 'snapshot content tampered')
    expected = generate(registry, requirement, objective, bindings, constraints)
    if snapshot != expected:
        c.fail('STALE_OR_INCOMPLETE_STATE', '$/snapshot', 'authoritative state/facts mismatch')
    return True


def retrieve(registry, identity, kind):
    c.digest(identity, '$/retrieval')
    definitions = registry.retrieve(pin=identity)
    state = registry.read()['state']
    if kind == 'definition':
        return definitions
    if kind == 'dependencies':
        return dict(closure={d['identity']: d['dependencies'] for d in definitions}, dependents=registry.dependents(identity))
    if kind == 'validation':
        # Parameterized abstractions use the unchanged registry admission probe.
        root = state['definitions'][identity]
        ex = registry.probe(root, state['definitions'], 64) if root['params'] else c.expand(package(registry, identity))
        return dict(status='valid', program_identity=ex['program_identity'], plan_identity=ex['plan_identity'], nodes=ex['nodes'], map=ex['map'])
    if kind == 'history':
        return dict(successors=state['successors'], migrations=state['migrations'])
    if kind == 'identity':
        return dict(identity=identity, canonical_identity=c.identity(state['definitions'][identity]), registry_token=registry.read()['token'])
    c.fail('ARGUMENT_SCHEMA', '$/retrieval', 'unsupported bounded retrieval kind')
