"""Ephemeral schema-envelope controls only; no dataset/export/model operations."""
import copy
import json
from pathlib import Path
import sys

import jsonschema
from referencing import Registry, Resource

OUT = Path(__file__).resolve().parents[2] / 'benchmark/results/phase6/r6_62'
schemas = {}
for path in OUT.glob('*.schema.json'):
    schema = json.loads(path.read_text(encoding='utf-8'))
    jsonschema.Draft202012Validator.check_schema(schema)
    schemas[schema['$id']] = schema
assert len(schemas) == 4
registry = Registry().with_resources((key, Resource.from_contents(value)) for key, value in schemas.items())
ref = {'path': 'SCHEMA_SHAPE_ONLY_NOT_AN_ARTIFACT', 'sha256': '0' * 64}
fixture = {
    'version': '',
    'requirement': {'episode': 'shape-only', 'source': ref, 'frc': ref, 'family': 'shape-only', 'component': 'shape-only'},
    'profile': {'name': 'shape-only', 'contract': ref, 'foundation': ref},
    'context': {'messages': [{'role': 'user', 'content': 'schema shape only'}], 'state': None, 'interface': ref},
    'target': {},
    'evidence': {'status': 'QUALIFIED', 'target_source': ref, 'validation': ref, 'acceptance': ref, 'observations': ref, 'admission': ref},
    'provenance': {'class': 'verified_endpoint', 'trace': None, 'limitations': ['not a qualified record']},
    'partition': {'split': 'training_development', 'export': 'training_allowed', 'ledger': ref}}
controls = 0
for name in ('A', 'B', 'C'):
    validator = jsonschema.Draft202012Validator(schemas[f'urn:lykoi:r6.62:{name}:1'], registry=registry)
    assert not validator.is_valid({})
    f = copy.deepcopy(fixture)
    f['version'] = f'lykoi-supervision-{name}-1'
    f['target'] = {'format': {'A': 'complete_symbolic_package', 'B': 'bounded_structured_update', 'C': 'typed_semantic_call'}[name],
                   'text': 'SCHEMA SHAPE ONLY', 'schema': ref}
    if name != 'A':
        f['context']['state'] = ref
        f['provenance'] = {'class': 'deterministic_expert_demonstration', 'trace': ref, 'limitations': ['shape only']}
        f['target'].update(ordinal=0, after=ref)
    if name == 'C':
        del f['target']['schema']
        f['target'].update(tool='shape-only', arguments={}, arguments_schema=ref, response=ref)
    validator.validate(f)
    negative = copy.deepcopy(f)
    negative['partition']['split'] = 'evaluation_only'
    assert not validator.is_valid(negative)
    negative = copy.deepcopy(f)
    negative['evidence']['status'] = 'NOT_REACHED'
    assert not validator.is_valid(negative)
    negative = copy.deepcopy(f)
    negative['unrecorded_reasoning'] = 'forbidden'
    assert not validator.is_valid(negative)
    negative = copy.deepcopy(f)
    negative['requirement']['source']['sha256'] = 'not-an-identity'
    assert not validator.is_valid(negative)
    if name != 'A':
        negative = copy.deepcopy(f)
        negative['context']['state'] = None
        assert not validator.is_valid(negative)
        negative = copy.deepcopy(f)
        negative['provenance']['trace'] = None
        assert not validator.is_valid(negative)
        controls += 2
    controls += 6
print(json.dumps({'passed': True, 'controls': controls, 'python': sys.version,
                  'schema_only': True, 'training_records_created': 0}))
