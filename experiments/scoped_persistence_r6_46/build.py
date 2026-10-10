"""Deterministic successor generation from preserved intent plus explicit profile."""
import importlib.util
import sys
from prepare import ROOT, HERE, OUT, load, sha, save, verify


def historical_generate(intent):
    folder = ROOT / 'experiments/value_added_r6_16'
    sys.path.insert(0, str(folder))
    spec = importlib.util.spec_from_file_location('r646_historical_generator', folder / 'generate.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate(intent, 'C')


def generate(intent, declaration):
    source, ir = historical_generate(intent)
    adapter = (HERE / 'adapter.py').read_text(encoding='utf-8')
    # Validate the declaration without running application code or IO.
    ns = {'SPEC': ir['base'], 'decode_state': None, 'Failure': Exception}
    exec(compile(adapter, str(HERE / 'adapter.py'), 'exec'), ns)
    ns['install_list_storage_profile'](ns, declaration)
    if declaration is not None:
        source += '\n' + adapter + '\ninstall_list_storage_profile(globals(), ' + repr(declaration) + ')\n'
    return source, ir


def main():
    verify(load(OUT / 'BASELINE.json')['protected_files'])
    verify(load(OUT / 'FREEZE.json')['files'])
    old = ROOT / 'benchmark/results/phase6/r6_44'
    intent = old / 'submissions/B/final.json'
    historical = old / 'build/submitted/B/final/application.py'
    source, ir = generate(load(intent), load(HERE / 'profile.json'))
    prior, prior_ir = historical_generate(load(intent))
    assert prior.encode('utf-8') == historical.read_bytes()
    assert ir == prior_ir == load(old / 'build/submitted/B/final/ir.json')
    destination = OUT / 'build/application.py'
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('x', encoding='utf-8', newline='\n') as f:
        f.write(source)
    save(OUT / 'build/ir.json', ir)
    inputs = [intent, historical, old / 'build/baseline-accepted/B/application.py',
              HERE / 'profile.json', HERE / 'adapter.py', HERE / 'build.py']
    save(OUT / 'IMPLEMENTATION.json', dict(inputs={p.relative_to(ROOT).as_posix(): sha(p) for p in inputs},
        application_sha256=sha(destination), ir_sha256=sha(OUT / 'build/ir.json'),
        predecessor_regeneration_exact=True, ir_unchanged=True, application_policy_unchanged=True,
        source_change='unchanged regenerated predecessor prefix plus explicit scoped decoder integration',
        profile=load(HERE / 'profile.json')))
    print('Built successor; predecessor regeneration and IR exact; scoped adapter only.')


if __name__ == '__main__':
    main()
