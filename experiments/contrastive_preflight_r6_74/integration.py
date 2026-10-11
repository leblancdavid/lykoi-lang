"""Round-specific identity helpers; avoid historical generic common imports."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_74'
PRIOR = ROOT / 'benchmark/results/phase6/r6_73/qualification_2'
sys.path.insert(0, str(ROOT / 'experiments/contrastive_binding_r6_73'))
from reconstruct import c, reconstruct, serialize, parse, Rejection, scorer, assembly
from compact_decoder import CompletionLanguage


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


publisher = load('r674_prior_publication', 'experiments/contrastive_binding_r6_73/publish.py')
q = publisher.q.q
f = publisher.f
STORE, PYTHON, q52 = f.STORE, f.PYTHON, f.q52
ARTIFACTS = STORE / 'r6-74'
canonical = c.canonical
identity = q.pin
sha = f.sha
read = f.read
file_manifest = f.file_manifest


def write(name, value):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def rows():
    return read(OUT / 'DATASET.json')['records']


def score(text, row):
    """Exact semantic dimensions plus unchanged authoritative functional scorer."""
    result = dict(strict_decision_validity=False, correct_operation='NOT_REACHED',
                  correct_operand_identities='NOT_REACHED', correct_operand_order='NOT_REACHED',
                  correct_dependencies='NOT_REACHED', reconstruction_success=False,
                  functional_acceptance='NOT_REACHED', accepted=False)
    try:
        decision, _ = parse(text)
        expected = row['target']
        result.update(strict_decision_validity=True,
                      correct_operation=decision['op'] == expected['op'],
                      correct_operand_identities=sorted(serialize(decision[k]) for k in ('left', 'right')) ==
                          sorted(serialize(expected[k]) for k in ('left', 'right')),
                      correct_operand_order=all(canonical(decision[k]) == canonical(expected[k]) for k in ('left', 'right')),
                      correct_dependencies=decision['deps'] == expected['deps'])
        action, after, validation = reconstruct(text, row['scope'])
        again = reconstruct(text, row['scope'])
        assert canonical((action, after, validation)) == canonical(again)
        action_row = dict(before=row['scope'], completion=[dict(role='assistant', content=serialize(action))], cases=row['cases'])
        functional = scorer.score(serialize(action), action_row)
        result.update(reconstruction_success=True, functional_acceptance=functional['accepted'],
                      action_identity=identity(action), observations=functional['observations'])
        result['accepted'] = all(result[k] is True for k in
            ('strict_decision_validity', 'correct_operation', 'correct_operand_identities',
             'correct_operand_order', 'correct_dependencies', 'reconstruction_success', 'functional_acceptance'))
        result['category'] = 'accepted' if result['accepted'] else 'valid_but_wrong'
    except Rejection as exc:
        result.update(category=exc.category, code=exc.code)
    return result


def frozen_check():
    for path, digest in read(OUT / 'SOURCE-FREEZE.json')['files'].items():
        assert sha(ROOT / path) == digest, path
    for path, digest in read(OUT / 'CONFIGURATION-FREEZE.json')['files'].items():
        assert sha(ROOT / path) == digest, path
    cfg = read(OUT / 'TRAINING-CONFIGURATION.json')['configuration']
    assert identity(cfg) == read(OUT / 'TRAINING-CONFIGURATION.json')['canonical_sha256']
    assert identity(read(OUT / 'DATASET.json')) == cfg['dataset_identity']
    assert identity(read(OUT / 'SAMPLING.json')) == cfg['sampling_identity']
    return dict(training_configuration_identity=identity(cfg))
