"""Prospective aggregate admission; historical R5.39 remains reproducible.

The present public profile model exposes every invocation input slot. Internal
external-capability slots are not invocation inputs and need no argv mapping.
There is no implicit internal-input exemption in this versioned profile model.
"""

from benchmark.semantic import application_boundary_r5_39 as previous
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic.refined_generator_r5_28 import canonical, sha

SCHEMA = {'version': 'R5.40', 'aggregate': previous.SCHEMA,
          'input_coverage': 'all declared invocation slots, including optional',
          'internal_input_policy': 'unsupported; capability slots are separate',
          'core_constructs': 30}
SCHEMA_ID = sha(canonical(SCHEMA))


def complete_inputs(application, specification):
    plans = pipeline.checked(application)
    for route in specification['operations']:
        for item in route.get('alternatives', {'state': route}).values():
            name = item['semantic']
            if name not in plans:
                raise ValueError('unknown semantic operation')
            mapped = [argument['slot'] for argument in item['arguments']]
            fields = set(plans[name].slots['input']['record'])
            if len(mapped) != len(set(mapped)) or set(mapped) != fields:
                raise ValueError('incomplete/duplicate public input mapping (including optional slots)')
    return plans


def aggregate(application, specification, declaration, configuration, manifest):
    complete_inputs(application, specification)
    return previous.aggregate(application, specification, declaration, configuration, manifest)


def check_aggregate(application, specification, declaration, configuration, manifest, profile):
    expected = aggregate(application, specification, declaration, configuration, manifest)
    if profile != expected:
        raise ValueError('stale binding/transport/aggregate profile identity')
    return expected
