"""Independent observation grounding; does not call the persistence decoder."""

import json

from benchmark.semantic import application_boundary_r5_39 as boundary
from benchmark.semantic import checked_launch_r5_36 as launch
from benchmark.semantic import checked_transport_r5_35 as transport
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic.refined_generator_r5_28 import canonical, sha
from benchmark.semantic.refined_runtime_r5_28 import valid


def expected_state(data, profile):
    if data is None:
        return 'persistence_missing', None
    try:
        value = json.loads(data)
    except ValueError:
        return 'persistence_invalid_json', None
    accepted = []
    for variant, desc in profile['alternatives'].items():
        if not valid(value, desc['codec']):
            continue
        ok = True
        for rule in desc['constraints']:
            target = value
            for key in rule['path']:
                target = target[key]
            if rule['kind'] == 'equals':
                ok &= type(target) is type(rule['value']) and target == rule['value']
            else:
                field = rule['identity']
                if field is not None:
                    ok &= len(target) == len({row[field] for row in target})
                ok &= all(any(not c.isspace() for c in row[field])
                          for row in target for field in rule['nonblank'])
                ok &= all(any(type(row[field]) is type(v) and row[field] == v for v in domain)
                          for row in target for field, domain in rule['domains'].items())
        if ok:
            accepted.append(variant)
    return (None, accepted[0]) if len(accepted) == 1 else ('persistence_invalid_state', None)


def challenge(application, root, spec, declaration, config, evidence, public, before, after):
    verdict = {layer: None for layer in ('APPLICATION_PROFILE', 'LAUNCH', 'TRANSPORT',
        'INPUT_BINDING', 'STATE/PERSISTENCE', 'SEMANTIC_EXECUTION', 'OUTPUT')}
    verdict['APPLICATION_PROFILE'] = False
    try:
        manifest = json.loads((root / 'provenance.json').read_bytes())
        authority = boundary.aggregate(application, spec, declaration, config, manifest)
        boundary.check_aggregate(application, spec, declaration, config, manifest,
                                 json.loads((root / 'application_boundary.json').read_bytes()))
        verdict['APPLICATION_PROFILE'] = (manifest['application'] == sha(canonical(application)) and
                                         launch.runtime.load(root) == authority['launch'])
        if not verdict['APPLICATION_PROFILE'] or evidence is None:
            return verdict
        state, directory = launch.expected_paths(config, public['cwd'])
        invocation = evidence['invocation']
        verdict['LAUNCH'] = (evidence['application'] == authority['application'] and
            evidence['launch'] == sha(canonical(authority['launch'])) and
            evidence['generation'] == manifest['generation'] and evidence['provenance'] == sha(canonical(manifest)) and
            evidence['transport_identity'] == sha(canonical(authority['transport'])) and
            evidence['profile_id'] == config['id'] and evidence['store'] == str(state) and
            evidence['trace_directory'] == str(directory) and
            evidence['entry'] == public['command'][2] and evidence['executable'] == public['command'][0] and
            public['evidence_files'] == [str(directory / (invocation + '.json'))] and
            all(evidence[k] == public[k] for k in ('argv', 'cwd', 'pid', 'stdout', 'stderr', 'exit')) and
            evidence['pre_digest'] == transport.runtime.digest(before) and
            evidence['post_digest'] == transport.runtime.digest(after))
        if not verdict['LAUNCH']:
            return verdict
        event, semantic = evidence['transport'], evidence['semantic']
        grounded = (event is not None and event['invocation'] == invocation and event['argv'] == public['argv'] and
            event['generation'] == manifest['generation'] and all(event[k] == public[k] for k in ('stdout', 'stderr', 'exit')) and
            event['pre_digest'] == transport.runtime.digest(before) and event['post_digest'] == transport.runtime.digest(after))
        verdict['TRANSPORT'] = grounded
        if not grounded:
            return verdict
        requested = public['argv'][0] if public['argv'] else None
        entry = authority['transport']['operations'].get(requested)
        route, expected = None, None
        effective = before
        initialized = before is None and spec['persistence']['missing'] == 'INITIALIZE_DECLARED_STATE'
        if initialized:
            effective = canonical(declaration['initial'][spec['persistence']['initial']]['value'])
        category, variant = expected_state(effective, declaration)
        payload = {'code': category}
        if entry is None:
            category, payload = 'transport_failure', {'code': 'unknown_public_operation'}
        elif category is None:
            route = entry['alternatives'].get(variant)
            if route is None:
                category, payload = 'invocation_failure', {'code': 'invocation_failure'}
            else:
                try:
                    raw = transport.expected_raw(public['argv'], route)
                except (ValueError, TypeError):
                    category, payload = 'transport_failure', {'code': 'malformed_public_arguments'}
                else:
                    expected = transport.expected_binding(route['semantic'], raw, route)
                    verdict['TRANSPORT'] &= event['raw'] == raw and event['operation'] == route['semantic']
                    verdict['INPUT_BINDING'] = event['binding'] == expected
                    if expected['failures']:
                        error = expected['failures'][0]
                        code = route['argument_codes'].get(error['argument'], {}).get(error['category'], route['error_codes'][error['category']])
                        category, payload = 'binding_failure', {'code': code}
                    elif semantic is None:
                        category, payload = 'invocation_failure', {'code': 'generated_execution_rejected'}
                    else:
                        category, payload = semantic['outcome']['kind'], semantic['outcome']['value']
                        internal = {'operation': route['semantic'], 'invocation': invocation,
                                    'input': expected['input'], **event['semantic_result']}
                        effective_after = after if semantic['attempted_write'] or before is not None else effective
                        checked = pipeline.challenge(application, root, semantic, internal, effective, effective_after)
                        verdict['SEMANTIC_EXECUTION'] = checked['grounded'] and checked['conformant']
                        post_category, post_variant = expected_state(effective_after, declaration)
                        verdict['STATE/PERSISTENCE'] = (post_category is None and
                            post_variant in route['state_transition']['post'] and semantic['pre'] == json.loads(effective) and
                            event['effective_pre'] == effective.decode() and event['initialized'] == initialized and
                            event['state_variant'] == variant and event['semantic_invoked'] and
                            (semantic['attempted_write'] or before == after))
        if verdict['STATE/PERSISTENCE'] is None and entry is not None:
            reached_semantic = expected is not None and not expected['failures'] and category == 'invocation_failure' and route is not None
            verdict['STATE/PERSISTENCE'] = (before == after and semantic is None and
                event['semantic_invoked'] == reached_semantic and event['state_variant'] == variant)
        if expected is None:
            verdict['TRANSPORT'] &= event['raw'] is None and event['binding'] is None
        descriptor = route['outcomes'][category] if route and category in route['outcomes'] else spec['failures'][category]
        wanted = transport.expected_output(payload, category, descriptor)
        verdict['OUTPUT'] = (all(public[k] == v for k, v in wanted.items()) and
                             event['category'] == category and event['classification'] == descriptor['status'])
    except (ValueError, TypeError, KeyError, OSError):
        pass
    return verdict
