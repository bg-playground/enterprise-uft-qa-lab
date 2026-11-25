import unittest
import tempfile
import os
from datetime import date
from unittest.mock import patch
import app
import record_policy as policy

class RecordsSIT(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        with patch.object(app,'DB',os.path.join(self.tmp.name,'records.db')):
            self.c=app.connect()
        self.addCleanup(self.c.close)
        app.submit(self.c,'REC001','Synthetic Invoice')
        app.process(self.c,'REC001')
        policy.classify(self.c,'REC001',date(2026,1,1),30)

    def test_sit_012_retention_boundary(self):
        with self.assertRaises(PermissionError):
            policy.dispose(self.c,'REC001',date(2026,1,30))
        self.assertTrue(policy.dispose(self.c,'REC001',date(2026,1,31)))
        row=self.c.execute('SELECT * FROM docs WHERE id=?',('REC001',)).fetchone()
        self.assertEqual(row['status'],'disposed')
        self.assertIsNone(row['pdf'])
        self.assertIsNone(row['digest'])
        self.assertFalse(policy.dispose(self.c,'REC001',date(2026,2,1)))
        with self.assertRaises(ValueError): app.process(self.c,'REC001')
        self.assertEqual(self.c.execute("SELECT count(*) FROM audit WHERE event='disposed'").fetchone()[0],1)

    def test_sit_013_legal_hold(self):
        policy.hold(self.c,'REC001',True)
        policy.hold(self.c,'REC001',True)
        with self.assertRaises(PermissionError):
            policy.dispose(self.c,'REC001',date(2027,1,1))
        self.assertIsNotNone(self.c.execute('SELECT pdf FROM docs').fetchone()[0])
        policy.hold(self.c,'REC001',False)
        self.assertTrue(policy.dispose(self.c,'REC001',date(2027,1,1)))
        self.assertEqual([x[0] for x in self.c.execute('SELECT event FROM audit ORDER BY seq')],
                         ['submitted','archived','classified','hold_set','hold_released','disposed'])

    def test_sit_014_search_and_invalid_classification(self):
        app.submit(self.c,'REC002','Queued Invoice')
        self.assertEqual([r['id'] for r in policy.search(self.c,'invoice')],['REC001'])
        with self.assertRaises(ValueError): policy.classify(self.c,'REC002',date(2026,1,1),30)
        with self.assertRaises(ValueError): policy.classify(self.c,'REC001',date(2026,1,1),0)
        policy.dispose(self.c,'REC001',date(2026,1,31))
        self.assertEqual(policy.search(self.c,'invoice'),[])
