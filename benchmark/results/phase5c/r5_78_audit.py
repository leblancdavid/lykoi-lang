"""Read-only audit of safe R5.78 evidence; no packaging/evaluation replay."""
import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import phase5_runner_v2 as r

OUT = ROOT / 'benchmark/results/phase5c/R5_78-evidence'


def main():
    guard = r.Boundary(ROOT, [ROOT / 'benchmark/requirements/B03.md',
                            ROOT / 'benchmark/harness/profiles/B03.json',
                            ROOT / 'benchmark/harness/capabilities/B03.json',
                            ROOT / 'benchmark/results/phase5c/R5_75-evidence/opened-static-documents.json'])
    with guard.active():
        files = list(OUT.glob('*.json'))
        for path in files:
            r.verify(r.load(path))
        summary = r.load(OUT / 'summary.json')
        frozen = r.load(OUT / 'transformation-freeze.json')
        state = r.load(OUT / 'state.json')
        health = r.load(OUT / 'health.json')
        tests = r.load(OUT / 'packaging-tests.json')
        gate = r.load(OUT / 'pre-B03-gate.json')
        r.require(summary['classification'] == 'R5_78_B03_PACKAGING_GAP'
                  and summary['phase'] == 'PRE_B03_SOURCE_INTERFACE_GATE'
                  and summary['B03_package'] == 'NOT_CREATED' and summary['stopped'], 'boundary mismatch')
        r.require(all(value == 0 for value in summary['accounting'].values())
                  and summary['protected_read_attempts'] == 0, 'nonzero B03 accounting')
        r.require(summary['transformation'] == tests['freeze'] == gate['freeze'] == frozen['identity']
                  and summary['state'] == state['identity'] and summary['health'] == health['identity'],
                  'evidence linkage mismatch')
        r.require(tests['status'] == 'PASS' and tests['tests'] == 16 and
                  tests['failures'] == tests['errors'] == 0 and gate['status'] == 'FAIL'
                  and gate['error'] == {'code': 'UNREPRESENTABLE_SOURCE'}
                  and gate['protected_processing'] == 'NOT_STARTED', 'gate accounting mismatch')
        for name, pin in state['files'].items():
            r.require(name not in r.RESOURCE_PATHS and '/B03.' not in name, 'protected state member')
            r.require(r.digest((ROOT / name).read_bytes().replace(b'\r\n', b'\n')) == pin, 'state drift')
        for name, pin in frozen['files'].items():
            r.require(r.digest((ROOT / name).read_bytes()) == pin, 'transformation drift')
        r.require(state['semantic_count'] == 30 and frozen['B03_access_before_freeze'] == 0, 'freeze mismatch')
        for stage in r.HEALTH_STAGES:
            row = r.load(OUT / ('health-' + stage + '.json'))
            r.require(row['status'] == 'PASS' and row['state'] == health['state']
                      and row['protected_read_attempts'] == 0, 'health mismatch')
            r.require({k: v for k, v in row.items() if k != 'identity'} == health['results'][stage],
                      'health detail mismatch')
        r.require(r.health_record(r.current_state(ROOT), health['results']) == health, 'health state drift')
        documents = r.load(OUT / 'document-tests.json')
        r.require(documents['status'] == 'PASS' and documents['detail']['passed'] == 33
                  and documents['protected_read_attempts'] == 0, 'document tests mismatch')
        source = (ROOT / 'benchmark/evaluation/source_packaging_r5_78.py').read_text(encoding='utf-8')
        tree = ast.parse(source)
        calls = {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        r.require(not calls & {'checked', 'inspect', 'aggregate', 'support_report',
                              'authorize', 'observe', 'from_opened', 'assemble'}, 'packager evaluation call')
        names = [*frozen['files'], 'benchmark/results/phase5c/r5_78_audit.py',
                 'benchmark/results/phase5c/R5_78-TRUSTED-PREEXPOSURE-B03-V1-PACKAGING.md',
                 'docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md']
        for name in names:
            text = (ROOT / name).read_text(encoding='utf-8')
            r.require(all(line == line.rstrip() for line in text.splitlines()), 'whitespace failure')
            if name.endswith('.md') or name.endswith('source_packaging_r5_78.py'):
                r.safe_bytes({'text': text})
        matrix = r.load(OUT / 'health-matrix-schema-trace-contamination.json')['detail']
        result = r.seal({'status': 'PASS', 'evidence_files_verified': len(files),
            'state_members_verified': len(state['files']), 'transformation': frozen['identity'],
            'protected_read_attempts': guard.attempts, 'observations_replayed': 0,
            'B03_packages_opened': 0, 'B03_runner_eligibility': 'NOT_VERIFIED_NO_PACKAGE',
            'publication': 'PASS', 'core_semantics': 30, 'profiles': matrix['profiles'],
            'rows': matrix['rows'], 'trace_leaves': matrix['trace_leaves'],
            'auditor': r.digest(Path(__file__).read_bytes())})
        r.persist(OUT / 'audit.json', result)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
