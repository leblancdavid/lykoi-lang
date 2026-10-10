import importlib.util, json, pathlib, sys, time
folder = pathlib.Path('D:\\Dev\\axiom\\experiments\\value_added_r6_16')
sys.path.insert(0, str(folder))
spec = importlib.util.spec_from_file_location('generator', folder / 'generate.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
start = time.perf_counter()
source, ir = module.generate(json.loads(pathlib.Path(sys.argv[1]).read_text()), 'C')
elapsed = time.perf_counter() - start
out = pathlib.Path(sys.argv[2]); out.mkdir()
(out / 'application.py').write_text(source, encoding='utf-8')
(out / 'ir.json').write_text(json.dumps(ir, indent=2), encoding='utf-8')
(out / 'timing.json').write_text(json.dumps({'validation_lowering_seconds': elapsed}))
print(json.dumps({'validation_lowering_seconds': elapsed, 'generated': str(out / 'application.py')}))
