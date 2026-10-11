"""Identity-only preflight and pre-candidate expectation freeze."""
import importlib.util
import json
from pathlib import Path
import sys
from fixtures import expectations, pin

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_73'
sys.path.insert(0, str(ROOT / 'experiments/semantic_binding_r6_72'))
spec = importlib.util.spec_from_file_location('r673_prior', ROOT / 'experiments/semantic_binding_r6_72/run.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
f = prior.f


def write(name, value):
    path = OUT / name
    assert not path.exists(), path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def baseline():
    return dict(inherited=prior.baseline(), r6_72=f.publication('r6_72'))


def check_freeze():
    frozen = f.read(OUT / 'EXPECTATION-FREEZE.json')
    for path, digest in frozen['files'].items():
        assert f.sha(ROOT / path) == digest, path
    assert baseline() == f.read(OUT / 'BASELINE.json')


def freeze():
    write('BASELINE.json', baseline())
    # Reserve structurally different families before creating any training rows.
    write('EVALUATION-RESERVATIONS.json', dict(version='r6.73-reservations-1',
        partition='evaluation_exploratory', solutions_published=False,
        families=[dict(id='E01-boundary-negation', structure='Inclusive negated bound with Int64 boundary values and type distractors'),
                  dict(id='E02-two-independent-prefixes', structure='Operands from independent prefix sources with reordered scope and distractors'),
                  dict(id='E03-unit-equality', structure='Unit equality and typed null with Bool/Int64 distractors')],
        exclusion='No training record from these families; no solution/fixture materialized in R6.73.',
        independence='Coordinator reservation only; future results exploratory, not independently withheld generalization.'))
    write('ACCEPTANCE-EXPECTATIONS.json', dict(version='r6.73-expectations-1', records=expectations(),
        review='COORDINATOR_ONLY; no independent reviewer available or delegated',
        expected_values_source='Literal manual arithmetic/logic, never reconstructed candidate output',
        ordering='Explicit left/right even for commutative operations',
        dependencies='Explicit sorted unique direct references; no transitive closure inference'))
    paths = [HERE / 'fixtures.py', HERE / 'freeze.py', HERE / 'SPECIFICATION.md', HERE / 'PROTOCOL.md',
             OUT / 'EVALUATION-RESERVATIONS.json', OUT / 'ACCEPTANCE-EXPECTATIONS.json']
    write('EXPECTATION-FREEZE.json', dict(version='r6.73-freeze-1', stage='BEFORE_RECONSTRUCTOR_IMPLEMENTATION_AND_CANDIDATES',
        files={p.relative_to(ROOT).as_posix(): f.sha(p) for p in paths}, coordinator_only=True))
    print('PASS baseline and pre-candidate freeze: 18 positives, 36 labeled alternatives, three reserved families')


if __name__ == '__main__':
    {'freeze': freeze, 'verify': check_freeze}[sys.argv[1]]()
