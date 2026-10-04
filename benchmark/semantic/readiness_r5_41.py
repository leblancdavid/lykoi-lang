"""Readiness consumes prospective boundary admission, not duplicate support rules."""

from benchmark.semantic import readiness_r5_38 as semantics
from benchmark.semantic import application_boundary_r5_41 as boundary
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic.refined_generator_r5_28 import canonical, sha


def inspect(application, specification=None, declaration=None, configuration=None, obligations=None, aggregate=None):
    report = semantics.inspect(application)
    report['gaps'] = [gap for gap in report['gaps'] if gap['stage'] not in ('binding', 'transport', 'state', 'launch')]
    report['version'], report['admission_policy'] = 'R5.41', boundary.SCHEMA_ID
    def check(path, stage, action):
        try:
            return action()
        except (ValueError, KeyError, TypeError) as exc:
            report['gaps'].append({'path': path, 'stage': stage, 'reason': str(exc)})
    plans = check(['application'], 'semantic', lambda: pipeline.checked(application))
    manifest = {'application': sha(canonical(application)), 'generation': 'static-readiness-r541',
                'units': {name: plan.digest for name, plan in (plans or {}).items()}}
    path = boundary.support_report(application, specification, declaration, configuration, manifest)
    report['gaps'].extend(path['findings'])
    routes, expected = path['routes'], path['aggregate']
    if expected is not None:
        report['boundary_identity'] = sha(canonical(expected))
        if aggregate is not None and aggregate != expected:
            report['gaps'].append({'path': ['aggregate'], 'stage': 'application_profile', 'reason': 'stale aggregate identity'})
    for index, obligation in enumerate(obligations or []):
        def required(obligation=obligation):
            if obligation.get('kind') == 'public_state_alternatives':
                if routes is None or any(name not in routes for name in obligation.get('public', [])):
                    raise ValueError('checked public state-alternative coverage missing')
            elif obligation.get('kind') == 'durable_content_constraints':
                if declaration is None or 'requirements' not in obligation:
                    raise ValueError('content obligations lack typed constraint coverage references')
                for variant, rules in obligation['requirements'].items():
                    existing = declaration['alternatives'].get(variant, {}).get('constraints', [])
                    if any(rule not in existing for rule in rules):
                        raise ValueError('required declared content constraint missing')
            else:
                raise ValueError('unrecognized contract obligation; review required')
        check(['obligations', index], 'readiness', required)
    report['status'] = 'READY' if not report['gaps'] else 'NOT_READY'
    report['generated'] = report['executed'] = False
    return report
