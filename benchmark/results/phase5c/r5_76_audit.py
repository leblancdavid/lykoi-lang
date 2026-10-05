"""Read-only audit of fresh non-protected evidence; no observation replay."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import phase5_runner_v2 as r

OUT = ROOT / 'benchmark/results/phase5c/R5_76-evidence'


def main():
    guard = r.Boundary(ROOT, [ROOT / 'benchmark/requirements/B03.md',
                             ROOT / 'benchmark/harness/profiles/B03.json',
                             ROOT / 'benchmark/harness/capabilities/B03.json',
                             ROOT / 'benchmark/results/phase5c/R5_75-evidence/opened-static-documents.json'])
    with guard.active():
        count = 0
        for path in OUT.rglob('*.json'):
            value = r.load(path)
            r.verify(value)
            count += 1
        summary = r.load(OUT / 'summary.json')
        r.require(summary['classification'] == 'R5_76_DOCUMENT_ENVELOPE_GAP', 'classification changed')
        state = r.load(OUT / 'state.json')
        for name, pin in state['files'].items():
            r.require(name not in r.RESOURCE_PATHS and '/B03.' not in name, 'protected state member')
            r.require(r.digest((ROOT / name).read_bytes().replace(b'\r\n', b'\n')) == pin, 'state member drift')
        r.require(state['semantic_count'] == 30, 'semantic drift')
        expected = {'supported': 'SYNTHETIC_STATIC_PASS', 'unsupported': 'SYNTHETIC_STATIC_UNSUPPORTED',
                    'malformed': 'SYNTHETIC_FIXTURE_MALFORMED', 'incomplete': 'SYNTHETIC_FIXTURE_INCOMPLETE'}
        for name, classification in expected.items():
            row = r.load(OUT / (name + '.json'))
            r.require(row['result']['classification'] == classification and row['post_check']['status'] == 'PASS',
                      'synthetic outcome mismatch')
            ledger = r.Ledger(OUT / (name + '-synthetic-ledger'))
            r.require(ledger.status() == 'one' and row['events'] == list(r.TRANSITIONS), 'lifecycle mismatch')
            r.require(ledger.events()[-1]['details']['result'] == row['result'], 'result linkage mismatch')
        matrix = r.load(OUT / 'health-matrix-schema-trace-contamination.json')['detail']
        r.require(matrix['core_semantics'] == 30 and matrix['schema']['valid']
                  and matrix['traceability']['valid'] and matrix['contamination'] == 'clean', 'health mismatch')
        # Include untracked source/prose in whitespace and publication checking.
        names = ['benchmark/evaluation/test_document_envelope_r5_76.py',
                 'benchmark/results/phase5c/r5_76_investigation.py',
                 'benchmark/results/phase5c/r5_76_audit.py',
                 'benchmark/results/phase5c/R5_76-GENERIC-DOCUMENT-ENVELOPE-CONTRACT-QUALIFICATION.md']
        for name in names:
            text = (ROOT / name).read_text(encoding='utf-8')
            r.require(all(line == line.rstrip() for line in text.splitlines()), 'new-file whitespace')
            if name.endswith('.md'):
                r.safe_bytes({'text': text})
        result = r.seal({'status': 'PASS', 'evidence_files_verified': count,
            'state_members_verified': len(state['files']), 'protected_read_attempts': guard.attempts,
            'core_semantics': 30, 'profiles': matrix['profiles'], 'rows': matrix['rows'],
            'trace_leaves': matrix['trace_leaves'], 'publication': 'PASS',
            'observations_replayed': 0, 'auditor': r.digest(Path(__file__).read_bytes())})
        r.persist(OUT / 'audit.json', result)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
