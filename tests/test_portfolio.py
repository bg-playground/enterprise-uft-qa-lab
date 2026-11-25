import json
import unittest
from pathlib import Path
class PortfolioSIT(unittest.TestCase):
    def test_sit_020_historical_snapshot(self):
        root=Path(__file__).resolve().parents[1]/'portfolio'
        d=json.loads((root/'evidence.json').read_text(encoding='utf-8'))
        self.assertEqual(d['head'],'ccd3afa790d24a4c677c598c5a5c89cf05f15b34')
        self.assertEqual(d['run'],14)
        self.assertEqual(len(d['jobs']),4)
        self.assertEqual(sum(j['passed'] for j in d['jobs']),38)
        self.assertEqual(sum(j['failed']+j['skipped'] for j in d['jobs']),0)
        self.assertEqual(len({j['artifact'] for j in d['jobs']}),4)
        self.assertIn('Historical',d['note'])
        self.assertNotIn('/api/',(root/'evidence.js').read_text(encoding='utf-8'))
