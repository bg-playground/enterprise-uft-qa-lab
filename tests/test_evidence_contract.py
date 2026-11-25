import copy
import io
import unittest
from evidence_contract import validate
from run_evidence import Results

class EvidenceSIT(unittest.TestCase):
    def test_sit_018_evidence_contract(self):
        class Example(unittest.TestCase):
            def test_subtests(self):
                for i in range(2):
                    with self.subTest(i=i):
                        self.assertEqual(i,0)
        result=unittest.TextTestRunner(stream=io.StringIO(),resultclass=Results).run(
            unittest.defaultTestLoader.loadTestsFromTestCase(Example))
        self.assertFalse(result.wasSuccessful())
        self.assertEqual(len(result.rows),1)
        self.assertEqual(result.rows[0]['outcome'],'failed')
        payload={'session':{'runner':'test'},'cases':result.rows,
                 'finish':{'status':'failed','summary':{'total':1,'passed':0,'failed':1,'skipped':0}}}
        validate(payload)
        for mutate in (
            lambda p:p['cases'].append(copy.deepcopy(p['cases'][0])),
            lambda p:p['cases'][0].update(duration_ms=-1),
            lambda p:p['finish'].update(status='passed'),
            lambda p:p['finish']['summary'].update(total=2),
            lambda p:p['cases'][0].update(auto_register_requirements=True)):
            broken=copy.deepcopy(payload)
            mutate(broken)
            with self.assertRaises(ValueError): validate(broken)
