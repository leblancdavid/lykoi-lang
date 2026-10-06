"""Fresh corpus producer/authority challenges, independent of old captures."""
import copy
import importlib.util
from pathlib import Path
import unittest

from lykoi_controller import Failure
from lykoi_workspace.query_schema import validate_output
from test_existing_composition import evaluation


class FreshTypedCorpusTests(unittest.TestCase):
    def test_all_twenty_fresh_closed_typed_outputs(self):
        records=evaluation.corpus.captures()
        self.assertEqual([r['id'] for r in records],[f'B{i:02d}' for i in range(1,21)])
        for r in records:
            with self.subTest(case=r['id']):
                validate_output({'obligations':r['rows']})
                self.assertTrue(r['rows']); self.assertEqual(len(r['rows']),len({o['id'] for o in r['rows']}))
                for row in r['rows']:
                    self.assertIn(row['source_quote'],r['source'])
                    p=row['relation']['parameters']
                    self.assertNotIn('meaning',p); self.assertNotIn('obligation_facet',p)
                    self.assertTrue('profile' in p or 'query' in p or 'required_capability' in p)
        self.assertEqual(sum(bool(r['question']) for r in records),2)

    def test_source_ambiguities_block_approval_before_structural(self):
        for record in evaluation.corpus.captures():
            if record['id'] not in ('B17','B20'): continue
            result=evaluation.evaluate(record)
            self.assertEqual(result['first_blocker'],'FORMALIZATION')
            self.assertTrue(all(v=='NOT_REACHED' for k,v in result['stages'].items() if k!='FORMALIZATION'))
            self.assertTrue(result['formalization']['contract']['issues'])

    def test_fresh_scalar_unknown_transform_does_not_claim_existing_support(self):
        record=evaluation.corpus.captures()[3]
        bad=copy.deepcopy(record)
        field=next(o for o in bad['rows'] if o['relation']['parameters']['facet']=='fields')
        field['relation']['parameters']['value'][-1]['preservation']='trimmed'
        with self.assertRaises(Failure): evaluation.evaluate(bad)

    def test_current_query_prerequisite_refusal_is_executed(self):
        record=evaluation.corpus.captures()[2]
        result=evaluation.evaluate(record)
        self.assertEqual(result['first_blocker'],'STRUCTURAL')
        projections=[a['content'] for a in result['audit']['artifacts'].values() if a['type']=='structural' and a['schema']=='sealed-pipeline-1']
        self.assertEqual(len(projections),1); self.assertIn('@query-profile',projections[0]['unsupported'])
        self.assertIn('Unsupported nullable/missing query field',str(projections[0]['profile_failure']))
        self.assertEqual(result['stages']['BDI'],'NOT_REACHED')


if __name__=='__main__': unittest.main()
