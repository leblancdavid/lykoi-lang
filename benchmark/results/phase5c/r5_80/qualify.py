"""Reproduce public R5.80 evidence; explicit file inventory, no discovery.

Outputs are prospective round records only. Never runs benchmark authorizations,
protected opening, static observations, program generation or application execution.
"""
import hashlib
import json
import re

from benchmark.evaluation import formal_requirements_r5_80 as f
from benchmark.results.phase5c.r5_80 import fixtures

HERE = fixtures.HERE


def load(name):
    return json.loads((HERE / name).read_text(encoding='utf-8'))


def coverage(candidates):
    ledger = {}
    for name, c in candidates.items():
        if name in ('LEAK', 'MISSING', 'INVENTED'):
            continue
        text = c['source']['text']
        spans = []
        for o in c['obligations']:
            starts = [m.start() for m in re.finditer(re.escape(o['source_quote']), text)]
            spans.extend((start, start + len(o['source_quote']), o['id']) for start in starts)
        rows = []
        # Preserve source code-point offsets and exact substrings, including
        # B01's line breaks. This is a mechanical locator ledger, not NLP proof.
        for match in re.finditer(r'[^.]+(?:\.|$)', text):
            start, end = match.span()
            while start < end and text[start].isspace():
                start += 1
            while end > start and text[end - 1].isspace():
                end -= 1
            if start == end:
                continue
            ids = sorted({oid for left, right, oid in spans if left < end and right > start})
            fragment = text[start:end]
            if ids:
                disposition = 'OBLIGATION_QUOTE_OVERLAP_REQUIRES_COVERAGE_REVIEW'
            elif 'unspecified' in fragment:
                disposition = 'EXPLICIT_UNSPECIFIED_BEHAVIOR'
            elif 'engine is not prescribed' in fragment:
                disposition = 'IMPLEMENTATION_FREEDOM'
            elif 'Use the complete public' in fragment:
                disposition = 'EXPLICIT_COMPONENT_CONTEXT'
            elif 'No additional supplemental' in fragment:
                disposition = 'EXPLICIT_SUPPLEMENTAL_SCOPE'
            else:
                disposition = 'REQUIRES_REVIEW'
            rows.append({'start': start, 'end': end, 'text': fragment,
                         'obligations': ids, 'disposition': disposition})
        ledger[name] = {'source_commitment': c['source']['sha256'], 'fragments': rows,
                        'active_issues': [i['id'] for i in c['issues']]}
    return {'kind': 'R5.80-code-point-source-locators', 'sources': ledger,
            'limit': 'Quote overlap locates evidence; does not decide fragment completeness or implication entailment. Independent reviews supply those judgments.'}


def run():
    candidates = load('candidates.json')
    receipts = load('reviews.json')['receipts']
    results = {}
    counts = {}
    for name, c in candidates.items():
        outcome = f.review_gate(c, receipts[name])
        counts[outcome] = counts.get(outcome, 0) + 1
        projection = f.project(c, receipts[name])
        results[name] = {'contract_commitment': f.validate(c), 'review': outcome, 'projection': projection}
    summary = {'classification': 'R5_80_REQUIREMENT_FORMALIZATION_PARTIAL',
               'source_candidates': 14, 'adversarial_mutants': 3,
               'review_counts_all_17': counts,
               'approved_projection_attempts': sum(r['review'] == 'APPROVED' for r in results.values()),
               'projected_calibrations': sum(r['projection']['status'] == 'PROJECTED' for r in results.values()),
               'unrepresentable_source': sum(r['projection']['status'] == 'UNREPRESENTABLE_SOURCE' for r in results.values()),
               'results': results,
               'protection': {'scope': 'R5.80 activity, not protected-file/ledger content inspection',
                   'B03_status': ['B03_PRISTINE', 'B03_NOT_EVALUATED', 'B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT'],
                   'source_reads': 0, 'protected_read_attempts': 0, 'formalization_attempts': 0,
                   'packaging_attempts': 0, 'authorizations': 0, 'reservations': 0, 'openings': 0,
                   'observations': 0, 'static_consumer_calls': 0, 'generation': 0,
                   'execution': 0, 'acceptance': 0, 'repair': 0}}
    positive = results['P01']['projection']
    summary['P01_projection_bindings'] = {
        'contract_commitment': f.validate(candidates['P01']),
        'document_commitment': f.digest(positive['document']),
        'coverage_commitment': f.digest(positive['coverage']),
        'behavioral_identity': positive['normalized']['identity']}
    summary['P01_projection_review'] = f.projection_gate(
        candidates['P01'], receipts['P01'], positive, load('projection-review.json'))
    b01 = fixtures.ROOT / 'benchmark/requirements/B01.md'
    # Separate physical provenance from the tool/source-text LF representation.
    raw = b01.read_bytes()
    summary['public_B01_provenance'] = {
        'path': 'benchmark/requirements/B01.md', 'physical_sha256': hashlib.sha256(raw).hexdigest(),
        'contract_text_sha256': candidates['B01']['source']['sha256'],
        'decoded_physical_text_equals_contract_text': raw.decode('utf-8') == candidates['B01']['source']['text'],
        'physical_text_with_newlines_normalized_equals_contract_text': raw.decode('utf-8').replace('\r\n', '\n') == candidates['B01']['source']['text'],
        'rule': 'Contract source is the LF public tool-text transcription; physical bytes are separately committed without modifying B01.'}
    return summary, coverage(candidates)


if __name__ == '__main__':
    evidence, ledger = run()
    for name, value in (('qualification.json', evidence), ('coverage.json', ledger)):
        (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in evidence.items() if k != 'results'}, indent=2))
