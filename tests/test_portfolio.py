import json
import unittest
from pathlib import Path
class PortfolioSIT(unittest.TestCase):
    def test_sit_020_historical_snapshot(self):
        root=Path(__file__).resolve().parents[1]/'portfolio'
        d=json.loads((root/'evidence.json').read_text(encoding='utf-8'))
        self.assertEqual(d['head'],'dd0812267ca079aece96245edcc43fa6126e826e')
        self.assertEqual(d['run'],22)
        self.assertEqual(len(d['jobs']),4)
        self.assertEqual(sum(j['passed'] for j in d['jobs']),57)
        self.assertEqual(sum(j['failed']+j['skipped'] for j in d['jobs']),0)
        self.assertEqual(len({j['artifact'] for j in d['jobs']}),4)
        self.assertIn('Historical',d['note'])
        self.assertNotIn('/api/',(root/'evidence.js').read_text(encoding='utf-8'))
