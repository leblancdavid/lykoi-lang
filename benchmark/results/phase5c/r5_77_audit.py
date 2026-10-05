"""Read-only independent V1 evidence audit; never replays a static observation."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import phase5_runner_v2 as r
from benchmark.evaluation import benchmark_documents_v1 as d

OUT = ROOT / 'benchmark/results/phase5c/R5_77-evidence'


def main():
    guard = r.Boundary(ROOT, [ROOT / 'benchmark/requirements/B03.md',
                            ROOT / 'benchmark/harness/profiles/B03.json',
                            ROOT / 'benchmark/harness/capabilities/B03.json',
                            ROOT / 'benchmark/results/phase5c/R5_75-evidence/opened-static-documents.json'])
    with guard.active():
        count = 0
        for path in OUT.rglob('*.json'):
            r.verify(r.load(path))
            count += 1
        summary = r.load(OUT / 'summary.json')
        r.require(summary['classification'] == 'R5_77_BENCHMARK_DOCUMENT_CONTRACT_V1_QUALIFIED', 'classification mismatch')
        state = r.load(OUT / 'state.json')
        for name, pin in state['files'].items():
            r.require(name not in r.RESOURCE_PATHS and '/B03.' not in name, 'protected state member')
            r.require(r.digest((ROOT / name).read_bytes().replace(b'\r\n', b'\n')) == pin, 'state member drift')
        r.require(state['semantic_count'] == 30, 'semantic drift')
        health = r.load(OUT / 'health.json')
        for stage in r.HEALTH_STAGES:
            row = r.load(OUT / ('health-' + stage + '.json'))
            r.require(row['status'] == 'PASS' and row['state'] == health['state'], 'health linkage mismatch')
        expected = {'supported': 'STATIC_SUPPORTED', 'unsupported': 'STATIC_UNSUPPORTED',
                    'malformed': 'DOCUMENT_FAILURE', 'incomplete': 'DOCUMENT_FAILURE',
                    'public-seed-bank': 'STATIC_SUPPORTED'}
        for name, classification in expected.items():
            row = r.load(OUT / (name + '.json'))
            r.require(row['result']['classification'] == classification and row['post_check']['status'] == 'PASS', 'outcome mismatch')
            r.require(row['freeze']['health'] == health['identity'] and row['freeze']['state'] == health['state'], 'freeze mismatch')
            ledger = r.Ledger(OUT / (name + '-ledger'))
            r.require(ledger.status() == 'one' and row['events'] == list(r.TRANSITIONS), 'lifecycle mismatch')
            r.require(ledger.events()[-1]['details']['result'] == row['result'], 'completion result mismatch')
            if row['result']['static_evaluated']:
                representation = r.load(OUT / (name + '-representation.json'))
                contract = d.verify_contract(representation['contract'])
                r.require(d.assemble(representation['documents']) == contract, 'representation identity mismatch')
                r.require(contract['identity'] == row['result']['contract_identity'], 'static identity mismatch')
                committed = sorted(v['commitment'] for v in row['commitment']['resources'].values())
                r.require(sorted(d.identity(doc) for doc in representation['documents']) == committed, 'document commitment mismatch')
                for field in ('generation', 'execution', 'acceptance', 'repair'):
                    r.require(row['result'][field] == 0, 'non-static work')
        matrix = r.load(OUT / 'health-matrix-schema-trace-contamination.json')['detail']
        r.require(matrix['schema']['valid'] and matrix['traceability']['valid']
                  and matrix['contamination'] == 'clean' and matrix['core_semantics'] == 30, 'matrix failure')
        names = [*state['files'].keys()]
        new_names = ['benchmark/evaluation/benchmark_documents_v1.py',
                     'benchmark/evaluation/test_benchmark_documents_v1.py',
                     'benchmark/results/phase5c/r5_77_qualification.py',
                     'benchmark/results/phase5c/r5_77_audit.py',
                     'schema/benchmark-document-contract-v1.schema.json',
                     'docs/benchmark-document-contract-v1.md',
                     'benchmark/results/phase5c/R5_77-VERSIONED-GENERIC-BENCHMARK-DOCUMENT-CONTRACT.md']
        for name in new_names:
            text = (ROOT / name).read_text(encoding='utf-8')
            r.require(all(line == line.rstrip() for line in text.splitlines()), 'new-file whitespace')
            if name.endswith(('.md', '.json')) or name.endswith('benchmark_documents_v1.py') and '/test_' not in name:
                r.safe_bytes({'text': text})
        # No actual benchmark content is opened, no historical ledger is loaded.
        # Intentional test-source rejection literals are not published as evidence values.
        result = r.seal({'status': 'PASS', 'evidence_files_verified': count,
            'state_members_verified': len(names), 'protected_read_attempts': guard.attempts,
            'core_semantics': 30, 'completed_lifecycles': 5, 'observations_replayed': 0,
            'profiles': matrix['profiles'], 'rows': matrix['rows'], 'trace_leaves': matrix['trace_leaves'],
            'publication': 'PASS', 'auditor': r.digest(Path(__file__).read_bytes())})
        r.persist(OUT / 'audit.json', result)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
