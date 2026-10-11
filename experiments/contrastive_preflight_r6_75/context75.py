"""Additive successor context; historical modules retain their own globals."""
import copy
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'experiments/contrastive_preflight_r6_74'))
import integration as prior

OUT = ROOT/'benchmark/results/phase6/r6_75'
OLD = prior.OUT
STORE, PYTHON = prior.STORE, prior.PYTHON
ARTIFACTS = STORE/'r6-75'
read, sha, identity, canonical = prior.read, prior.sha, prior.identity, prior.canonical
serialize, score, reconstruct = prior.serialize, prior.score, prior.reconstruct
file_manifest, q52 = prior.file_manifest, prior.q52
CompletionLanguage = prior.CompletionLanguage
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', CUDA_VISIBLE_DEVICES='',
           HF_HUB_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1', TOKENIZERS_PARALLELISM='false')


def write(name, value):
    prior_path = prior.OUT
    try:
        prior.OUT = OUT
        prior.write(name, value)
    finally:
        prior.OUT = prior_path


def guard():
    assert Path(sys.executable).resolve() == PYTHON.resolve()
    assert sys.version_info[:3] == (3, 12, 11)
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == ''
    assert os.environ.get('HF_HUB_OFFLINE') == '1'


def rows():
    return read(OLD/'DATASET.json')['records']


def corrected(row):
    result = copy.deepcopy(row)
    if row['partition'] == 'training_calibration':
        return result
    scope = result['scope']
    scope['name'] = row['scope']['name'].replace('-', '_')
    scope.pop('identity')
    scope['identity'] = identity(scope)
    result['scope_identity'] = scope['identity']
    result['prompt'][1]['content'] = serialize(dict(requirement=result['requirement'], scope=scope))
    return result


def check_remapping(original, successor):
    assert len(original['records']) == len(successor['records']) == 30
    for old, new in zip(original['records'], successor['records']):
        assert new == corrected(old), 'IDENTIFIER_OR_EXPECTATION_DRIFT'
    assert len({r['scope']['name'] for r in successor['records'][:24]}) == 24


def frozen_check():
    for path, digest in read(OUT/'PREFLIGHT-FREEZE.json')['files'].items():
        assert sha(ROOT/path) == digest, path
    cfg = read(OUT/'TRAINING-CONFIGURATION.json')['configuration']
    assert identity(cfg) == read(OUT/'TRAINING-CONFIGURATION.json')['canonical_sha256']
    return dict(training_configuration_identity=identity(cfg))
